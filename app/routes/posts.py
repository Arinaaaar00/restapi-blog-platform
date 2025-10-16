from fastapi import APIRouter, HTTPException

from ..models.post import Post, PostCreate
from ..services.post_service import PostService
from ..services.user_service import UserService

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=Post)
async def create_post(post: PostCreate, author_id: int):
    if not UserService.user_exists(author_id):
        raise HTTPException(status_code=404, detail="Author not found")
    
    try:
        return PostService.create_post(author_id, post.title, post.content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[Post])
async def get_posts():
    return PostService.get_all_posts()


@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: int):
    post = PostService.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=Post)
async def update_post(post_id: int, post: PostCreate):
    try:
        updated_post = PostService.update_post(post_id, post.title, post.content)
        if not updated_post:
            raise HTTPException(status_code=404, detail="Post not found")
        return updated_post
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{post_id}")
async def delete_post(post_id: int):
    success = PostService.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}