"""
SQLAlchemy ORM 模型定义
Database ORM models for Silver Age Actuary system
"""
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    JSON, ForeignKey, Enum as SQLEnum, Text, Table
)
from sqlalchemy.orm import relationship as db_relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.base import Base
from app.schemas.core import (
    JointType, IncidentType, SeverityLevel, VerificationStatus
)


class User(Base):
    """用户表 - 核心用户信息"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    profile = db_relationship("UserProfileModel", back_populates="user", uselist=False)
    skeleton_data = db_relationship("SkeletonDataModel", back_populates="user")
    incidents = db_relationship("IncidentModel", back_populates="user")
    frailty_assessments = db_relationship("FrailtyAssessmentModel", back_populates="user")
    risk_predictions = db_relationship("RiskPredictionModel", back_populates="user")


class UserProfileModel(Base):
    """用户档案表 - 详细健康和偏好数据"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    
    # 基线指标
    average_daily_steps = Column(Integer, default=0)
    average_sleep_hours = Column(Float, default=7.0)
    baseline_mobility_score = Column(Float, default=0.5)
    typical_activity_periods = Column(JSON, default=list)  # List of [start_hour, end_hour]
    
    # 护理偏好
    preferred_language = Column(String, default="zh-CN")
    ambient_light_enabled = Column(Boolean, default=True)
    audio_alerts_enabled = Column(Boolean, default=True)
    voice_confirmation_enabled = Column(Boolean, default=True)
    emergency_auto_escalation = Column(Boolean, default=True)
    notification_preferences = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = db_relationship("User", back_populates="profile")
    medical_conditions = db_relationship("MedicalConditionModel", back_populates="profile")
    mobility_aids = db_relationship("MobilityAidModel", back_populates="profile")
    emergency_contacts = db_relationship("EmergencyContactModel", back_populates="profile")


class MedicalConditionModel(Base):
    """医疗状况表"""
    __tablename__ = "medical_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    condition_name = Column(String, nullable=False)
    diagnosed_date = Column(DateTime(timezone=True), nullable=False)
    severity = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    profile = db_relationship("UserProfileModel", back_populates="medical_conditions")


class MobilityAidModel(Base):
    """移动辅助设备表"""
    __tablename__ = "mobility_aids"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    aid_type = Column(String, nullable=False)  # walker, cane, wheelchair, etc.
    start_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    profile = db_relationship("UserProfileModel", back_populates="mobility_aids")


class EmergencyContactModel(Base):
    """紧急联系人表"""
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    name = Column(String, nullable=False)
    relationship = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    priority = Column(Integer, default=1)  # 1 = highest priority
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    profile = db_relationship("UserProfileModel", back_populates="emergency_contacts")


class SkeletonDataModel(Base):
    """骨骼数据表 - 匿名化姿态和运动数据"""
    __tablename__ = "skeleton_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    keypoints = Column(JSON, nullable=False)  # List of keypoint dicts
    confidence_scores = Column(JSON, nullable=False)  # List of floats
    anonymized = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = db_relationship("User", back_populates="skeleton_data")


class FrailtyAssessmentModel(Base):
    """衰弱评估表 - 历史衰弱指数计算"""
    __tablename__ = "frailty_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    score = Column(Float, nullable=False)  # 0.0 to 1.0
    components = Column(JSON, nullable=False)  # Dict of component scores
    calculation_date = Column(DateTime(timezone=True), nullable=False, index=True)
    confidence_interval_lower = Column(Float, nullable=False)
    confidence_interval_upper = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = db_relationship("User", back_populates="frailty_assessments")


class RiskPredictionModel(Base):
    """风险预测表 - 预测模型输出和置信度分数"""
    __tablename__ = "risk_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    prediction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    fall_risk_score = Column(Float, nullable=False)
    medical_emergency_risk = Column(Float, nullable=False)
    mobility_decline_risk = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False)
    contributing_factors = Column(JSON, nullable=False)  # List of strings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = db_relationship("User", back_populates="risk_predictions")


