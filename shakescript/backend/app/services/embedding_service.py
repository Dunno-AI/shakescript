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
        auth_id: str,
    ):
        doc = Document(text=content)
        nodes = self.splitter.get_nodes_from_documents([doc])
        characters_json = json.dumps(characters)

        chunk_data = []
        for chunk_number, node in enumerate(nodes):
            chunk_text = node.text
            embedding = self.embedding_model.get_text_embedding(chunk_text)
            importance_score = self._calculate_importance_score(
                story_id, chunk_text, characters, episode_number
            )

            chunk_data.append(
                {
                    "story_id": story_id,
                    "episode_id": episode_id,
                    "episode_number": episode_number,
                    "chunk_number": chunk_number,
                    "content": chunk_text,
                    "characters": characters_json,
                    "embedding": "[" + ",".join(map(str, embedding)) + "]",
                    "importance_score": importance_score,
                    "auth_id": auth_id,  # Add auth_id for RLS
                }
            )

        result = (
            self.db_service.supabase.table("chunks")
            .insert(chunk_data)
            .eq("auth_id", auth_id)  # Enforce RLS
            .execute()
        )
        if not result.data:
            raise ValueError("Failed to store chunks in the database")

    def retrieve_relevant_chunks(
        self,
        story_id: int,
        current_episode_info: str,
        k: int = 5,
        character_names: List[str] = [],
        auth_id: str = None,
    ) -> List[Dict]:
        query_embedding = self.embedding_model.get_text_embedding(current_episode_info)
        query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        query = (
            self.db_service.supabase.table("chunks")
            .select(
                "id, episode_number, chunk_number, content, importance_score, embedding"
            )
            .eq("story_id", story_id)
            .eq("auth_id", auth_id)  # Enforce RLS
        )
        if character_names:
            query = query.contains(
                "characters", json.dumps(character_names)
            )  # Ensure JSON compatibility

        # Perform similarity search using embedding (pseudo-code; adjust based on Supabase vector support)
        chunks_result = query.order("importance_score", desc=True).limit(k).execute()

        # Add foundational chunks
        foundational_chunks = (
            self.db_service.supabase.table("chunks")
            .select("id, episode_number, chunk_number, content, importance_score")
            .eq("story_id", story_id)
            .eq("auth_id", auth_id)  # Enforce RLS
            .in_(
                "episode_number",
                [
                    1,
                    int(
                        self.db_service.get_story_info(story_id, auth_id)[
                            "num_episodes"
                        ]
                        * 0.5
                    ),
                ],
            )
            .limit(2)
            .execute()
        )

        chunks = (chunks_result.data or []) + (foundational_chunks.data or [])
        return [
            {
                "id": chunk["id"],
                "episode_number": chunk["episode_number"],
                "chunk_number": chunk["chunk_number"],
                "content": chunk["content"],
            }
            for chunk in sorted(
                chunks, key=lambda x: (x.get("importance_score", 0)), reverse=True
            )[:k]
        ]

    def _calculate_importance_score(
        self, story_id: int, chunk: str, characters: List[str], episode_number: int
    ) -> float:
        score = 0
        # Boost for key characters
        for char in characters:
            if char.lower() in chunk.lower():
                score += 1
        # Boost for early or midpoint episodes
        story_info = self.db_service.get_story_info(story_id)
        if episode_number == 1 or episode_number == int(
            story_info["num_episodes"] * 0.5
        ):
            score += 2
        return score
