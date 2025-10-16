from datetime import datetime

from app.models.user import User, UserCreate
from app.storage.database import users_db


class UserService:
    _user_id_counter = 1

    @classmethod
    def create_user(cls, user_data: UserCreate) -> User:
        for existing_user in users_db.values():
            if existing_user.email == user_data.email:
                raise ValueError("Email already registered")
            if existing_user.login == user_data.login:
                raise ValueError("Login already taken")
        now = datetime.now()
        user_id = cls._user_id_counter
        cls._user_id_counter += 1
        new_user = User(
            id=user_id, email=user_data.email, login=user_data.login, created_at=now, updated_at=now
        )
        users_db[user_id] = new_user
        return new_user

    @staticmethod
    def get_all_users() -> list[User]:
        return list(users_db.values())

    @staticmethod
    def get_user(user_id: int) -> User | None:
        return users_db.get(user_id)

    @staticmethod
    def user_exists(user_id: int) -> bool:
        return user_id in users_db

    @staticmethod
    def update_user(user_id: int, user_data: UserCreate) -> User | None:
        if user_id not in users_db:
            return None
        for existing_user_id, existing_user in users_db.items():
            if existing_user_id != user_id:
                if existing_user.email == user_data.email:
                    raise ValueError("Email already registered")
                if existing_user.login == user_data.login:
                    raise ValueError("Login already taken")
        existing_user = users_db[user_id]
        updated_user = User(
            id=user_id,
            email=user_data.email,
            login=user_data.login,
            created_at=existing_user.created_at,
            updated_at=datetime.now(),
        )
        users_db[user_id] = updated_user
        return updated_user

    @staticmethod
    def delete_user(user_id: int) -> bool:
        if user_id not in users_db:
            return False
        from .post_service import PostService

        PostService.delete_user_posts(user_id)
        del users_db[user_id]
        return True
