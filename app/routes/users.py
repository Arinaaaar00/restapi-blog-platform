from fastapi import APIRouter, HTTPException

from ..models.user import User, UserCreate
from ..services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    try:
        return UserService.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[User])
async def get_users():
    return UserService.get_all_users()


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserCreate):
    try:
        updated_user = UserService.update_user(user_id, user)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    success = UserService.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}