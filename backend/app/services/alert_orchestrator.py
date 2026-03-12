"""
警报编排和分类系统
Alert Orchestration and Classification System

实现需求4.2和2.1：
- 按严重程度分类警报（低、中、高、紧急）
- 为每个警报级别配备相应的响应协议
- 处理事件并协调响应
- 跟踪响应状态
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

from app.schemas.core import (
    IncidentData, SeverityLevel, IncidentType, VerificationStatus, SkeletonData, UserProfile
)
from app.services.multimodal_verifier import MultiModalVerifier
from app.services.emergency_dispatcher import EmergencyDispatcher


class ResponseProtocol(str, Enum):
    """响应协议类型"""
    MONITOR = "monitor"  # 监控观察
    NOTIFY_FAMILY = "notify_family"  # 通知家属
    VOICE_CONFIRMATION = "voice_confirmation"  # 语音确认
    CONTACT_CARE_CIRCLE = "contact_care_circle"  # 联系关爱圈
    DISPATCH_EMERGENCY = "dispatch_emergency"  # 派遣紧急服务
    ESCALATE = "escalate"  # 升级处理


class ResponseStatus(str, Enum):
    """响应状态"""
    INITIATED = "initiated"  # 已启动
    IN_PROGRESS = "in_progress"  # 进行中
    AWAITING_CONFIRMATION = "awaiting_confirmation"  # 等待确认
    CONFIRMED = "confirmed"  # 已确认
    RESOLVED = "resolved"  # 已解决
    ESCALATED = "escalated"  # 已升级
    CANCELLED = "cancelled"  # 已取消


@dataclass
class ResponsePlan:
    """响应计划"""
    response_id: str
    incident_id: str
    severity: SeverityLevel
    protocols: List[ResponseProtocol]
    initiated_at: datetime
    expected_completion: datetime
    status: ResponseStatus = ResponseStatus.INITIATED
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_action(self, action_type: str, details: Dict[str, Any]) -> None:
        """添加已执行的操作"""
        self.actions_taken.append({
            "action_type": action_type,
            "timestamp": datetime.utcnow(),
            "details": details
        })


@dataclass
class AlertResponse:
    """警报响应"""
    alert_id: str
    incident_id: str
    severity: SeverityLevel
    message: str
    response_plan: ResponsePlan
    created_at: datetime = field(default_factory=datetime.utcnow)


class AlertOrchestrator:
    """
    警报编排器 - 处理事件、分类严重程度并协调响应
    
    核心功能：
    1. 处理传入的事件数据
    2. 根据事件类型和上下文分类严重程度
    3. 为每个严重程度级别生成适当的响应协议
    4. 跟踪响应状态和进度
    """
    
    # 严重程度分类规则
    SEVERITY_RULES = {
        IncidentType.FALL: SeverityLevel.EMERGENCY,
        IncidentType.FALL_DETECTED: SeverityLevel.EMERGENCY,
        IncidentType.MEDICAL_EMERGENCY: SeverityLevel.EMERGENCY,
        IncidentType.PROLONGED_INACTIVITY: SeverityLevel.HIGH,
        IncidentType.ABNORMAL_MOVEMENT: SeverityLevel.MEDIUM,
        IncidentType.MISSED_MEDICATION: SeverityLevel.LOW,
    }
    
    # 响应协议配置 - 每个严重程度级别的标准响应流程
    RESPONSE_PROTOCOLS = {
        SeverityLevel.LOW: [
            ResponseProtocol.MONITOR,
            ResponseProtocol.NOTIFY_FAMILY
        ],
        SeverityLevel.MEDIUM: [
            ResponseProtocol.MONITOR,
            ResponseProtocol.NOTIFY_FAMILY,
            ResponseProtocol.VOICE_CONFIRMATION
        ],
        SeverityLevel.HIGH: [
            ResponseProtocol.VOICE_CONFIRMATION,
            ResponseProtocol.NOTIFY_FAMILY,
            ResponseProtocol.CONTACT_CARE_CIRCLE
        ],
        SeverityLevel.EMERGENCY: [
            ResponseProtocol.VOICE_CONFIRMATION,
            ResponseProtocol.CONTACT_CARE_CIRCLE,
            ResponseProtocol.DISPATCH_EMERGENCY
        ]
    }
    
    # 响应时间限制（秒）
    RESPONSE_TIMEOUTS = {
        SeverityLevel.LOW: 3600,  # 1小时
        SeverityLevel.MEDIUM: 900,  # 15分钟
        SeverityLevel.HIGH: 300,  # 5分钟
        SeverityLevel.EMERGENCY: 5,  # 5秒（需求2.1）
    }
    
    def __init__(self):
        """初始化警报编排器"""
        self._active_responses: Dict[str, ResponsePlan] = {}
        self._multimodal_verifier = MultiModalVerifier()
        self._emergency_dispatcher = EmergencyDispatcher()
    
    def classify_severity(
        self, 
        incident: IncidentData,
        context: Optional[Dict[str, Any]] = None
    ) -> SeverityLevel:
        """
        分类事件严重程度
        
        Args:
            incident: 事件数据
            context: 可选的上下文信息（用户健康状况、历史记录等）
            
        Returns:
            SeverityLevel: 分类的严重程度
        """
        # 基础严重程度（基于事件类型）
        base_severity = self.SEVERITY_RULES.get(
            incident.incident_type, 
            SeverityLevel.MEDIUM
        )
        
        # 如果事件已经有严重程度，使用更严重的那个
        if incident.severity:
            severity_order = [
                SeverityLevel.LOW,
                SeverityLevel.MEDIUM,
                SeverityLevel.HIGH,
                SeverityLevel.EMERGENCY
            ]
            base_idx = severity_order.index(base_severity)
            incident_idx = severity_order.index(incident.severity)
            base_severity = severity_order[max(base_idx, incident_idx)]
        
        # 根据上下文调整严重程度
        if context:
            # 如果用户有高风险医疗状况，提升严重程度
            if context.get("high_risk_conditions"):
                if base_severity == SeverityLevel.MEDIUM:
                    base_severity = SeverityLevel.HIGH
                elif base_severity == SeverityLevel.HIGH:
                    base_severity = SeverityLevel.EMERGENCY
            
            # 如果是重复事件，提升严重程度
            if context.get("recent_similar_incidents", 0) > 2:
                if base_severity == SeverityLevel.LOW:
                    base_severity = SeverityLevel.MEDIUM
                elif base_severity == SeverityLevel.MEDIUM:
                    base_severity = SeverityLevel.HIGH
        
        return base_severity
    
    def get_response_protocols(self, severity: SeverityLevel) -> List[ResponseProtocol]:
        """
        获取指定严重程度的响应协议
        
        Args:
            severity: 严重程度级别
            
        Returns:
            List[ResponseProtocol]: 响应协议列表
        """
        return self.RESPONSE_PROTOCOLS.get(severity, [ResponseProtocol.MONITOR])
    
    def process_incident(
        self, 
        incident: IncidentData,
        context: Optional[Dict[str, Any]] = None,
        visual_data: Optional[SkeletonData] = None,
        audio_data: Optional[Dict[str, Any]] = None
    ) -> AlertResponse:
        """
        处理事件并生成警报响应
        
        Args:
            incident: 事件数据
            context: 可选的上下文信息
            visual_data: 可选的视觉骨骼数据（用于多模态验证）
            audio_data: 可选的音频数据（用于多模态验证）
            
        Returns:
            AlertResponse: 警报响应对象
        """
        # 如果提供了多模态数据，进行验证（需求4.1, 4.4）
        if visual_data or audio_data:
            verification_result = self._multimodal_verifier.verify_incident(
                visual_data=visual_data,
                audio_data=audio_data
            )
            
            # 更新事件的验证状态
            incident.verification_status = verification_result.verification_status
            
            # 如果检测到误报，取消警报（需求4.3）
            if verification_result.false_positive_detected:
                # 记录误报事件用于模型改进
                return self._handle_false_positive(incident, verification_result)
        
        # 分类严重程度
        severity = self.classify_severity(incident, context)
        
        # 获取响应协议
        protocols = self.get_response_protocols(severity)
        
        # 计算预期完成时间
        timeout_seconds = self.RESPONSE_TIMEOUTS[severity]
        expected_completion = datetime.utcnow() + timedelta(seconds=timeout_seconds)
        
        # 创建响应计划
        response_id = str(uuid.uuid4())
        response_plan = ResponsePlan(
            response_id=response_id,
            incident_id=incident.incident_id,
            severity=severity,
            protocols=protocols,
            initiated_at=datetime.utcnow(),
            expected_completion=expected_completion,
            status=ResponseStatus.INITIATED
        )
        
        # 存储活跃响应
        self._active_responses[response_id] = response_plan
        
        # 生成警报消息
        message = self._generate_alert_message(incident, severity)
        
        # 创建警报响应
        alert_response = AlertResponse(
            alert_id=str(uuid.uuid4()),
            incident_id=incident.incident_id,
            severity=severity,
            message=message,
            response_plan=response_plan
        )
        
        return alert_response
    
    def coordinate_response(self, alert: AlertResponse) -> ResponsePlan:
        """
        协调警报响应执行
        
        Args:
            alert: 警报响应对象
            
        Returns:
            ResponsePlan: 更新后的响应计划
        """
        response_plan = alert.response_plan
        
        # 更新状态为进行中
        response_plan.status = ResponseStatus.IN_PROGRESS
        
        # 根据协议执行相应操作
        for protocol in response_plan.protocols:
            self._execute_protocol(protocol, response_plan, alert)
        
        return response_plan
    
    def track_response_status(self, response_id: str) -> Optional[ResponsePlan]:
        """
        跟踪响应状态
        
        Args:
            response_id: 响应计划ID
            
        Returns:
            Optional[ResponsePlan]: 响应计划对象，如果不存在则返回None
        """
        return self._active_responses.get(response_id)
    
    def update_response_status(
        self, 
        response_id: str, 
        status: ResponseStatus,
        action_details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新响应状态
        
        Args:
            response_id: 响应计划ID
            status: 新的响应状态
            action_details: 可选的操作详情
            
        Returns:
            bool: 更新是否成功
        """
        response_plan = self._active_responses.get(response_id)
        if not response_plan:
            return False
        
        response_plan.status = status
        
        if action_details:
            response_plan.add_action(
                action_type=f"status_update_{status.value}",
                details=action_details
            )
        
        # 如果响应已解决或取消，从活跃响应中移除
        if status in [ResponseStatus.RESOLVED, ResponseStatus.CANCELLED]:
            self._active_responses.pop(response_id, None)
        
        return True
    
    def _generate_alert_message(
        self, 
        incident: IncidentData, 
        severity: SeverityLevel
    ) -> str:
        """生成警报消息"""
        severity_labels = {
            SeverityLevel.LOW: "低级",
            SeverityLevel.MEDIUM: "中级",
            SeverityLevel.HIGH: "高级",
            SeverityLevel.EMERGENCY: "紧急"
        }
        
        incident_labels = {
            IncidentType.FALL: "跌倒",
            IncidentType.FALL_DETECTED: "跌倒检测",
            IncidentType.MEDICAL_EMERGENCY: "医疗紧急情况",
            IncidentType.PROLONGED_INACTIVITY: "长时间不活动",
            IncidentType.ABNORMAL_MOVEMENT: "异常移动",
            IncidentType.MISSED_MEDICATION: "错过用药"
        }
        
        severity_label = severity_labels.get(severity, "未知")
        incident_label = incident_labels.get(incident.incident_type, "未知事件")
        
        timestamp_str = incident.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        message = (
            f"【{severity_label}警报】检测到{incident_label}\n"
            f"时间：{timestamp_str}\n"
            f"用户：{incident.user_id}\n"
            f"位置：{incident.location.address or '未知'}"
        )
        
        return message
    
    def _execute_protocol(
        self, 
        protocol: ResponseProtocol, 
        response_plan: ResponsePlan,
        alert: AlertResponse
    ) -> None:
        """
        执行响应协议
        
        注意：这是一个框架方法，实际实现需要集成具体的通知和调度服务
        """
        action_details = {
            "protocol": protocol.value,
            "alert_id": alert.alert_id,
            "severity": alert.severity.value
        }
        
        if protocol == ResponseProtocol.MONITOR:
            # 启动监控
            action_details["action"] = "monitoring_initiated"
            response_plan.add_action("execute_protocol", action_details)
        
        elif protocol == ResponseProtocol.NOTIFY_FAMILY:
            # 通知家属
            action_details["action"] = "family_notified"
            response_plan.add_action("execute_protocol", action_details)
        
        elif protocol == ResponseProtocol.VOICE_CONFIRMATION:
            # 启动语音确认
            action_details["action"] = "voice_confirmation_initiated"
            action_details["timeout_seconds"] = 30  # 需求2.2：30秒超时
            response_plan.add_action("execute_protocol", action_details)
            response_plan.status = ResponseStatus.AWAITING_CONFIRMATION
        
        elif protocol == ResponseProtocol.CONTACT_CARE_CIRCLE:
            # 联系关爱圈
            action_details["action"] = "care_circle_contacted"
            response_plan.add_action("execute_protocol", action_details)
        
        elif protocol == ResponseProtocol.DISPATCH_EMERGENCY:
            # 派遣紧急服务
            action_details["action"] = "emergency_services_dispatched"
            action_details["location"] = {
                "latitude": alert.response_plan.actions_taken[0].get("details", {}).get("latitude"),
                "longitude": alert.response_plan.actions_taken[0].get("details", {}).get("longitude")
            }
            response_plan.add_action("execute_protocol", action_details)
        
        elif protocol == ResponseProtocol.ESCALATE:
            # 升级处理
            action_details["action"] = "response_escalated"
            response_plan.add_action("execute_protocol", action_details)
            response_plan.status = ResponseStatus.ESCALATED
    
    def get_active_responses(self) -> List[ResponsePlan]:
        """获取所有活跃的响应计划"""
        return list(self._active_responses.values())
    
    def get_response_by_incident(self, incident_id: str) -> Optional[ResponsePlan]:
        """根据事件ID获取响应计划"""
        for response in self._active_responses.values():
            if response.incident_id == incident_id:
                return response
        return None
    
    def _handle_false_positive(
        self, 
        incident: IncidentData,
        verification_result
    ) -> AlertResponse:
        """
        处理误报事件（需求4.3）
        
        Args:
            incident: 事件数据
            verification_result: 验证结果
            
        Returns:
            AlertResponse: 取消的警报响应
        """
        # 创建取消的响应计划
        response_id = str(uuid.uuid4())
        response_plan = ResponsePlan(
            response_id=response_id,
            incident_id=incident.incident_id,
            severity=SeverityLevel.LOW,
            protocols=[ResponseProtocol.MONITOR],
            initiated_at=datetime.utcnow(),
            expected_completion=datetime.utcnow(),
            status=ResponseStatus.CANCELLED
        )
        
        # 记录误报检测
        response_plan.add_action(
            action_type="false_positive_detected",
            details={
                "verification_result": {
                    "confidence_score": verification_result.confidence_score,
                    "sensor_count": len(verification_result.sensor_inputs),
                    "consensus_details": verification_result.consensus_details
                },
                "learning_data": verification_result.learning_data
            }
        )
        
        # 生成取消消息
        message = (
            f"【警报已取消】检测到误报\n"
            f"事件ID：{incident.incident_id}\n"
            f"用户：{incident.user_id}\n"
            f"置信度：{verification_result.confidence_score:.2f}\n"
            f"已记录用于模型改进"
        )
        
        # 创建警报响应
        alert_response = AlertResponse(
            alert_id=str(uuid.uuid4()),
            incident_id=incident.incident_id,
            severity=SeverityLevel.LOW,
            message=message,
            response_plan=response_plan
        )
        
        return alert_response
    
    def get_multimodal_verifier(self) -> MultiModalVerifier:
        """获取多模态验证器实例"""
        return self._multimodal_verifier

    def get_emergency_dispatcher(self) -> EmergencyDispatcher:
        """获取紧急调度器实例"""
        return self._emergency_dispatcher
    
    def execute_emergency_workflow(
        self,
        incident: IncidentData,
        user_profile: UserProfile,
        auto_escalate: bool = True
    ) -> Dict[str, Any]:
        """
        执行完整的紧急响应工作流（需求2.2, 2.3, 2.4, 2.5）
        
        这个方法整合了AlertOrchestrator和EmergencyDispatcher，
        提供了一个完整的紧急响应流程。
        
        Args:
            incident: 事件数据
            user_profile: 用户档案
            auto_escalate: 是否在超时后自动升级（默认True）
            
        Returns:
            Dict[str, Any]: 工作流执行结果
        """
        workflow_result = {
            "incident_id": incident.incident_id,
            "user_id": incident.user_id,
            "steps_completed": [],
            "dispatch_id": None,
            "voice_confirmation_sent": False,
            "care_circle_contacted": False,
            "emergency_dispatched": False
        }
        
        # 步骤1: 处理事件并创建警报
        alert_response = self.process_incident(incident)
        workflow_result["alert_id"] = alert_response.alert_id
        workflow_result["severity"] = alert_response.severity.value
        workflow_result["steps_completed"].append("alert_created")
        
        # 步骤2: 启动紧急调度
        dispatch_result = self._emergency_dispatcher.initiate_emergency_response(
            incident,
            user_profile
        )
        workflow_result["dispatch_id"] = dispatch_result.dispatch_id
        workflow_result["steps_completed"].append("dispatch_initiated")
        
        # 步骤3: 如果是紧急或高级别事件，发送语音确认
        if alert_response.severity in [SeverityLevel.EMERGENCY, SeverityLevel.HIGH]:
            voice_confirmation = self._emergency_dispatcher.send_voice_confirmation(
                dispatch_result.dispatch_id,
                user_profile.user_id,
                incident
            )
            workflow_result["voice_confirmation_sent"] = True
            workflow_result["voice_confirmation_id"] = voice_confirmation.request_id
            workflow_result["voice_timeout_seconds"] = voice_confirmation.timeout_seconds
            workflow_result["steps_completed"].append("voice_confirmation_sent")
        
        # 步骤4: 如果配置了自动升级，准备关爱圈联系
        if auto_escalate and user_profile.care_preferences.emergency_auto_escalation:
            # 注意：在实际应用中，这里应该等待语音确认超时
            # 这里我们只是准备好联系信息
            workflow_result["auto_escalate_enabled"] = True
            workflow_result["emergency_contacts_count"] = len(user_profile.emergency_contacts)
            workflow_result["steps_completed"].append("auto_escalate_prepared")
        
        # 步骤5: 创建紧急信息包（需求2.4）
        emergency_package = self._emergency_dispatcher.create_emergency_package(
            incident,
            user_profile
        )
        workflow_result["emergency_package_id"] = emergency_package.package_id
        workflow_result["steps_completed"].append("emergency_package_created")
        
        # 步骤6: 协调响应执行
        response_plan = self.coordinate_response(alert_response)
        workflow_result["response_plan_id"] = response_plan.response_id
        workflow_result["response_status"] = response_plan.status.value
        workflow_result["steps_completed"].append("response_coordinated")
        
        return workflow_result
    
    def handle_voice_confirmation_timeout(
        self,
        dispatch_id: str,
        user_profile: UserProfile,
        incident: IncidentData
    ) -> Dict[str, Any]:
        """
        处理语音确认超时（需求2.3）
        
        当用户在30秒内未响应语音确认时，自动联系关爱圈
        
        Args:
            dispatch_id: 调度ID
            user_profile: 用户档案
            incident: 事件数据
            
        Returns:
            Dict[str, Any]: 升级结果
        """
        escalation_result = {
            "dispatch_id": dispatch_id,
            "escalation_triggered": False,
            "care_circle_contacted": False,
            "emergency_dispatched": False
        }
        
        # 联系关爱圈
        contact_results = self._emergency_dispatcher.contact_care_circle(
            dispatch_id,
            user_profile.emergency_contacts,
            incident
        )
        
        escalation_result["escalation_triggered"] = True
        escalation_result["care_circle_contacted"] = True
        escalation_result["contacts_attempted"] = len(contact_results)
        escalation_result["successful_contacts"] = sum(1 for r in contact_results if r.success)
        
        # 如果是紧急事件，同时派遣紧急服务
        if incident.severity == SeverityLevel.EMERGENCY:
            emergency_package = self._emergency_dispatcher.create_emergency_package(
                incident,
                user_profile
            )
            
            emergency_contact = self._emergency_dispatcher.dispatch_emergency_services(
                dispatch_id,
                emergency_package
            )
            
            escalation_result["emergency_dispatched"] = True
            escalation_result["emergency_service_contacted"] = emergency_contact.success
        
        return escalation_result
