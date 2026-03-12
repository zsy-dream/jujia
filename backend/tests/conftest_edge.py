"""
Pytest配置 - 仅用于边缘处理测试
不加载FastAPI应用，避免配置问题
"""
import os
import pytest

# 设置测试环境变量
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/test_db"
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"
os.environ["DEBUG"] = "True"
