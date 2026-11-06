from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Họ và tên người dùng"
    )
    email: EmailStr = Field(..., description="Email phải đúng định dạng chuẩn")
    password: str = Field(
        ...,
        min_length=6,
        max_length=50,
        description="Mật khẩu tối thiểu 6 ký tự"
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
