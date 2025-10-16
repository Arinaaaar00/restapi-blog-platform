from datetime import datetime

from app.models.post import Post
from app.storage.database import posts_db


class PostService:
    _post_id_counter = 1

    @classmethod
    def create_post(cls, author_id: int, title: str, content: str) -> Post:
        if not title.strip():
            raise ValueError("Title cannot be empty")
        if not content.strip():
            raise ValueError("Content cannot be empty")
        now = datetime.now()
        post_id = cls._post_id_counter
        cls._post_id_counter += 1
        new_post = Post(
            id=post_id,
            author_id=author_id,
            title=title,
            content=content,
            created_at=now,
            updated_at=now,
        )
        posts_db[post_id] = new_post
        return new_post

    @staticmethod
    def get_all_posts() -> list[Post]:
        return list(posts_db.values())

    @staticmethod
    def get_post(post_id: int) -> Post | None:
        return posts_db.get(post_id)

    @staticmethod
    def update_post(post_id: int, title: str, content: str) -> Post | None:
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
            updated_at=datetime.now(),
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
    def delete_user_posts(author_id: int) -> None:
        posts_to_delete = [
            post_id for post_id, post in posts_db.items() if post.author_id == author_id
        ]
        for post_id in posts_to_delete:
            del posts_db[post_id]
