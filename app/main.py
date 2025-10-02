from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from app.models.user import User, UserCreate
from app.models.post import Post, PostCreate
from app.storage.database import users_db, posts_db, user_id_counter, post_id_counter

app = FastAPI(title="Blog API", description="Базовый REST API для ведения блога")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Blog API is running", "users_count": len(users_db), "posts_count": len(posts_db)}

@app.get("/api/v1/users", response_model=list[User])
async def get_users():
    return list(users_db.values())

@app.post("/api/v1/users", response_model=User)
async def create_user(user: UserCreate):
    global user_id_counter
    

    for existing_user in users_db.values():
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if existing_user.login == user.login:
            raise HTTPException(status_code=400, detail="Login already taken")
    
    now = datetime.now()
    user_id = user_id_counter
    user_id_counter += 1
    
    new_user = User(
        id=user_id,
        email=user.email,
        login=user.login,
        created_at=now,
        updated_at=now
    )
    
    users_db[user_id] = new_user
    return new_user

@app.get("/api/v1/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

@app.get("/api/v1/posts", response_model=list[Post])
async def get_posts():
    return list(posts_db.values())

@app.post("/api/v1/posts", response_model=Post)
async def create_post(post: PostCreate, author_id: int):
    global post_id_counter
    
    if author_id not in users_db:
        raise HTTPException(status_code=404, detail="Author not found")
    
    now = datetime.now()
    post_id = post_id_counter
    post_id_counter += 1
    
    new_post = Post(
        id=post_id,
        author_id=author_id,
        title=post.title,
        content=post.content,
        created_at=now,
        updated_at=now
    )
    
    posts_db[post_id] = new_post
    return new_post

@app.get("/api/v1/posts/{post_id}", response_model=Post)
async def get_post(post_id: int):
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    return posts_db[post_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)