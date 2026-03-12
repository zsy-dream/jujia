@echo off
echo ========================================
echo 银龄精算师 - 启动后端服务
echo ========================================
echo.

cd backend

echo 检查 Python 环境...
python --version
echo.

echo 启动 FastAPI 服务器...
echo 后端 API 将在 http://localhost:8000 启动
echo API 文档: http://localhost:8000/docs
echo.
echo 按 Ctrl+C 停止服务
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
