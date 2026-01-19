import os
from qdrant_client import QdrantClient
import logging
from importlib.metadata import version
import re
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct
)

print("Qdrant client version:", version("qdrant-client"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not (QDRANT_URL and QDRANT_API_KEY):
    logger.error("❌ Configuration error: QDRANT_URL or QDRANT_API_KEY not found in environment or .env file.")
    raise RuntimeError(
        "Configuration error: QDRANT_URL or QDRANT_API_KEY not found. "
        "Please set it as an environment variable or in your .env file."
    )

def get_remote_client():
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        https=True
)


model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
VECTOR_SIZE = model.get_sentence_embedding_dimension()
DEFAULT_COLLECTION_NAME = "compliance_collection"


def _process_text_to_points(text):
    sections = [sec.strip() for sec in re.split(r"\n\s*\n", text) if sec.strip()]
    points = []
    for sec in sections:
        embedding = model.encode(sec).tolist()
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={"text": sec}
            )
        )
    return points


def build_text_index_remote(text, collection_name=DEFAULT_COLLECTION_NAME):
    qdrant = get_remote_client()

    if qdrant.collection_exists(collection_name):
        qdrant.delete_collection(collection_name)

    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )

    points = _process_text_to_points(text)

    qdrant.upsert(
        collection_name=collection_name,
        points=points
    )
    print(f"Inserted {len(points)} sections into Qdrant.")


def update_text_index_remote(text, collection_name=DEFAULT_COLLECTION_NAME):
    qdrant = get_remote_client()

    if not qdrant.collection_exists(collection_name):
        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )

    points = _process_text_to_points(text)

    qdrant.upsert(
        collection_name=collection_name,
        points=points
    )
    print(f"Updated {collection_name} with {len(points)} sections.")


def ask(query: str, top_k=5, collection_name=DEFAULT_COLLECTION_NAME):
    qdrant = get_remote_client()
    query_emb = model.encode(query).tolist()
    results = qdrant.search(
        collection_name=collection_name,
        query_vector=query_emb,
        limit=top_k
    )
    return [(hit.score, hit.payload["text"]) for hit in results]
