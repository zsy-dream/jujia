"""
核心数据模型和类型定义
Core data models and type definitions for Silver Age Actuary system
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum


class JointType(str, Enum):
    """骨骼关节类型枚举"""
    NOSE = "nose"
    LEFT_EYE = "left_eye"
    RIGHT_EYE = "right_eye"
    LEFT_EAR = "left_ear"
    RIGHT_EAR = "right_ear"
    LEFT_SHOULDER = "left_shoulder"
    RIGHT_SHOULDER = "right_shoulder"
    LEFT_ELBOW = "left_elbow"
    RIGHT_ELBOW = "right_elbow"
    LEFT_WRIST = "left_wrist"
    RIGHT_WRIST = "right_wrist"
    LEFT_HIP = "left_hip"
    RIGHT_HIP = "right_hip"
    LEFT_KNEE = "left_knee"
    RIGHT_KNEE = "right_knee"
    LEFT_ANKLE = "left_ankle"
    RIGHT_ANKLE = "right_ankle"


class IncidentType(str, Enum):
    """事件类型枚举"""
    FALL = "fall"
    FALL_DETECTED = "fall_detected"  # Alias for fall detection events
    MEDICAL_EMERGENCY = "medical_emergency"
    PROLONGED_INACTIVITY = "prolonged_inactivity"
    ABNORMAL_MOVEMENT = "abnormal_movement"
    MISSED_MEDICATION = "missed_medication"


class SeverityLevel(str, Enum):
    """严重程度级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"


