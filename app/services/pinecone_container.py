from fastapi import HTTPException
from pinecone import Pinecone
from starlette import status

from app.config import Settings

TOP_K = 9

settings = Settings()

VECTOR_SIZE: int = 576
EMPTY_VECTOR: list[float] = VECTOR_SIZE * [0.1]


class PineconeContainer:
    # The updates from Pinecone take a little bit to reflect,
    # so if you upload and then instantly remove, it will probably not work.

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.pc = Pinecone(api_key=settings.pinecone_api_key, environment=settings.pinecone_env)
        self.index = self.pc.Index(name="bottle-caps")

    def query_database(self, vector):
        result = self.index.query(vector=[vector], top_k=TOP_K, namespace="bottle-caps")
        return self.parse_result_query(result)

    def query_with_metadata(self, vector: list[float], metadata: dict):
        result = self.index.query(
            vector=vector,
            filter=metadata,
            top_k=TOP_K,
            include_metadata=True,
            namespace="bottle-caps",
        )
        return self.parse_result_query(result)

    def upsert_into_pinecone(self, vector_id: str, values: list[float], metadata: dict) -> None:
        cap = {"id": vector_id, "values": values, "metadata": metadata}
        return self.upsert_dict_pinecone(cap)

    def upsert_dict_pinecone(self, cap_info: dict) -> None:
        """Upsert dictionary into pinecone.

        Args:
        ----
            cap_info (dict): The dictionary can contain the following keys: id, values, metadata.

        """
        self.index.upsert(vectors=[cap_info], namespace="bottle-caps")

    def upsert_multiple_pinecone(self, vectors):
        self.index.upsert(vectors=vectors, namespace="bottle-caps")

    def remove_vector(self, name: str, user_id: str) -> None:
        res = self.index.query(
            filter={"name": name, "user_id": user_id},
            top_k=1,
            vector=EMPTY_VECTOR,
            include_metadata=True,
            namespace="bottle-caps",
        )
        if len(res["matches"]) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Image does not exist."
            )
        vector_obj = res["matches"][0]
        self.index.delete(
            ids=[vector_obj["id"]],
            namespace="bottle-caps",
        )

    @staticmethod
    def parse_result_query(result_query):
        return result_query["matches"]

    def empty_index(self) -> None:
        self.index.delete(delete_all=True, namespace="bottle-caps")
