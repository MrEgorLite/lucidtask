from datetime import datetime

from pydantic import BaseModel, constr


class PostCreateSchema(BaseModel):
    text: constr(min_length=1, max_length=1_000_000)  # Limit post size to 1MB


class PostResponseSchema(BaseModel):
    id: int
    text: str
    created_at: datetime
    user_id: int

    model_config = {"from_attributes": True}


class PostsResponseSchema(BaseModel):
    posts: list[PostResponseSchema]
