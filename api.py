import logging
from html import escape
from pathlib import Path

import httpx
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from hishel import AsyncCacheTransport, AsyncFileStorage
from starlette.middleware.cors import CORSMiddleware

from models.subtopics import Subtopics

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
logger = logging.getLogger(__name__)
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
    base_path=Path(".cache")
)  # Use AsyncFileStorage for async compatibility

# Create an HTTPX AsyncTransport (default transport)
transport = httpx.AsyncHTTPTransport()

# Wrap the transport with AsyncCacheTransport for caching
cache_transport = AsyncCacheTransport(transport=transport, storage=storage)


@app.get("/api/wikidata")
async def wikidata_proxy(
    srsearch: str = Query(..., description="Search query for Wikidata")
):
    try:
        # Create an async client with caching
        async with httpx.AsyncClient(transport=cache_transport) as client:
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
            return response.json()
    except httpx.HTTPStatusError as e:
        # Handle HTTP errors from the Wikidata API
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Failed to fetch data from Wikidata",
        )
    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail=str(e))
