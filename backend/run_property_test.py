"""
简单的属性测试运行器
Simple property test runner without conftest dependencies
"""
import os
import sys

# 设置环境变量
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/test_db"
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://localhost:5173"

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# 运行测试
if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([
        "tests/test_property_realtime_performance.py",
        "-v",
        "--tb=short",
        "-p", "no:cacheprovider"
    ]))
