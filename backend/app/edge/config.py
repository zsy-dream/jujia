"""
边缘设备配置 - Edge Device Configuration
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class CameraConfig:
    """摄像头配置"""
    camera_id: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
    format: str = "MJPEG"
    
    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Camera width and height must be positive")
        if self.fps <= 0:
            raise ValueError("FPS must be positive")


@dataclass
class PrivacyConfig:
    """隐私保护配置"""
    enable_video_storage: bool = False  # 永不存储原始视频
    enable_anonymization: bool = True  # 始终匿名化
    enable_encryption: bool = True  # 始终加密传输
    audit_logging: bool = True  # 审计日志
    max_retention_hours: int = 0  # 不保留原始视频
    
    def __post_init__(self):
        # 强制隐私保护设置
        if self.enable_video_storage:
            raise ValueError("Video storage is not allowed for privacy protection")
        if not self.enable_anonymization:
            raise ValueError("Anonymization must be enabled")
        if not self.enable_encryption:
            raise ValueError("Encryption must be enabled")


@dataclass
class ProcessingConfig:
    """处理配置"""
    target_latency_ms: int = 100  # 目标延迟100毫秒
    pose_confidence_threshold: float = 0.5
    fall_detection_enabled: bool = True
    buffer_size: int = 30  # 缓冲帧数
    
    def __post_init__(self):
        if self.target_latency_ms <= 0:
            raise ValueError("Target latency must be positive")
        if not 0.0 <= self.pose_confidence_threshold <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
