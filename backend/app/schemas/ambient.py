"""
环境交互界面数据模型
Ambient interface data models for Silver Age Actuary system
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum


class RiskLevel(str, Enum):
    """风险级别枚举"""
    NORMAL = "normal"
    CAUTION = "caution"
    ATTENTION_NEEDED = "attention_needed"
    EMERGENCY = "emergency"


class HealthStatus(str, Enum):
    """健康状态枚举"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class LightingPattern(str, Enum):
    """灯光模式枚举"""
    CALM_BLUE = "calm_blue"
    AMBER_CAUTION = "amber_caution"
    PULSING_RED = "pulsing_red"
    MEDICATION_REMINDER = "medication_reminder"
    SYSTEM_STATUS = "system_status"
    OFF = "off"


class EmergencyType(str, Enum):
    """紧急类型枚举"""
    FALL = "fall"
    MEDICAL = "medical"
    FIRE = "fire"
    INTRUSION = "intrusion"


class ReminderType(str, Enum):
    """提醒类型枚举"""
    MEDICATION = "medication"
    APPOINTMENT = "appointment"
    ACTIVITY = "activity"
    HYDRATION = "hydration"


@dataclass
class LightingConfig:
    """灯光配置"""
    enabled: bool = True
    brightness_day: float = 0.8  # 0.0 to 1.0
    brightness_night: float = 0.3  # 0.0 to 1.0
    transition_duration: float = 2.0  # seconds
    smart_home_integration: Optional[str] = None  # "philips_hue", "lifx", etc.
    device_ids: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """验证灯光配置"""
        if not 0.0 <= self.brightness_day <= 1.0:
            raise ValueError(f"brightness_day must be between 0.0 and 1.0, got {self.brightness_day}")
        if not 0.0 <= self.brightness_night <= 1.0:
            raise ValueError(f"brightness_night must be between 0.0 and 1.0, got {self.brightness_night}")
        if self.transition_duration < 0:
            raise ValueError(f"transition_duration cannot be negative, got {self.transition_duration}")


@dataclass
class AudioConfig:
    """音频配置"""
    enabled: bool = True
    volume_day: float = 0.7  # 0.0 to 1.0
    volume_night: float = 0.4  # 0.0 to 1.0
    voice_enabled: bool = True
    preferred_voice: str = "zh-CN-female"
    audio_device: Optional[str] = None
    
    def __post_init__(self):
        """验证音频配置"""
        if not 0.0 <= self.volume_day <= 1.0:
            raise ValueError(f"volume_day must be between 0.0 and 1.0, got {self.volume_day}")
        if not 0.0 <= self.volume_night <= 1.0:
            raise ValueError(f"volume_night must be between 0.0 and 1.0, got {self.volume_night}")


@dataclass
class UserPreferences:
    """用户偏好"""
    user_id: str
    lighting_config: LightingConfig
    audio_config: AudioConfig
    quiet_hours_start: int = 22  # 22:00
    quiet_hours_end: int = 7  # 07:00
    medication_reminder_advance: int = 15  # minutes before
    
    def __post_init__(self):
        """验证用户偏好"""
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        if not 0 <= self.quiet_hours_start <= 23:
            raise ValueError(f"quiet_hours_start must be between 0 and 23, got {self.quiet_hours_start}")
        if not 0 <= self.quiet_hours_end <= 23:
            raise ValueError(f"quiet_hours_end must be between 0 and 23, got {self.quiet_hours_end}")
        if self.medication_reminder_advance < 0:
            raise ValueError(f"medication_reminder_advance cannot be negative")


@dataclass
class SystemHealth:
    """系统健康状态"""
    overall_status: str  # "healthy", "degraded", "offline"
    edge_device_online: bool
    cloud_connection: bool
    last_heartbeat: datetime
    error_count: int = 0
    
    def __post_init__(self):
        """验证系统健康状态"""
        if self.overall_status not in ["healthy", "degraded", "offline"]:
            raise ValueError(f"Invalid overall_status: {self.overall_status}")
        if self.error_count < 0:
            raise ValueError(f"error_count cannot be negative")


@dataclass
class MedicationReminder:
    """药物提醒"""
    medication_name: str
    scheduled_time: datetime
    dosage: str
    instructions: Optional[str] = None
    reminder_sent: bool = False
    acknowledged: bool = False
    
    def __post_init__(self):
        """验证药物提醒"""
        if not self.medication_name:
            raise ValueError("medication_name cannot be empty")
        if not self.dosage:
            raise ValueError("dosage cannot be empty")


@dataclass
class VoiceResponse:
    """语音响应"""
    message: str
    language: str = "zh-CN"
    voice_type: str = "female"
    urgency: str = "normal"  # "low", "normal", "high", "emergency"
    
    def __post_init__(self):
        """验证语音响应"""
        if not self.message:
            raise ValueError("message cannot be empty")
        if self.urgency not in ["low", "normal", "high", "emergency"]:
            raise ValueError(f"Invalid urgency level: {self.urgency}")


@dataclass
class AmbientFeedback:
    """环境反馈状态"""
    timestamp: datetime
    user_id: str
    health_status: HealthStatus
    risk_level: RiskLevel
    lighting_pattern: LightingPattern
    audio_message: Optional[str] = None
    brightness: float = 0.8
    
    def __post_init__(self):
        """验证环境反馈"""
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        if not 0.0 <= self.brightness <= 1.0:
            raise ValueError(f"brightness must be between 0.0 and 1.0, got {self.brightness}")
