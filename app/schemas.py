from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# Schema dữ liệu gửi lên khi Đăng ký (Request Body)
class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Họ và tên người dùng")
    email: EmailStr = Field(..., description="Email phải đúng định dạng chuẩn")
    password: str = Field(..., min_length=6, max_length=50, description="Mật khẩu tối thiểu 6 ký tự")

# Schema dữ liệu trả về cho Client (Response)
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True  # Cho phép Pydantic đọc dữ liệu từ SQLAlchemy Model