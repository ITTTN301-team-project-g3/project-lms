
import os
import logging
import bcrypt

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserLogin, Token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])

security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if not SECRET_KEY:
    raise ValueError("SECRET_KEY chưa được cấu hình trong file .env")


def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post(
    "/api/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(
            User.email == user.email
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email đã được đăng ký"
            )

        hashed_password = bcrypt.hashpw(
            user.password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("ascii")

        new_user = User(
            full_name=user.full_name,
            email=user.email,
            password_hash=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except HTTPException:
        raise

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email đã được đăng ký"
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error while registering user")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo tài khoản lúc này"
        ) from exc


@router.post(
    "/api/auth/login",
    response_model=Token
)
@router.post(
    "/auth/login",
    response_model=Token
)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    account = db.query(User).filter(
        User.email == user.email
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )

    is_password_valid = bcrypt.checkpw(
        user.password.encode("utf-8"),
        account.password_hash.encode("ascii")
    )

    if not is_password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )

    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa"
        )

    access_token = create_access_token(account.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ"
            )

        user_id = int(user_id)

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"}
        )

    current_user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not current_user or not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại hoặc đã bị vô hiệu hóa"
        )

    return current_user


@router.get(
    "/api/auth/me",
    response_model=UserResponse
)
@router.get(
    "/auth/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
