"""
紧急响应调度器单元测试
Unit tests for EmergencyDispatcher
"""
import pytest
from datetime import datetime, timedelta
from app.services.emergency_dispatcher import (
    EmergencyDispatcher,
    DispatchStatus,
    ContactMethod,
    VoiceConfirmationRequest,
    ContactResult,
    EmergencyPackage,
    DispatchResult
)
from app.schemas.core import (
    IncidentData,
    IncidentType,
    SeverityLevel,
    VerificationStatus,
    Location,
    UserProfile,
    EmergencyContact,
    MedicalCondition,
    MobilityAid,
    CarePreferences,
    BaselineMetrics
)


@pytest.fixture
def dispatcher():
    """创建EmergencyDispatcher实例"""
    return EmergencyDispatcher()


@pytest.fixture
def fall_incident():
    """创建跌倒事件"""
    return IncidentData(
        incident_id="incident_001",
        user_id="user_123",
        incident_type=IncidentType.FALL,
        timestamp=datetime.utcnow(),
        severity=SeverityLevel.EMERGENCY,
        location=Location(latitude=39.9042, longitude=116.4074, address="北京市朝阳区"),
        sensor_data={"fall_detected": True, "impact_force": 8.5},
        verification_status=VerificationStatus.CONFIRMED
    )


@pytest.fixture
def user_profile():
    """创建用户档案"""
    return UserProfile(
        user_id="user_123",
        age=75,
        medical_conditions=[
            MedicalCondition(
                condition_name="高血压",
                diagnosed_date=datetime(2020, 1, 1),
                severity="moderate",
                notes="每日服药控制"
            ),
            MedicalCondition(
                condition_name="糖尿病",
                diagnosed_date=datetime(2018, 6, 15),
                severity="mild",
                notes="饮食控制"
            )
        ],
        mobility_aids=[
            MobilityAid(
                aid_type="walker",
                start_date=datetime(2021, 3, 1),
                notes="室内使用"
            )
        ],
        emergency_contacts=[
            EmergencyContact(
                name="张明",
                relationship="儿子",
                phone="13800138001",
                email="zhangming@example.com",
                priority=1
            ),
            EmergencyContact(
                name="李华",
                relationship="女儿",
                phone="13800138002",
                email="lihua@example.com",
                priority=2
            )
        ],
        care_preferences=CarePreferences(
            preferred_language="zh-CN",
            voice_confirmation_enabled=True,
            emergency_auto_escalation=True
        ),
        baseline_metrics=BaselineMetrics(
            average_daily_steps=3000,
            average_sleep_hours=7.5,
            typical_activity_periods=[(8, 12), (14, 18)],
            baseline_mobility_score=0.6
        )
    )


