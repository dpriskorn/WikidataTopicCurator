import asyncio
import logging
from datetime import timedelta
from html import escape
from pathlib import Path

import httpx
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from hishel import AsyncCacheTransport, AsyncFileStorage
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from starlette.middleware.cors import CORSMiddleware
from tenacity import (
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
    retry,
)
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from contextlib import asynccontextmanager

from models.subtopics import Subtopics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the tracer provider
trace_provider = TracerProvider()

# Set up OTLP exporter to send traces to Tempo
#otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)

# Add the OTLP exporter to the tracer provider
#trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

# Add a console exporter for demonstration purposes
#trace_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

# Set the global tracer provider
trace.set_tracer_provider(trace_provider)


# FastAPI Application Setup
app = FastAPI()

# Apply OpenTelemetry instrumentation before app starts
FastAPIInstrumentor.instrument_app(app)  # ✅ Pass an instance
RequestsInstrumentor().instrument()

# Apply Prometheus instrumentation before app starts
instrumentator = Instrumentator().instrument(app)  # ✅ Move out of lifespan

# Define lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    instrumentator.expose(app)  # ✅ Only expose here, not instrument
    yield  # The application is now running

# Assign lifespan function after middleware is set
app.router.lifespan_context = lifespan

# Allow all origins (adjust for security needs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

documentation_url = ""  # TODO: Add documentation URL
router = APIRouter(prefix="/v0")


@router.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})


@router.get("/subtopics")
def subtopics(
    lang: str = Query("en", alias="lang"),
    qid: str = Query("", alias="qid"),
):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("subtopics_endpoint") as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.route", "/subtopics")
        span.set_attribute("query.lang", lang)
        span.set_attribute("query.qid", qid)
        lang = escape(lang)
        qid = escape(qid)

        if not qid:
            with tracer.start_as_current_span("error_handling"):
                return JSONResponse(content={"error": "Got no QID"}, status_code=400)
        if not lang:
            with tracer.start_as_current_span("error_handling"):
                return JSONResponse(content={"error": "Got no language code"}, status_code=400)
        else:
            with tracer.start_as_current_span("fetch_and_parse_subtopics"):
                topics = Subtopics(qid=qid, lang=lang)
                topics.fetch_and_parse()
                return JSONResponse(
                    content={
                        "message": "Success",
                        "subtopics": topics.subtopics_json,
                        "lang": lang,
                        "qid": qid,
                    }
                )

# Initialize an asynchronous file-based cache
storage = AsyncFileStorage(
    base_path=Path(".cache"),
    ttl=timedelta(hours=1).total_seconds(),
)

# Create an HTTPX AsyncTransport (default transport)
transport = httpx.AsyncHTTPTransport()

# Wrap the transport with AsyncCacheTransport for caching
cache_transport = AsyncCacheTransport(transport=transport, storage=storage)

# Create a semaphore to limit concurrent requests
semaphore = asyncio.Semaphore(10)

# Retry configuration for the proxy server
@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((httpx.HTTPStatusError, ValueError)),
)
async def fetch_wikidata_data(client, srsearch):
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
    response.raise_for_status()
    return response.json()

@router.get("/api/wikidata")
async def wikidata_proxy(srsearch: str = Query(..., description="Search query for Wikidata")):
    try:
        logger.debug(f"Received request with srsearch: {srsearch}")
        async with httpx.AsyncClient(transport=cache_transport) as client:
            data = await fetch_wikidata_data(client, srsearch)
            if not data:
                logger.warning("All retries failed. Returning default response.")
                return {"error": "Could not get data from Wikidata"}
            return data
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router)
