# 银龄精算师 - 家庭关爱仪表板

Vue3 + Vite + TailwindCSS 响应式前端应用，提供实时健康监控和风险评估可视化。

## 功能特性

### 实时健康监控
- WebSocket 连接实时更新健康状态
- 衰弱指数可视化（0-100分）
- 风险等级指示（低、中、高、紧急）
- 连接状态监控和自动重连

### 活动摘要
- 每日步数追踪
- 睡眠时长监控
- 移动能力评分
- 实时活动更新

### 风险趋势分析
- 7/14/30天风险趋势图表
- 风险区域可视化
- 交互式数据点
- 趋势线平滑显示

### 警报系统
- 多级别警报（低、中、高、紧急）
- 实时警报推送
- 警报历史记录
- 警报类型分类

## 技术栈

- **Vue 3.4** - 组合式 API
- **Vite 5.0** - 快速构建工具
- **TailwindCSS 3.4** - 实用优先的 CSS 框架
- **Pinia 2.1** - 状态管理
- **Vue Router 4.2** - 路由管理
- **Axios 1.6** - HTTP 客户端

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 可复用组件
│   │   ├── HealthStatusCard.vue    # 健康状态卡片
│   │   ├── ActivitySummary.vue     # 活动摘要
│   │   ├── RiskTrendChart.vue      # 风险趋势图表
│   │   └── AlertsList.vue          # 警报列表
│   ├── stores/              # Pinia 状态管理
│   │   └── healthStore.js          # 健康数据状态
│   ├── views/               # 页面视图
│   │   └── Dashboard.vue           # 主仪表板
│   ├── router/              # 路由配置
│   │   └── index.js
│   ├── App.vue              # 根组件
│   ├── main.js              # 应用入口
│   └── style.css            # 全局样式
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 开发指南

### 安装依赖

```bash
cd frontend
npm install
```

### 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:5173 启动

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## WebSocket 连接

前端通过 WebSocket 连接到后端实时健康监控服务：

```javascript
// WebSocket URL 格式
ws://localhost:8000/ws/health/{user_id}
```

### 消息类型

1. **health_status** - 健康状态更新
```json
{
  "type": "health_status",
  "status": "normal",
  "frailty_score": 0.15,
  "timestamp": "2024-01-01T12:00:00"
}
```

2. **activity_update** - 活动数据更新
```json
{
  "type": "activity_update",
  "daily_steps": 5420,
  "sleep_hours": 7.5,
  "mobility_score": 0.85,
  "timestamp": "2024-01-01T12:00:00"
}
```

3. **risk_trend** - 风险趋势数据
```json
{
  "type": "risk_trend",
  "trends": [
    {"date": 1704067200, "risk_score": 0.15},
    ...
  ],
  "timestamp": "2024-01-01T12:00:00"
}
```

4. **alert** - 警报通知
```json
{
  "type": "alert",
  "alert_id": "alert-123",
  "alert_type": "fall",
  "severity": "high",
  "message": "检测到跌倒事件",
  "timestamp": "2024-01-01T12:00:00"
}
```

## 响应式设计

应用采用移动优先的响应式设计：

- **移动设备** (< 768px): 单列布局
- **平板设备** (768px - 1024px): 两列布局
- **桌面设备** (> 1024px): 三列网格布局

## UI 设计原则

遵循 uiverse.io 高端 UI 设计标准：

- 柔和的渐变背景
- 圆角卡片设计（rounded-2xl）
- 微妙的阴影效果
- 平滑的过渡动画
- 清晰的视觉层次
- 直观的颜色编码（蓝色=正常，琥珀=警告，红色=紧急）

## 状态管理

使用 Pinia 管理全局健康数据状态：

```javascript
import { useHealthStore } from '@/stores/healthStore'

const healthStore = useHealthStore()

// 连接 WebSocket
healthStore.connectWebSocket(userId)

// 访问状态
const healthStatus = healthStore.healthStatus
const riskLevel = healthStore.riskLevel
const alerts = healthStore.alerts
```

## 环境配置

创建 `.env` 文件配置环境变量：

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 浏览器支持

- Chrome/Edge (最新版本)
- Firefox (最新版本)
- Safari (最新版本)

## 许可证

Copyright © 2024 银龄精算师项目
