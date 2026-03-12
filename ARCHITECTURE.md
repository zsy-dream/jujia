# 银龄精算师 - 系统架构文档

## 架构概览

银龄精算师采用现代化的微服务架构，结合边缘计算和云服务，实现隐私保护的老年人护理监控。

## 技术栈

### 后端技术
- **FastAPI 0.109.0**: 高性能异步Web框架
- **SQLAlchemy 2.0.25**: ORM和数据库抽象层
- **PostgreSQL 16**: 关系型数据库
- **Pydantic 2.5.3**: 数据验证和设置管理
- **Python-Jose**: JWT令牌处理
- **Passlib**: 密码哈希和验证

### 前端技术
- **Vue 3.4.15**: 渐进式JavaScript框架
- **Vite 5.0.11**: 下一代前端构建工具
- **TailwindCSS 3.4.1**: 实用优先的CSS框架
- **Vue Router 4.2.5**: 官方路由管理器
- **Pinia 2.1.7**: Vue状态管理库
- **Axios 1.6.5**: HTTP客户端
- **说明**: 当前前端代码基于 JavaScript 实现，未启用 TypeScript

### 测试框架
- **Pytest 7.4.4**: Python测试框架
- **Hypothesis 6.98.3**: 属性测试库
- **Pytest-Asyncio**: 异步测试支持
- **HTTPX**: 异步HTTP客户端测试

### 基础设施
- **Docker & Docker Compose**: 容器化和编排
- **PostgreSQL 16**: 数据持久化
- **Uvicorn**: ASGI服务器

## 分层架构设计

### 1. API层 (app/api/)
**职责**: 处理HTTP请求和响应
- 路由定义和端点实现
- 请求验证和响应序列化
- 错误处理和状态码管理
- API版本控制

**设计原则**:
- RESTful API设计
- 清晰的端点命名
- 统一的响应格式
- 完整的错误处理

### 2. 服务层 (app/services/)
**职责**: 实现业务逻辑
- 核心业务规则实现
- 跨模型的复杂操作
- 外部服务集成
- 事件处理和编排

**设计原则**:
- 单一职责原则
- 依赖注入
- 可测试性优先
- 清晰的接口定义

### 3. 数据层 (app/models/)
**职责**: 数据持久化和ORM
- SQLAlchemy模型定义
- 数据库关系映射
- 查询优化
- 数据迁移

**设计原则**:
- 规范化数据库设计
- 适当的索引策略
- 外键约束
- 审计跟踪

### 4. 模式层 (app/schemas/)
**职责**: 数据验证和序列化
- Pydantic模型定义
- 请求/响应验证
- 数据转换
- 类型安全

**设计原则**:
- 严格的类型定义
- 输入验证
- 输出序列化
- 文档生成

### 5. 核心层 (app/core/)
**职责**: 配置和共享功能
- 应用配置管理
- 安全和认证
- 工具函数
- 常量定义

**设计原则**:
- 环境变量管理
- 安全最佳实践
- 可重用组件
- 配置集中化

## 数据库设计

### 核心表结构

#### 用户管理
- **users**: 用户账户和认证信息
- **user_profiles**: 详细健康档案和偏好
- **emergency_contacts**: 关爱圈联系人

#### 监控数据
- **skeleton_data**: 匿名化姿态关键点
- **activity_logs**: 日常活动记录
- **frailty_assessments**: 衰弱指数评估
- **risk_predictions**: 风险预测结果

#### 事件管理
- **incidents**: 健康事件记录
- **alerts**: 警报和通知
- **response_logs**: 响应协调日志

#### B2B功能
- **institutions**: 护理机构信息
- **audit_logs**: 系统审计跟踪

### 索引策略
- 时序数据索引: (user_id, timestamp)
- 状态查询索引: (incident_id, status)
- 审计查询索引: (user_id, timestamp)

### 数据完整性
- 外键约束确保引用完整性
- 级联删除保护用户隐私
- 触发器自动更新时间戳
- 检查约束验证数据有效性

## 安全架构

### 认证和授权
- JWT令牌认证
- 基于角色的访问控制(RBAC)
- 令牌刷新机制
- 会话管理

### 数据保护
- 密码bcrypt哈希
- 敏感数据加密
- 传输层安全(TLS)
- 数据匿名化

### 隐私保护
- 边缘计算优先
- 最小数据收集
- 用户同意管理
- 数据保留策略

### 审计和合规
- 全面审计日志
- 访问跟踪
- 合规报告
- 事件响应

## API设计

