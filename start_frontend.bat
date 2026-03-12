@echo off
echo ========================================
echo 银龄精算师 - 启动前端服务
echo ========================================
echo.

cd frontend

echo 检查 Node.js 环境...
node --version
npm --version
echo.

echo 检查依赖...
if not exist "node_modules" (
    echo 首次运行，正在安装依赖...
    echo 这可能需要几分钟时间，请耐心等待...
    npm install
    echo.
    echo 依赖安装完成！
    echo.
)

echo 启动 Vite 开发服务器...
echo 前端应用将在 http://localhost:5173 启动
echo.
echo 按 Ctrl+C 停止服务
echo.

npm run dev
