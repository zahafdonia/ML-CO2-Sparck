import json
import time
import logging
import requests
from kafka import KafkaProducer
from typing import Dict, Any

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KafkaProducer")

# ================= CONFIG =================
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "streaming_data"

API_URL = "http://api:8000/stream"  # nom du service docker
MAX_RETRIES = 5
RETRY_DELAY = 5

# ================= PRODUCER =================
class StreamProducer:

    def __init__(self):
        self.producer = self._connect_kafka()

    def _connect_kafka(self) -> KafkaProducer:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                producer = KafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    retries=3,
                    linger_ms=10
                )
                logger.info("✅ Connected to Kafka")
                return producer
            except Exception as e:
                logger.warning(f"Kafka connection failed ({attempt}/{MAX_RETRIES}): {e}")
                time.sleep(RETRY_DELAY)

        raise RuntimeError("❌ Unable to connect to Kafka")

    def stream_from_api(self):
        """Lit des objets JSON depuis FastAPI"""
        while True:
            try:
                with requests.get(API_URL, stream=True, timeout=10) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            yield json.loads(line)
            except Exception as e:
                logger.error(f"API error: {e}")
                time.sleep(RETRY_DELAY)

    def send_record(self, record: Dict[str, Any]):
        """Envoie UN enregistrement à Kafka"""
        try:
            self.producer.send(KAFKA_TOPIC, value=record)
            self.producer.flush()
        except Exception as e:
            logger.error(f"Kafka send failed: {e}")

    def run(self):
        logger.info("🚀 Kafka Producer started")
        for record in self.stream_from_api():
            self.send_record(record)
            time.sleep(0.5)  # contrôle du débit

# ================= MAIN =================
if __name__ == "__main__":
    producer = StreamProducer()
    producer.run()
