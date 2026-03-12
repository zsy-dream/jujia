"""
机构仪表板服务
Institution Dashboard Service for B2B management platform

实现需求：
- 需求7.1: 多住户风险热力图和优先警报显示
- 需求7.2: 员工分配跟踪和响应时间监控
- 需求7.3: 监管要求的合规报告生成
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
import uuid

from app.schemas.institution import (
    InstitutionDashboardData,
    RiskHeatmapData,
    ResidentInfo,
    PriorityAlert,
    StaffAssignment,
    ResponseTimeMetrics,
    ComplianceReport,
    ResponseStatus,
    StaffRole
)
from app.schemas.core import SeverityLevel, IncidentType
from app.models.core import (
    InstitutionModel,
    InstitutionResidentModel,
    User,
    RiskPredictionModel,
    IncidentModel,
    AlertModel,
    StaffAssignmentModel,
    StaffMemberModel,
    ComplianceReportModel
)


class InstitutionDashboardService:
    """机构仪表板服务 - B2B管理平台核心服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_data(
        self,
        institution_id: str,
        include_inactive: bool = False
    ) -> InstitutionDashboardData:
        """
        获取机构仪表板综合数据
        
        验证需求7.1: 多住户风险热力图和优先警报显示
        """
        timestamp = datetime.utcnow()
        
        # 获取风险热力图数据
        risk_heatmap = self._generate_risk_heatmap(institution_id, include_inactive)
        
        # 获取优先警报
        priority_alerts = self._get_priority_alerts(institution_id)
        
        # 获取员工指标
        staff_metrics = self._get_staff_metrics(institution_id)
        
        # 生成摘要统计
        summary_stats = self._generate_summary_stats(
            institution_id,
            risk_heatmap,
            priority_alerts,
            staff_metrics
        )
        
        return InstitutionDashboardData(
            institution_id=institution_id,
            timestamp=timestamp,
            risk_heatmap=risk_heatmap,
            priority_alerts=priority_alerts,
            staff_metrics=staff_metrics,
            summary_stats=summary_stats
        )
    
    def _generate_risk_heatmap(
        self,
        institution_id: str,
        include_inactive: bool = False
    ) -> RiskHeatmapData:
        """
        生成多住户风险热力图
        
        验证需求7.1: 显示所有被监控个体的风险热力图
        """
        # 查询机构的所有住户
        query = self.db.query(
            InstitutionResidentModel,
            User,
            RiskPredictionModel
        ).join(
            User, InstitutionResidentModel.user_id == User.id
        ).outerjoin(
            RiskPredictionModel,
            and_(
                RiskPredictionModel.user_id == User.id,
                RiskPredictionModel.prediction_date >= datetime.utcnow() - timedelta(days=1)
            )
        ).filter(
            InstitutionResidentModel.institution_id == institution_id
        )
        
        if not include_inactive:
            query = query.filter(InstitutionResidentModel.is_active == True)
        
        results = query.all()
        
        residents = []
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        total_active_alerts = 0
        
        for resident_model, user, risk_pred in results:
            # 计算当前风险分数
            if risk_pred:
                # 综合风险分数：跌倒风险、医疗紧急风险、移动能力下降风险的加权平均
                current_risk_score = (
                    risk_pred.fall_risk_score * 0.4 +
                    risk_pred.medical_emergency_risk * 0.4 +
                    risk_pred.mobility_decline_risk * 0.2
                )
            else:
                current_risk_score = 0.5  # 默认中等风险
            
            # 获取最近事件日期
            last_incident = self.db.query(IncidentModel).filter(
                IncidentModel.user_id == user.id
            ).order_by(IncidentModel.timestamp.desc()).first()
            
            last_incident_date = last_incident.timestamp if last_incident else None
            
            # 获取活跃警报数量
            active_alerts_count = self.db.query(AlertModel).join(
                IncidentModel
            ).filter(
                IncidentModel.user_id == user.id,
                AlertModel.resolved_at.is_(None)
            ).count()
            
            total_active_alerts += active_alerts_count
            
            # 分类风险级别
            if current_risk_score >= 0.7:
                high_risk_count += 1
            elif current_risk_score >= 0.4:
                medium_risk_count += 1
            else:
                low_risk_count += 1
            
            residents.append(ResidentInfo(
                user_id=user.id,
                full_name=user.full_name,
                room_number=resident_model.room_number,
                age=user.age,
                current_risk_score=current_risk_score,
                last_incident_date=last_incident_date,
                active_alerts_count=active_alerts_count
            ))
        
        return RiskHeatmapData(
            institution_id=institution_id,
            timestamp=datetime.utcnow(),
            residents=residents,
            high_risk_count=high_risk_count,
            medium_risk_count=medium_risk_count,
            low_risk_count=low_risk_count,
            total_active_alerts=total_active_alerts
        )
    
    def _get_priority_alerts(
        self,
        institution_id: str,
        limit: int = 50
    ) -> List[PriorityAlert]:
        """
        获取优先警报列表
        
        验证需求7.1: 优先警报显示
        """
        # 查询未解决的警报，按严重程度和时间排序
        alerts = self.db.query(
            AlertModel,
            IncidentModel,
            User,
            InstitutionResidentModel,
            StaffAssignmentModel
        ).join(
            IncidentModel, AlertModel.incident_id == IncidentModel.id
        ).join(
            User, IncidentModel.user_id == User.id
        ).join(
            InstitutionResidentModel, User.id == InstitutionResidentModel.user_id
        ).outerjoin(
            StaffAssignmentModel,
            and_(
                StaffAssignmentModel.incident_id == IncidentModel.id,
                StaffAssignmentModel.response_status.in_(['pending', 'in_progress'])
            )
        ).filter(
            InstitutionResidentModel.institution_id == institution_id,
            AlertModel.resolved_at.is_(None)
        ).order_by(
            # 按严重程度排序：emergency > high > medium > low
            case(
                (AlertModel.severity == SeverityLevel.EMERGENCY, 1),
                (AlertModel.severity == SeverityLevel.HIGH, 2),
                (AlertModel.severity == SeverityLevel.MEDIUM, 3),
                (AlertModel.severity == SeverityLevel.LOW, 4),
                else_=5
            ),
            AlertModel.sent_at.desc()
        ).limit(limit).all()
        
        priority_alerts = []
        for alert, incident, user, resident, assignment in alerts:
            assigned_staff = None
            response_status = ResponseStatus.PENDING
            
            if assignment:
                staff = self.db.query(StaffMemberModel).filter(
                    StaffMemberModel.id == assignment.staff_id
                ).first()
                if staff:
                    assigned_staff = staff.full_name
                response_status = ResponseStatus(assignment.response_status)
            
            priority_alerts.append(PriorityAlert(
                alert_id=str(alert.id),
                resident_id=user.id,
                resident_name=user.full_name,
                room_number=resident.room_number,
                incident_type=incident.incident_type.value,
                severity=alert.severity,
                timestamp=alert.sent_at,
                assigned_staff=assigned_staff,
                response_status=response_status
            ))
        
        return priority_alerts
    
    def _get_staff_metrics(
        self,
        institution_id: str
    ) -> List[ResponseTimeMetrics]:
        """
        获取员工响应时间指标
        
        验证需求7.2: 员工分配跟踪和响应时间监控
        """
        # 查询机构的所有活跃员工
        staff_members = self.db.query(StaffMemberModel).filter(
            StaffMemberModel.institution_id == institution_id,
            StaffMemberModel.is_active == True
        ).all()
        
        metrics = []
        for staff in staff_members:
            # 获取员工的所有分配
            assignments = self.db.query(StaffAssignmentModel).filter(
                StaffAssignmentModel.staff_id == staff.id
            ).all()
            
            total_assignments = len(assignments)
            completed_assignments = sum(
                1 for a in assignments if a.response_status == 'completed'
            )
            pending_assignments = sum(
                1 for a in assignments if a.response_status == 'pending'
            )
            
            # 计算平均响应时间（仅已完成的任务）
            response_times = []
            for assignment in assignments:
                if assignment.response_started_at and assignment.assigned_at:
                    response_time = (
                        assignment.response_started_at - assignment.assigned_at
                    ).total_seconds()
                    response_times.append(response_time)
            
            avg_response_time = (
                sum(response_times) / len(response_times)
                if response_times else 0.0
            )
            
            # 计算质量分数（基于完成率和响应时间）
            completion_rate = (
                completed_assignments / total_assignments
                if total_assignments > 0 else 0.0
            )
            
            # 响应时间评分：< 5分钟 = 1.0, > 30分钟 = 0.0
            time_score = max(0.0, min(1.0, 1.0 - (avg_response_time / 1800)))
            
            quality_score = (completion_rate * 0.6 + time_score * 0.4)
            
            metrics.append(ResponseTimeMetrics(
                staff_id=staff.id,
                staff_name=staff.full_name,
                total_assignments=total_assignments,
                average_response_time_seconds=avg_response_time,
                completed_assignments=completed_assignments,
                pending_assignments=pending_assignments,
                quality_score=quality_score
            ))
        
        return metrics
    
    def _generate_summary_stats(
        self,
        institution_id: str,
        risk_heatmap: RiskHeatmapData,
        priority_alerts: List[PriorityAlert],
        staff_metrics: List[ResponseTimeMetrics]
    ) -> Dict[str, Any]:
        """生成摘要统计数据"""
        return {
            "total_residents": len(risk_heatmap.residents),
            "high_risk_residents": risk_heatmap.high_risk_count,
            "medium_risk_residents": risk_heatmap.medium_risk_count,
            "low_risk_residents": risk_heatmap.low_risk_count,
            "total_active_alerts": risk_heatmap.total_active_alerts,
            "emergency_alerts": sum(
                1 for a in priority_alerts if a.severity == SeverityLevel.EMERGENCY
            ),
            "total_staff": len(staff_metrics),
            "average_staff_quality": (
                sum(m.quality_score for m in staff_metrics) / len(staff_metrics)
                if staff_metrics else 0.0
            ),
            "pending_assignments": sum(m.pending_assignments for m in staff_metrics)
        }
    
    def assign_staff_to_incident(
        self,
        incident_id: str,
        staff_id: str,
        notes: Optional[str] = None
    ) -> StaffAssignment:
        """
        分配员工到事件
        
        验证需求7.2: 员工分配跟踪
        """
        # 验证事件存在
        incident = self.db.query(IncidentModel).filter(
            IncidentModel.id == incident_id
        ).first()
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        # 验证员工存在
        staff = self.db.query(StaffMemberModel).filter(
            StaffMemberModel.id == staff_id
        ).first()
        if not staff:
            raise ValueError(f"Staff member {staff_id} not found")
        
        # 创建分配记录
        assignment_id = str(uuid.uuid4())
        assignment_model = StaffAssignmentModel(
            id=assignment_id,
            staff_id=staff_id,
            resident_id=incident.user_id,
            incident_id=incident_id,
            assigned_at=datetime.utcnow(),
            response_status='pending',
            notes=notes
        )
        
        self.db.add(assignment_model)
        self.db.commit()
        self.db.refresh(assignment_model)
        
        return StaffAssignment(
            assignment_id=assignment_id,
            staff_id=staff_id,
            staff_name=staff.full_name,
            staff_role=StaffRole(staff.role),
            resident_id=incident.user_id,
            incident_id=incident_id,
            assigned_at=assignment_model.assigned_at,
            response_status=ResponseStatus.PENDING,
            notes=notes
        )
    
    def update_assignment_status(
        self,
        assignment_id: str,
        status: ResponseStatus,
        notes: Optional[str] = None
    ) -> StaffAssignment:
        """
        更新员工分配状态
        
        验证需求7.2: 响应时间监控
        """
        assignment = self.db.query(StaffAssignmentModel).filter(
            StaffAssignmentModel.id == assignment_id
        ).first()
        
        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found")
        
        assignment.response_status = status.value
        
        if status == ResponseStatus.IN_PROGRESS and not assignment.response_started_at:
            assignment.response_started_at = datetime.utcnow()
        
        if status == ResponseStatus.COMPLETED and not assignment.response_completed_at:
            assignment.response_completed_at = datetime.utcnow()
        
        if notes:
            assignment.notes = notes
        
        assignment.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(assignment)
        
        staff = self.db.query(StaffMemberModel).filter(
            StaffMemberModel.id == assignment.staff_id
        ).first()
        
        return StaffAssignment(
            assignment_id=assignment.id,
            staff_id=assignment.staff_id,
            staff_name=staff.full_name if staff else "Unknown",
            staff_role=StaffRole(staff.role) if staff else StaffRole.CAREGIVER,
            resident_id=assignment.resident_id,
            incident_id=assignment.incident_id,
            assigned_at=assignment.assigned_at,
            response_started_at=assignment.response_started_at,
            response_completed_at=assignment.response_completed_at,
            response_status=status,
            notes=assignment.notes
        )
    
    def generate_compliance_report(
        self,
        institution_id: str,
        report_type: str,
        period_start: datetime,
        period_end: datetime
    ) -> ComplianceReport:
        """
        生成合规报告
        
        验证需求7.3: 监管要求的合规报告生成
        """
        # 验证机构存在
        institution = self.db.query(InstitutionModel).filter(
            InstitutionModel.id == institution_id
        ).first()
        if not institution:
            raise ValueError(f"Institution {institution_id} not found")
        
        # 查询期间内的所有事件
        incidents = self.db.query(IncidentModel).join(
            InstitutionResidentModel,
            IncidentModel.user_id == InstitutionResidentModel.user_id
        ).filter(
            InstitutionResidentModel.institution_id == institution_id,
            IncidentModel.timestamp >= period_start,
            IncidentModel.timestamp <= period_end
        ).all()
        
        total_incidents = len(incidents)
        
        # 按严重程度分类事件
        incidents_by_severity = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "emergency": 0
        }
        for incident in incidents:
            incidents_by_severity[incident.severity.value] += 1
        
        # 计算平均响应时间
        assignments = self.db.query(StaffAssignmentModel).join(
            IncidentModel,
            StaffAssignmentModel.incident_id == IncidentModel.id
        ).join(
            InstitutionResidentModel,
            IncidentModel.user_id == InstitutionResidentModel.user_id
        ).filter(
            InstitutionResidentModel.institution_id == institution_id,
            IncidentModel.timestamp >= period_start,
            IncidentModel.timestamp <= period_end,
            StaffAssignmentModel.response_started_at.isnot(None)
        ).all()
        
        response_times = []
        for assignment in assignments:
            if assignment.response_started_at and assignment.assigned_at:
                response_time = (
                    assignment.response_started_at - assignment.assigned_at
                ).total_seconds()
                response_times.append(response_time)
        
        avg_response_time = (
            sum(response_times) / len(response_times)
            if response_times else 0.0
        )
        
        # 计算员工响应率
        total_assignments = self.db.query(StaffAssignmentModel).join(
            IncidentModel,
            StaffAssignmentModel.incident_id == IncidentModel.id
        ).join(
            InstitutionResidentModel,
            IncidentModel.user_id == InstitutionResidentModel.user_id
        ).filter(
            InstitutionResidentModel.institution_id == institution_id,
            IncidentModel.timestamp >= period_start,
            IncidentModel.timestamp <= period_end
        ).count()
        
        responded_assignments = self.db.query(StaffAssignmentModel).join(
            IncidentModel,
            StaffAssignmentModel.incident_id == IncidentModel.id
        ).join(
            InstitutionResidentModel,
            IncidentModel.user_id == InstitutionResidentModel.user_id
        ).filter(
            InstitutionResidentModel.institution_id == institution_id,
            IncidentModel.timestamp >= period_start,
            IncidentModel.timestamp <= period_end,
            StaffAssignmentModel.response_status.in_(['completed', 'in_progress'])
        ).count()
        
        staff_response_rate = (
            responded_assignments / total_assignments
            if total_assignments > 0 else 0.0
        )
        
        # 计算误报率
        false_positives = sum(
            1 for incident in incidents
            if incident.verification_status.value == 'false_positive'
        )
        false_positive_rate = (
            false_positives / total_incidents
            if total_incidents > 0 else 0.0
        )
        
        # 监管要求检查
        regulatory_requirements_met = []
        regulatory_requirements_pending = []
        
        # 示例监管要求
        if avg_response_time < 300:  # 5分钟
            regulatory_requirements_met.append("Emergency response time < 5 minutes")
        else:
            regulatory_requirements_pending.append("Emergency response time < 5 minutes")
        
        if staff_response_rate >= 0.95:
            regulatory_requirements_met.append("Staff response rate >= 95%")
        else:
            regulatory_requirements_pending.append("Staff response rate >= 95%")
        
        if false_positive_rate <= 0.05:
            regulatory_requirements_met.append("False positive rate <= 5%")
        else:
            regulatory_requirements_pending.append("False positive rate <= 5%")
        
        # 生成建议
        recommendations = []
        if avg_response_time >= 300:
            recommendations.append(
                "Improve staff response time through additional training and resource allocation"
            )
        if staff_response_rate < 0.95:
            recommendations.append(
                "Increase staff coverage during peak incident hours"
            )
        if false_positive_rate > 0.05:
            recommendations.append(
                "Review and adjust alert sensitivity to reduce false positives"
            )
        
        # 创建报告记录
        report_id = str(uuid.uuid4())
        report_model = ComplianceReportModel(
            id=report_id,
            institution_id=institution_id,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            generated_at=datetime.utcnow(),
            total_incidents=total_incidents,
            incidents_by_severity=incidents_by_severity,
            average_response_time_seconds=avg_response_time,
            staff_response_rate=staff_response_rate,
            false_positive_rate=false_positive_rate,
            regulatory_requirements_met=regulatory_requirements_met,
            regulatory_requirements_pending=regulatory_requirements_pending,
            recommendations=recommendations
        )
        
        self.db.add(report_model)
        self.db.commit()
        
        return ComplianceReport(
            report_id=report_id,
            institution_id=institution_id,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            generated_at=report_model.generated_at,
            total_incidents=total_incidents,
            incidents_by_severity=incidents_by_severity,
            average_response_time_seconds=avg_response_time,
            staff_response_rate=staff_response_rate,
            false_positive_rate=false_positive_rate,
            regulatory_requirements_met=regulatory_requirements_met,
            regulatory_requirements_pending=regulatory_requirements_pending,
            recommendations=recommendations
        )
