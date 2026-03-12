"""
独立测试运行器 - 衰弱指数计算属性测试
Standalone test runner for frailty calculation property tests
"""
import os
import sys

# 设置环境变量
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/test_silver_age_actuary"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://localhost:5173"
os.environ["DEBUG"] = "True"

# 运行pytest
import pytest

if __name__ == "__main__":
    sys.exit(pytest.main([
        "tests/test_property_frailty_calculation.py",
        "-v",
        "--tb=short",
        "-x"  # 第一个失败后停止
    ]))
