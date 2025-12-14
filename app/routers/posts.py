from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.db_utils import get_db
from app.database import Post, Tag, Comment, post_tags, bookmarks, post_reactions
from app.schemas import PostCreate, PostUpdate, PostResponse, CommentCreate, CommentResponse, TagResponse
from app.auth import get_current_active_user, get_optional_user
from app.database import User

router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


@router.get("", response_model=List[PostResponse])
def get_posts(
    search: Optional[str] = Query(None, description="Search in title and content"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all posts with pagination, search and filtering - PUBLIC endpoint"""
    query = db.query(Post).filter(Post.is_published == True)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Post.post_title.ilike(search_term),
                Post.post_content.ilike(search_term)
            )
        )
    
    if tag:
        query = query.join(Post.tags).filter(Tag.tag_name == tag.lower())
    
    total = query.count()
    posts = query.order_by(Post.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # Add counts
    result = []
    for post in posts:
        post_dict = PostResponse.from_orm(post)
        post_dict.likes_count = len(post.liked_by)
        post_dict.comments_count = len(post.comments)
        result.append(post_dict)
    
    return result


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new post"""
    new_post = Post(
        user_id=current_user.id,
        post_title=post_data.post_title,
        post_content=post_data.post_content,
        is_published=post_data.is_published
    )
    
    # Handle tags
    if post_data.tag_names:
        for tag_name in post_data.tag_names:
            tag_name = tag_name.lower().strip()
            tag = db.query(Tag).filter(Tag.tag_name == tag_name).first()
            if not tag:
                tag = Tag(tag_name=tag_name)
                db.add(tag)
            new_post.tags.append(tag)
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    post_dict = PostResponse.from_orm(new_post)
    post_dict.likes_count = 0
    post_dict.comments_count = 0
    
    return post_dict


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get specific post by ID - PUBLIC endpoint"""
    post = db.query(Post).filter(Post.id == post_id, Post.is_published == True).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Increment view counter
    post.view_counter += 1
    db.commit()
    
    post_dict = PostResponse.from_orm(post)
    post_dict.likes_count = len(post.liked_by)
    post_dict.comments_count = len(post.comments)
    
    return post_dict


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only edit own posts"
        )
    
    if post_update.post_title is not None:
        post.post_title = post_update.post_title
    
    if post_update.post_content is not None:
        post.post_content = post_update.post_content
    
    if post_update.is_published is not None:
        post.is_published = post_update.is_published
    
    # Update tags
    if post_update.tag_names is not None:
        post.tags.clear()
        for tag_name in post_update.tag_names:
            tag_name = tag_name.lower().strip()
            tag = db.query(Tag).filter(Tag.tag_name == tag_name).first()
            if not tag:
                tag = Tag(tag_name=tag_name)
                db.add(tag)
            post.tags.append(tag)
    
    db.commit()
    db.refresh(post)
    
    post_dict = PostResponse.from_orm(post)
    post_dict.likes_count = len(post.liked_by)
    post_dict.comments_count = len(post.comments)
    
    return post_dict


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete own posts"
        )
    
    db.delete(post)
    db.commit()
    return None


@router.post("/{post_id}/like", status_code=status.HTTP_200_OK)
def like_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Like a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Check if already liked
    existing = db.execute(
        post_reactions.select().where(
            post_reactions.c.user_id == current_user.id,
            post_reactions.c.post_id == post_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked this post"
        )
    
    db.execute(
        post_reactions.insert().values(
            user_id=current_user.id,
            post_id=post_id
        )
    )
    db.commit()
    
    return {"message": "Post liked successfully"}


@router.delete("/{post_id}/like", status_code=status.HTTP_200_OK)
def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unlike a post"""
    result = db.execute(
        post_reactions.delete().where(
            post_reactions.c.user_id == current_user.id,
            post_reactions.c.post_id == post_id
        )
    )
    db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not liked"
        )
    
    return {"message": "Post unliked successfully"}


@router.post("/{post_id}/bookmark", status_code=status.HTTP_200_OK)
def bookmark_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Bookmark a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Check if already bookmarked
    existing = db.execute(
        bookmarks.select().where(
            bookmarks.c.user_id == current_user.id,
            bookmarks.c.post_id == post_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already bookmarked this post"
        )
    
    db.execute(
        bookmarks.insert().values(
            user_id=current_user.id,
            post_id=post_id
        )
    )
    db.commit()
    
    return {"message": "Post bookmarked successfully"}


@router.delete("/{post_id}/bookmark", status_code=status.HTTP_200_OK)
def unbookmark_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove post from bookmarks"""
    result = db.execute(
        bookmarks.delete().where(
            bookmarks.c.user_id == current_user.id,
            bookmarks.c.post_id == post_id
        )
    )
    db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post not bookmarked"
        )
    
    return {"message": "Bookmark removed successfully"}


@router.get("/{post_id}/comments", response_model=List[CommentResponse])
def get_post_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get all comments for a post - PUBLIC endpoint"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.desc()).all()
    return comments


@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a comment on a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Verify parent comment exists if specified
    if comment_data.parent_comment_id:
        parent = db.query(Comment).filter(
            Comment.id == comment_data.parent_comment_id,
            Comment.post_id == post_id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )
    
    new_comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        comment_text=comment_data.comment_text,
        parent_comment_id=comment_data.parent_comment_id
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return new_comment
