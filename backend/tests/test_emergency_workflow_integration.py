"""
紧急响应工作流集成测试
Integration tests for complete emergency response workflow
"""
import pytest
from datetime import datetime, timedelta
from app.services.alert_orchestrator import AlertOrchestrator
from app.services.emergency_dispatcher import EmergencyDispatcher, DispatchStatus
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
def orchestrator():
    """创建AlertOrchestrator实例"""
    return AlertOrchestrator()


@pytest.fixture
def emergency_fall_incident():
    """创建紧急跌倒事件"""
    return IncidentData(
        incident_id="emergency_001",
        user_id="user_789",
        incident_type=IncidentType.FALL,
        timestamp=datetime.utcnow(),
        severity=SeverityLevel.EMERGENCY,
        location=Location(
            latitude=39.9042,
            longitude=116.4074,
            address="北京市朝阳区建国路88号"
        ),
        sensor_data={
            "fall_detected": True,
            "impact_force": 9.2,
            "user_immobile": True
        },
        verification_status=VerificationStatus.CONFIRMED
    )


@pytest.fixture
def elderly_user_profile():
    """创建老年用户档案"""
    return UserProfile(
        user_id="user_789",
        age=78,
        medical_conditions=[
            MedicalCondition(
                condition_name="心脏病",
                diagnosed_date=datetime(2019, 3, 15),
                severity="severe",
                notes="需要定期服用心脏药物"
            ),
            MedicalCondition(
                condition_name="骨质疏松",
                diagnosed_date=datetime(2020, 7, 20),
                severity="moderate",
                notes="跌倒风险高"
            )
        ],
        mobility_aids=[
            MobilityAid(
                aid_type="walker",
                start_date=datetime(2021, 1, 10),
                notes="日常使用助行器"
            )
        ],
        emergency_contacts=[
            EmergencyContact(
                name="王芳",
                relationship="女儿",
                phone="13900139001",
                email="wangfang@example.com",
                priority=1
            ),
            EmergencyContact(
                name="王强",
                relationship="儿子",
                phone="13900139002",
                email="wangqiang@example.com",
                priority=2
            ),
            EmergencyContact(
                name="李护士",
                relationship="护理人员",
                phone="13900139003",
                email="linurse@example.com",
                priority=3
            )
        ],
        care_preferences=CarePreferences(
            preferred_language="zh-CN",
            voice_confirmation_enabled=True,
            emergency_auto_escalation=True
        ),
        baseline_metrics=BaselineMetrics(
            average_daily_steps=2000,
            average_sleep_hours=8.0,
            typical_activity_periods=[(9, 11), (15, 17)],
            baseline_mobility_score=0.4
        )
    )


class TestEmergencyWorkflowIntegration:
    """测试紧急响应工作流集成"""
    
    def test_execute_complete_emergency_workflow(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试执行完整紧急响应工作流（需求2.2, 2.3, 2.4, 2.5）"""
        # 执行完整工作流
        workflow_result = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile,
            auto_escalate=True
        )
        
        # 验证工作流结果
        assert workflow_result["incident_id"] == emergency_fall_incident.incident_id
        assert workflow_result["user_id"] == elderly_user_profile.user_id
        assert workflow_result["severity"] == SeverityLevel.EMERGENCY.value
        
        # 验证所有步骤都已完成
        expected_steps = [
            "alert_created",
            "dispatch_initiated",
            "voice_confirmation_sent",
            "auto_escalate_prepared",
            "emergency_package_created",
            "response_coordinated"
        ]
        
        for step in expected_steps:
            assert step in workflow_result["steps_completed"]
    
    def test_workflow_creates_alert_and_dispatch(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试工作流创建警报和调度"""
        workflow_result = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile
        )
        
        # 验证警报已创建
        assert "alert_id" in workflow_result
        
        # 验证调度已启动
        assert "dispatch_id" in workflow_result
        dispatch_id = workflow_result["dispatch_id"]
        
        # 从调度器获取调度状态
        dispatcher = orchestrator.get_emergency_dispatcher()
        dispatch_status = dispatcher.get_dispatch_status(dispatch_id)
        
        assert dispatch_status is not None
        assert dispatch_status.incident_id == emergency_fall_incident.incident_id
        assert dispatch_status.monitoring_active is True
    
    def test_workflow_sends_voice_confirmation_for_emergency(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试紧急事件发送语音确认（需求2.2）"""
        workflow_result = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile
        )
        
        # 验证语音确认已发送
        assert workflow_result["voice_confirmation_sent"] is True
        assert "voice_confirmation_id" in workflow_result
        assert workflow_result["voice_timeout_seconds"] == 30  # 需求2.2
    
    def test_workflow_creates_emergency_package(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试工作流创建紧急信息包（需求2.4）"""
        workflow_result = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile
        )
        
        # 验证紧急信息包已创建
        assert "emergency_package_id" in workflow_result
        
        # 从调度器获取紧急信息包
        dispatcher = orchestrator.get_emergency_dispatcher()
        dispatch_status = dispatcher.get_dispatch_status(workflow_result["dispatch_id"])
        
        # 注意：在execute_emergency_workflow中，我们创建了包但没有派遣
        # 所以这里我们只验证包ID存在
        assert workflow_result["emergency_package_id"] is not None
    
    def test_workflow_enables_auto_escalation(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试工作流启用自动升级"""
        workflow_result = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile,
            auto_escalate=True
        )
        
        # 验证自动升级已准备
        assert workflow_result["auto_escalate_enabled"] is True
        assert workflow_result["emergency_contacts_count"] == len(elderly_user_profile.emergency_contacts)
    
    def test_workflow_without_auto_escalation(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试禁用自动升级的工作流"""
        workflow_result = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile,
            auto_escalate=False
        )
        
        # 验证自动升级未启用
        assert "auto_escalate_enabled" not in workflow_result or workflow_result["auto_escalate_enabled"] is False