### API 接口全景 (v0.3.0)
```
/
├── GET /                              # 根接口
├── GET /health                        # 健康检查
├── /api/auth                          # 认证接口
│   ├── POST /register
│   ├── POST /login
│   └── GET /me
├── /api/profile                       # 用户档案接口
│   ├── CRUD /
│   ├── */emergency-contacts/*
│   ├── */medical-conditions/*
│   └── */mobility-aids/*
├── /api/v1/risk                       # 风险评估
│   ├── GET /frailty/{user_id}
│   ├── GET /prediction/{user_id}
│   ├── GET /report/{user_id}
│   └── GET /trends/{user_id}
├── /api/v1/alerts                     # 警报与事件
│   ├── POST /incidents
│   ├── GET  /incidents/{user_id}
│   ├── GET  /active/{user_id}
│   ├── POST /incidents/{id}/verify
│   └── POST /{alert_id}/resolve
├── /api/v1/health                     # 健康数据
│   ├── POST /activity
│   ├── GET  /activity/{user_id}
│   ├── POST /skeleton
│   └── GET  /recommendations/{user_id}
├── /api/v1/vision                     # 视觉AI
│   ├── POST /pose/analyze
│   ├── POST /pose/batch
│   ├── POST /fall/detect
│   ├── POST /activity/recognize
│   └── GET  /stats
├── /api/v1/institution                # 机构管理
│   ├── GET /{id}/dashboard
│   ├── GET /{id}/residents
│   └── GET /{id}/compliance
├── /api/v1/insurance                  # 保险数据
│   ├── GET /population-report
│   ├── GET /assessment/{user_id}
│   └── GET /audit-trail
├── /api/v1/collaboration              # 协作与护理排期
│   ├── POST /threads
│   ├── POST /threads/{id}/messages
│   ├── GET  /threads
│   ├── POST /care-plans
│   ├── GET  /care-plans/resident/{id}
│   └── PUT  /tasks/{task_id}
└── /ws/health/{user_id}               # 实时健康 WebSocket
```

### 响应格式
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 前端架构

### 组件结构
```
src/
├── api/                # API 服务层 (NEW)
│   ├── client.js        # Axios 基础客户端 + safeRequest 降级
│   ├── risk.js          # 风险评估 API
│   ├── vision.js        # 视觉AI API
│   ├── health.js        # 健康数据 API
│   ├── alerts.js        # 警报事件 API
│   ├── institution.js   # 机构管理 API
│   ├── insurance.js     # 保险数据 API
│   └── index.js         # 统一导出
├── views/              # 页面组件
│   ├── Dashboard.vue
│   ├── DoctorDashboard.vue
│   ├── DataPrivacy.vue
│   ├── FamilyApp.vue
│   ├── InstitutionDashboard.vue
│   ├── Reports.vue
│   ├── Profile.vue
│   └── Settings.vue
├── components/         # 可重用组件
│   ├── DemoMode.vue
│   ├── VoiceAssistant.vue
│   ├── ActuarialModelPanel.vue
│   ├── InterventionDemo.vue
│   └── 其他仪表板组件
├── stores/             # Pinia状态管理
│   └── healthStore.js
├── router/             # 路由配置
│   └── index.js
└── utils/              # 工具函数
    └── realisticMockData.js
```

### API 服务层设计
- 统一 Axios 客户端 (`client.js`) 处理认证、拦截、超时
- `safeRequest(apiFn, fallback)` 包装器：后端不可用时自动降级到 mock 数据
- Dashboard.vue 已接入真实 API，同时保留 mock 数据作为回退

### 状态管理
- **health store**: WebSocket 连接状态、健康状态、活动摘要、风险趋势、警报数据
- 主仪表板页面同时结合 `realisticMockData.js` 提供演示数据

### 路由守卫
- 认证检查
- 权限验证
- 页面访问控制
- 重定向逻辑

## 测试策略

### 单元测试
- 测试单个函数和类
- 模拟外部依赖
- 边缘情况覆盖
- 快速执行

### 属性测试
- 使用Hypothesis生成测试数据
- 验证通用属性
- 发现边缘情况
- 提高测试覆盖率

### 集成测试
- 测试组件交互
- 数据库操作验证
- API端点测试
- 端到端流程

### 测试覆盖率目标
- 核心业务逻辑: 90%+
- API端点: 85%+
- 数据模型: 80%+
- 工具函数: 95%+

## 部署架构

### 开发环境
- Docker Compose本地开发
- 热重载支持
- 开发数据库
- 调试工具

### 生产环境
- Kubernetes集群部署
- 负载均衡
- 自动扩展
- 监控和日志

### CI/CD流程
1. 代码提交触发构建
2. 运行测试套件
3. 构建Docker镜像
4. 部署到测试环境
5. 自动化测试
6. 部署到生产环境

## 性能优化

### 数据库优化
- 查询优化和索引
- 连接池管理
- 读写分离
- 缓存策略

### API优化
- 异步处理
- 响应压缩
- 分页和限流
- CDN加速

### 前端优化
- 代码分割
- 懒加载
- 资源压缩
- 缓存策略

## 监控和日志

### 应用监控
- 性能指标
- 错误追踪
- 用户行为分析
- 资源使用

### 日志管理
- 结构化日志
- 日志级别
- 日志聚合
- 日志分析

### 告警机制
- 性能告警
- 错误告警
- 安全告警
- 业务告警

## 扩展性考虑

### 水平扩展
- 无状态API设计
- 数据库分片
- 缓存集群
- 消息队列

### 垂直扩展
- 资源优化
- 性能调优
- 硬件升级
- 容量规划

### 模块化设计
- 微服务架构
- 服务解耦
- API网关
- 服务发现

## 未来规划

### 短期目标
- 完成核心功能开发
- 实现基础监控
- 部署测试环境
- 用户测试

### 中期目标
- 边缘计算集成
- AI模型训练
- B2B功能完善
- 性能优化

### 长期目标
- 多地区部署
- 高可用架构
- 智能化升级
- 生态系统建设
