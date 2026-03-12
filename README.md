# 银龄精算师 - Silver Age Actuary

老年人护理监控系统 - 基于AI的隐私保护健康风险评估和紧急响应服务

## 项目结构

```
silver-age-actuary/
├── backend/
│   ├── app/
│   │   ├── api/              # 10个路由模块 (auth,profile,risk,alerts,health,vision,...)
│   │   ├── core/             # 配置、安全
│   │   ├── db/               # 数据库配置
│   │   ├── models/           # SQLAlchemy模型
│   │   ├── schemas/          # Pydantic模式 (core.py + api_models.py)
│   │   ├── services/         # 业务逻辑 (18个服务模块)
│   │   └── main.py           # v0.3.0 入口
│   ├── scripts/              # 工具脚本
│   │   └── seed_demo_data.py # 演示数据生成器
│   ├── tests/               # ~40个测试文件
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/              # API服务层 (7个模块 + 基础客户端)
│   │   ├── views/            # 9个页面组件
│   │   ├── components/       # 16+可复用组件
│   │   ├── stores/           # Pinia状态管理
│   │   └── router/           # 路由配置
│   └── package.json
└── docker-compose.yml
```

## 技术栈

### 后端
- **FastAPI**: 现代、快速的Python Web框架
- **SQLAlchemy**: ORM数据库工具
- **PostgreSQL**: 关系型数据库
- **Pytest + Hypothesis**: 测试框架（单元测试和属性测试）

### 前端
- **Vue 3**: 渐进式JavaScript框架
- **Vite**: 下一代前端构建工具
- **TailwindCSS**: 实用优先的CSS框架
- **Pinia**: Vue状态管理
- **Axios**: HTTP 客户端

### 基础设施
- **Docker**: 容器化部署
- **PostgreSQL / SQLite**: Docker 环境使用 PostgreSQL，本地开发默认可使用 SQLite

## 快速开始

### 前置要求
- Docker和Docker Compose
- Node.js 20+ (本地开发)
- Python 3.11+ (本地开发)

### 使用Docker启动

1. 克隆仓库并进入目录
```bash
cd silver-age-actuary
```

2. 复制环境变量文件
```bash
cp .env.example .env
```

3. 启动所有服务
```bash
docker-compose up -d
```

4. 访问应用
- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 本地开发

#### 后端开发
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### 前端开发
```bash
cd frontend
npm install
npm run dev
```

#### 运行测试
```bash
cd backend
pytest
```

## 当前实现说明 (v0.3.0)

### 后端 API (10 个路由组)
- **认证**: 注册/登录/当前用户
- **用户档案**: CRUD + 紧急联系人/病史/辅具
- **风险评估**: 衰弱指数/风险预测/30天报告/趋势分析
- **警报事件**: 事件上报/查询/多模态验证/警报解除
- **健康数据**: 活动数据/骨骼数据/健康建议
- **视觉AI**: 姿态分析/跌倒检测/活动识别/处理统计
- **机构管理**: 看板/住户/合规报告
- **保险数据**: 人群报告/个人评估/审计跟踪
- **协作**: 线程/护理计划/任务
- **WebSocket**: 实时健康数据推送

### 视觉AI管线
- **姿态估计**: 重心计算、躯干角度、髈-膝角度、平衡评分、姿态分类、步态指标
- **跌倒检测**: 4特征融合算法 (CoG下降率+躯干角度+速度+不动检测)，跌倒类型分类，严重度估计
- **活动识别**: 站立/坐下/行走/躺卧/运动 5类，卡路里估算

### 精算模型
- **Gompertz 死亡力模型**: h(t) = a·exp(b·t)，累积风险、生存概率、期望寿命
- **Kaplan-Meier 生存分析**: 非参数生存曲线 + Greenwood 95%CI + RMST
- **Cox 比例风险模型**: 8个协变量，风险比、事件概率、风险分层
- **保费定价引擎**: 等价原理，年龄系数插值，HR调整，健康折扣

### 前端
- 9个页面 + 16+组件，支持多角色（子女/医生/机构/老人）
- API 服务层 (`src/api/`) 对接后端，`safeRequest` 自动降级到 mock 数据
- 演示模式 / 语音助手 / 精算模型面板 / 干预链演示

### 演示数据
- `backend/scripts/seed_demo_data.py` 生成 3 位演示用户×30天数据
- 运行 `python -m scripts.seed_demo_data` 生成 `backend/demo_data/` 目录

## 核心功能

- ✅ 多模态视觉AI管线（姿态估计 + 跌倒检测 + 活动识别）
- ✅ 学术级精算模型（Gompertz + Kaplan-Meier + Cox + 保费定价）
- ✅ 全量 API 已暴露（10个路由组，40+端点）
- ✅ 前后端联通（API服务层 + mock 自动降级）
- ✅ 演示数据种子脚本（3用户×30天×多维数据）
- ✅ 隐私保护的边缘计算与匿名化处理
- ✅ 家庭关爱仪表板与多角色展示界面
- ✅ WebSocket 实时健康数据推送
- ✅ 协作线程与护理排期接口
- ✅ 语音助手、干预链、演示模式前端组件

## 开发指南

### 分层架构
- **API层**: FastAPI路由和端点
- **服务层**: 业务逻辑和编排
- **数据层**: SQLAlchemy模型和数据库操作
- **核心层**: 配置、工具和共享功能

### 测试策略
- **单元测试**: 特定功能和边缘情况
- **属性测试**: 使用Hypothesis验证通用属性
- **集成测试**: 端到端工作流验证

## 许可证

MIT License
