from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.schema import Document
from app.core.config import settings
from app.services.db_service import DBService
from supabase import Client
from typing import List, Dict
from llama_index.embeddings.gemini import GeminiEmbedding


class EmbeddingService:
    def __init__(self, client: Client):
        self.embedding_model = GeminiEmbedding(
            model_name="models/embedding-001",
            api_key=settings.GEMINI_API_KEY,
        )
        self.db_service = DBService(client)
        self.splitter = SemanticSplitterNodeParser(
            embed_model=self.embedding_model,
            buffer_size=1,
            breakpoint_percentile_threshold=95,
        )
        self.client = client
        # self.embedding_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)

    def _process_and_store_chunks(
        self,
        story_id: int,
        episode_id: int,
        episode_number: int,
        content: str,
        characters: List[str],
        auth_id: str,
    ):
        """
        This function is used to divide the episodes into chunks and store it in the DB.
        """
        doc = Document(text=content)
        nodes = self.splitter.get_nodes_from_documents(
            [doc], embed_model=self.embedding_model
        )

        chunk_data = []
        for chunk_number, node in enumerate(nodes):
            content = node.text
            embedding = self.embedding_model.get_text_embedding(content)
            importance_score = self._calculate_importance_score(
                story_id, content, characters, episode_number, auth_id
            )

            chunk_data.append(
                {
                    "story_id": story_id,
                    "episode_id": episode_id,
                    "episode_number": episode_number,
                    "chunk_number": chunk_number,
                    "content": content,
                    "characters": characters,
                    "embedding": embedding,
                    "importance_score": importance_score,
                    "auth_id": auth_id,
                }
            )

        if not chunk_data:
            return

        result = self.client.table("chunks").insert(chunk_data).execute()

        if not result.data:
            raise ValueError("Failed to store chunks in the database")

    def retrieve_relevant_chunks(
        self,
        story_id: int,
        current_episode_info: str,
        auth_id: str,
        k: int = 5,
    ) -> List[Dict]:
        query_embedding = self.embedding_model.get_text_embedding(current_episode_info)

        chunks_result = self.client.rpc(
            "match_chunks",
            {
                "p_story_id": story_id,
                "p_auth_id": auth_id,
                "p_query_embedding": query_embedding,
                "p_k": k,
            },
        ).execute()

        foundational_chunks = (
            self.client.table("chunks")
            .select("id, episode_number, chunk_number, content, importance_score")
            .eq("story_id", story_id)
            .eq("auth_id", auth_id)
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
                "content": chunk.get("content") or chunk.get("content"),
            }
            for chunk in sorted(
                chunks,
                key=lambda x: (x.get("importance_score", 0), x.get("similarity", 0)),
                reverse=True,
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

        story_info = self.db_service.get_story_info(story_id, auth_id)
        if "error" in story_info:
            return score

        num_episodes = story_info.get("num_episodes", 1)
        if num_episodes == 0:
            num_episodes = 1

        if episode_number == 1 or episode_number == int(num_episodes * 0.5):
            score += 2
        return score