class TestEmergencyResponseInitiation:
    """测试紧急响应启动"""
    
    def test_initiate_emergency_response(self, dispatcher, fall_incident, user_profile):
        """测试启动紧急响应"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        assert dispatch_result is not None
        assert dispatch_result.incident_id == fall_incident.incident_id
        assert dispatch_result.status == DispatchStatus.INITIATED
        assert dispatch_result.monitoring_active is True
    
    def test_dispatch_has_unique_id(self, dispatcher, fall_incident, user_profile):
        """测试调度有唯一ID"""
        dispatch1 = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        # 创建另一个事件
        incident2 = IncidentData(
            incident_id="incident_002",
            user_id="user_123",
            incident_type=IncidentType.FALL,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.EMERGENCY,
            location=Location(latitude=39.9042, longitude=116.4074),
            sensor_data={},
            verification_status=VerificationStatus.PENDING
        )
        
        dispatch2 = dispatcher.initiate_emergency_response(incident2, user_profile)
        
        assert dispatch1.dispatch_id != dispatch2.dispatch_id
    
    def test_dispatch_stored_in_active_dispatches(self, dispatcher, fall_incident, user_profile):
        """测试调度存储在活跃调度中"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        retrieved = dispatcher.get_dispatch_status(dispatch_result.dispatch_id)
        assert retrieved is not None
        assert retrieved.dispatch_id == dispatch_result.dispatch_id
    
    def test_dispatch_has_initial_status_update(self, dispatcher, fall_incident, user_profile):
        """测试调度有初始状态更新"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        assert len(dispatch_result.status_updates) > 0
        first_update = dispatch_result.status_updates[0]
        assert first_update["status"] == DispatchStatus.INITIATED.value


class TestVoiceConfirmation:
    """测试语音确认功能"""
    
    def test_send_voice_confirmation(self, dispatcher, fall_incident, user_profile):
        """测试发送语音确认"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        assert voice_confirmation is not None
        assert voice_confirmation.user_id == user_profile.user_id
        assert voice_confirmation.incident_id == fall_incident.incident_id
        assert voice_confirmation.timeout_seconds == 30  # 需求2.2
    
    def test_voice_confirmation_timeout_is_30_seconds(self, dispatcher, fall_incident, user_profile):
        """测试语音确认超时为30秒（需求2.2）"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        time_diff = (voice_confirmation.expires_at - voice_confirmation.initiated_at).total_seconds()
        assert abs(time_diff - 30) < 1  # 30秒，允许1秒误差
    
    def test_voice_confirmation_message_generation(self, dispatcher, fall_incident, user_profile):
        """测试语音确认消息生成"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        assert "跌倒" in voice_confirmation.message
        assert "我很好" in voice_confirmation.message or "确认" in voice_confirmation.message
    
    def test_voice_confirmation_updates_dispatch_status(self, dispatcher, fall_incident, user_profile):
        """测试语音确认更新调度状态"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        assert dispatch_result.status == DispatchStatus.VOICE_CONFIRMATION_SENT
        assert dispatch_result.voice_confirmation is not None
    
    def test_check_voice_confirmation_timeout(self, dispatcher, fall_incident, user_profile):
        """测试检查语音确认超时"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        # 刚发送，不应该超时
        is_timeout = dispatcher.check_voice_confirmation_timeout(voice_confirmation.request_id)
        assert is_timeout is False
    
    def test_voice_confirmation_expires_after_timeout(self, dispatcher, fall_incident, user_profile):
        """测试语音确认在超时后过期"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        # 手动设置过期时间为过去
        voice_confirmation.expires_at = datetime.utcnow() - timedelta(seconds=1)
        
        is_timeout = dispatcher.check_voice_confirmation_timeout(voice_confirmation.request_id)
        assert is_timeout is True
    
    def test_record_voice_response(self, dispatcher, fall_incident, user_profile):
        """测试记录语音响应"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        success = dispatcher.record_voice_response(
            voice_confirmation.request_id,
            "我很好"
        )
        
        assert success is True
        assert voice_confirmation.response_received is True
        assert voice_confirmation.response_text == "我很好"
    
    def test_voice_response_updates_dispatch_status(self, dispatcher, fall_incident, user_profile):
        """测试语音响应更新调度状态"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        dispatcher.record_voice_response(
            voice_confirmation.request_id,
            "我很好"
        )
        
        assert dispatch_result.status == DispatchStatus.USER_RESPONDED
    
    def test_voice_response_prevents_timeout(self, dispatcher, fall_incident, user_profile):
        """测试语音响应防止超时"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        # 记录响应
        dispatcher.record_voice_response(voice_confirmation.request_id, "我很好")
        
        # 手动设置过期时间为过去
        voice_confirmation.expires_at = datetime.utcnow() - timedelta(seconds=1)
        
        # 即使过期时间已过，因为已收到响应，不应该超时
        is_timeout = dispatcher.check_voice_confirmation_timeout(voice_confirmation.request_id)
        assert is_timeout is False


