# 🚀 银龄精算师 - 快速启动指南

## 最简单的启动方式

### Windows 用户

我已经为你创建了启动脚本，只需要：

#### 1️⃣ 启动后端
双击运行 `start_backend.bat` 或在命令行执行：
```bash
start_backend.bat
```

#### 2️⃣ 启动前端
打开新的命令行窗口，双击运行 `start_frontend.bat` 或执行：
```bash
start_frontend.bat
```

---

## 📍 访问地址

启动成功后，在浏览器中访问：

### 🎨 前端应用（主界面）
```
http://localhost:5173
```

### 🔧 后端 API
```
http://localhost:8000
```

### 📚 API 交互式文档
```
http://localhost:8000/docs
```
在这里可以测试所有 API 端点

---

## ✅ 验证服务是否启动成功

### 检查后端
在浏览器访问: http://localhost:8000/health

应该看到:
```json
{"status": "healthy"}
```

### 检查前端
在浏览器访问: http://localhost:5173

应该看到银龄精算师的仪表板界面

---

## 🎯 功能演示

启动后，你可以：

1. **查看仪表板** - http://localhost:5173
   - 实时监控数据
   - 风险评估图表
   - 活动摘要

2. **测试 API** - http://localhost:8000/docs
   - 用户认证
   - 用户档案管理
   - 协作线程与护理排期
   - WebSocket 实时推送

3. **查看 API 文档** - http://localhost:8000/redoc
   - 完整的 API 参考文档

---

## 🛑 停止服务

在运行服务的命令行窗口中按 `Ctrl+C`

---

## ⚠️ 常见问题

### 端口被占用

如果看到 "Address already in use" 错误：

```bash
# 查找占用端口的进程
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# 终止进程（替换 <PID> 为实际进程ID）
taskkill /PID <PID> /F
```

### 缺少依赖

**后端:**
```bash
cd backend
pip install -r requirements.txt
```

**前端:**
```bash
cd frontend
npm install
```

### 数据库连接失败

本地开发模式下，后端默认可使用 SQLite，不一定需要 PostgreSQL。

如果需要使用 PostgreSQL，请参考根目录的 `docker-compose.yml`。

---

## 📱 系统功能

启动后可以体验：

- ✅ 实时监控仪表板
- ✅ 风险评估和趋势分析
- ✅ 警报管理系统
- ✅ 健康推荐引擎
- ✅ 活动数据可视化
- ✅ WebSocket 实时推送

---

## 📚 更多信息

- 系统架构: `ARCHITECTURE.md`
- 项目完成情况: `PROJECT_COMPLETION_CHECKLIST.md`
- 项目概述: `README.md`

---

**准备好了吗？运行启动脚本，开始体验银龄精算师系统！** 🎉
