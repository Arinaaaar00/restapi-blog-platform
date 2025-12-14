from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, users, posts

app = FastAPI(
    title="Chic & Chat - Blog для светских дам",
    description="Элегантная платформа для ведения блога",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)


@app.get("/")
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/posts")
async def posts_page(request: Request):
    """Posts page"""
    return templates.TemplateResponse("posts.html", {"request": request})


@app.get("/post/{post_id}")
async def post_page(request: Request, post_id: int):
    """Single post page"""
    return templates.TemplateResponse("post.html", {"request": request})


@app.get("/create-post")
async def create_post_page(request: Request):
    """Create post page"""
    return templates.TemplateResponse("create_post.html", {"request": request})


@app.get("/users")
async def users_page(request: Request):
    """Users page"""
    return templates.TemplateResponse("users.html", {"request": request})


@app.get("/profile/{user_id}")
async def profile_page(request: Request, user_id: int):
    """User profile page"""
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get("/bookmarks")
async def bookmarks_page(request: Request):
    """Bookmarks page"""
    return templates.TemplateResponse("bookmarks.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Chic & Chat is running beautifully!"}
