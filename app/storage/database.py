from app.models.post import Post
from app.models.user import User

users_db: dict[int, User] = {}
posts_db: dict[int, Post] = {}


def init_sample_data() -> None:
    from app.models.user import UserCreate
    from app.services.post_service import PostService
    from app.services.user_service import UserService

    user = UserService.create_user(
        UserCreate(email="admin@example.com", login="admin", password="admin123")
    )
    PostService.create_post(
        author_id=user.id,
        title="Добро пожаловать в блог!",
        content="Это первый пост в нашем блоге.",
    )


init_sample_data()