class TestCareCircleContact:
    """测试关爱圈联系功能"""
    
    def test_contact_care_circle(self, dispatcher, fall_incident, user_profile):
        """测试联系关爱圈（需求2.3）"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        contact_results = dispatcher.contact_care_circle(
            dispatch_result.dispatch_id,
            user_profile.emergency_contacts,
            fall_incident
        )
        
        assert len(contact_results) > 0
        assert dispatch_result.status == DispatchStatus.CARE_CIRCLE_CONTACTED
    
    def test_care_circle_contacts_by_priority(self, dispatcher, fall_incident, user_profile):
        """测试关爱圈按优先级联系"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        contact_results = dispatcher.contact_care_circle(
            dispatch_result.dispatch_id,
            user_profile.emergency_contacts,
            fall_incident
        )
        
        # 验证联系顺序（优先级1的联系人应该先被联系）
        # 由于每个联系人可能有多个联系方式，我们检查第一个联系人的名字
        first_contact_name = contact_results[0].contact_name
        assert first_contact_name == "张明"  # 优先级1
    
    def test_care_circle_multiple_contact_methods(self, dispatcher, fall_incident, user_profile):
        """测试关爱圈使用多种联系方式"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        contact_results = dispatcher.contact_care_circle(
            dispatch_result.dispatch_id,
            user_profile.emergency_contacts,
            fall_incident
        )
        
        # 应该尝试多种联系方式
        contact_methods = [result.contact_method for result in contact_results]
        assert ContactMethod.VOICE_CALL in contact_methods or ContactMethod.SMS in contact_methods
    
    def test_care_circle_contact_results_stored(self, dispatcher, fall_incident, user_profile):
        """测试关爱圈联系结果被存储"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        contact_results = dispatcher.contact_care_circle(
            dispatch_result.dispatch_id,
            user_profile.emergency_contacts,
            fall_incident
        )
        
        assert dispatch_result.care_circle_contacts == contact_results
        assert len(dispatch_result.care_circle_contacts) > 0


class TestEmergencyPackage:
    """测试紧急信息包功能"""
    
    def test_create_emergency_package(self, dispatcher, fall_incident, user_profile):
        """测试创建紧急信息包（需求2.4）"""
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        assert package is not None
        assert package.user_id == user_profile.user_id
        assert package.incident == fall_incident
        assert package.location == fall_incident.location
    
    def test_emergency_package_includes_location(self, dispatcher, fall_incident, user_profile):
        """测试紧急信息包包含位置信息（需求2.4）"""
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        assert package.location.latitude == fall_incident.location.latitude
        assert package.location.longitude == fall_incident.location.longitude
        assert package.location.address == fall_incident.location.address
    
    def test_emergency_package_includes_medical_history(self, dispatcher, fall_incident, user_profile):
        """测试紧急信息包包含病史（需求2.4）"""
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        assert "medical_conditions" in package.medical_history
        assert len(package.medical_history["medical_conditions"]) == 2
        assert package.medical_history["age"] == user_profile.age
    
    def test_emergency_package_includes_event_details(self, dispatcher, fall_incident, user_profile):
        """测试紧急信息包包含事件详情（需求2.4）"""
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        assert package.event_details["incident_type"] == fall_incident.incident_type.value
        assert package.event_details["severity"] == fall_incident.severity.value
        assert "sensor_data" in package.event_details
    
    def test_emergency_package_includes_emergency_contacts(self, dispatcher, fall_incident, user_profile):
        """测试紧急信息包包含紧急联系人"""
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        assert len(package.emergency_contacts) == len(user_profile.emergency_contacts)
        assert package.emergency_contacts[0].name == "张明"
    
    def test_emergency_package_to_dict(self, dispatcher, fall_incident, user_profile):
        """测试紧急信息包转换为字典"""
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        package_dict = package.to_dict()
        
        assert "package_id" in package_dict
        assert "location" in package_dict
        assert "medical_history" in package_dict
        assert "event_details" in package_dict
        assert "emergency_contacts" in package_dict


