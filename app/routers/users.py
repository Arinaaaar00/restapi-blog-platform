from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.db_utils import get_db
from app.database import User, Post, user_subscriptions, bookmarks
from app.schemas import UserResponse, UserUpdate, UserWithStats, PostResponse
from app.auth import get_current_active_user, get_optional_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me/bookmarks", response_model=List[PostResponse])
def get_my_bookmarks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's bookmarked posts"""
    # Get all bookmarked posts for current user
    posts = db.query(Post).join(
        bookmarks,
        Post.id == bookmarks.c.post_id
    ).filter(
        bookmarks.c.user_id == current_user.id,
        Post.is_published == True
    ).order_by(Post.created_at.desc()).all()
    
    # Add counts
    result = []
    for post in posts:
        post_dict = PostResponse.from_orm(post)
        post_dict.likes_count = len(post.liked_by)
        post_dict.comments_count = len(post.comments)
        result.append(post_dict)
    
    return result


@router.get("", response_model=List[UserWithStats])
def get_users(
    search: Optional[str] = Query(None, description="Search by username or email"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all users with pagination and search"""
    query = db.query(User).filter(User.is_active == True)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    total = query.count()
    users = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # Add stats to users
    result = []
    for user in users:
        user_dict = UserWithStats.from_orm(user)
        user_dict.posts_count = db.query(func.count(Post.id)).filter(Post.user_id == user.id).scalar()
        user_dict.followers_count = db.query(func.count(user_subscriptions.c.follower_id)).filter(
            user_subscriptions.c.following_id == user.id
        ).scalar()
        user_dict.following_count = db.query(func.count(user_subscriptions.c.following_id)).filter(
            user_subscriptions.c.follower_id == user.id
        ).scalar()
        result.append(user_dict)
    
    return result


@router.get("/{user_id}", response_model=UserWithStats)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_dict = UserWithStats.from_orm(user)
    user_dict.posts_count = db.query(func.count(Post.id)).filter(Post.user_id == user.id).scalar()
    user_dict.followers_count = db.query(func.count(user_subscriptions.c.follower_id)).filter(
        user_subscriptions.c.following_id == user.id
    ).scalar()
    user_dict.following_count = db.query(func.count(user_subscriptions.c.following_id)).filter(
        user_subscriptions.c.follower_id == user.id
    ).scalar()
    
    return user_dict


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user information"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update own profile"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if email is taken
    if user_update.email and user_update.email != user.email:
        if db.query(User).filter(User.email == user_update.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
        user.email = user_update.email
    
    # Check if username is taken
    if user_update.username and user_update.username != user.username:
        if db.query(User).filter(User.username == user_update.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user.username = user_update.username
    
    if user_update.profile_text is not None:
        user.profile_text = user_update.profile_text
    
    if user_update.avatar_path is not None:
        user.avatar_path = user_update.avatar_path
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete user account"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(user)
    db.commit()
    return None


@router.get("/{user_id}/posts", response_model=List[PostResponse])
def get_user_posts(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all posts by a specific user - PUBLIC endpoint"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Show only published posts for public access
    query = db.query(Post).filter(Post.user_id == user_id, Post.is_published == True)
    
    posts = query.order_by(Post.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # Add counts
    result = []
    for post in posts:
        post_dict = PostResponse.from_orm(post)
        post_dict.likes_count = len(post.liked_by)
        post_dict.comments_count = len(post.comments)
        result.append(post_dict)
    
    return result


@router.post("/{user_id}/follow", status_code=status.HTTP_200_OK)
def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Follow a user"""
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself"
        )
    
    user_to_follow = db.query(User).filter(User.id == user_id).first()
    if not user_to_follow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Check if already following
    existing = db.execute(
        user_subscriptions.select().where(
            user_subscriptions.c.follower_id == current_user.id,
            user_subscriptions.c.following_id == user_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )
    
    db.execute(
        user_subscriptions.insert().values(
            follower_id=current_user.id,
            following_id=user_id
        )
    )
    db.commit()
    
    return {"message": "Successfully followed user"}


@router.delete("/{user_id}/follow", status_code=status.HTTP_200_OK)
def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user"""
    result = db.execute(
        user_subscriptions.delete().where(
            user_subscriptions.c.follower_id == current_user.id,
            user_subscriptions.c.following_id == user_id
        )
    )
    db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not following this user"
        )
    
    return {"message": "Successfully unfollowed user"}
