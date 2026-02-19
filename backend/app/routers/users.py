"User management endpoints"
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..database import get_db
from ..models import User, UserRole
from ..schemas import UserCreate, UserUpdate, UserResponse, UserLogin, Token, TokenRefresh
from ..auth import (
    get_password_hash, verify_password, create_access_token, 
    create_refresh_token, get_current_user, require_admin
)
from jose import JWTError, jwt
from ..config import settings

router = APIRouter()

@router.post(/register, response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    "Register a new user (admin only in production)"
    # Check if user exists
    result = await db.execute(
        select(User).filter((User.email == user_data.email) | (User.username == user_data.username))
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=User with this email or username already exists)
    
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        department=user_data.department,
        role=user_data.role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post(/login, response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    "Login and get access token"
    result = await db.execute(select(User).filter(User.username == credentials.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=Incorrect username or password
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail=User account is disabled)
    
    access_token = create_access_token(data={sub: user.id})
    refresh_token = create_refresh_token(data={sub: user.id})
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post(/refresh, response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    "Refresh access token"
    try:
        payload = jwt.decode(token_data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get(type) != refresh:
            raise HTTPException(status_code=401, detail=Invalid token type)
        user_id = payload.get(sub)
    except JWTError:
        raise HTTPException(status_code=401, detail=Invalid refresh token)
    
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail=User not found or inactive)
    
    access_token = create_access_token(data={sub: user.id})
    refresh_token = create_refresh_token(data={sub: user.id})
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.get(/me, response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    "Get current user information"
    return current_user

@router.get(/, response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    "List all users (admin only)"
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

@router.get(/user_id, response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    "Get user by ID"
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=User not found)
    return user

@router.patch(/user_id, response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    "Update user (admin only)"
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=User not found)
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return user

@router.delete(/user_id, status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    "Delete user (admin only)"
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=User not found)
    
    await db.delete(user)
    await db.commit()
EOF