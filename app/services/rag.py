import os
import asyncio
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

class RAGService:
    def __init__(self):
        self.vectorstore = PineconeVectorStore(
            index_name=os.getenv("PINECONE_INDEX_NAME"),
            embedding=OpenAIEmbeddings(model="text-embedding-3-small")
        )

    async def get_context(self, query: str, department: str | None = None):
        """
        Retrieves concise, relevant context for voice responses.
        """
        try:
            # Run blocking Pinecone call in thread pool
            docs = await asyncio.to_thread(
                self.vectorstore.similarity_search,
                query,
                3
            )

            if not docs:
                return ""

            # Trim context for voice (important)
            context_chunks = []
            total_chars = 0
            MAX_CHARS = 1200  # ~400 tokens

            for doc in docs:
                text = doc.page_content.strip()
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
