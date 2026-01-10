import os
import asyncio
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings


class RAGService:
    def __init__(self):
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(os.getenv("PINECONE_INDEX_NAME"))

        # Embeddings (same model as ingestion)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

    async def get_context(self, query: str, department: str | None = None):
        """
        Retrieves concise, relevant context for voice responses.
        Functionality preserved exactly as before.
        """
        try:
            # Create query embedding (run sync code in thread)
            query_embedding = await asyncio.to_thread(
                self.embeddings.embed_query,
                query
            )

            # Query Pinecone (run sync call in thread)
            results = await asyncio.to_thread(
                self.index.query,
                vector=query_embedding,
                top_k=3,
                include_metadata=True
            )

            matches = results.get("matches", [])
            if not matches:
                return ""

            # Trim context for voice (IMPORTANT – preserved)
            context_chunks = []
            total_chars = 0
            MAX_CHARS = 1200  # ~400 tokens

            for match in matches:
                metadata = match.get("metadata", {})
                text = metadata.get("text", "").strip()

                if not text:
                    continue

                if total_chars + len(text) > MAX_CHARS:
                    break

                context_chunks.append(text)
                total_chars += len(text)

            return "\n\n---\n\n".join(context_chunks)

        except Exception as e:
            print("⚠️ RAG ERROR:", e)
            return ""
