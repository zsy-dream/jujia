"""
API Pydantic 模型
用于所有新 API 端点的请求/响应模型
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, ConfigDict, Field


# ==================== 风险评估 API 模型 ====================

class FrailtyIndexResponse(BaseModel):
    """衰弱指数响应"""
    user_id: str
    score: float = Field(..., ge=0.0, le=1.0)
    components: Dict[str, float]
    calculation_date: datetime
    confidence_interval: Tuple[float, float]
    risk_level: str  # low, medium, high, emergency


class RiskPredictionResponse(BaseModel):
    """风险预测响应"""
    user_id: str
    prediction_date: datetime
    fall_risk_score: float
    medical_emergency_risk: float
    mobility_decline_risk: float
    confidence_level: float
    contributing_factors: List[str]


class RiskTrendPoint(BaseModel):
    """风险趋势数据点"""
    date: str
    fall_risk: float
    emergency_risk: float
    mobility_risk: float
    frailty_score: float


class RiskTrendsResponse(BaseModel):
    """风险趋势响应"""
    user_id: str
    period_days: int
    trends: List[RiskTrendPoint]
    overall_trend: str  # improving, stable, declining


class RiskReportResponse(BaseModel):
    """30天风险评估报告"""
    user_id: str
    report_date: datetime
    period_start: datetime
    period_end: datetime
    frailty_index: FrailtyIndexResponse
    risk_prediction: RiskPredictionResponse
    trend_analysis: Dict[str, Any]
    confidence_intervals: Dict[str, Tuple[float, float]]
    recommendations: List[str]
    alert_level: str


# ==================== 警报与事件 API 模型 ====================

class IncidentCreateRequest(BaseModel):
    """事件上报请求"""
    user_id: str
    incident_type: str  # fall, medical_emergency, prolonged_inactivity, etc.
    severity: str = "medium"  # low, medium, high, emergency
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    sensor_data: Dict[str, Any] = Field(default_factory=dict)


class IncidentResponse(BaseModel):
    """事件响应"""
    incident_id: str
    user_id: str
    incident_type: str
    timestamp: datetime
    severity: str
    location: Dict[str, Any]
    verification_status: str
    alert_id: Optional[str] = None
    response_plan_id: Optional[str] = None


class AlertResponse(BaseModel):
    """警报响应"""
    alert_id: str
    incident_id: str
    severity: str
    message: str
    response_protocols: List[str]
    status: str
    created_at: datetime


class VerifyIncidentRequest(BaseModel):
    """多模态验证请求"""
    visual_confidence: Optional[float] = None
    audio_data: Optional[Dict[str, Any]] = None
    additional_sensors: Optional[List[Dict[str, Any]]] = None


class VerificationResponse(BaseModel):
    """验证结果响应"""
    incident_id: str
    is_confirmed: bool
    confidence_score: float
    verification_status: str
    false_positive_detected: bool
    consensus_details: Dict[str, Any]


# ==================== 健康数据 API 模型 ====================

class ActivityDataCreate(BaseModel):
    """活动数据上传"""
    user_id: str
    date: datetime
    steps_count: int = Field(..., ge=0)
    active_minutes: int = Field(..., ge=0)
    sleep_hours: float = Field(..., ge=0, le=24)
    mobility_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class ActivityDataResponse(BaseModel):
    """活动数据响应"""
    id: int
    user_id: str
    date: datetime
    steps_count: int
    active_minutes: int
    sleep_hours: float
    mobility_score: Optional[float]

    model_config = ConfigDict(from_attributes=True)


class SkeletonDataCreate(BaseModel):
    """骨骼姿态数据上传"""
    user_id: str
    keypoints: List[Dict[str, Any]]
    confidence_scores: List[float]


class HealthRecommendationsResponse(BaseModel):
    """健康建议响应"""
    user_id: str
    generated_at: datetime
    recommendations: List[Dict[str, str]]
    risk_summary: Dict[str, float]
    activity_summary: Dict[str, Any]


# ==================== 机构管理 API 模型 ====================

class InstitutionDashboardResponse(BaseModel):
    """机构看板响应"""
    institution_id: str
    institution_name: str
    total_residents: int
    active_alerts: int
    risk_distribution: Dict[str, int]
    average_frailty_score: float
    average_response_time_seconds: float
    recent_incidents: List[Dict[str, Any]]
    staff_on_duty: int
    compliance_score: float


class ResidentSummary(BaseModel):
    """住户摘要"""
    user_id: str
    full_name: str
    age: int
    room_number: str
    risk_level: str
    frailty_score: float
    last_activity: Optional[datetime] = None
    active_alerts: int = 0


class ResidentListResponse(BaseModel):
    """住户列表响应"""
    institution_id: str
    total: int
    residents: List[ResidentSummary]


class ComplianceReportResponse(BaseModel):
    """合规报告响应"""
    report_id: str
    institution_id: str
    period_start: datetime
    period_end: datetime
    total_incidents: int
    incidents_by_severity: Dict[str, int]
    average_response_time_seconds: float
    staff_response_rate: float
    false_positive_rate: float
    regulatory_requirements_met: List[str]
    recommendations: List[str]

    model_config = ConfigDict(from_attributes=True)


# ==================== 保险数据 API 模型 ====================

class PopulationReportResponse(BaseModel):
    """人群风险报告响应"""
    report_id: str
    generation_date: datetime
    population_size: int
    age_distribution: Dict[str, int]
    risk_distribution: Dict[str, int]
    average_fall_risk: float
    average_medical_emergency_risk: float
    average_frailty_score: float
    trend_analysis: Dict[str, Any]
    anonymization_method: str
    privacy_guarantees: Dict[str, Any]


class IndividualAssessmentResponse(BaseModel):
    """个人保单评估响应"""
    assessment_id: str
    anonymous_id: str
    assessment_date: datetime
    risk_profile: Dict[str, Any]
    predicted_events: Dict[str, float]
    event_probabilities_30day: Dict[str, float]
    event_probabilities_90day: Dict[str, float]
    actuarial_score: float
    premium_risk_category: str
    recommended_coverage_level: str
    health_trajectory: str


class AuditTrailResponse(BaseModel):
    """审计跟踪响应"""
    entries: List[Dict[str, Any]]
    total: int


# ==================== 视觉AI API 模型 ====================

class PoseAnalysisRequest(BaseModel):
    """姿态分析请求"""
    user_id: str
    keypoints: List[Dict[str, Any]]
    confidence_scores: List[float]
    timestamp: Optional[datetime] = None


class PoseAnalysisResponse(BaseModel):
    """姿态分析响应"""
    user_id: str
    timestamp: datetime
    body_orientation: str  # standing, sitting, lying, walking
    posture_quality: float  # 0-1
    balance_score: float  # 0-1
    gait_metrics: Optional[Dict[str, float]] = None
    anomaly_detected: bool = False
    processing_time_ms: float


class FallDetectionRequest(BaseModel):
    """跌倒检测请求"""
    user_id: str
    skeleton_sequence: List[Dict[str, Any]]  # 时间序列骨骼数据
    audio_data: Optional[Dict[str, Any]] = None


class FallDetectionResponse(BaseModel):
    """跌倒检测响应"""
    user_id: str
    timestamp: datetime
    fall_detected: bool
    fall_confidence: float  # 0-1
    fall_type: Optional[str] = None  # forward, backward, lateral, collapse
    severity_estimate: str  # low, medium, high
    contributing_factors: List[str]
    processing_time_ms: float
    edge_processed: bool = True  # 标识为边缘计算处理


class ActivityRecognitionRequest(BaseModel):
    """活动识别请求"""
    user_id: str
    skeleton_sequence: List[Dict[str, Any]]
    duration_seconds: float = 10.0


class ActivityRecognitionResponse(BaseModel):
    """活动识别响应"""
    user_id: str
    timestamp: datetime
    primary_activity: str  # standing, sitting, walking, lying, exercising
    activity_confidence: float
    activity_duration_seconds: float
    activity_history: List[Dict[str, Any]]
    calories_estimate: float
    processing_time_ms: float


class VisionProcessingStatsResponse(BaseModel):
    """视觉处理统计响应"""
    total_frames_processed: int
    average_processing_time_ms: float
    fall_detections_today: int
    false_positive_rate: float
    edge_processing_ratio: float  # 边缘vs云端处理比例
    privacy_compliance: Dict[str, bool]
    uptime_hours: float


# ==================== 通用响应模型 ====================

class SuccessResponse(BaseModel):
    """通用成功响应"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """通用错误响应"""
    success: bool = False
    error: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