class IncidentModel(Base):
    """事件表 - 紧急和健康事件记录"""
    __tablename__ = "incidents"
    
    id = Column(String, primary_key=True, index=True)  # incident_id
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    incident_type = Column(SQLEnum(IncidentType), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    severity = Column(SQLEnum(SeverityLevel), nullable=False)
    
    # 位置信息
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    
    sensor_data = Column(JSON, nullable=False)
    verification_status = Column(
        SQLEnum(VerificationStatus), 
        default=VerificationStatus.PENDING,
        nullable=False
    )
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = db_relationship("User", back_populates="incidents")
    alerts = db_relationship("AlertModel", back_populates="incident")


class AlertModel(Base):
    """警报表 - 警报生成和响应跟踪"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False, index=True)
    alert_type = Column(String, nullable=False)
    severity = Column(SQLEnum(SeverityLevel), nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # 关系
    incident = db_relationship("IncidentModel", back_populates="alerts")


class ActivityLogModel(Base):
    """活动日志表 - 日常活动模式和指标"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    steps_count = Column(Integer, default=0)
    active_minutes = Column(Integer, default=0)
    sleep_hours = Column(Float, default=0.0)
    mobility_score = Column(Float, nullable=True)
    activity_summary = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLogModel(Base):
    """审计日志表 - 合规和安全审计跟踪"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)  # Nullable for system events
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# ==================== B2B Institution Models ====================

class InstitutionModel(Base):
    """机构表 - B2B客户机构信息"""
    __tablename__ = "institutions"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    institution_type = Column(String, nullable=False)  # nursing_home, assisted_living, hospital
    address = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    contact_phone = Column(String, nullable=False)
    license_number = Column(String, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    residents = db_relationship("InstitutionResidentModel", back_populates="institution")
    staff_members = db_relationship("StaffMemberModel", back_populates="institution")
    compliance_reports = db_relationship("ComplianceReportModel", back_populates="institution")


class InstitutionResidentModel(Base):
    """机构住户关联表"""
    __tablename__ = "institution_residents"
    
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(String, ForeignKey("institutions.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    room_number = Column(String, nullable=False)
    admission_date = Column(DateTime(timezone=True), nullable=False)
    discharge_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    institution = db_relationship("InstitutionModel", back_populates="residents")
    user = db_relationship("User")


class StaffMemberModel(Base):
    """员工表"""
    __tablename__ = "staff_members"
    
    id = Column(String, primary_key=True, index=True)
    institution_id = Column(String, ForeignKey("institutions.id"), nullable=False, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    role = Column(String, nullable=False)  # caregiver, nurse, doctor, administrator
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    institution = db_relationship("InstitutionModel", back_populates="staff_members")
    assignments = db_relationship("StaffAssignmentModel", back_populates="staff_member")


class StaffAssignmentModel(Base):
    """员工分配表 - 跟踪员工响应和任务"""
    __tablename__ = "staff_assignments"
    
    id = Column(String, primary_key=True, index=True)
    staff_id = Column(String, ForeignKey("staff_members.id"), nullable=False, index=True)
    resident_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=True, index=True)
    
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    response_started_at = Column(DateTime(timezone=True), nullable=True)
    response_completed_at = Column(DateTime(timezone=True), nullable=True)
    response_status = Column(String, default="pending", nullable=False)  # pending, in_progress, completed, cancelled
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    staff_member = db_relationship("StaffMemberModel", back_populates="assignments")
    resident = db_relationship("User")
    incident = db_relationship("IncidentModel")


class ComplianceReportModel(Base):
    """合规报告表"""
    __tablename__ = "compliance_reports"
    
    id = Column(String, primary_key=True, index=True)
    institution_id = Column(String, ForeignKey("institutions.id"), nullable=False, index=True)
    report_type = Column(String, nullable=False)  # monthly, quarterly, annual, incident
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 合规指标
    total_incidents = Column(Integer, default=0)
    incidents_by_severity = Column(JSON, default=dict)
    average_response_time_seconds = Column(Float, default=0.0)
    staff_response_rate = Column(Float, default=0.0)
    false_positive_rate = Column(Float, default=0.0)
    
    # 监管要求
    regulatory_requirements_met = Column(JSON, default=list)
    regulatory_requirements_pending = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    institution = db_relationship("InstitutionModel", back_populates="compliance_reports")


# ==================== Collaboration & Communication Models ====================

class CommunicationThreadModel(Base):
    """沟通进程表 - 记录警报或护理干预的相关沟通反馈"""
    __tablename__ = "communication_threads"
    
    id = Column(String, primary_key=True, index=True)
    entity_id = Column(String, nullable=False, index=True) # 可能是 incident_id, alert_id 或 task_id
    entity_type = Column(String, nullable=False) # 'incident', 'alert', 'intervention_task'
    title = Column(String, nullable=False)
    status = Column(String, default="open") # open, closed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    messages = db_relationship("MessageModel", back_populates="thread")


class MessageModel(Base):
    """消息表 - 保存在进程中的具体留言记录"""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, index=True)
    thread_id = Column(String, ForeignKey("communication_threads.id"), nullable=False, index=True)
    sender_id = Column(String, ForeignKey("users.id"), nullable=True) # 发送人（可以是家属、员工，若为系统则是null）
    sender_name = Column(String, nullable=False)
    sender_role = Column(String, nullable=False) # system, family, caregiver, doctor, admin
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 关系
    thread = db_relationship("CommunicationThreadModel", back_populates="messages")


# ==================== Care Plan & Intervention Models ====================

class CarePlanModel(Base):
    """护理计划表 - 针对高风险用户的自动化照护排期"""
    __tablename__ = "care_plans"
    
    id = Column(String, primary_key=True, index=True)
    resident_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    institution_id = Column(String, ForeignKey("institutions.id"), nullable=False, index=True)
    created_by_id = Column(String, nullable=True) # 创建人ID，系统生成的为null
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_risk_score_reduction = Column(Float, nullable=True) # 设定的降低风险目标
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="active") # active, completed, suspended
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InterventionTaskModel(Base):
    """干预任务表 - 基于护理计划或突发高风险生成的具体执行任务"""
    __tablename__ = "intervention_tasks"
    
    id = Column(String, primary_key=True, index=True)
    care_plan_id = Column(String, ForeignKey("care_plans.id"), nullable=True, index=True)
    resident_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    assigned_staff_id = Column(String, ForeignKey("staff_members.id"), nullable=True, index=True)
    
    task_type = Column(String, nullable=False) # 比如 'medication_review', 'mobility_exercise', 'fall_hazard_check'
    description = Column(Text, nullable=False)
    priority = Column(SQLEnum(SeverityLevel), default=SeverityLevel.MEDIUM)
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String, default="pending") # pending, in_progress, completed, cancelled
    completion_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
