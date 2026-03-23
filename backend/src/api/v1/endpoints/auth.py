import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ....core.database import get_session
from ....core.security import verify_password, get_password_hash, create_access_token, get_current_user
from ....models.user import (
    User, UserCreate, UserRead, UserUpdate, UserChangePassword,
    TokenResponse, StyleQuizResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


def _user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        username=user.username,
        style_profile=user.style_profile,
        gender=user.gender,
        country=user.country,
        bio=user.bio,
        avatar_url=user.avatar_url,
        closet_visibility=user.closet_visibility,
        created_at=user.created_at,
    )


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
    return TokenResponse(access_token=token, user=_user_read(user))


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
    return TokenResponse(access_token=token, user=_user_read(user))


@router.post("/quiz")
async def save_style_quiz(
    quiz: StyleQuizResponse,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Save style preferences (excluding profile fields)
    profile_data = quiz.model_dump(exclude={"gender", "country"})
    current_user.style_profile = profile_data

    # Persist profile fields if provided
    if quiz.gender is not None:
        current_user.gender = quiz.gender
    if quiz.country is not None:
        current_user.country = quiz.country

    session.add(current_user)
    session.commit()
    return {"message": "Style profile saved", "profile": profile_data}


@router.patch("/profile", response_model=UserRead)
async def update_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    data = updates.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(current_user, field, value)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return _user_read(current_user)


@router.post("/change-password")
async def change_password(
    payload: UserChangePassword,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = get_password_hash(payload.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Password updated"}


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return _user_read(current_user)
