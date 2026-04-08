from typing import TypedDict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth import authenticate_user, create_access_token, get_password_hash
from app.connection import get_session
from app.models import RoleType, User, UserDefault

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: RoleType
    bio: str = ""


class RegisterResponse(TypedDict):
    status: int
    data: UserDefault


class TokenResponse(TypedDict):
    access_token: str
    token_type: str


@router.post("/register", response_model=RegisterResponse)
def register(
    payload: RegisterRequest,
    session: Session = Depends(get_session),
) -> RegisterResponse:
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        role=payload.role,
        bio=payload.bio,
        hashed_password=get_password_hash(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"status": 200, "data": UserDefault.model_validate(user)}


@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> TokenResponse:
    user = authenticate_user(session, form_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
