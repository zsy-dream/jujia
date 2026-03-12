"""
机构管理相关数据模型
Institution management data models for B2B dashboard
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum

from app.schemas.core import SeverityLevel


class StaffRole(str, Enum):
    """员工角色"""
    CAREGIVER = "caregiver"
    NURSE = "nurse"
    DOCTOR = "doctor"
    ADMINISTRATOR = "administrator"
    COORDINATOR = "coordinator"


class ResponseStatus(str, Enum):
    """响应状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class InstitutionProfile:
    """机构档案"""
    institution_id: str
    name: str
    institution_type: str  # "nursing_home", "assisted_living", "hospital"
    address: str
    contact_email: str
    contact_phone: str
    license_number: str
    capacity: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.institution_id:
            raise ValueError("institution_id cannot be empty")
        if self.capacity < 1:
            raise ValueError("Capacity must be at least 1")


@dataclass
class ResidentInfo:
    """住户信息（用于机构仪表板）"""
    user_id: str
    full_name: str
    room_number: str
    age: int
    current_risk_score: float
    last_incident_date: Optional[datetime] = None
    active_alerts_count: int = 0
    
    def __post_init__(self):
        if not 0.0 <= self.current_risk_score <= 1.0:
            raise ValueError(f"Risk score must be between 0.0 and 1.0, got {self.current_risk_score}")


@dataclass
class RiskHeatmapData:
    """风险热力图数据"""
    institution_id: str
    timestamp: datetime
    residents: List[ResidentInfo]
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    total_active_alerts: int
    
    def __post_init__(self):
        if not self.institution_id:
            raise ValueError("institution_id cannot be empty")


@dataclass
class StaffAssignment:
    """员工分配记录"""
    assignment_id: str
    staff_id: str
    staff_name: str
    staff_role: StaffRole
    resident_id: str
    incident_id: Optional[str] = None
    assigned_at: datetime = field(default_factory=datetime.utcnow)
    response_started_at: Optional[datetime] = None
    response_completed_at: Optional[datetime] = None
    response_status: ResponseStatus = ResponseStatus.PENDING
    notes: Optional[str] = None
    
    def __post_init__(self):
        if not self.assignment_id:
            raise ValueError("assignment_id cannot be empty")
        if not self.staff_id:
            raise ValueError("staff_id cannot be empty")
        if not self.resident_id:
            raise ValueError("resident_id cannot be empty")


@dataclass
class ResponseTimeMetrics:
    """响应时间指标"""
    staff_id: str
    staff_name: str
    total_assignments: int
    average_response_time_seconds: float
    completed_assignments: int
    pending_assignments: int
    quality_score: float  # 0.0 to 1.0
    
    def __post_init__(self):
        if not 0.0 <= self.quality_score <= 1.0:
            raise ValueError(f"Quality score must be between 0.0 and 1.0, got {self.quality_score}")


@dataclass
class ComplianceReport:
    """合规报告"""
    report_id: str
    institution_id: str
    report_type: str  # "monthly", "quarterly", "annual", "incident"
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    
    # 合规指标
    total_incidents: int
    incidents_by_severity: Dict[str, int]
    average_response_time_seconds: float
    staff_response_rate: float  # 0.0 to 1.0
    false_positive_rate: float  # 0.0 to 1.0
    
    # 监管要求
    regulatory_requirements_met: List[str]
    regulatory_requirements_pending: List[str]
    
    # 建议
    recommendations: List[str]
    
    def __post_init__(self):
        if not self.report_id:
            raise ValueError("report_id cannot be empty")
        if self.period_start > self.period_end:
            raise ValueError("period_start must be before period_end")
        if not 0.0 <= self.staff_response_rate <= 1.0:
            raise ValueError("staff_response_rate must be between 0.0 and 1.0")
        if not 0.0 <= self.false_positive_rate <= 1.0:
            raise ValueError("false_positive_rate must be between 0.0 and 1.0")


@dataclass
class PriorityAlert:
    """优先警报（用于机构仪表板）"""
    alert_id: str
    resident_id: str
    resident_name: str
    room_number: str
    incident_type: str
    severity: SeverityLevel
    timestamp: datetime
    assigned_staff: Optional[str] = None
    response_status: ResponseStatus = ResponseStatus.PENDING
    
    def __post_init__(self):
        if not self.alert_id:
            raise ValueError("alert_id cannot be empty")


@dataclass
class InstitutionDashboardData:
    """机构仪表板综合数据"""
    institution_id: str
    timestamp: datetime
    risk_heatmap: RiskHeatmapData
    priority_alerts: List[PriorityAlert]
    staff_metrics: List[ResponseTimeMetrics]
    summary_stats: Dict[str, Any]
    
    def __post_init__(self):
        if not self.institution_id:
            raise ValueError("institution_id cannot be empty")
