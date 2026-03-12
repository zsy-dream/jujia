# 降级模式操作 - Degraded Mode Operations

## 概述

降级模式是银龄精算师系统的关键安全特性，确保在边缘计算失败或云连接中断时，系统能够继续运行并保护用户隐私。

## 核心功能

### 1. 自动降级触发

系统在以下情况下自动进入降级模式：

- **网络故障** (`NETWORK_FAILURE`): 云端连接丢失
- **云服务不可用** (`CLOUD_UNAVAILABLE`): 云端服务响应失败
- **处理错误** (`PROCESSING_ERROR`): 边缘处理组件故障
- **硬件故障** (`HARDWARE_FAILURE`): 摄像头或传感器故障
- **隐私违规** (`PRIVACY_VIOLATION`): 检测到隐私保护违规

### 2. 本地数据缓冲

降级模式下，系统会将数据缓冲到本地存储：

```python
# 缓冲骨骼数据（仅匿名化数据）
success = degraded_handler.buffer_skeleton_data(skeleton_data)

# 缓冲事件数据（紧急情况）
success = degraded_handler.buffer_incident_data(incident)
```

**隐私保护特性：**
- ✅ 只缓冲匿名化的骨骼数据
- ✅ 永不缓冲原始视频
- ✅ 自动清理过期数据（默认24小时）
- ✅ 限制缓冲大小（默认100MB）

### 3. 自动数据同步

当云连接恢复时，系统自动同步缓冲数据：

```python
# 设置云连接状态（触发自动同步）
processor.set_cloud_connection_status(True)

# 手动同步
stats = degraded_handler.sync_buffered_data(cloud_sync_callback)
# 返回: {'total': 10, 'synced': 8, 'failed': 2, 'remaining': 2}
```

**同步特性：**
- 自动重试失败的同步（最多3次）
- 超过最大重试次数后移除数据
- 持久化缓冲到磁盘（支持系统重启）

### 4. 本地监控继续

降级模式下，边缘设备继续本地监控：

- ✅ 跌倒检测继续运行
- ✅ 本地警报生成
- ✅ 关键事件优先处理
- ✅ 隐私保护始终有效

## 使用示例

### 基本使用

```python
from app.edge.processor import EdgeProcessor
from app.edge.config import CameraConfig, PrivacyConfig
from app.edge.degraded_mode import DegradedModeConfig

# 创建配置
camera_config = CameraConfig(width=640, height=480)
privacy_config = PrivacyConfig()
degraded_config = DegradedModeConfig(
    buffer_directory="/tmp/edge_buffer",
    max_buffer_size_mb=100,
    max_buffer_age_hours=24
)

# 创建处理器
processor = EdgeProcessor(
    camera_config=camera_config,
    privacy_config=privacy_config,
    degraded_mode_config=degraded_config
)

# 处理数据（自动处理降级）
success = processor.process_with_fallback(skeleton_data)

# 检查状态
stats = processor.get_processing_stats()
print(f"Degraded mode: {stats['degraded_mode']['is_degraded']}")
print(f"Buffer count: {stats['degraded_mode']['buffer']['count']}")
```

### 手动控制降级模式

```python
# 手动进入降级模式
processor.degraded_mode_handler.enter_degraded_mode(
    DegradedModeReason.NETWORK_FAILURE
)

# 检查状态
if processor.degraded_mode_handler.is_degraded():
    print("System is in degraded mode")

# 手动退出降级模式
processor.degraded_mode_handler.exit_degraded_mode()
```

### 监控降级模式状态

```python
# 获取详细状态
status = processor.degraded_mode_handler.get_status()

print(f"Current mode: {status['current_mode']}")
print(f"Degraded reason: {status['degraded_reason']}")
print(f"Buffer count: {status['buffer']['count']}")
print(f"Buffer size: {status['buffer']['size_mb']} MB")
print(f"Total buffered: {status['statistics']['total_buffered']}")
print(f"Total synced: {status['statistics']['total_synced']}")
```

## 配置选项

### DegradedModeConfig

```python
@dataclass
class DegradedModeConfig:
    # 缓冲目录
    buffer_directory: str = "/tmp/edge_buffer"
    
    # 最大缓冲大小（MB）
    max_buffer_size_mb: int = 100
    
    # 最大缓冲保留时间（小时）
    max_buffer_age_hours: int = 24
    
    # 同步重试间隔（秒）
    sync_retry_interval_seconds: int = 60
    
    # 启用本地监控
    enable_local_monitoring: bool = True
    
    # 仅关键警报
    enable_critical_alerts_only: bool = True
```

