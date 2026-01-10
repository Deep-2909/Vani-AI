import os
import hashlib
from dotenv import load_dotenv

from pinecone import Pinecone
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()

DATA_DIR = "./data"


def infer_department_from_path(path: str) -> str:
    path = path.lower()
    if "water" in path:
        return "Water (DJB)"
    if "police" in path:
        return "Police"
    if "pollution" in path:
        return "Pollution (DPCC)"
    return "General/PGC"


def run_ingestion():
    print("🔄 Starting ingestion...")

    # 1. Load PDFs
    loader = DirectoryLoader(
        DATA_DIR,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    docs = loader.load()
    print(f"📄 Loaded {len(docs)} pages")

    if not docs:
        print("⚠️ No documents found.")
        return

    # 2. Split documents
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)

    # 3. Initialize embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    # 4. Initialize Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    # 5. Prepare vectors
    vectors = []
    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        chunk_id = hashlib.md5(
            (source + chunk.page_content).encode("utf-8")
        ).hexdigest()

        metadata = {
            "source": source,
            "department": infer_department_from_path(source),
            "text": chunk.page_content
        }

        embedding = embeddings.embed_query(chunk.page_content)

        vectors.append({
            "id": chunk_id,
            "values": embedding,
            "metadata": metadata
        })

    # 6. Upsert to Pinecone
    index.upsert(vectors=vectors)

    print("✅ Knowledge base updated successfully")


if __name__ == "__main__":
    run_ingestion()
