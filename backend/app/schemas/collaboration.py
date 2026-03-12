"""
协作通信与护理计划数据模型
Collaboration and Care Plan Data Models
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.core import SeverityLevel


# ==================== Communication Models ====================

class MessageCreate(BaseModel):
    content: str
    sender_role: str = Field(..., description="Role of the sender: system, family, caregiver, doctor, admin")


class MessageResponse(BaseModel):
    id: str
    thread_id: str
    sender_id: Optional[str]
    sender_name: str
    sender_role: str
    content: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class CommunicationThreadCreate(BaseModel):
    entity_id: str
    entity_type: str = Field(..., description="'incident', 'alert', or 'intervention_task'")
    title: str


class CommunicationThreadResponse(BaseModel):
    id: str
    entity_id: str
    entity_type: str
    title: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    messages: List[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ==================== Care Plan & Intervention Models ====================

class InterventionTaskCreate(BaseModel):
    resident_id: str
    assigned_staff_id: Optional[str] = None
    task_type: str
    description: str
    priority: SeverityLevel = SeverityLevel.MEDIUM
    due_date: datetime


class InterventionTaskUpdate(BaseModel):
    assigned_staff_id: Optional[str] = None
    status: Optional[str] = None  # pending, in_progress, completed, cancelled
    completion_notes: Optional[str] = None


class InterventionTaskResponse(BaseModel):
    id: str
    care_plan_id: Optional[str]
    resident_id: str
    assigned_staff_id: Optional[str]
    task_type: str
    description: str
    priority: SeverityLevel
    due_date: datetime
    status: str
    completion_notes: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class CarePlanCreate(BaseModel):
    resident_id: str
    institution_id: str
    title: str
    description: Optional[str] = None
    target_risk_score_reduction: Optional[float] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    tasks: List[InterventionTaskCreate] = []


class CarePlanResponse(BaseModel):
    id: str
    resident_id: str
    institution_id: str
    created_by_id: Optional[str]
    title: str
    description: Optional[str]
    target_risk_score_reduction: Optional[float]
    start_date: datetime
    end_date: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    tasks: List[InterventionTaskResponse] = []

    model_config = ConfigDict(from_attributes=True)