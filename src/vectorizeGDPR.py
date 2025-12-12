import re
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct
)
from llama_index.readers.file import PDFReader  # you can replace with PyPDF if you prefer


# ---------------------------
# 1) Load PDF + Split Sections
# ---------------------------
pdf_path = "../static/compliance/gdpr.pdf"
pdf_reader = PDFReader()
raw_docs = pdf_reader.load_data(file=pdf_path)

# Concatenate pages
full_text = "\n".join([doc.text for doc in raw_docs])

# Split on empty lines (section-level chunks)
sections = [sec.strip() for sec in re.split(r"\n\s*\n", full_text) if sec.strip()]


# ---------------------------
# 2) Load Sentence Transformer
# ---------------------------
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
VECTOR_SIZE = model.get_sentence_embedding_dimension()


# ---------------------------
# 3) Connect to Qdrant
# ---------------------------
qdrant = QdrantClient(
    url="YOUR_QDRANT_URL",
    api_key="YOUR_API_KEY"
)

collection_name = "gdpr_sections"


# ---------------------------
# 4) Create Qdrant Collection
# ---------------------------
qdrant.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=VECTOR_SIZE,
        distance=Distance.COSINE
    )
)


# ---------------------------
# 5) Insert Embeddings
# ---------------------------
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

qdrant.upsert(
    collection_name=collection_name,
    points=points
)


print(f"Inserted {len(points)} sections into Qdrant.")


# ---------------------------
# 6) Semantic Query
# ---------------------------
def ask(query: str, top_k=5):
    query_emb = model.encode(query).tolist()

    results = qdrant.search(
        collection_name=collection_name,
        query_vector=query_emb,
        limit=top_k
    )

    return [(hit.score, hit.payload["text"]) for hit in results]


# ---------------------------
# 7) Example Query
# ---------------------------
answers = ask("What are the data subject rights under GDPR?")
print("\nTop Answers:\n")
for score, text in answers:
    print(f"- Score {score:.4f} → {text[:300]}...\n")
