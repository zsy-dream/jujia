# 核心数据模型文档

## 概述

本目录包含银龄精算师系统的核心数据模型定义，包括Python数据类（dataclasses）和SQLAlchemy ORM模型。

## 文件结构

- `core.py` - SQLAlchemy ORM模型定义
- `../schemas/core.py` - Python数据类和类型定义
- `../core/validation.py` - 数据验证工具函数

## 核心数据模型

### 1. SkeletonData (骨骼数据)
隐私保护的姿态估计数据，从视频中提取但不存储原始图像。

**字段：**
- `timestamp`: 数据采集时间
- `user_id`: 用户标识符
- `keypoints`: 关键点列表（关节位置）
- `confidence_scores`: 每个关键点的置信度分数
- `anonymized`: 是否已匿名化（必须为True）

**验证规则：**
- 必须已匿名化
- 关键点数量必须与置信度分数数量匹配
- 所有置信度分数必须在[0.0, 1.0]范围内

### 2. FrailtyIndex (衰弱指数)
基于多项生理指标的标准化健康评估分数。

**字段：**
- `user_id`: 用户标识符
- `score`: 衰弱分数（0.0-1.0）
- `components`: 组件分数字典（移动性、活动、睡眠等）
- `calculation_date`: 计算日期
- `confidence_interval`: 置信区间（下限，上限）

**验证规则：**
- 分数必须在[0.0, 1.0]范围内
- 置信区间必须满足：0.0 ≤ lower ≤ upper ≤ 1.0
- 所有组件分数必须在[0.0, 1.0]范围内

### 3. IncidentData (事件数据)
紧急和健康事件记录。

**字段：**
- `incident_id`: 事件唯一标识符
- `user_id`: 用户标识符
- `incident_type`: 事件类型（跌倒、医疗紧急情况等）
- `timestamp`: 事件发生时间
- `severity`: 严重程度（低、中、高、紧急）
- `location`: 位置信息（纬度、经度、地址）
- `sensor_data`: 传感器数据字典
- `verification_status`: 验证状态

**验证规则：**
- 必填字段不能为空
- 位置坐标必须有效（纬度：-90到90，经度：-180到180）
- 时间戳不能在未来

### 4. RiskPrediction (风险预测)
预测模型输出和置信度分数。

**字段：**
- `user_id`: 用户标识符
- `prediction_date`: 预测日期
- `fall_risk_score`: 跌倒风险分数
- `medical_emergency_risk`: 医疗紧急情况风险
- `mobility_decline_risk`: 移动能力下降风险
- `confidence_level`: 置信度水平
- `contributing_factors`: 贡献因素列表

**验证规则：**
- 所有风险分数必须在[0.0, 1.0]范围内
- 贡献因素列表不能为空

### 5. UserProfile (用户档案)
详细健康和偏好数据。

**字段：**
- `user_id`: 用户标识符
- `age`: 年龄
- `medical_conditions`: 医疗状况列表
- `mobility_aids`: 移动辅助设备列表
- `emergency_contacts`: 紧急联系人列表
- `care_preferences`: 护理偏好
- `baseline_metrics`: 基线健康指标

**验证规则：**
- 年龄必须在0-150范围内
- 至少需要一个紧急联系人
- 紧急联系人优先级必须唯一

## 数据库ORM模型

### 主要表

1. **users** - 核心用户信息和身份验证
2. **user_profiles** - 详细健康和偏好数据
3. **medical_conditions** - 健康状况和药物跟踪
4. **mobility_aids** - 移动辅助设备记录
5. **emergency_contacts** - 关爱圈和紧急联系人信息
6. **skeleton_data** - 匿名化姿态和运动数据
7. **frailty_assessments** - 历史衰弱指数计算
8. **risk_predictions** - 预测模型输出和置信度分数
9. **incidents** - 紧急和健康事件记录
10. **alerts** - 警报生成和响应跟踪
11. **activity_logs** - 日常活动模式和指标
12. **audit_logs** - 合规和安全审计跟踪

## 使用示例

### 创建骨骼数据

```python
from datetime import datetime
from app.schemas.core import SkeletonData, Keypoint, JointType

keypoints = [
    Keypoint(JointType.NOSE, 100.0, 200.0, visibility=0.9),
    Keypoint(JointType.LEFT_SHOULDER, 80.0, 220.0, visibility=0.85)
]

skeleton = SkeletonData(
    timestamp=datetime.utcnow(),
    user_id="user123",
    keypoints=keypoints,
    confidence_scores=[0.9, 0.85],
    anonymized=True
)
```

### 验证数据

```python
from app.core.validation import validate_skeleton_data

is_valid, error = validate_skeleton_data(skeleton)
if not is_valid:
    print(f"Validation error: {error}")
```

### 创建用户档案

```python
from app.schemas.core import (
    UserProfile, EmergencyContact, CarePreferences, BaselineMetrics
)

profile = UserProfile(
    user_id="user123",
    age=75,
    medical_conditions=[],
    mobility_aids=[],
    emergency_contacts=[
        EmergencyContact(
            name="张三",
            relationship="son",
            phone="13800138000",
            priority=1
        )
    ],
    care_preferences=CarePreferences(),
    baseline_metrics=BaselineMetrics(
        average_daily_steps=3000,
        average_sleep_hours=7.5,
        typical_activity_periods=[(8, 10), (14, 16)],
        baseline_mobility_score=0.7
    )
)
```

## 测试

运行单元测试：

```bash
cd backend
python -m pytest tests/test_core_models.py -v
```

所有数据模型都有全面的单元测试，覆盖：
- 有效数据创建
- 边界条件验证
- 错误处理
- 隐私合规性检查

## 隐私保护

系统实施严格的隐私保护措施：

1. **骨骼数据必须匿名化** - 所有SkeletonData实例必须设置`anonymized=True`
2. **不存储原始视频** - 只存储提取的骨骼关键点
3. **敏感数据检测** - 验证函数检查并拒绝包含敏感信息的数据
4. **审计日志** - 所有数据访问都被记录用于合规性

## 需求映射

- **需求1.1, 1.2** - SkeletonData模型实现隐私保护的姿态数据
- **需求3.1** - FrailtyIndex模型实现衰弱指数计算
- **需求1.2** - 数据验证确保类型安全和完整性
