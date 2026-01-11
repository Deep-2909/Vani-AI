import os
import hashlib
from dotenv import load_dotenv
from pathlib import Path

from pinecone import Pinecone
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()

DATA_DIR = "./data"


def infer_department_from_path(path: str) -> str:
    """Infer department from file path or name"""
    path = path.lower()
    
    if "water" in path or "djb" in path or "jal" in path:
        return "Water (DJB)"
    if "police" in path or "law" in path or "crime" in path:
        return "Police"
    if "pollution" in path or "dpcc" in path or "air" in path or "environment" in path:
        return "Pollution (DPCC)"
    if "road" in path or "pwd" in path or "pothole" in path:
        return "Roads (PWD)"
    if "electricity" in path or "power" in path:
        return "Electricity"
    if "health" in path or "hospital" in path:
        return "Health"
    if "education" in path or "school" in path:
        return "Education"
    
    return "General/PGC"


def load_single_pdf(file_path: str):
    """
    Load a single PDF file with error handling.
    Returns list of documents or empty list if failed.
    """
    try:
        print(f"  📄 Loading: {os.path.basename(file_path)}")
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        print(f"    ✅ Loaded {len(docs)} pages")
        return docs
    except Exception as e:
        print(f"    ❌ Failed to load: {str(e)[:100]}")
        return []


def load_single_text(file_path: str):
    """
    Load a single text file with error handling.
    """
    try:
        print(f"  📄 Loading: {os.path.basename(file_path)}")
        loader = TextLoader(file_path)
        docs = loader.load()
        print(f"    ✅ Loaded text file")
        return docs
    except Exception as e:
        print(f"    ❌ Failed to load: {str(e)[:100]}")
        return []


def load_all_documents(data_dir: str):
    """
    Load all documents from data directory with robust error handling.
    Supports PDF and TXT files.
    """
    all_docs = []
    failed_files = []
    successful_files = []
    
    # Get all files
    data_path = Path(data_dir)
    pdf_files = list(data_path.glob("**/*.pdf"))
    txt_files = list(data_path.glob("**/*.txt"))
    
    print(f"\n📂 Found {len(pdf_files)} PDF files and {len(txt_files)} text files")
    print("=" * 70)
    
    # Process PDFs
    print("\n📚 Processing PDF files...")
    for pdf_file in pdf_files:
        docs = load_single_pdf(str(pdf_file))
        if docs:
            all_docs.extend(docs)
            successful_files.append(str(pdf_file))
        else:
            failed_files.append(str(pdf_file))
    
    # Process text files
    if txt_files:
        print("\n📝 Processing text files...")
        for txt_file in txt_files:
            docs = load_single_text(str(txt_file))
            if docs:
                all_docs.extend(docs)
                successful_files.append(str(txt_file))
            else:
                failed_files.append(str(txt_file))
    
    return all_docs, successful_files, failed_files