class VerificationStatus(str, Enum):
    """验证状态"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    CANCELLED = "cancelled"


@dataclass
class Keypoint:
    """骨骼关键点数据"""
    joint_type: JointType
    x: float
    y: float
    z: Optional[float] = None
    visibility: float = 1.0
    
    def __post_init__(self):
        """数据验证"""
        if not 0.0 <= self.visibility <= 1.0:
            raise ValueError(f"Visibility must be between 0.0 and 1.0, got {self.visibility}")
        if self.z is not None and self.z < 0:
            raise ValueError(f"Z coordinate cannot be negative, got {self.z}")


@dataclass
class SkeletonData:
    """骨骼姿态数据 - 隐私保护的姿态估计数据"""
    timestamp: datetime
    user_id: str
    keypoints: List[Keypoint]
    confidence_scores: List[float]
    anonymized: bool = True
    
    def __post_init__(self):
        """数据完整性验证"""
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        
        if len(self.keypoints) != len(self.confidence_scores):
            raise ValueError(
                f"Keypoints count ({len(self.keypoints)}) must match "
                f"confidence_scores count ({len(self.confidence_scores)})"
            )
        
        for score in self.confidence_scores:
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {score}")
        
        # Privacy protection: all skeleton data must be anonymized
        if not self.anonymized:
            raise ValueError("Skeleton data must be anonymized for privacy protection")


@dataclass
class Location:
    """位置信息"""
    latitude: float
    longitude: float
    address: Optional[str] = None
    
    def __post_init__(self):
        """位置数据验证"""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {self.latitude}")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {self.longitude}")


@dataclass
class IncidentData:
    """事件数据 - 紧急和健康事件记录"""
    incident_id: str
    user_id: str
    incident_type: IncidentType
    timestamp: datetime
    severity: SeverityLevel
    location: Location
    sensor_data: Dict[str, Any]
    verification_status: VerificationStatus = VerificationStatus.PENDING
    
    def __post_init__(self):
        """事件数据验证"""
        if not self.incident_id:
            raise ValueError("incident_id cannot be empty")
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        if not isinstance(self.sensor_data, dict):
            raise ValueError("sensor_data must be a dictionary")


@dataclass
class FrailtyIndex:
    """衰弱指数 - 基于多项生理指标的标准化健康评估分数"""
    user_id: str
    score: float  # 0.0 到 1.0
    components: Dict[str, float]
    calculation_date: datetime
    confidence_interval: Tuple[float, float]
    
    def __post_init__(self):
        """衰弱指数验证"""
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Frailty score must be between 0.0 and 1.0, got {self.score}")
        
        # 验证置信区间
        lower, upper = self.confidence_interval
        if not 0.0 <= lower <= upper <= 1.0:
            raise ValueError(
                f"Invalid confidence interval: ({lower}, {upper}). "
                "Must satisfy 0.0 <= lower <= upper <= 1.0"
            )
        
        # 验证组件分数
        for component, value in self.components.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"Component '{component}' score must be between 0.0 and 1.0, got {value}"
                )


@dataclass
class RiskPrediction:
    """风险预测 - 预测模型输出和置信度分数"""
    user_id: str
    prediction_date: datetime
    fall_risk_score: float
    medical_emergency_risk: float
    mobility_decline_risk: float
    confidence_level: float
    contributing_factors: List[str]
    
    def __post_init__(self):
        """风险预测验证"""
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        
        # 验证所有风险分数在0-1范围内
        risk_scores = {
            "fall_risk_score": self.fall_risk_score,
            "medical_emergency_risk": self.medical_emergency_risk,
            "mobility_decline_risk": self.mobility_decline_risk,
            "confidence_level": self.confidence_level
        }
        
        for name, score in risk_scores.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0, got {score}")


@dataclass
class RiskAssessmentReport:
    """风险评估报告 - 30天分析报告"""
    user_id: str
    report_date: datetime
    period_start: datetime
    period_end: datetime
    current_frailty: 'FrailtyIndex'
    risk_prediction: 'RiskPrediction'
    trend_analysis: Dict[str, Any]
    confidence_intervals: Dict[str, Tuple[float, float]]
    recommendations: List[str]
    alert_level: str  # "low", "medium", "high", "emergency"
    
    def __post_init__(self):
        """风险评估报告验证"""
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        
        if self.alert_level not in ["low", "medium", "high", "emergency"]:
            raise ValueError(
                f"alert_level must be one of: low, medium, high, emergency. Got: {self.alert_level}"
            )
        
        if self.period_start > self.period_end:
            raise ValueError("period_start must be before period_end")
        
        # 验证置信区间
        for risk_type, (lower, upper) in self.confidence_intervals.items():
            if not 0.0 <= lower <= upper <= 1.0:
                raise ValueError(
                    f"Invalid confidence interval for {risk_type}: ({lower}, {upper})"
                )



@dataclass
class MedicalCondition:
    """医疗状况"""
    condition_name: str
    diagnosed_date: datetime
    severity: str
    notes: Optional[str] = None


@dataclass
class MobilityAid:
    """移动辅助设备"""
    aid_type: str  # e.g., "walker", "cane", "wheelchair"
    start_date: datetime
    notes: Optional[str] = None


@dataclass
class EmergencyContact:
    """紧急联系人"""
    name: str
    relationship: str
    phone: str
    email: Optional[str] = None
    priority: int = 1  # 1 = highest priority
    
    def __post_init__(self):
        """紧急联系人验证"""
        if not self.name:
            raise ValueError("Emergency contact name cannot be empty")
        if not self.phone:
            raise ValueError("Emergency contact phone cannot be empty")
        if self.priority < 1:
            raise ValueError(f"Priority must be >= 1, got {self.priority}")


@dataclass
class CarePreferences:
    """护理偏好"""
    preferred_language: str = "zh-CN"
    ambient_light_enabled: bool = True
    audio_alerts_enabled: bool = True
    voice_confirmation_enabled: bool = True
    emergency_auto_escalation: bool = True
    notification_preferences: Dict[str, bool] = field(default_factory=lambda: {
        "sms": True,
        "email": True,
        "push": True
    })


@dataclass
class BaselineMetrics:
    """基线健康指标"""
    average_daily_steps: int
    average_sleep_hours: float
    typical_activity_periods: List[Tuple[int, int]]  # (start_hour, end_hour)
    baseline_mobility_score: float
    
    def __post_init__(self):
        """基线指标验证"""
        if self.average_daily_steps < 0:
            raise ValueError("Average daily steps cannot be negative")
        if not 0 <= self.average_sleep_hours <= 24:
            raise ValueError(f"Average sleep hours must be between 0 and 24, got {self.average_sleep_hours}")
        if not 0.0 <= self.baseline_mobility_score <= 1.0:
            raise ValueError(f"Baseline mobility score must be between 0.0 and 1.0, got {self.baseline_mobility_score}")


@dataclass
class UserProfile:
    """用户档案 - 详细健康和偏好数据"""
    user_id: str
    age: int
    medical_conditions: List[MedicalCondition]
    mobility_aids: List[MobilityAid]
    emergency_contacts: List[EmergencyContact]
    care_preferences: CarePreferences
    baseline_metrics: BaselineMetrics
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """用户档案验证"""
        if not self.user_id:
            raise ValueError("user_id cannot be empty")
        
        if self.age < 0 or self.age > 150:
            raise ValueError(f"Age must be between 0 and 150, got {self.age}")
        
        if not self.emergency_contacts:
            raise ValueError("At least one emergency contact is required")
        
        # 验证紧急联系人优先级唯一性
        priorities = [contact.priority for contact in self.emergency_contacts]
        if len(priorities) != len(set(priorities)):
            raise ValueError("Emergency contact priorities must be unique")