class TestEmergencyServiceDispatch:
    """测试紧急服务派遣功能"""
    
    def test_dispatch_emergency_services(self, dispatcher, fall_incident, user_profile):
        """测试派遣紧急服务（需求2.4）"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        contact_result = dispatcher.dispatch_emergency_services(
            dispatch_result.dispatch_id,
            package
        )
        
        assert contact_result is not None
        assert contact_result.success is True
        assert "Emergency" in contact_result.contact_name or "120" in contact_result.contact_name
    
    def test_emergency_dispatch_updates_status(self, dispatcher, fall_incident, user_profile):
        """测试紧急派遣更新状态"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        dispatcher.dispatch_emergency_services(dispatch_result.dispatch_id, package)
        
        assert dispatch_result.status == DispatchStatus.EMERGENCY_DISPATCHED
        assert dispatch_result.emergency_service_contact is not None
    
    def test_emergency_dispatch_stores_package(self, dispatcher, fall_incident, user_profile):
        """测试紧急派遣存储信息包"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        dispatcher.dispatch_emergency_services(dispatch_result.dispatch_id, package)
        
        assert dispatch_result.emergency_package == package


class TestContinuousMonitoring:
    """测试持续监控功能"""
    
    def test_monitoring_active_on_initiation(self, dispatcher, fall_incident, user_profile):
        """测试启动时监控激活（需求2.5）"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        assert dispatch_result.monitoring_active is True
    
    def test_update_monitoring_status(self, dispatcher, fall_incident, user_profile):
        """测试更新监控状态（需求2.5）"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        success = dispatcher.update_monitoring_status(
            dispatch_result.dispatch_id,
            {
                "vital_signs": "stable",
                "user_movement": "detected",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        assert success is True
        assert dispatch_result.status == DispatchStatus.MONITORING
    
    def test_monitoring_status_updates_recorded(self, dispatcher, fall_incident, user_profile):
        """测试监控状态更新被记录"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        initial_update_count = len(dispatch_result.status_updates)
        
        dispatcher.update_monitoring_status(
            dispatch_result.dispatch_id,
            {"status": "monitoring_active"}
        )
        
        assert len(dispatch_result.status_updates) > initial_update_count
    
    def test_monitoring_stops_on_resolution(self, dispatcher, fall_incident, user_profile):
        """测试解决时监控停止"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        dispatcher.resolve_dispatch(
            dispatch_result.dispatch_id,
            {"resolution": "user_confirmed_safe"}
        )
        
        assert dispatch_result.monitoring_active is False
    
    def test_monitoring_stops_on_cancellation(self, dispatcher, fall_incident, user_profile):
        """测试取消时监控停止"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        dispatcher.cancel_dispatch(
            dispatch_result.dispatch_id,
            "false_alarm"
        )
        
        assert dispatch_result.monitoring_active is False


