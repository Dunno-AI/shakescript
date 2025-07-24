from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.schema import Document
from app.core.config import settings
from app.services.db_service import DBService
from typing import List, Dict
import json
from supabase import Client


class EmbeddingService:
    def __init__(self, client: Client):
        """
        FIX: Initializes with the authenticated client passed from the parent service.
        """
        self.embedding_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)
        # Use the passed-in authenticated client to initialize DBService
        self.db_service = DBService(client)
        self.splitter = SemanticSplitterNodeParser(
            buffer_size=1,
            breakpoint_percentile_threshold=95,
            embed_model=self.embedding_model,
        )
        # Keep a direct reference to the authenticated client for its own use
        self.client = client

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

        chunk_data = []
        for chunk_number, node in enumerate(nodes):
            chunk_text = node.text
            embedding = self.embedding_model.get_text_embedding(chunk_text)
            # FIX: Pass auth_id down to the calculation method
            importance_score = self._calculate_importance_score(
                story_id, chunk_text, characters, episode_number, auth_id
            )

            chunk_data.append(
                {
                    "story_id": story_id,
                    "episode_id": episode_id,
                    "episode_number": episode_number,
                    "chunk_number": chunk_number,
                    "content": chunk_text,
                    "characters": json.dumps(
                        characters
                    ),  # Keep as JSON string as per original
                    "embedding": embedding,  # Pass as native list
                    "importance_score": importance_score,
                    "auth_id": auth_id,
                }
            )

        if not chunk_data:
            return

        # FIX: The .eq() call after .insert() is invalid.
        # RLS is enforced because auth_id is part of the data being inserted.
        result = self.client.table("chunks").insert(chunk_data).execute()

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

        # FIX: Add a check for auth_id to fail early.
        if not auth_id:
            raise ValueError("auth_id is required to retrieve relevant chunks")

        query = (
            self.client.table("chunks")
            .select("id, episode_number, chunk_number, content, importance_score")
            .eq("story_id", story_id)
            .eq("auth_id", auth_id)
        )

        if character_names:
            query = query.contains("characters", json.dumps(character_names))

        chunks_result = query.order("importance_score", desc=True).limit(k).execute()

        # Add foundational chunks
        story_info = self.db_service.get_story_info(story_id, auth_id)
        if "error" in story_info:
            return (
                chunks_result.data or []
            )  # Return only matched chunks if story info fails

        midpoint = int(story_info.get("num_episodes", 1) * 0.5)
        if midpoint == 0:
            midpoint = 1

        foundational_chunks = (
            self.client.table("chunks")
            .select("id, episode_number, chunk_number, content, importance_score")
            .eq("story_id", story_id)
            .eq("auth_id", auth_id)
            .in_("episode_number", [1, midpoint])
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
        self,
        story_id: int,
        chunk: str,
        characters: List[str],
        episode_number: int,
        auth_id: str,
    ) -> float:
        score = 0
        for char in characters:
            if char.lower() in chunk.lower():
                score += 1

        # FIX: Pass auth_id to get_story_info as it's required for RLS.
        story_info = self.db_service.get_story_info(story_id, auth_id)
        if "error" in story_info:
            return score  # Return base score if story isn't found

        num_episodes = story_info.get("num_episodes", 1)
        if num_episodes == 0:
            num_episodes = 1

        if episode_number == 1 or episode_number == int(num_episodes * 0.5):
            score += 2

        return score
