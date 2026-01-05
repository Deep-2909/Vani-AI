import os
import hashlib
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

DATA_DIR = "./data"

def run_ingestion():
    print("🔄 Starting ingestion...")

    loader = DirectoryLoader(
        DATA_DIR,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    docs = loader.load()
    print(f"📄 Loaded {len(docs)} pages")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,      # voice-optimized
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)

    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        chunk_id = hashlib.md5(
            (source + chunk.page_content).encode("utf-8")
        ).hexdigest()

        chunk.metadata.update({
            "chunk_id": chunk_id,
            "source": source,
            "department": infer_department_from_path(source)
        })

    PineconeVectorStore.from_documents(
        chunks,
        OpenAIEmbeddings(model="text-embedding-3-small"),
        index_name=os.getenv("PINECONE_INDEX_NAME")
    )

    print("✅ Knowledge base updated successfully")


def infer_department_from_path(path: str) -> str:
    path = path.lower()
    if "water" in path:
        return "Water (DJB)"
    if "police" in path:
        return "Police"
    if "pollution" in path:
        return "Pollution (DPCC)"
    return "General/PGC"


if __name__ == "__main__":
    run_ingestion()
