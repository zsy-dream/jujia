"""
紧急响应调度系统
Emergency Response Dispatcher System

实现需求2.2, 2.3, 2.4, 2.5：
- 30秒超时的AI语音确认
- 联系关爱圈和紧急服务
- 紧急信息打包（位置、病史、事件详情）
- 持续监控和状态更新
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

from app.schemas.core import (
    IncidentData, Location, UserProfile, EmergencyContact
)


class DispatchStatus(str, Enum):
    """调度状态"""
    INITIATED = "initiated"  # 已启动
    VOICE_CONFIRMATION_SENT = "voice_confirmation_sent"  # 语音确认已发送
    USER_RESPONDED = "user_responded"  # 用户已响应
    NO_RESPONSE = "no_response"  # 无响应
    CARE_CIRCLE_CONTACTED = "care_circle_contacted"  # 关爱圈已联系
    EMERGENCY_DISPATCHED = "emergency_dispatched"  # 紧急服务已派遣
    MONITORING = "monitoring"  # 持续监控中
    RESOLVED = "resolved"  # 已解决
    CANCELLED = "cancelled"  # 已取消


class ContactMethod(str, Enum):
    """联系方式"""
    PHONE = "phone"
    SMS = "sms"
    EMAIL = "email"
    PUSH_NOTIFICATION = "push_notification"
    VOICE_CALL = "voice_call"


@dataclass
class VoiceConfirmationRequest:
    """语音确认请求"""
    request_id: str
    user_id: str
    incident_id: str
    message: str
    initiated_at: datetime
    timeout_seconds: int = 30  # 需求2.2：30秒超时
    expires_at: datetime = field(init=False)
    response_received: bool = False
    response_text: Optional[str] = None
    response_timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """计算过期时间"""
        self.expires_at = self.initiated_at + timedelta(seconds=self.timeout_seconds)
    
    def is_expired(self) -> bool:
        """检查是否已过期"""
        return datetime.utcnow() > self.expires_at
    
    def record_response(self, response_text: str) -> None:
        """记录用户响应"""
        self.response_received = True
        self.response_text = response_text
        self.response_timestamp = datetime.utcnow()


@dataclass
class ContactResult:
    """联系结果"""
    contact_id: str
    contact_name: str
    contact_method: ContactMethod
    success: bool
    attempted_at: datetime
    response_received: bool = False
    response_time: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class EmergencyPackage:
    """紧急信息包 - 需求2.4"""
    package_id: str
    user_id: str
    incident: IncidentData
    location: Location
    medical_history: Dict[str, Any]
    event_details: Dict[str, Any]
    emergency_contacts: List[EmergencyContact]
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式用于传输"""
        return {
            "package_id": self.package_id,
            "user_id": self.user_id,
            "incident": {
                "incident_id": self.incident.incident_id,
                "type": self.incident.incident_type.value,
                "severity": self.incident.severity.value,
                "timestamp": self.incident.timestamp.isoformat(),
                "sensor_data": self.incident.sensor_data
            },
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
                "address": self.location.address
            },
            "medical_history": self.medical_history,
            "event_details": self.event_details,
            "emergency_contacts": [
                {
                    "name": contact.name,
                    "relationship": contact.relationship,
                    "phone": contact.phone,
                    "email": contact.email,
                    "priority": contact.priority
                }
                for contact in self.emergency_contacts
            ],
            "created_at": self.created_at.isoformat()
        }


@dataclass
class DispatchResult:
    """调度结果"""
    dispatch_id: str
    incident_id: str
    status: DispatchStatus
    voice_confirmation: Optional[VoiceConfirmationRequest] = None
    care_circle_contacts: List[ContactResult] = field(default_factory=list)
    emergency_service_contact: Optional[ContactResult] = None
    emergency_package: Optional[EmergencyPackage] = None
    monitoring_active: bool = False
    status_updates: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_status_update(self, status: DispatchStatus, details: Dict[str, Any]) -> None:
        """添加状态更新"""
        self.status = status
        self.status_updates.append({
            "status": status.value,
            "timestamp": datetime.utcnow(),
            "details": details
        })


