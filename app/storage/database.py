from datetime import datetime
from app.models.user import User
from app.models.post import Post

users_db = {}
posts_db = {}
user_id_counter = 1
post_id_counter = 1

def init_sample_data():
    """Initialize sample data for testing"""
    global user_id_counter, post_id_counter
    
    user_id = user_id_counter
    user_id_counter += 1
    users_db[user_id] = User(
        id=user_id,
        email="admin@example.com",
        login="admin",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    post_id = post_id_counter
    post_id_counter += 1
    posts_db[post_id] = Post(
        id=post_id,
        author_id=user_id,
        title="Добро пожаловать в блог!",
        content="Это первый пост в нашем блоге. Здесь вы можете делиться своими мыслями и идеями.",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

init_sample_data()