def validate_pdf(file_path: str) -> bool:
    """
    Quick validation to check if file is a valid PDF.
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except:
        return False


def scan_and_report_files(data_dir: str):
    """
    Scan data directory and report on file status.
    """
    print("\n🔍 Scanning data directory...")
    print("=" * 70)
    
    data_path = Path(data_dir)
    pdf_files = list(data_path.glob("**/*.pdf"))
    
    valid_pdfs = []
    invalid_pdfs = []
    
    for pdf_file in pdf_files:
        if validate_pdf(str(pdf_file)):
            valid_pdfs.append(pdf_file)
        else:
            invalid_pdfs.append(pdf_file)
    
    print(f"\n✅ Valid PDFs: {len(valid_pdfs)}")
    for pdf in valid_pdfs:
        print(f"   - {pdf.name}")
    
    if invalid_pdfs:
        print(f"\n❌ Invalid/Corrupted PDFs: {len(invalid_pdfs)}")
        for pdf in invalid_pdfs:
            print(f"   - {pdf.name}")
        print("\n💡 These files will be skipped during ingestion.")
        print("   Consider removing or re-downloading them.")
    
    return valid_pdfs, invalid_pdfs


def run_ingestion():
    print("=" * 70)
    print("🔄 STARTING KNOWLEDGE BASE INGESTION")
    print("=" * 70)
    
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"\n❌ Error: Data directory '{DATA_DIR}' not found!")
        print("💡 Please create the directory and add your documents.")
        return
    
    # Scan and report files
    valid_pdfs, invalid_pdfs = scan_and_report_files(DATA_DIR)
    
    if not valid_pdfs:
        print("\n❌ No valid documents found in data directory!")
        return
    
    # Confirm before proceeding
    print("\n" + "=" * 70)
    response = input("Continue with ingestion? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Ingestion cancelled.")
        return
    
    # Load documents
    print("\n" + "=" * 70)
    print("📚 LOADING DOCUMENTS")
    print("=" * 70)
    
    docs, successful_files, failed_files = load_all_documents(DATA_DIR)
    
    # Report results
    print("\n" + "=" * 70)
    print("📊 LOADING SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully loaded: {len(successful_files)} files")
    print(f"📄 Total pages/chunks: {len(docs)}")
    
    if failed_files:
        print(f"\n❌ Failed to load: {len(failed_files)} files")
        for file in failed_files:
            print(f"   - {os.path.basename(file)}")
        print("\n💡 These files were skipped. Check if they are corrupted.")
    
    if not docs:
        print("\n❌ No documents were loaded successfully!")
        return
    
    # Split documents
    print("\n" + "=" * 70)
    print("✂️  SPLITTING DOCUMENTS")
    print("=" * 70)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ Created {len(chunks)} text chunks")
    
    # Initialize embeddings
    print("\n" + "=" * 70)
    print("🧠 CREATING EMBEDDINGS")
    print("=" * 70)
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )
    print("✅ Embeddings model initialized")
    
    # Initialize Pinecone
    print("\n" + "=" * 70)
    print("📌 CONNECTING TO PINECONE")
    print("=" * 70)
    
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        print("✅ Connected to Pinecone")
    except Exception as e:
        print(f"❌ Failed to connect to Pinecone: {e}")
        return
    
    # Prepare vectors
    print("\n" + "=" * 70)
    print("🔧 PREPARING VECTORS")
    print("=" * 70)
    
    vectors = []
    batch_size = 100
    
    for i, chunk in enumerate(chunks):
        if i % batch_size == 0:
            print(f"  Processing chunk {i+1}/{len(chunks)}...")
        
        try:
            source = chunk.metadata.get("source", "unknown")
            chunk_id = hashlib.md5(
                (source + chunk.page_content).encode("utf-8")
            ).hexdigest()
            
            metadata = {
                "source": os.path.basename(source),
                "full_path": source,
                "department": infer_department_from_path(source),
                "text": chunk.page_content[:1000],  # Limit text size
                "page": chunk.metadata.get("page", 0)
            }
            
            embedding = embeddings.embed_query(chunk.page_content)
            
            vectors.append({
                "id": chunk_id,
                "values": embedding,
                "metadata": metadata
            })
        except Exception as e:
            print(f"  ⚠️  Error processing chunk {i}: {str(e)[:50]}")
            continue
    
    print(f"✅ Prepared {len(vectors)} vectors")
    
    # Upsert to Pinecone in batches
    print("\n" + "=" * 70)
    print("☁️  UPLOADING TO PINECONE")
    print("=" * 70)
    
    batch_size = 100
    total_batches = (len(vectors) + batch_size - 1) // batch_size
    
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        try:
            index.upsert(vectors=batch)
            print(f"  ✅ Uploaded batch {batch_num}/{total_batches} ({len(batch)} vectors)")
        except Exception as e:
            print(f"  ❌ Failed to upload batch {batch_num}: {str(e)[:100]}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ INGESTION COMPLETE!")
    print("=" * 70)
    print(f"\n📊 FINAL STATISTICS:")
    print(f"   • Files processed: {len(successful_files)}")
    print(f"   • Files failed: {len(failed_files)}")
    print(f"   • Total pages: {len(docs)}")
    print(f"   • Text chunks: {len(chunks)}")
    print(f"   • Vectors uploaded: {len(vectors)}")
    print(f"\n💡 Your knowledge base is ready!")
    print(f"   The AI can now answer questions based on these documents.")


def ingest_single_file(file_path: str) -> dict:
    """
    Ingest a single file into Pinecone vector database.
    Returns a dict with success status and message.

    Args:
        file_path: Path to the file to ingest (PDF or TXT)

    Returns:
        dict: {"success": bool, "message": str, "chunks": int}
    """
    print(f"🔄 Starting ingestion for: {os.path.basename(file_path)}")

    # Check if file exists
    if not os.path.exists(file_path):
        return {
            "success": False,
            "message": f"File not found: {file_path}",
            "chunks": 0
        }

    # Validate file type
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in ['.pdf', '.txt']:
        return {
            "success": False,
            "message": f"Unsupported file type: {file_ext}. Only PDF and TXT are supported.",
            "chunks": 0
        }

    # Load the single file
    docs = []
    try:
        if file_ext == '.pdf':
            # Validate PDF first
            if not validate_pdf(file_path):
                return {
                    "success": False,
                    "message": "Invalid PDF file. File may be corrupted or not a real PDF.",
                    "chunks": 0
                }
            print(f"  📄 Loading PDF...")
            docs = load_single_pdf(file_path)
        elif file_ext == '.txt':
            print(f"  📄 Loading text file...")
            docs = load_single_text(file_path)

        if not docs:
            return {
                "success": False,
                "message": "Failed to load document. File may be corrupted.",
                "chunks": 0
            }

        print(f"  ✅ Loaded {len(docs)} pages/sections")

    except Exception as e:
        return {
            "success": False,
            "message": f"Error loading file: {str(e)[:100]}",
            "chunks": 0
        }

    # Split documents
    print("  ✂️  Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    print(f"  ✅ Created {len(chunks)} text chunks")

    # Initialize embeddings
    print("  🧠 Creating embeddings...")
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to initialize embeddings: {str(e)[:100]}",
            "chunks": 0
        }

    # Initialize Pinecone
    print("  📌 Connecting to Pinecone...")
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to connect to Pinecone: {str(e)[:100]}",
            "chunks": 0
        }

    # Prepare vectors
    print("  🔧 Preparing vectors...")
    vectors = []

    for i, chunk in enumerate(chunks):
        try:
            source = chunk.metadata.get("source", file_path)
            chunk_id = hashlib.md5(
                (source + chunk.page_content).encode("utf-8")
            ).hexdigest()

            metadata = {
                "source": os.path.basename(source),
                "full_path": source,
                "department": infer_department_from_path(source),
                "text": chunk.page_content[:1000],
                "page": chunk.metadata.get("page", 0)
            }

            embedding = embeddings.embed_query(chunk.page_content)

            vectors.append({
                "id": chunk_id,
                "values": embedding,
                "metadata": metadata
            })
        except Exception as e:
            print(f"    ⚠️  Error processing chunk {i}: {str(e)[:50]}")
            continue

    if not vectors:
        return {
            "success": False,
            "message": "Failed to create vectors from document",
            "chunks": 0
        }

    print(f"  ✅ Prepared {len(vectors)} vectors")

    # Upsert to Pinecone in batches
    print("  ☁️  Uploading to Pinecone...")
    batch_size = 100
    total_batches = (len(vectors) + batch_size - 1) // batch_size
    uploaded_count = 0

    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        batch_num = (i // batch_size) + 1

        try:
            index.upsert(vectors=batch)
            uploaded_count += len(batch)
            print(f"    ✅ Uploaded batch {batch_num}/{total_batches} ({len(batch)} vectors)")
        except Exception as e:
            print(f"    ❌ Failed to upload batch {batch_num}: {str(e)[:100]}")

    # Success!
    print(f"✅ Ingestion complete for {os.path.basename(file_path)}")
    return {
        "success": True,
        "message": f"Successfully ingested {os.path.basename(file_path)}",
        "chunks": uploaded_count
    }


if __name__ == "__main__":
    run_ingestion()
