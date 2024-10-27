import os

from pinecone import Pinecone

from app.config import Settings

TOP_K = 9

settings = Settings()


class PineconeContainer:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.pinecone_api_key, environment=settings.pinecone_env)
        self.index = self.pc.Index(name="bottle-caps")

    def query_database(self, vector):
        result = self.index.query(vector=[vector], top_k=TOP_K, namespace="bottle_caps")
        return self.parse_result_query(result)

    def query_with_metadata(self, vector: list[float], metadata: dict):
        result = self.index.query(
            vector=vector,
            filter=metadata,
            top_k=TOP_K,
            include_metadata=True,
            namespace="bottle_caps",
        )
        return self.parse_result_query(result)

    def upsert_one_pinecone(self, cap_info):
        self.index.upsert(vectors=[cap_info], namespace="bottle_caps")

    def upsert_multiple_pinecone(self, vectors):
        self.index.upsert(vectors=vectors, namespace="bottle_caps")

    @staticmethod
    def parse_result_query(result_query):
        return result_query["matches"]

    def empty_index(self) -> None:
        self.index.delete(delete_all=True, namespace="bottle_caps")
