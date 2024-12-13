from dotenv import load_dotenv

from app.services.pinecone_container import PineconeContainer


def empty_pinecone() -> None:
    """Empty the Pinecone index, right now I'm using it for tests."""
    load_dotenv()
    pinecone_container: PineconeContainer = PineconeContainer()  # noqa: F841
    # pinecone_container.empty_index() noqa: ERA001


if __name__ == "__main__":
    empty_pinecone()
