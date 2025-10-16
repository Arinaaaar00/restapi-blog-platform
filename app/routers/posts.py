from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.models.post import Post, PostCreate
from app.services.post_service import PostService
from app.services.user_service import UserService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, tags=["html"])
async def read_root(request: Request) -> HTMLResponse:
    posts = PostService.get_all_posts()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})


@router.get("/posts/create", response_class=HTMLResponse, tags=["html"])
async def show_create_post_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("create_post.html", {"request": request})


@router.post("/posts/create", response_class=HTMLResponse, tags=["html"])
async def handle_create_post(
    request: Request, author_id: int = Form(...), title: str = Form(...), content: str = Form(...)
) -> HTMLResponse:
    if not UserService.user_exists(author_id):
        raise HTTPException(status_code=404, detail="Author not found")

    new_post = PostService.create_post(author_id, title, content)

    return templates.TemplateResponse("post.html", {"request": request, "post": new_post})


@router.get("/posts/{post_id}", response_class=HTMLResponse, tags=["html"])
async def view_post(request: Request, post_id: int) -> HTMLResponse:
    post = PostService.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse("post.html", {"request": request, "post": post})


@router.get("/posts/{post_id}/edit", response_class=HTMLResponse, tags=["html"])
async def show_edit_post_form(request: Request, post_id: int) -> HTMLResponse:
    post = PostService.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})


@router.post("/posts/{post_id}/edit", response_class=HTMLResponse, tags=["html"])
async def handle_edit_post(
    request: Request, post_id: int, title: str = Form(...), content: str = Form(...)
) -> HTMLResponse:
    updated_post = PostService.update_post(post_id, title, content)
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse("post.html", {"request": request, "post": updated_post})


@router.get("/posts", response_model=list[Post], tags=["api"])
async def get_posts() -> list[Post]:
    return PostService.get_all_posts()


@router.post("/posts", response_model=Post, tags=["api"])
async def create_post(post: PostCreate, author_id: int) -> Post:
    if not UserService.user_exists(author_id):
        raise HTTPException(status_code=404, detail="Author not found")

    try:
        return PostService.create_post(author_id, post.title, post.content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/posts/{post_id}", response_model=Post, tags=["api"])
async def get_post_api(post_id: int) -> Post:
    post = PostService.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/posts/{post_id}", response_model=Post, tags=["api"])
async def update_post_api(post_id: int, post: PostCreate) -> Post:
    try:
        updated_post = PostService.update_post(post_id, post.title, post.content)
        if not updated_post:
            raise HTTPException(status_code=404, detail="Post not found")
        return updated_post
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/posts/{post_id}", tags=["api"])
async def delete_post_api(post_id: int) -> dict:
    success = PostService.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted successfully"}
