from fastapi import APIRouter, HTTPException

from app.models.user import User, UserCreate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/users", response_model=list[User])
async def get_users() -> list[User]:
    return UserService.get_all_users()


@router.post("/users", response_model=User)
async def create_user(user: UserCreate) -> User:
    try:
        return UserService.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int) -> User:
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserCreate) -> User:
    try:
        updated_user = UserService.update_user(user_id, user)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/users/{user_id}")
async def delete_user(user_id: int) -> dict:
    success = UserService.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
