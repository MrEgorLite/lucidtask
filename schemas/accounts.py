from typing import Annotated
from annotated_types import MinLen
from pydantic import BaseModel, EmailStr, field_validator
from database import account_validators


class UserBaseSchema(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        return account_validators.validate_email(value)


class UserRegistrationRequestSchema(UserBaseSchema):
    password: Annotated[str, MinLen(8)]

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        return account_validators.validate_password_strength(value)


class UserRegistrationResponseSchema(BaseModel):
    access_token: str
    token_type: str

    model_config = {"from_attributes": True}



class LoginRequestSchema(UserRegistrationRequestSchema):
    pass


class LoginResponseSchema(UserRegistrationResponseSchema):
    pass
