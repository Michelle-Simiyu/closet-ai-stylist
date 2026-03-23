import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ....core.database import get_session
from ....core.security import verify_password, get_password_hash, create_access_token, get_current_user
from ....models.user import User, UserCreate, UserRead, TokenResponse, StyleQuizResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_session),
):
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token({"sub": user.id})
    logger.info(f"New user registered: {user.email}")
    return TokenResponse(
        access_token=token,
        user=UserRead(
            id=user.id,
            email=user.email,
            username=user.username,
            style_profile=user.style_profile,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user.id})
    return TokenResponse(
        access_token=token,
        user=UserRead(
            id=user.id,
            email=user.email,
            username=user.username,
            style_profile=user.style_profile,
            created_at=user.created_at,
        ),
    )


@router.post("/quiz")
async def save_style_quiz(
    quiz: StyleQuizResponse,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    current_user.style_profile = quiz.model_dump()
    session.add(current_user)
    session.commit()
    return {"message": "Style profile saved", "profile": quiz.model_dump()}


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        style_profile=current_user.style_profile,
        created_at=current_user.created_at,
    )
