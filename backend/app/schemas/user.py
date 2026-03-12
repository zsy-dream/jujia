"""
用户和档案相关的Pydantic模式
User and profile related Pydantic schemas for API
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# 认证相关模式
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    age: int = Field(..., ge=0, le=150)


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    age: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 紧急联系人模式
class EmergencyContactCreate(BaseModel):
    name: str
    relationship: str
    phone: str
    email: Optional[EmailStr] = None
    priority: int = Field(default=1, ge=1)


class EmergencyContactUpdate(BaseModel):
    name: Optional[str] = None
    relationship: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    priority: Optional[int] = Field(None, ge=1)


class EmergencyContactResponse(BaseModel):
    id: int
    name: str
    relationship: str
    phone: str
    email: Optional[str]
    priority: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 医疗状况模式
class MedicalConditionCreate(BaseModel):
    condition_name: str
    diagnosed_date: datetime
    severity: str
    notes: Optional[str] = None


class MedicalConditionUpdate(BaseModel):
    condition_name: Optional[str] = None
    diagnosed_date: Optional[datetime] = None
    severity: Optional[str] = None
    notes: Optional[str] = None


class MedicalConditionResponse(BaseModel):
    id: int
    condition_name: str
    diagnosed_date: datetime
    severity: str
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 移动辅助设备模式
class MobilityAidCreate(BaseModel):
    aid_type: str
    start_date: datetime
    notes: Optional[str] = None


class MobilityAidUpdate(BaseModel):
    aid_type: Optional[str] = None
    start_date: Optional[datetime] = None
    notes: Optional[str] = None


class MobilityAidResponse(BaseModel):
    id: int
    aid_type: str
    start_date: datetime
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# 用户档案模式
class UserProfileCreate(BaseModel):
    # 基线指标
    average_daily_steps: int = Field(default=0, ge=0)
    average_sleep_hours: float = Field(default=7.0, ge=0, le=24)
    baseline_mobility_score: float = Field(default=0.5, ge=0.0, le=1.0)
    typical_activity_periods: List[List[int]] = Field(default_factory=list)

    # 护理偏好
    preferred_language: str = "zh-CN"
    ambient_light_enabled: bool = True
    audio_alerts_enabled: bool = True
    voice_confirmation_enabled: bool = True
    emergency_auto_escalation: bool = True
    notification_preferences: Dict[str, bool] = Field(default_factory=lambda: {
        "sms": True,
        "email": True,
        "push": True
    })

    @field_validator('typical_activity_periods')
    @classmethod
    def validate_activity_periods(cls, v):
        for period in v:
            if len(period) != 2:
                raise ValueError('Each activity period must have exactly 2 elements [start_hour, end_hour]')
            if not (0 <= period[0] <= 23 and 0 <= period[1] <= 23):
                raise ValueError('Hours must be between 0 and 23')
            if period[0] >= period[1]:
                raise ValueError('Start hour must be less than end hour')
        return v


class UserProfileUpdate(BaseModel):
    # 基线指标
    average_daily_steps: Optional[int] = Field(None, ge=0)
    average_sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    baseline_mobility_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    typical_activity_periods: Optional[List[List[int]]] = None

    # 护理偏好
    preferred_language: Optional[str] = None
    ambient_light_enabled: Optional[bool] = None
    audio_alerts_enabled: Optional[bool] = None
    voice_confirmation_enabled: Optional[bool] = None
    emergency_auto_escalation: Optional[bool] = None
    notification_preferences: Optional[Dict[str, bool]] = None

    @field_validator('typical_activity_periods')
    @classmethod
    def validate_activity_periods(cls, v):
        if v is not None:
            for period in v:
                if len(period) != 2:
                    raise ValueError('Each activity period must have exactly 2 elements [start_hour, end_hour]')
                if not (0 <= period[0] <= 23 and 0 <= period[1] <= 23):
                    raise ValueError('Hours must be between 0 and 23')
                if period[0] >= period[1]:
                    raise ValueError('Start hour must be less than end hour')
        return v


class UserProfileResponse(BaseModel):
    id: int
    user_id: str

    # 基线指标
    average_daily_steps: int
    average_sleep_hours: float
    baseline_mobility_score: float
    typical_activity_periods: List[List[int]]

    # 护理偏好
    preferred_language: str
    ambient_light_enabled: bool
    audio_alerts_enabled: bool
    voice_confirmation_enabled: bool
    emergency_auto_escalation: bool
    notification_preferences: Dict[str, bool]

    created_at: datetime
    updated_at: Optional[datetime]

    # 关联数据
    medical_conditions: List[MedicalConditionResponse] = []
    mobility_aids: List[MobilityAidResponse] = []
    emergency_contacts: List[EmergencyContactResponse] = []

    model_config = ConfigDict(from_attributes=True)