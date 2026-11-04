from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Chuỗi kết nối MySQL (Đổi root:password và localhost/port theo máy của cậu)
# Định dạng: mysql+pymysql://<username>:<password>@<host>:<port>/<db_name>
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/team_project_db"

# Khởi tạo Engine kết nối
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Tự động kiểm tra kết nối sống trước khi query
    echo=True            # In các câu lệnh SQL ra terminal khi dev
)

# Khởi tạo SessionMaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Khởi tạo Base class cho các Model kế thừa
Base = declarative_base()

# Dependency cung cấp Session DB cho từng Request trong FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()