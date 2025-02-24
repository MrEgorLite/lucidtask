from fastapi import status, APIRouter, Depends
from sqlalchemy.orm import Session

from config.dependencies import get_jwt_auth_manager
from schemas.accounts import UserRegistrationResponseSchema, UserRegistrationRequestSchema, LoginResponseSchema, \
    LoginRequestSchema
from security.jwt_interface import JWTAuthManagerInterface
from services.user_service import create_user, login_user
from database.session_sqlite import get_sqlite_db as get_db

router = APIRouter()


@router.post(
    "/register/",
    response_model=UserRegistrationResponseSchema,
    summary="Register a new user",
    description="<h3>Register a new user with an email and password.</h3>",
    responses={
        409: {
            "description": "Conflict - User with this email already exists.",
            "content": {
                "application/json": {"example": {"detail": "A user with this email test@example.com already exists."}}
            },
        },
        500: {
            "description": "Internal Server Error - An error occurred during user creation.",
            "content": {"application/json": {"example": {"detail": "An error occurred during user creation."}}},
        },
    },
    status_code=status.HTTP_201_CREATED,
)
def register(
        user_data: UserRegistrationRequestSchema,
        db: Session = Depends(get_db),
        jwt_auth_manager: JWTAuthManagerInterface = Depends(get_jwt_auth_manager),
):
    user = create_user(user_data=user_data, db=db)
    db.commit()
    access_token = jwt_auth_manager.create_access_token({"user_id": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post(
    "/login/",
    response_model=LoginResponseSchema,
    summary="Login user",
    description="<h3>Login user with email and password</h3>",
    responses={
        401: {
            "description": "Unauthorized - Invalid email or password.",
            "content": {"application/json": {"example": {"detail": "Invalid email or password."}}},
        },
        403: {
            "description": "Forbidden - User account is not activated.",
            "content": {"application/json": {"example": {"detail": "User account is not activated."}}},
        },
        500: {
            "description": "Internal Server Error - An error occurred during user login.",
            "content": {"application/json": {"example": {"detail": "An error occurred during login."}}},
        },
    },
    status_code=status.HTTP_200_OK,
)
def login(
    user_data: LoginRequestSchema,
    db: Session = Depends(get_db),
    jwt_auth_manager: JWTAuthManagerInterface = Depends(get_jwt_auth_manager),
):
    return login_user(user_data=user_data, db=db, jwt_auth_manager=jwt_auth_manager)