class TestVoiceConfirmationTimeout:
    """测试语音确认超时处理"""
    
    def test_handle_voice_confirmation_timeout(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试处理语音确认超时（需求2.3）"""
        # 首先执行工作流
        workflow_result = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile
        )
        
        dispatch_id = workflow_result["dispatch_id"]
        
        # 处理语音确认超时
        escalation_result = orchestrator.handle_voice_confirmation_timeout(
            dispatch_id,
            elderly_user_profile,
            emergency_fall_incident
        )
        
        # 验证升级已触发
        assert escalation_result["escalation_triggered"] is True
        assert escalation_result["care_circle_contacted"] is True
        assert escalation_result["contacts_attempted"] > 0
    
    def test_timeout_contacts_care_circle(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试超时后联系关爱圈（需求2.3）"""
        workflow_result = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile
        )
        
        escalation_result = orchestrator.handle_voice_confirmation_timeout(
            workflow_result["dispatch_id"],
            elderly_user_profile,
            emergency_fall_incident
        )
        
        # 验证关爱圈已联系
        assert escalation_result["care_circle_contacted"] is True
        # 每个联系人尝试多种联系方式，但如果第一种成功就不会尝试第二种
        # 所以联系尝试次数至少等于联系人数量
        assert escalation_result["contacts_attempted"] >= len(elderly_user_profile.emergency_contacts)
    
    def test_timeout_dispatches_emergency_for_emergency_severity(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试紧急事件超时后派遣紧急服务（需求2.4）"""
        workflow_result = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile
        )
        
        escalation_result = orchestrator.handle_voice_confirmation_timeout(
            workflow_result["dispatch_id"],
            elderly_user_profile,
            emergency_fall_incident
        )
        
        # 验证紧急服务已派遣
        assert escalation_result["emergency_dispatched"] is True
        assert escalation_result["emergency_service_contacted"] is True
    
    def test_timeout_does_not_dispatch_emergency_for_high_severity(
        self,
        orchestrator,
        elderly_user_profile
    ):
        """测试高级事件超时后不派遣紧急服务"""
        # 创建高级事件（非紧急）
        high_incident = IncidentData(
            incident_id="high_001",
            user_id="user_789",
            incident_type=IncidentType.PROLONGED_INACTIVITY,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.HIGH,
            location=Location(latitude=39.9042, longitude=116.4074),
            sensor_data={"inactive_hours": 10},
            verification_status=VerificationStatus.CONFIRMED
        )
        
        workflow_result = orchestrator.execute_emergency_workflow(
            high_incident,
            elderly_user_profile
        )
        
        escalation_result = orchestrator.handle_voice_confirmation_timeout(
            workflow_result["dispatch_id"],
            elderly_user_profile,
            high_incident
        )
        
        # 验证关爱圈已联系，但紧急服务未派遣
        assert escalation_result["care_circle_contacted"] is True
        assert escalation_result["emergency_dispatched"] is False


class TestContinuousMonitoring:
    """测试持续监控功能"""
    
    def test_monitoring_active_after_workflow_execution(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试工作流执行后监控激活（需求2.5）"""
        workflow_result = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile
        )
        
        # 获取调度状态
        dispatcher = orchestrator.get_emergency_dispatcher()
        dispatch_status = dispatcher.get_dispatch_status(workflow_result["dispatch_id"])
        
        # 验证监控已激活
        assert dispatch_status.monitoring_active is True
    
    def test_monitoring_status_updates(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试监控状态更新（需求2.5）"""
        workflow_result = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile
        )
        
        dispatcher = orchestrator.get_emergency_dispatcher()
        dispatch_id = workflow_result["dispatch_id"]
        
        # 添加监控状态更新
        success = dispatcher.update_monitoring_status(
            dispatch_id,
            {
                "vital_signs": "stable",
                "user_movement": "detected",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        assert success is True
        
        # 验证状态更新已记录
        dispatch_status = dispatcher.get_dispatch_status(dispatch_id)
        assert dispatch_status.status == DispatchStatus.MONITORING
        assert len(dispatch_status.status_updates) > 0


class TestEmergencyPackageContent:
    """测试紧急信息包内容"""
    
    def test_emergency_package_includes_all_required_info(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试紧急信息包包含所有必需信息（需求2.4）"""
        workflow_result = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile
        )
        
        dispatcher = orchestrator.get_emergency_dispatcher()
        
        # 创建紧急信息包
        package = dispatcher.create_emergency_package(
            emergency_fall_incident,
            elderly_user_profile
        )
        
        # 验证位置信息
        assert package.location.latitude == emergency_fall_incident.location.latitude
        assert package.location.longitude == emergency_fall_incident.location.longitude
        assert package.location.address == emergency_fall_incident.location.address
        
        # 验证病史信息
        assert "medical_conditions" in package.medical_history
        assert len(package.medical_history["medical_conditions"]) == 2
        assert package.medical_history["age"] == 78
        
        # 验证事件详情
        assert package.event_details["incident_type"] == IncidentType.FALL.value
        assert package.event_details["severity"] == SeverityLevel.EMERGENCY.value
        
        # 验证紧急联系人
        assert len(package.emergency_contacts) == 3
    
    def test_emergency_package_serialization(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试紧急信息包序列化"""
        dispatcher = orchestrator.get_emergency_dispatcher()
        package = dispatcher.create_emergency_package(
            emergency_fall_incident,
            elderly_user_profile
        )
        
        # 转换为字典
        package_dict = package.to_dict()
        
        # 验证所有关键字段存在
        assert "package_id" in package_dict
        assert "user_id" in package_dict
        assert "incident" in package_dict
        assert "location" in package_dict
        assert "medical_history" in package_dict
        assert "event_details" in package_dict
        assert "emergency_contacts" in package_dict
        assert "created_at" in package_dict


class TestMultipleSimultaneousEmergencies:
    """测试多个同时发生的紧急情况"""
    
    def test_handle_multiple_emergencies(
        self,
        orchestrator,
        emergency_fall_incident,
        elderly_user_profile
    ):
        """测试处理多个紧急情况"""
        # 创建第一个紧急情况
        workflow1 = orchestrator.execute_emergency_workflow(
            emergency_fall_incident,
            elderly_user_profile
        )
        
        # 创建第二个紧急情况
        incident2 = IncidentData(
            incident_id="emergency_002",
            user_id="user_999",
            incident_type=IncidentType.MEDICAL_EMERGENCY,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.EMERGENCY,
            location=Location(latitude=31.2304, longitude=121.4737),
            sensor_data={"heart_rate_abnormal": True},
            verification_status=VerificationStatus.CONFIRMED
        )
        
        workflow2 = orchestrator.execute_emergency_workflow(
            incident2,
            elderly_user_profile
        )
        
        # 验证两个工作流都已创建
        assert workflow1["dispatch_id"] != workflow2["dispatch_id"]
        
        # 验证两个调度都是活跃的
        dispatcher = orchestrator.get_emergency_dispatcher()
        active_dispatches = dispatcher.get_active_dispatches()
        assert len(active_dispatches) == 2
