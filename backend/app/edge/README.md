# 边缘计算模块 - Edge Computing Module

## 概述

边缘计算模块实现了隐私优先的视频处理和骨骼提取功能，确保原始视频永不离开设备，只传输匿名化的骨骼姿态数据。

## 核心组件

### 1. EdgeProcessor（边缘处理器）

主处理单元，集成视频处理、骨骼提取和隐私保护。

**核心功能：**
- 视频流处理 - 从摄像头捕获视频帧
- 骨骼提取 - 提取姿态关键点
- 跌倒检测 - 实时检测跌倒事件
- 隐私保护 - 确保不存储或传输原始视频

**使用示例：**
```python
from app.edge.processor import EdgeProcessor
from app.edge.config import CameraConfig, PrivacyConfig

# 配置
camera_config = CameraConfig(width=640, height=480, fps=30)
privacy_config = PrivacyConfig()

# 创建处理器
processor = EdgeProcessor(camera_config, privacy_config)

# 处理视频流
for skeleton_data in processor.process_video_stream(user_id="user_123"):
    # skeleton_data 是匿名化的骨骼数据
    print(f"Processed frame with {len(skeleton_data.keypoints)} keypoints")
    
    # 检测跌倒
    fall_event = processor.detect_falls(skeleton_data)
    if fall_event.detected:
        print(f"Fall detected with confidence {fall_event.confidence}")
```

### 2. SkeletonExtractor（骨骼提取器）

使用YOLOv8和OpenPose进行姿态关键点提取。

**核心功能：**
- 人体检测（YOLOv8）
- 姿态估计（OpenPose）
- 关键点提取和转换
- 性能监控（目标<100ms）

**使用示例：**
```python
from app.edge.skeleton_extractor import SkeletonExtractor, VideoFrame
from app.edge.config import ProcessingConfig
import numpy as np

# 配置
config = ProcessingConfig(target_latency_ms=100)
extractor = SkeletonExtractor(config=config)

# 提取姿态
frame_data = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
frame = VideoFrame(frame_data, datetime.utcnow())
pose = extractor.extract_pose(frame)

# 匿名化数据
skeleton_data = extractor.anonymize_data(pose, user_id="user_123")

# 获取性能统计
stats = extractor.get_performance_stats()
print(f"Average processing time: {stats['average_ms']}ms")
```

### 3. PrivacyEngine（隐私引擎）

数据匿名化和隐私合规验证。

**核心功能：**
- 数据匿名化 - 移除生物识别标识符
- 传输验证 - 确保只传输匿名化数据
- 审计日志 - 记录所有隐私相关操作
- 违规检测 - 阻止任何违反隐私的操作

**使用示例：**
```python
from app.edge.privacy_engine import PrivacyEngine
from app.edge.config import PrivacyConfig

# 配置
config = PrivacyConfig()
engine = PrivacyEngine(config)

# 匿名化骨骼数据
anonymized = engine.anonymize_skeleton_data(skeleton_data)

# 验证传输
validation = engine.validate_data_transmission(anonymized)
if not validation.is_valid:
    print(f"Privacy violations: {validation.violations}")

# 加密数据
encrypted = engine.encrypt_skeleton_data(anonymized)

# 审计合规性
report = engine.audit_privacy_compliance()
print(f"Compliance status: {report['compliance_status']}")
```

## 配置

### CameraConfig（摄像头配置）

```python
@dataclass
class CameraConfig:
    camera_id: int = 0          # 摄像头ID
    width: int = 640            # 分辨率宽度
    height: int = 480           # 分辨率高度
    fps: int = 30               # 帧率
    format: str = "MJPEG"       # 视频格式
```

### PrivacyConfig（隐私配置）

```python
@dataclass
class PrivacyConfig:
    enable_video_storage: bool = False      # 永不存储原始视频
    enable_anonymization: bool = True       # 始终匿名化
    enable_encryption: bool = True          # 始终加密传输
    audit_logging: bool = True              # 审计日志
    max_retention_hours: int = 0            # 不保留原始视频
```

**注意：** 隐私配置强制执行隐私保护，不允许修改关键设置。

### ProcessingConfig（处理配置）

```python
@dataclass
class ProcessingConfig:
    target_latency_ms: int = 100                # 目标延迟100毫秒
    pose_confidence_threshold: float = 0.5      # 姿态置信度阈值
    fall_detection_enabled: bool = True         # 启用跌倒检测
    buffer_size: int = 30                       # 缓冲帧数
```

## 隐私保护机制

### 1. 数据匿名化

- **用户ID哈希化：** 使用SHA-256哈希化用户ID
- **面部特征模糊化：** 降低面部关键点精度到10像素
- **可见性降低：** 面部关键点可见性降低到≤0.5

### 2. 传输验证

- **匿名化检查：** 确保所有SkeletonData标记为anonymized=True
- **视频数据阻止：** 检测并拒绝大型二进制数据（>100KB）
- **加密要求：** 强制所有传输使用加密

### 3. 审计日志

记录所有隐私相关操作：
- 数据匿名化事件
- 数据加密事件
- 隐私违规尝试
- 传输验证结果

### 4. 降级模式

处理失败时的隐私保护：
- 立即停止视频处理
- 清除所有缓存数据
- 生成合规报告
- 通知系统管理员

## 性能要求

- **实时处理：** 目标延迟 < 100ms
- **跌倒检测：** 5秒内触发紧急协议
- **姿态估计：** 100ms内完成处理

## 测试

运行手动测试：

```bash
cd backend
python test_edge_manual.py
```

运行单元测试：

```bash
cd backend
pytest tests/test_edge_processor.py -v
```

## 依赖

- numpy >= 1.26.3 - 数组处理
- 未来集成：
  - YOLOv8 - 人体检测
  - OpenPose - 姿态估计
  - OpenCV - 视频处理

## 架构设计原则

1. **隐私优先：** 原始视频永不离开设备
2. **实时处理：** 目标延迟<100ms
3. **降级模式：** 处理失败时保持隐私保护
4. **审计跟踪：** 记录所有隐私相关操作
5. **强制合规：** 配置级别强制隐私保护

## 未来改进

1. **真实模型集成：** 集成真实的YOLOv8和OpenPose模型
2. **硬件加速：** 使用GPU加速姿态估计
3. **多摄像头支持：** 支持多个摄像头同时处理
4. **高级加密：** 使用AES-256-GCM加密
5. **边缘AI优化：** 针对边缘设备优化模型

## 相关需求

- **需求1.1：** 边缘设备提取骨骼姿态数据而不存储原始视频
- **需求1.2：** 边缘设备匿名化所有生物识别标识符
- **需求1.3：** 100毫秒内完成姿态估计处理
- **需求1.4：** 阻止视频存储并记录隐私违规
- **需求1.5：** 降级模式下保持隐私保护