class TestDispatchManagement:
    """测试调度管理功能"""
    
    def test_get_dispatch_status(self, dispatcher, fall_incident, user_profile):
        """测试获取调度状态"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        retrieved = dispatcher.get_dispatch_status(dispatch_result.dispatch_id)
        
        assert retrieved is not None
        assert retrieved.dispatch_id == dispatch_result.dispatch_id
    
    def test_get_nonexistent_dispatch(self, dispatcher):
        """测试获取不存在的调度"""
        retrieved = dispatcher.get_dispatch_status("nonexistent_id")
        assert retrieved is None
    
    def test_resolve_dispatch(self, dispatcher, fall_incident, user_profile):
        """测试解决调度"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        success = dispatcher.resolve_dispatch(
            dispatch_result.dispatch_id,
            {"resolution": "user_safe"}
        )
        
        assert success is True
        assert dispatch_result.status == DispatchStatus.RESOLVED
    
    def test_resolved_dispatch_removed_from_active(self, dispatcher, fall_incident, user_profile):
        """测试已解决的调度从活跃列表中移除"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        dispatch_id = dispatch_result.dispatch_id
        
        dispatcher.resolve_dispatch(dispatch_id, {"resolution": "user_safe"})
        
        retrieved = dispatcher.get_dispatch_status(dispatch_id)
        assert retrieved is None
    
    def test_cancel_dispatch(self, dispatcher, fall_incident, user_profile):
        """测试取消调度"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        success = dispatcher.cancel_dispatch(
            dispatch_result.dispatch_id,
            "false_alarm"
        )
        
        assert success is True
        assert dispatch_result.status == DispatchStatus.CANCELLED
    
    def test_cancelled_dispatch_removed_from_active(self, dispatcher, fall_incident, user_profile):
        """测试已取消的调度从活跃列表中移除"""
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        dispatch_id = dispatch_result.dispatch_id
        
        dispatcher.cancel_dispatch(dispatch_id, "false_alarm")
        
        retrieved = dispatcher.get_dispatch_status(dispatch_id)
        assert retrieved is None
    
    def test_get_active_dispatches(self, dispatcher, fall_incident, user_profile):
        """测试获取所有活跃调度"""
        dispatch1 = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        # 创建第二个事件
        incident2 = IncidentData(
            incident_id="incident_002",
            user_id="user_456",
            incident_type=IncidentType.MEDICAL_EMERGENCY,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.EMERGENCY,
            location=Location(latitude=31.2304, longitude=121.4737),
            sensor_data={},
            verification_status=VerificationStatus.PENDING
        )
        
        dispatch2 = dispatcher.initiate_emergency_response(incident2, user_profile)
        
        active_dispatches = dispatcher.get_active_dispatches()
        assert len(active_dispatches) == 2
        
        dispatch_ids = [d.dispatch_id for d in active_dispatches]
        assert dispatch1.dispatch_id in dispatch_ids
        assert dispatch2.dispatch_id in dispatch_ids


class TestCompleteEmergencyWorkflow:
    """测试完整紧急响应工作流"""
    
    def test_complete_emergency_workflow_with_no_response(self, dispatcher, fall_incident, user_profile):
        """测试无响应的完整紧急工作流（需求2.2, 2.3, 2.4）"""
        # 1. 启动紧急响应
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        assert dispatch_result.status == DispatchStatus.INITIATED
        
        # 2. 发送语音确认
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        assert dispatch_result.status == DispatchStatus.VOICE_CONFIRMATION_SENT
        
        # 3. 模拟30秒超时（无响应）
        voice_confirmation.expires_at = datetime.utcnow() - timedelta(seconds=1)
        is_timeout = dispatcher.check_voice_confirmation_timeout(voice_confirmation.request_id)
        assert is_timeout is True
        
        # 4. 联系关爱圈
        contact_results = dispatcher.contact_care_circle(
            dispatch_result.dispatch_id,
            user_profile.emergency_contacts,
            fall_incident
        )
        assert dispatch_result.status == DispatchStatus.CARE_CIRCLE_CONTACTED
        assert len(contact_results) > 0
        
        # 5. 创建紧急信息包
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        assert package.location == fall_incident.location
        assert "medical_conditions" in package.medical_history
        
        # 6. 派遣紧急服务
        emergency_contact = dispatcher.dispatch_emergency_services(
            dispatch_result.dispatch_id,
            package
        )
        assert dispatch_result.status == DispatchStatus.EMERGENCY_DISPATCHED
        assert emergency_contact.success is True
        
        # 7. 持续监控
        assert dispatch_result.monitoring_active is True
    
    def test_complete_emergency_workflow_with_user_response(self, dispatcher, fall_incident, user_profile):
        """测试用户响应的完整紧急工作流"""
        # 1. 启动紧急响应
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        # 2. 发送语音确认
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        # 3. 用户响应"我很好"
        dispatcher.record_voice_response(voice_confirmation.request_id, "我很好")
        assert dispatch_result.status == DispatchStatus.USER_RESPONDED
        assert voice_confirmation.response_received is True
        
        # 4. 取消调度（用户确认安全）
        dispatcher.cancel_dispatch(dispatch_result.dispatch_id, "user_confirmed_safe")
        assert dispatch_result.status == DispatchStatus.CANCELLED
        assert dispatch_result.monitoring_active is False