class EmergencyDispatcher:
    """
    紧急响应调度器 - 协调紧急响应工作流
    
    核心功能：
    1. 发送AI语音确认（30秒超时）
    2. 联系关爱圈成员
    3. 派遣紧急服务
    4. 打包紧急信息（位置、病史、事件详情）
    5. 持续监控和状态更新
    """
    
    # 语音确认超时时间（秒）- 需求2.2
    VOICE_CONFIRMATION_TIMEOUT = 30
    
    # 关爱圈联系超时时间（秒）- 需求2.3
    CARE_CIRCLE_TIMEOUT = 30
    
    def __init__(self):
        """初始化紧急调度器"""
        self._active_dispatches: Dict[str, DispatchResult] = {}
        self._voice_confirmations: Dict[str, VoiceConfirmationRequest] = {}
    
    def initiate_emergency_response(
        self,
        incident: IncidentData,
        user_profile: UserProfile
    ) -> DispatchResult:
        """
        启动紧急响应工作流
        
        Args:
            incident: 事件数据
            user_profile: 用户档案
            
        Returns:
            DispatchResult: 调度结果
        """
        dispatch_id = str(uuid.uuid4())
        
        # 创建调度结果
        dispatch_result = DispatchResult(
            dispatch_id=dispatch_id,
            incident_id=incident.incident_id,
            status=DispatchStatus.INITIATED
        )
        
        # 添加初始状态更新
        dispatch_result.add_status_update(
            DispatchStatus.INITIATED,
            {
                "user_id": incident.user_id,
                "incident_type": incident.incident_type.value,
                "severity": incident.severity.value
            }
        )
        
        # 存储活跃调度
        self._active_dispatches[dispatch_id] = dispatch_result
        
        # 启动持续监控（需求2.5）
        dispatch_result.monitoring_active = True
        
        return dispatch_result
    
    def send_voice_confirmation(
        self,
        dispatch_id: str,
        user_id: str,
        incident: IncidentData
    ) -> VoiceConfirmationRequest:
        """
        发送AI语音确认 - 需求2.2
        
        Args:
            dispatch_id: 调度ID
            user_id: 用户ID
            incident: 事件数据
            
        Returns:
            VoiceConfirmationRequest: 语音确认请求
        """
        dispatch_result = self._active_dispatches.get(dispatch_id)
        if not dispatch_result:
            raise ValueError(f"Dispatch {dispatch_id} not found")
        
        # 生成语音确认消息
        message = self._generate_voice_confirmation_message(incident)
        
        # 创建语音确认请求
        request_id = str(uuid.uuid4())
        voice_confirmation = VoiceConfirmationRequest(
            request_id=request_id,
            user_id=user_id,
            incident_id=incident.incident_id,
            message=message,
            initiated_at=datetime.utcnow(),
            timeout_seconds=self.VOICE_CONFIRMATION_TIMEOUT
        )
        
        # 存储语音确认请求
        self._voice_confirmations[request_id] = voice_confirmation
        dispatch_result.voice_confirmation = voice_confirmation
        
        # 更新调度状态
        dispatch_result.add_status_update(
            DispatchStatus.VOICE_CONFIRMATION_SENT,
            {
                "request_id": request_id,
                "timeout_seconds": self.VOICE_CONFIRMATION_TIMEOUT,
                "expires_at": voice_confirmation.expires_at.isoformat()
            }
        )
        
        return voice_confirmation
    
    def check_voice_confirmation_timeout(
        self,
        request_id: str
    ) -> bool:
        """
        检查语音确认是否超时
        
        Args:
            request_id: 语音确认请求ID
            
        Returns:
            bool: 是否超时
        """
        voice_confirmation = self._voice_confirmations.get(request_id)
        if not voice_confirmation:
            return False
        
        return voice_confirmation.is_expired() and not voice_confirmation.response_received
    
    def record_voice_response(
        self,
        request_id: str,
        response_text: str
    ) -> bool:
        """
        记录用户语音响应
        
        Args:
            request_id: 语音确认请求ID
            response_text: 响应文本
            
        Returns:
            bool: 是否成功记录
        """
        voice_confirmation = self._voice_confirmations.get(request_id)
        if not voice_confirmation:
            return False
        
        # 记录响应
        voice_confirmation.record_response(response_text)
        
        # 查找对应的调度并更新状态
        for dispatch_result in self._active_dispatches.values():
            if (dispatch_result.voice_confirmation and 
                dispatch_result.voice_confirmation.request_id == request_id):
                dispatch_result.add_status_update(
                    DispatchStatus.USER_RESPONDED,
                    {
                        "request_id": request_id,
                        "response_text": response_text,
                        "response_time": voice_confirmation.response_timestamp.isoformat()
                    }
                )
                break
        
        return True
    
    def contact_care_circle(
        self,
        dispatch_id: str,
        emergency_contacts: List[EmergencyContact],
        incident: IncidentData
    ) -> List[ContactResult]:
        """
        联系关爱圈 - 需求2.3
        
        Args:
            dispatch_id: 调度ID
            emergency_contacts: 紧急联系人列表
            incident: 事件数据
            
        Returns:
            List[ContactResult]: 联系结果列表
        """
        dispatch_result = self._active_dispatches.get(dispatch_id)
        if not dispatch_result:
            raise ValueError(f"Dispatch {dispatch_id} not found")
        
        contact_results = []
        
        # 按优先级排序联系人
        sorted_contacts = sorted(emergency_contacts, key=lambda c: c.priority)
        
        for contact in sorted_contacts:
            # 尝试多种联系方式
            contact_methods = [ContactMethod.VOICE_CALL, ContactMethod.SMS]
            
            for method in contact_methods:
                result = self._attempt_contact(contact, method, incident)
                contact_results.append(result)
                
                # 如果成功联系，记录并继续下一个联系人
                if result.success:
                    break
        
        # 存储联系结果
        dispatch_result.care_circle_contacts = contact_results
        
        # 更新调度状态
        dispatch_result.add_status_update(
            DispatchStatus.CARE_CIRCLE_CONTACTED,
            {
                "contacts_attempted": len(contact_results),
                "successful_contacts": sum(1 for r in contact_results if r.success),
                "contact_details": [
                    {
                        "name": r.contact_name,
                        "method": r.contact_method.value,
                        "success": r.success
                    }
                    for r in contact_results
                ]
            }
        )
        
        return contact_results
    
    def dispatch_emergency_services(
        self,
        dispatch_id: str,
        emergency_package: EmergencyPackage
    ) -> ContactResult:
        """
        派遣紧急服务 - 需求2.4
        
        Args:
            dispatch_id: 调度ID
            emergency_package: 紧急信息包
            
        Returns:
            ContactResult: 联系结果
        """
        dispatch_result = self._active_dispatches.get(dispatch_id)
        if not dispatch_result:
            raise ValueError(f"Dispatch {dispatch_id} not found")
        
        # 存储紧急信息包
        dispatch_result.emergency_package = emergency_package
        
        # 联系紧急服务（模拟）
        contact_result = ContactResult(
            contact_id=str(uuid.uuid4()),
            contact_name="Emergency Services (120)",
            contact_method=ContactMethod.VOICE_CALL,
            success=True,
            attempted_at=datetime.utcnow()
        )
        
        dispatch_result.emergency_service_contact = contact_result
        
        # 更新调度状态
        dispatch_result.add_status_update(
            DispatchStatus.EMERGENCY_DISPATCHED,
            {
                "package_id": emergency_package.package_id,
                "location": {
                    "latitude": emergency_package.location.latitude,
                    "longitude": emergency_package.location.longitude,
                    "address": emergency_package.location.address
                },
                "incident_type": emergency_package.incident.incident_type.value,
                "dispatched_at": contact_result.attempted_at.isoformat()
            }
        )
        
        return contact_result
    
    def create_emergency_package(
        self,
        incident: IncidentData,
        user_profile: UserProfile
    ) -> EmergencyPackage:
        """
        创建紧急信息包 - 需求2.4
        
        Args:
            incident: 事件数据
            user_profile: 用户档案
            
        Returns:
            EmergencyPackage: 紧急信息包
        """
        # 提取医疗历史
        medical_history = {
            "age": user_profile.age,
            "medical_conditions": [
                {
                    "name": condition.condition_name,
                    "severity": condition.severity,
                    "diagnosed_date": condition.diagnosed_date.isoformat()
                }
                for condition in user_profile.medical_conditions
            ],
            "mobility_aids": [
                {
                    "type": aid.aid_type,
                    "start_date": aid.start_date.isoformat()
                }
                for aid in user_profile.mobility_aids
            ]
        }
        
        # 提取事件详情
        event_details = {
            "incident_type": incident.incident_type.value,
            "severity": incident.severity.value,
            "timestamp": incident.timestamp.isoformat(),
            "sensor_data": incident.sensor_data,
            "verification_status": incident.verification_status.value
        }
        
        # 创建紧急信息包
        package = EmergencyPackage(
            package_id=str(uuid.uuid4()),
            user_id=incident.user_id,
            incident=incident,
            location=incident.location,
            medical_history=medical_history,
            event_details=event_details,
            emergency_contacts=user_profile.emergency_contacts
        )
        
        return package
    
    def update_monitoring_status(
        self,
        dispatch_id: str,
        status_update: Dict[str, Any]
    ) -> bool:
        """
        更新持续监控状态 - 需求2.5
        
        Args:
            dispatch_id: 调度ID
            status_update: 状态更新信息
            
        Returns:
            bool: 是否成功更新
        """
        dispatch_result = self._active_dispatches.get(dispatch_id)
        if not dispatch_result:
            return False
        
        # 添加监控状态更新
        dispatch_result.add_status_update(
            DispatchStatus.MONITORING,
            status_update
        )
        
        return True
    
    def get_dispatch_status(self, dispatch_id: str) -> Optional[DispatchResult]:
        """
        获取调度状态
        
        Args:
            dispatch_id: 调度ID
            
        Returns:
            Optional[DispatchResult]: 调度结果，如果不存在则返回None
        """
        return self._active_dispatches.get(dispatch_id)
    
    def resolve_dispatch(
        self,
        dispatch_id: str,
        resolution_details: Dict[str, Any]
    ) -> bool:
        """
        解决调度
        
        Args:
            dispatch_id: 调度ID
            resolution_details: 解决详情
            
        Returns:
            bool: 是否成功解决
        """
        dispatch_result = self._active_dispatches.get(dispatch_id)
        if not dispatch_result:
            return False
        
        # 停止监控
        dispatch_result.monitoring_active = False
        
        # 更新状态为已解决
        dispatch_result.add_status_update(
            DispatchStatus.RESOLVED,
            resolution_details
        )
        
        # 从活跃调度中移除
        self._active_dispatches.pop(dispatch_id, None)
        
        return True
    
    def cancel_dispatch(
        self,
        dispatch_id: str,
        cancellation_reason: str
    ) -> bool:
        """
        取消调度
        
        Args:
            dispatch_id: 调度ID
            cancellation_reason: 取消原因
            
        Returns:
            bool: 是否成功取消
        """
        dispatch_result = self._active_dispatches.get(dispatch_id)
        if not dispatch_result:
            return False
        
        # 停止监控
        dispatch_result.monitoring_active = False
        
        # 更新状态为已取消
        dispatch_result.add_status_update(
            DispatchStatus.CANCELLED,
            {"reason": cancellation_reason}
        )
        
        # 从活跃调度中移除
        self._active_dispatches.pop(dispatch_id, None)
        
        return True
    
    def get_active_dispatches(self) -> List[DispatchResult]:
        """获取所有活跃的调度"""
        return list(self._active_dispatches.values())
    
    def _generate_voice_confirmation_message(self, incident: IncidentData) -> str:
        """生成语音确认消息"""
        incident_labels = {
            "fall": "跌倒",
            "fall_detected": "跌倒",
            "medical_emergency": "医疗紧急情况",
            "prolonged_inactivity": "长时间不活动",
            "abnormal_movement": "异常移动"
        }
        
        incident_label = incident_labels.get(
            incident.incident_type.value,
            "紧急情况"
        )
        
        message = (
            f"您好，我们检测到{incident_label}。"
            f"如果您一切正常，请说'我很好'或按下确认按钮。"
            f"如果需要帮助，请说'需要帮助'。"
        )
        
        return message
    
    def _attempt_contact(
        self,
        contact: EmergencyContact,
        method: ContactMethod,
        incident: IncidentData
    ) -> ContactResult:
        """
        尝试联系紧急联系人
        
        注意：这是一个框架方法，实际实现需要集成具体的通信服务
        """
        contact_id = str(uuid.uuid4())
        
        # 模拟联系尝试
        # 在实际实现中，这里会调用真实的通信API
        success = True  # 假设联系成功
        
        result = ContactResult(
            contact_id=contact_id,
            contact_name=contact.name,
            contact_method=method,
            success=success,
            attempted_at=datetime.utcnow()
        )
        
        return result
