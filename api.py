import asyncio
import logging
from datetime import timedelta
from html import escape
from pathlib import Path

import httpx
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from hishel import AsyncCacheTransport, AsyncFileStorage
from starlette.middleware.cors import CORSMiddleware
from tenacity import wait_exponential, stop_after_attempt, retry_if_exception_type, retry

from models.subtopics import Subtopics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI
app = FastAPI()
router = APIRouter(prefix="/v0")  # Adds /v0/ to all endpoints
# Allow all origins (you can restrict this to just your frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:3000"] to be more secure
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
documentation_url = ""  # todo add documentation_url


@app.get("/subtopics")
def subtopics(
    lang: str = Query("en", alias="lang"),
    qid: str = Query("", alias="qid"),
):
    lang = escape(lang)
    qid = escape(qid)

    if not qid:
        return JSONResponse(content={"error": "Got no QID"}, status_code=400)
    if not lang:
        return JSONResponse(content={"error": "Got no language code"}, status_code=400)
    else:
        subtopics_ = Subtopics(
            qid=qid,
            lang=lang,
        )
        subtopics_.fetch_and_parse()
        return JSONResponse(
            content={
                "message": "Success",
                "subtopics": subtopics.subtopics_json,
                "lang": lang,
                "qid": qid,
            }
        )


# Initialize an asynchronous file-based cache
storage = AsyncFileStorage(
    base_path=Path(".cache",
                   ttl=timedelta(
                       hours=1
                       #seconds=5
                   ).total_seconds())
)  # Use AsyncFileStorage for async compatibility

# Create an HTTPX AsyncTransport (default transport)
transport = httpx.AsyncHTTPTransport()

# Wrap the transport with AsyncCacheTransport for caching
cache_transport = AsyncCacheTransport(transport=transport, storage=storage)

# Create a semaphore to limit concurrent requests
semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent requests


# Retry configuration for the proxy server
@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),  # Exponential backoff (1s, 2s, 4s, ...)
    stop=stop_after_attempt(3),  # Stop after 5 attempts
    retry=retry_if_exception_type((httpx.HTTPStatusError, ValueError)),  # Retry on HTTP errors or invalid response
)
async def fetch_wikidata_data(client, srsearch):
    """
    Fetch data from the Wikidata API with retries.
    """
    logger.debug(f"Sending request to Wikidata API with srsearch: {srsearch}")
    response = await client.get(
        "https://www.wikidata.org/w/api.php",
        params={
            "action": "query",
            "format": "json",
            "list": "search",
            "formatversion": 2,
            "srsearch": srsearch,
            "srlimit": 1,
            "srprop": "size",
        },
    )
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Validate the response structure
    # if not response.json().get("query", {}).get("searchinfo", {}).get("totalhits"):
    #     raise ValueError("Invalid response structure from Wikidata API")

    return response.json()


@app.get("/api/wikidata")
async def wikidata_proxy(srsearch: str = Query(..., description="Search query for Wikidata")):
    try:
        logger.debug(f"Received request with srsearch: {srsearch}")

        # Create an async client with caching
        async with httpx.AsyncClient(transport=cache_transport) as client:
            # Fetch data from Wikidata with retries
            data = await fetch_wikidata_data(client, srsearch)

            # If all retries fail, return a default response
            if not data:
                logger.warning("All retries failed. Returning default response.")
                return {"error": "Could not get data from Wikidata"}

            return data
    except Exception as e:
        # Log other errors
        logger.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))