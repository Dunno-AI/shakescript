from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.schema import Document
from app.core.config import settings
from app.services.db_service import DBService
from typing import List, Dict
import json


class EmbeddingService:
    def __init__(self):
        self.embedding_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)
        self.db_service = DBService()
        self.splitter = SemanticSplitterNodeParser(
            buffer_size=1,
            breakpoint_percentile_threshold=95,
            embed_model=self.embedding_model,
        )

    def _process_and_store_chunks(
        self,
        story_id: int,
        episode_id: int,
        episode_number: int,
        content: str,
        characters: List[str],
    ):
        """Process episode content into semantic chunks and store them with embeddings."""
        doc = Document(text=content)
        nodes = self.splitter.get_nodes_from_documents([doc])
        characters_json = json.dumps(characters)

        for chunk_number, node in enumerate(nodes):
            chunk_text = node.text
            embedding = self.embedding_model.get_text_embedding(chunk_text)
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"

            result = (
                self.db_service.supabase.table("chunks")
                .insert(
                    {
                        "story_id": story_id,
                        "episode_id": episode_id,
                        "episode_number": episode_number,
                        "chunk_number": chunk_number,
                        "content": chunk_text,
                        "characters": characters_json,
                        "embedding": embedding_str,
                    }
                )
                .execute()
            )

            if not result.data:
                print(f"Failed to store chunk {chunk_number} for episode {episode_id}")

    def retrieve_relevant_chunks(
        self, story_id: int, current_episode_info: str, k: int = 3
    ) -> List[Dict]:
        """Retrieve the most relevant chunks using pgvector similarity search."""
        query_embedding = self.embedding_model.get_text_embedding(current_episode_info)
        query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        chunks_result = self.db_service.supabase.rpc(
            "match_chunks",
            {"story_id": story_id, "query_embedding": query_embedding_str, "k": k},
        ).execute()

        if not chunks_result.data or len(chunks_result.data) == 0:
            return []

        return [
            {
                "id": chunk["id"],
                "episode_number": chunk["episode_number"],
                "chunk_number": chunk["chunk_number"],
                "content": chunk["content"],
                "characters": chunk["characters"],
            }
            for chunk in chunks_result.data
        ]
