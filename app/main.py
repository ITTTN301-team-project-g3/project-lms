from fastapi import FastAPI
from app.database import engine, Base
from app import models

# Tạo tự động tất cả các bảng trong Database nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Team Project Manager API",
    description="API Quản lý dự án nhóm - Sprint 1",
    version="1.0.0"
)

@app.get("/", summary="Kiểm tra trạng thái Server")
def root():
    return {"message": "Server FastAPI hoạt động tốt cho Ngày 1!"}