from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User
from backend.schemas.user import RefreshTokenRequest, TokenResponse, UserCreate, UserLogin
from backend.security.auth import get_current_user
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=dict)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> dict:
    user = AuthService.register_user(
        db=db,
        username=user_data.username,
        email=str(user_data.email),
        full_name=user_data.full_name,
        password=user_data.password,
        role=user_data.role,
        date_of_birth=user_data.date_of_birth,
        gender=user_data.gender,
        phone=user_data.phone,
    )
    return {
        "id": user.id,
        "patient_id": user.patient_id,
        "username": user.username,
        "email": user.email,
        "message": "User registered successfully",
    }


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)) -> dict:
    ip_address = request.client.host if request.client else None
    return AuthService.authenticate_user(db=db, username=user_data.username, password=user_data.password, ip_address=ip_address)


@router.post("/refresh-token", response_model=dict)
def refresh_token(payload: RefreshTokenRequest) -> dict[str, str]:
    return AuthService.refresh_access_token(payload.refresh_token)


@router.post("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    return AuthService.logout(current_user, request, db)
