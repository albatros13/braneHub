import os
from api.qdrant_remote_client import get_remote_client

# Llama
from llama_index.core import SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core.indices import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore

COLLECTION_NAME = "compliance_collection"
INDEX_PATH = "/static/data/compliance_index"


def get_documents(input_dir, required_exts=None):
    """
    Load documents from a local folder
    :param input_dir:
    :param required_exts:
    :return:
    """
    relative_fn = lambda filename: {
        "file_id": os.path.basename(filename),
        "file_path": filename[filename.find('static'):]
    }
    return SimpleDirectoryReader(input_dir=input_dir, recursive=True, file_metadata=relative_fn, required_exts=required_exts).load_data()


def build_text_index_remote():
    """
    Create a QDrant remote store
    :return:
    """
    client = get_remote_client()

    chunk_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)
    storage_context = StorageContext.from_defaults(vector_store=chunk_store)
    documents = get_documents("static/compliance/", required_exts=[".txt"])
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    index.storage_context.persist(persist_dir="."+INDEX_PATH)


def update_text_index_remote(documents):
    client = get_remote_client()
    text_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME, access="w")
    storage_context = StorageContext.from_defaults(vector_store=text_store, persist_dir=".."+INDEX_PATH)
    index = load_index_from_storage(storage_context)
    index.refresh_ref_docs(documents)
    index.storage_context.persist(persist_dir=".."+INDEX_PATH)


if __name__ == "__main__":
    docs = get_documents()
    build_text_index_remote()