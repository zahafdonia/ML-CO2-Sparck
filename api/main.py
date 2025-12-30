import pandas as pd
import json
import asyncio
import os
import logging
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Dict, Any

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CO2-Streaming-API")

# ================= APP =================
app = FastAPI(
    title="CO2 Streaming API",
    description="Stream CSV records as NDJSON for Kafka ingestion",
    version="1.0.0"
)

# ================= CONFIG =================
CSV_FILE = "/data/co2_processed.csv"
STREAM_DELAY = 0.5  # seconds

# ================= CSV ITERATOR =================
def csv_iterator(file_path: str):
    if not os.path.exists(file_path):
        logger.error(f"CSV file not found: {file_path}")
        raise FileNotFoundError(f"CSV not found: {file_path}")

    df = pd.read_csv(file_path)
    logger.info(f"CSV loaded with {len(df)} rows")

    while True:  # LOOP INFINI (Kappa)
        for _, row in df.iterrows():
            yield row.to_dict()

# ================= STREAM =================
async def stream_csv() -> AsyncGenerator[str, None]:
    try:
        for record in csv_iterator(CSV_FILE):
            yield json.dumps(record) + "\n"
            await asyncio.sleep(STREAM_DELAY)
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield json.dumps({"error": str(e)}) + "\n"

# ================= ENDPOINT =================
@app.get(
    "/stream",
    summary="Stream CO2 data",
    description="Returns CO2 vehicle data as NDJSON stream"
)
async def stream_endpoint():
    return StreamingResponse(
        stream_csv(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
