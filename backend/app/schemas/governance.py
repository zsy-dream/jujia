"""
Data Governance and Compliance Schemas

Defines data structures for consent management, data retention policies,
breach detection, and audit logging.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class ConsentType(str, Enum):
    """Types of data consent"""
    MONITORING = "monitoring"
    HEALTH_DATA = "health_data"
    INSURANCE_SHARING = "insurance_sharing"
    RESEARCH = "research"
    MARKETING = "marketing"


class ConsentStatus(str, Enum):
    """Status of consent"""
    GRANTED = "granted"
    REVOKED = "revoked"
    EXPIRED = "expired"


class DataCategory(str, Enum):
    """Categories of data for retention policies"""
    SKELETON_DATA = "skeleton_data"
    HEALTH_METRICS = "health_metrics"
    INCIDENT_DATA = "incident_data"
    AUDIT_LOGS = "audit_logs"
    USER_PROFILE = "user_profile"


class BreachSeverity(str, Enum):
    """Severity levels for data breaches"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditAction(str, Enum):
    """Types of auditable actions"""
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    CONSENT_CHANGE = "consent_change"
    EXPORT = "export"
    SHARE = "share"


class ConsentRecord(BaseModel):
    """Data consent record"""
    consent_id: str
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus
    granted_at: datetime
    revoked_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    purpose_description: str
    data_usage_details: str
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "consent_id": "consent_123",
            "user_id": "user_456",
            "consent_type": "monitoring",
            "status": "granted",
            "granted_at": "2024-01-01T00:00:00Z",
            "purpose_description": "24/7 health monitoring for fall detection",
            "data_usage_details": "Video processing for skeleton extraction, no raw video storage"
        }
    })


class RetentionPolicy(BaseModel):
    """Data retention policy"""
    policy_id: str
    data_category: DataCategory
    retention_days: int
    auto_delete: bool = True
    description: str
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "policy_id": "policy_001",
            "data_category": "skeleton_data",
            "retention_days": 90,
            "auto_delete": True,
            "description": "Skeleton data retained for 90 days for trend analysis"
        }
    })


class BreachIncident(BaseModel):
    """Data breach incident record"""
    incident_id: str
    detected_at: datetime
    severity: BreachSeverity
    affected_users: List[str]
    data_categories_affected: List[DataCategory]
    description: str
    containment_actions: List[str]
    notification_sent: bool = False
    notification_sent_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "incident_id": "breach_001",
            "detected_at": "2024-01-01T12:00:00Z",
            "severity": "high",
            "affected_users": ["user_123", "user_456"],
            "data_categories_affected": ["health_metrics"],
            "description": "Unauthorized access attempt detected",
            "containment_actions": ["Account locked", "Password reset required"],
            "notification_sent": False
        }
    })


class AuditLogEntry(BaseModel):
    """Audit log entry"""
    log_id: str
    timestamp: datetime
    user_id: str
    action: AuditAction
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    success: bool = True
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "log_id": "log_001",
            "timestamp": "2024-01-01T12:00:00Z",
            "user_id": "user_123",
            "action": "data_access",
            "resource_type": "health_metrics",
            "resource_id": "metric_456",
            "details": {"operation": "read", "fields": ["frailty_score"]},
            "ip_address": "192.168.1.1",
            "success": True
        }
    })


class ConsentRequest(BaseModel):
    """Request to grant consent"""
    user_id: str
    consent_type: ConsentType
    purpose_description: str
    data_usage_details: str
    expires_in_days: Optional[int] = None


class ConsentRevocation(BaseModel):
    """Request to revoke consent"""
    consent_id: str
    user_id: str
    reason: Optional[str] = None
