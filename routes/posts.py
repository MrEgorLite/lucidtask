from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session
from starlette import status

from database.models.post import PostModel
from database.models.user import UserModel
from schemas.post import PostResponseSchema, PostCreateSchema, PostsResponseSchema
from services.user_dependency import get_current_user
from database.session_sqlite import get_sqlite_db as get_db

router = APIRouter()

@router.post("/")
def add_post(
    post: PostCreateSchema,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> PostResponseSchema:
    new_post = PostModel(
        text=post.text,
        user_id=user.id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return PostResponseSchema(
        id=new_post.id,
        text=new_post.text,
        created_at=new_post.created_at,
        user_id=user.id,
    )

@router.get("/")
@cache(expire=300)
def get_posts(
        user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    posts = db.query(PostModel).all()

    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No posts found",
        )
    for post in posts:
        print(f"id: {post.id}, text: {post.text}")
    return PostsResponseSchema(
        posts=[PostResponseSchema(
            id=post.id,
            text=post.text,
            created_at=post.created_at,
            user_id=post.user_id,
        ) for post in posts],
    )

@router.delete("/{id}")
def delete_post(
        id: int,
        user: UserModel = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    post = db.query(PostModel).filter(PostModel.id == id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No post found",
        )

    if post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this post",
        )

    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}
