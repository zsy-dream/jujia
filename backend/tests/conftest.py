"""
Pytest配置和共享fixtures
"""
import os

# 必须在任何导入之前设置环境变量
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///./test_silver_age.db"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["CORS_ORIGINS"] = '["http://localhost:3000","http://localhost:5173"]'
os.environ["DEBUG"] = "True"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 延迟导入，确保环境变量已设置
from app.main import app
from app.db.base import Base, get_db

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_silver_age.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
