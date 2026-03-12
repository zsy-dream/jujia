"""
降级模式处理器 - Degraded Mode Handler
边缘计算失败时的后备处理，确保系统故障期间的隐私保护
Fallback processing when edge computing fails, ensuring privacy protection during system failures
"""
import json
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from app.schemas.core import SkeletonData, IncidentData


class DegradedModeReason(Enum):
    """降级模式原因"""
    NETWORK_FAILURE = "network_failure"
    CLOUD_UNAVAILABLE = "cloud_unavailable"
    PROCESSING_ERROR = "processing_error"
    HARDWARE_FAILURE = "hardware_failure"
    PRIVACY_VIOLATION = "privacy_violation"


class OperationMode(Enum):
    """操作模式"""
    NORMAL = "normal"
    DEGRADED = "degraded"
    OFFLINE = "offline"


@dataclass
class BufferedData:
    """缓冲数据结构"""
    data_id: str
    data_type: str
    timestamp: datetime
    data: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'data_id': self.data_id,
            'data_type': self.data_type,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BufferedData':
        """从字典创建"""
        return cls(
            data_id=data['data_id'],
            data_type=data['data_type'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            data=data['data'],
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3)
        )


@dataclass
class DegradedModeConfig:
    """降级模式配置"""
    buffer_directory: str = "/tmp/edge_buffer"
    max_buffer_size_mb: int = 100
    max_buffer_age_hours: int = 24
    sync_retry_interval_seconds: int = 60
    enable_local_monitoring: bool = True
    enable_critical_alerts_only: bool = True
    
    def __post_init__(self):
        # 创建缓冲目录
        Path(self.buffer_directory).mkdir(parents=True, exist_ok=True)


