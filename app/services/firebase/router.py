from fastapi import APIRouter, UploadFile
from app.services.firebase.firebase_container import FirebaseContainer

firebase_router: APIRouter = APIRouter()
firebase_container: FirebaseContainer = FirebaseContainer()


@firebase_router.post("/firebase/", tags=["Firebase"])
async def post_image(file: UploadFile, name: str, user_id: str) -> None:
    return firebase_container.add_image_to_container(file, name, user_id)
