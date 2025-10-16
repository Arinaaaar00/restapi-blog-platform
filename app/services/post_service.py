from datetime import datetime
from typing import List, Optional

from ..models.post import Post
from ..storage.database import posts_db, post_id_counter


class PostService:
    @staticmethod
    def create_post(author_id: int, title: str, content: str) -> Post:
        if not title.strip():
            raise ValueError("Title cannot be empty")
        
        if not content.strip():
            raise ValueError("Content cannot be empty")
        
        global post_id_counter
        now = datetime.now()
        post_id = post_id_counter
        post_id_counter += 1
        
        new_post = Post(
            id=post_id,
            author_id=author_id,
            title=title,
            content=content,
            created_at=now,
            updated_at=now
        )
        
        posts_db[post_id] = new_post
        return new_post

    @staticmethod
    def get_all_posts() -> List[Post]:
        return list(posts_db.values())

    @staticmethod
    def get_post(post_id: int) -> Optional[Post]:
        return posts_db.get(post_id)

    @staticmethod
    def update_post(post_id: int, title: str, content: str) -> Optional[Post]:
        if post_id not in posts_db:
            return None
        
        if not title.strip():
            raise ValueError("Title cannot be empty")
        
        if not content.strip():
            raise ValueError("Content cannot be empty")
        
        existing_post = posts_db[post_id]
        updated_post = Post(
            id=post_id,
            author_id=existing_post.author_id,
            title=title,
            content=content,
            created_at=existing_post.created_at,
            updated_at=datetime.now()
        )
        
        posts_db[post_id] = updated_post
        return updated_post

    @staticmethod
    def delete_post(post_id: int) -> bool:
        if post_id not in posts_db:
            return False
        
        del posts_db[post_id]
        return True

    @staticmethod
    def delete_user_posts(author_id: int):
        posts_to_delete = [
            post_id for post_id, post in posts_db.items() 
            if post.author_id == author_id
        ]
        for post_id in posts_to_delete:
            del posts_db[post_id]