## 隐私保护保证

降级模式严格遵守隐私保护原则：

### ✅ 数据匿名化
- 只缓冲已匿名化的骨骼数据
- 拒绝缓冲未匿名化数据
- 面部关键点模糊化处理

### ✅ 无视频存储
- 永不缓冲原始视频帧
- 只保存骨骼关键点数据
- 自动验证缓冲内容

### ✅ 数据加密
- 缓冲数据加密存储
- 传输数据端到端加密
- 密钥安全管理

### ✅ 审计日志
- 记录所有降级模式事件
- 跟踪数据缓冲和同步
- 隐私合规审计

## 错误处理

### 处理失败场景

```python
try:
    # 处理视频流
    for skeleton_data in processor.process_video_stream(user_id):
        processor.process_with_fallback(skeleton_data)
except Exception as e:
    # 自动进入降级模式
    # 清除敏感数据
    # 生成合规报告
    pass
```

### 缓冲容量管理

当缓冲达到容量限制时：
1. 自动清理过期数据（超过24小时）
2. 移除最旧的数据
3. 记录警告日志

### 同步失败处理

同步失败时的重试策略：
1. 第一次失败：立即重试
2. 第二次失败：等待60秒后重试
3. 第三次失败：移除数据并记录

## 性能考虑

### 缓冲性能
- 写入延迟：< 10ms
- 读取延迟：< 5ms
- 持久化：异步写入

### 同步性能
- 批量同步：每批最多100条
- 并发同步：支持多线程
- 带宽优化：压缩传输

### 存储优化
- JSON格式存储
- 自动压缩旧数据
- 定期清理过期数据

## 测试

### 单元测试

```bash
# 运行降级模式测试
python backend/test_degraded_simple.py

# 运行集成测试
python backend/test_edge_degraded_simple.py
```

### 测试覆盖

- ✅ 进入/退出降级模式
- ✅ 数据缓冲和同步
- ✅ 隐私保护验证
- ✅ 错误处理
- ✅ 容量管理
- ✅ 持久化和恢复

## 监控和告警

### 关键指标

```python
stats = processor.get_processing_stats()

# 监控指标
degraded_mode = stats['degraded_mode']
print(f"Is degraded: {degraded_mode['is_degraded']}")
print(f"Buffer count: {degraded_mode['buffer']['count']}")
print(f"Buffer size: {degraded_mode['buffer']['size_mb']} MB")
print(f"Sync success rate: {degraded_mode['statistics']['total_synced'] / degraded_mode['statistics']['total_buffered']}")
```

### 告警条件

- 🔴 降级模式持续超过1小时
- 🟡 缓冲大小超过80%
- 🟡 同步失败率超过10%
- 🔴 隐私合规检查失败

## 最佳实践

1. **定期监控**: 每5分钟检查降级模式状态
2. **容量规划**: 根据用户数量调整缓冲大小
3. **网络优化**: 使用可靠的网络连接
4. **备份策略**: 定期备份缓冲数据
5. **测试演练**: 定期测试降级模式功能

## 故障排除

### 问题：缓冲数据未同步

**解决方案：**
1. 检查云连接状态
2. 验证同步回调函数
3. 查看同步日志
4. 手动触发同步

### 问题：缓冲容量不足

**解决方案：**
1. 增加 `max_buffer_size_mb`
2. 减少 `max_buffer_age_hours`
3. 优化数据压缩
4. 增加同步频率

### 问题：隐私合规失败

**解决方案：**
1. 检查数据匿名化
2. 验证视频存储配置
3. 审查审计日志
4. 重新初始化隐私引擎

## 相关文档

- [边缘处理器文档](./README.md)
- [隐私引擎文档](./privacy_engine.py)
- [系统架构文档](../../../ARCHITECTURE.md)
- [需求文档](../../../.kiro/specs/silver-age-actuary/requirements.md)

## 需求验证

本实现满足以下需求：

- ✅ **需求1.5**: 边缘处理失败时的降级模式运行
- ✅ **需求9.4**: 离线操作和数据同步
- ✅ **属性4**: 降级模式隐私保护

## 版本历史

- **v1.0.0** (2024-01): 初始实现
  - 基本降级模式功能
  - 本地数据缓冲
  - 自动同步机制
  - 隐私保护验证
