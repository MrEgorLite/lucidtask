from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.models.user import UserModel
from schemas.accounts import UserRegistrationRequestSchema, LoginRequestSchema, LoginResponseSchema
from security.jwt_interface import JWTAuthManagerInterface


def create_user(
        user_data: UserRegistrationRequestSchema,
        db: Session,
) -> UserModel | HTTPException:
    user = db.query(UserModel).filter_by(email=user_data.email).first()

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"A user with this email {user_data.email} already exists."
        )

    try:
        new_user = UserModel.create(
            email=user_data.email,
            raw_password=user_data.password,
        )
        db.add(new_user)
        db.flush()


        return new_user
    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during user creation.",
        )


def login_user(
    user_data: LoginRequestSchema,
    db: Session,
    jwt_auth_manager: JWTAuthManagerInterface,
) -> LoginResponseSchema:
    user = db.query(UserModel).filter_by(email=user_data.email).first()

    if not user or not user.verify_password(raw_password=user_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    try:
        access_token = jwt_auth_manager.create_access_token({"user_id": user.id})

        return LoginResponseSchema(
            access_token=access_token,
            token_type="Bearer"
        )

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login.",
        )