class DegradedModeHandler:
    """
    降级模式处理器 - 边缘计算失败时的后备处理
    
    核心功能：
    1. 本地数据缓冲 - 在无法连接云端时缓存数据
    2. 隐私保护 - 确保降级模式下的隐私合规
    3. 自动同步 - 连接恢复后自动同步缓冲数据
    4. 本地监控 - 降级模式下继续本地跌倒检测
    
    设计原则：
    - 隐私优先：降级模式下也不存储原始视频
    - 弹性恢复：自动检测连接恢复并同步
    - 资源管理：限制缓冲大小和保留时间
    """
    
    def __init__(self, config: Optional[DegradedModeConfig] = None):
        """
        初始化降级模式处理器
        
        Args:
            config: 降级模式配置
        """
        self.config = config or DegradedModeConfig()
        self.current_mode = OperationMode.NORMAL
        self.degraded_reason: Optional[DegradedModeReason] = None
        self.degraded_since: Optional[datetime] = None
        
        # 数据缓冲
        self.buffer: List[BufferedData] = []
        self.buffer_file = Path(self.config.buffer_directory) / "buffer.json"
        
        # 统计信息
        self.buffered_count = 0
        self.synced_count = 0
        self.failed_sync_count = 0
        
        # 加载持久化缓冲
        self._load_buffer()
    
    def enter_degraded_mode(self, reason: DegradedModeReason):
        """
        进入降级模式
        
        Args:
            reason: 降级原因
        """
        if self.current_mode != OperationMode.DEGRADED:
            self.current_mode = OperationMode.DEGRADED
            self.degraded_reason = reason
            self.degraded_since = datetime.utcnow()
            
            print(f"[DegradedMode] Entered degraded mode: {reason.value}")
            print(f"[DegradedMode] Local monitoring: {self.config.enable_local_monitoring}")
            print(f"[DegradedMode] Critical alerts only: {self.config.enable_critical_alerts_only}")
    
    def exit_degraded_mode(self):
        """退出降级模式，恢复正常操作"""
        if self.current_mode == OperationMode.DEGRADED:
            duration = (datetime.utcnow() - self.degraded_since).total_seconds()
            print(f"[DegradedMode] Exiting degraded mode after {duration:.1f} seconds")
            
            self.current_mode = OperationMode.NORMAL
            self.degraded_reason = None
            self.degraded_since = None
    
    def is_degraded(self) -> bool:
        """检查是否处于降级模式"""
        return self.current_mode == OperationMode.DEGRADED
    
    def buffer_skeleton_data(self, skeleton_data: SkeletonData) -> bool:
        """
        缓冲骨骼数据（隐私保护）
        
        只缓冲匿名化的骨骼数据，永不缓冲原始视频
        
        Args:
            skeleton_data: 骨骼数据（必须已匿名化）
            
        Returns:
            True如果成功缓冲
        """
        # 验证隐私合规
        if not skeleton_data.anonymized:
            print("[DegradedMode] ERROR: Cannot buffer non-anonymized data")
            return False
        
        # 检查缓冲大小限制
        if not self._check_buffer_capacity():
            print("[DegradedMode] WARNING: Buffer capacity exceeded, removing old data")
            self._cleanup_old_buffer_data()
        
        # 创建缓冲数据
        buffered = BufferedData(
            data_id=f"skeleton_{skeleton_data.timestamp.timestamp()}",
            data_type="skeleton_data",
            timestamp=skeleton_data.timestamp,
            data={
                'user_id': skeleton_data.user_id,
                'timestamp': skeleton_data.timestamp.isoformat(),
                'keypoints': [
                    {
                        'joint_type': kp.joint_type.value,
                        'x': kp.x,
                        'y': kp.y,
                        'z': kp.z,
                        'visibility': kp.visibility
                    }
                    for kp in skeleton_data.keypoints
                ],
                'confidence_scores': skeleton_data.confidence_scores,
                'anonymized': skeleton_data.anonymized
            }
        )
        
        self.buffer.append(buffered)
        self.buffered_count += 1
        
        # 持久化缓冲
        self._save_buffer()
        
        return True
    
    def buffer_incident_data(self, incident: IncidentData) -> bool:
        """
        缓冲事件数据（紧急情况）
        
        Args:
            incident: 事件数据
            
        Returns:
            True如果成功缓冲
        """
        # 检查缓冲容量
        if not self._check_buffer_capacity():
            self._cleanup_old_buffer_data()
        
        # 创建缓冲数据
        buffered = BufferedData(
            data_id=incident.incident_id,
            data_type="incident_data",
            timestamp=incident.timestamp,
            data={
                'incident_id': incident.incident_id,
                'user_id': incident.user_id,
                'incident_type': incident.incident_type.value,
                'timestamp': incident.timestamp.isoformat(),
                'severity': incident.severity.value,
                'location': {
                    'latitude': incident.location.latitude,
                    'longitude': incident.location.longitude,
                    'address': incident.location.address
                } if incident.location else None,
                'verification_status': incident.verification_status.value
            }
        )
        
        self.buffer.append(buffered)
        self.buffered_count += 1
        
        # 持久化缓冲
        self._save_buffer()
        
        return True
    
    def sync_buffered_data(self, cloud_sync_callback) -> Dict[str, int]:
        """
        同步缓冲数据到云端
        
        Args:
            cloud_sync_callback: 云端同步回调函数
            
        Returns:
            同步统计信息
        """
        if not self.buffer:
            return {
                'total': 0,
                'synced': 0,
                'failed': 0,
                'remaining': 0
            }
        
        synced = 0
        failed = 0
        
        # 复制缓冲列表以避免迭代时修改
        buffer_copy = self.buffer.copy()
        
        for buffered_data in buffer_copy:
            try:
                # 尝试同步到云端
                success = cloud_sync_callback(buffered_data)
                
                if success:
                    # 同步成功，从缓冲中移除
                    self.buffer.remove(buffered_data)
                    synced += 1
                    self.synced_count += 1
                else:
                    # 同步失败，增加重试计数
                    buffered_data.retry_count += 1
                    failed += 1
                    
                    # 如果超过最大重试次数，移除数据
                    if buffered_data.retry_count >= buffered_data.max_retries:
                        print(f"[DegradedMode] Max retries exceeded for {buffered_data.data_id}, removing")
                        self.buffer.remove(buffered_data)
                        self.failed_sync_count += 1
                        
            except Exception as e:
                print(f"[DegradedMode] Sync error for {buffered_data.data_id}: {e}")
                buffered_data.retry_count += 1
                failed += 1
        
        # 持久化更新后的缓冲
        self._save_buffer()
        
        return {
            'total': len(buffer_copy),
            'synced': synced,
            'failed': failed,
            'remaining': len(self.buffer)
        }
    
    def _check_buffer_capacity(self) -> bool:
        """
        检查缓冲容量
        
        Returns:
            True如果有足够容量
        """
        # 检查缓冲大小
        buffer_size_mb = self._get_buffer_size_mb()
        
        if buffer_size_mb >= self.config.max_buffer_size_mb:
            return False
        
        return True
    
    def _get_buffer_size_mb(self) -> float:
        """
        获取缓冲大小（MB）
        
        Returns:
            缓冲大小
        """
        if not self.buffer_file.exists():
            return 0.0
        
        size_bytes = self.buffer_file.stat().st_size
        return size_bytes / (1024 * 1024)
    
    def _cleanup_old_buffer_data(self):
        """清理过期的缓冲数据"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.config.max_buffer_age_hours)
        
        original_count = len(self.buffer)
        self.buffer = [
            data for data in self.buffer
            if data.timestamp > cutoff_time
        ]
        
        removed_count = original_count - len(self.buffer)
        if removed_count > 0:
            print(f"[DegradedMode] Cleaned up {removed_count} old buffer entries")
            self._save_buffer()
    
    def _save_buffer(self):
        """持久化缓冲到磁盘"""
        try:
            buffer_data = [data.to_dict() for data in self.buffer]
            
            with open(self.buffer_file, 'w') as f:
                json.dump(buffer_data, f, indent=2)
                
        except Exception as e:
            print(f"[DegradedMode] Failed to save buffer: {e}")
    
    def _load_buffer(self):
        """从磁盘加载缓冲"""
        try:
            if self.buffer_file.exists():
                with open(self.buffer_file, 'r') as f:
                    buffer_data = json.load(f)
                
                self.buffer = [BufferedData.from_dict(data) for data in buffer_data]
                print(f"[DegradedMode] Loaded {len(self.buffer)} buffered entries")
                
        except Exception as e:
            print(f"[DegradedMode] Failed to load buffer: {e}")
            self.buffer = []
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取降级模式状态
        
        Returns:
            状态信息
        """
        status = {
            'current_mode': self.current_mode.value,
            'is_degraded': self.is_degraded(),
            'degraded_reason': self.degraded_reason.value if self.degraded_reason else None,
            'degraded_duration_seconds': (
                (datetime.utcnow() - self.degraded_since).total_seconds()
                if self.degraded_since else 0
            ),
            'buffer': {
                'count': len(self.buffer),
                'size_mb': self._get_buffer_size_mb(),
                'max_size_mb': self.config.max_buffer_size_mb,
                'oldest_entry': (
                    min(data.timestamp for data in self.buffer).isoformat()
                    if self.buffer else None
                )
            },
            'statistics': {
                'total_buffered': self.buffered_count,
                'total_synced': self.synced_count,
                'total_failed': self.failed_sync_count
            },
            'config': {
                'local_monitoring_enabled': self.config.enable_local_monitoring,
                'critical_alerts_only': self.config.enable_critical_alerts_only,
                'max_buffer_age_hours': self.config.max_buffer_age_hours
            }
        }
        
        return status
    
    def clear_buffer(self):
        """清空缓冲（用于测试或维护）"""
        self.buffer.clear()
        self._save_buffer()
        print("[DegradedMode] Buffer cleared")
