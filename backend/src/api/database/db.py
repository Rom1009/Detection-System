from sqlmodel import SQLModel, create_engine, Session
import os
from entities.entities import PredictionLog, UserFeedback # Import để SQLModel biết có bảng này

# Lấy URL từ biến môi trường (trong file .env hoặc Docker)
DATABASE_URL = os.getenv("DATABASE_URL")

# Kết nối DB
engine = create_engine(DATABASE_URL)

# Hàm này chạy 1 lần lúc start server để "Migrate" (Tạo bảng)
def create_db_and_tables():
    print("🔄 Đang kiểm tra và tạo bảng Database...")
    SQLModel.metadata.create_all(engine)
    print("✅ Database đã sẵn sàng!")

# Dependency để lấy session dùng trong API
def get_session():
    with Session(engine) as session:
        yield session