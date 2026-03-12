"""
警报编排器单元测试
Unit tests for AlertOrchestrator
"""
import pytest
from datetime import datetime, timedelta
from app.services.alert_orchestrator import (
    AlertOrchestrator,
    ResponseProtocol,
    ResponseStatus,
    ResponsePlan,
    AlertResponse
)
from app.schemas.core import (
    IncidentData,
    IncidentType,
    SeverityLevel,
    VerificationStatus,
    Location
)


@pytest.fixture
def orchestrator():
    """创建AlertOrchestrator实例"""
    return AlertOrchestrator()


@pytest.fixture
def fall_incident():
    """创建跌倒事件"""
    return IncidentData(
        incident_id="incident_001",
        user_id="user_123",
        incident_type=IncidentType.FALL,
        timestamp=datetime.utcnow(),
        severity=SeverityLevel.EMERGENCY,
        location=Location(latitude=39.9042, longitude=116.4074, address="北京市"),
        sensor_data={"fall_detected": True, "impact_force": 8.5},
        verification_status=VerificationStatus.PENDING
    )


@pytest.fixture
def medication_incident():
    """创建用药提醒事件"""
    return IncidentData(
        incident_id="incident_002",
        user_id="user_123",
        incident_type=IncidentType.MISSED_MEDICATION,
        timestamp=datetime.utcnow(),
        severity=SeverityLevel.LOW,
        location=Location(latitude=39.9042, longitude=116.4074, address="北京市"),
        sensor_data={"medication_name": "阿司匹林", "scheduled_time": "08:00"},
        verification_status=VerificationStatus.PENDING
    )


class TestSeverityClassification:
    """测试严重程度分类"""
    
    def test_fall_classified_as_emergency(self, orchestrator, fall_incident):
        """测试跌倒事件被分类为紧急"""
        severity = orchestrator.classify_severity(fall_incident)
        assert severity == SeverityLevel.EMERGENCY
    
    def test_missed_medication_classified_as_low(self, orchestrator, medication_incident):
        """测试错过用药被分类为低级"""
        severity = orchestrator.classify_severity(medication_incident)
        assert severity == SeverityLevel.LOW
    
    def test_prolonged_inactivity_classified_as_high(self, orchestrator):
        """测试长时间不活动被分类为高级"""
        incident = IncidentData(
            incident_id="incident_003",
            user_id="user_123",
            incident_type=IncidentType.PROLONGED_INACTIVITY,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.HIGH,
            location=Location(latitude=39.9042, longitude=116.4074),
            sensor_data={"inactive_hours": 12},
            verification_status=VerificationStatus.PENDING
        )
        severity = orchestrator.classify_severity(incident)
        assert severity == SeverityLevel.HIGH
    
    def test_abnormal_movement_classified_as_medium(self, orchestrator):
        """测试异常移动被分类为中级"""
        incident = IncidentData(
            incident_id="incident_004",
            user_id="user_123",
            incident_type=IncidentType.ABNORMAL_MOVEMENT,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.MEDIUM,
            location=Location(latitude=39.9042, longitude=116.4074),
            sensor_data={"movement_pattern": "irregular"},
            verification_status=VerificationStatus.PENDING
        )
        severity = orchestrator.classify_severity(incident)
        assert severity == SeverityLevel.MEDIUM
    
    def test_severity_escalation_with_high_risk_conditions(self, orchestrator, medication_incident):
        """测试高风险医疗状况导致严重程度升级"""
        context = {"high_risk_conditions": True}
        
        # 将低级事件改为中级
        incident = IncidentData(
            incident_id="incident_005",
            user_id="user_123",
            incident_type=IncidentType.ABNORMAL_MOVEMENT,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.MEDIUM,
            location=Location(latitude=39.9042, longitude=116.4074),
            sensor_data={},
            verification_status=VerificationStatus.PENDING
        )
        severity = orchestrator.classify_severity(incident, context)
        assert severity == SeverityLevel.HIGH
    
    def test_severity_escalation_with_repeated_incidents(self, orchestrator, medication_incident):
        """测试重复事件导致严重程度升级"""
        context = {"recent_similar_incidents": 3}
        severity = orchestrator.classify_severity(medication_incident, context)
        assert severity == SeverityLevel.MEDIUM


class TestResponseProtocols:
    """测试响应协议"""
    
    def test_emergency_protocols(self, orchestrator):
        """测试紧急级别的响应协议"""
        protocols = orchestrator.get_response_protocols(SeverityLevel.EMERGENCY)
        assert ResponseProtocol.VOICE_CONFIRMATION in protocols
        assert ResponseProtocol.CONTACT_CARE_CIRCLE in protocols
        assert ResponseProtocol.DISPATCH_EMERGENCY in protocols
    
    def test_high_protocols(self, orchestrator):
        """测试高级别的响应协议"""
        protocols = orchestrator.get_response_protocols(SeverityLevel.HIGH)
        assert ResponseProtocol.VOICE_CONFIRMATION in protocols
        assert ResponseProtocol.NOTIFY_FAMILY in protocols
        assert ResponseProtocol.CONTACT_CARE_CIRCLE in protocols
    
    def test_medium_protocols(self, orchestrator):
        """测试中级别的响应协议"""
        protocols = orchestrator.get_response_protocols(SeverityLevel.MEDIUM)
        assert ResponseProtocol.MONITOR in protocols
        assert ResponseProtocol.NOTIFY_FAMILY in protocols
        assert ResponseProtocol.VOICE_CONFIRMATION in protocols
    
    def test_low_protocols(self, orchestrator):
        """测试低级别的响应协议"""
        protocols = orchestrator.get_response_protocols(SeverityLevel.LOW)
        assert ResponseProtocol.MONITOR in protocols
        assert ResponseProtocol.NOTIFY_FAMILY in protocols


class TestIncidentProcessing:
    """测试事件处理"""
    
    def test_process_fall_incident(self, orchestrator, fall_incident):
        """测试处理跌倒事件"""
        alert_response = orchestrator.process_incident(fall_incident)
        
        assert alert_response.incident_id == fall_incident.incident_id
        assert alert_response.severity == SeverityLevel.EMERGENCY
        assert alert_response.response_plan is not None
        assert alert_response.response_plan.status == ResponseStatus.INITIATED
    
    def test_process_incident_creates_response_plan(self, orchestrator, fall_incident):
        """测试处理事件创建响应计划"""
        alert_response = orchestrator.process_incident(fall_incident)
        response_plan = alert_response.response_plan
        
        assert response_plan.incident_id == fall_incident.incident_id
        assert response_plan.severity == SeverityLevel.EMERGENCY
        assert len(response_plan.protocols) > 0
        assert response_plan.initiated_at is not None
        assert response_plan.expected_completion > response_plan.initiated_at
    
    def test_emergency_response_timeout_is_5_seconds(self, orchestrator, fall_incident):
        """测试紧急响应超时时间为5秒（需求2.1）"""
        alert_response = orchestrator.process_incident(fall_incident)
        response_plan = alert_response.response_plan
        
        time_diff = (response_plan.expected_completion - response_plan.initiated_at).total_seconds()
        assert abs(time_diff - 5) < 1  # 5秒，允许1秒误差
    
    def test_alert_message_generation(self, orchestrator, fall_incident):
        """测试警报消息生成"""
        alert_response = orchestrator.process_incident(fall_incident)
        
        assert "紧急警报" in alert_response.message
        assert "跌倒" in alert_response.message
        assert fall_incident.user_id in alert_response.message
    
    def test_process_incident_stores_active_response(self, orchestrator, fall_incident):
        """测试处理事件存储活跃响应"""
        alert_response = orchestrator.process_incident(fall_incident)
        response_id = alert_response.response_plan.response_id
        
        tracked_response = orchestrator.track_response_status(response_id)
        assert tracked_response is not None
        assert tracked_response.response_id == response_id


class TestResponseCoordination:
    """测试响应协调"""
    
    def test_coordinate_response_updates_status(self, orchestrator, fall_incident):
        """测试协调响应更新状态"""
        alert_response = orchestrator.process_incident(fall_incident)
        
        response_plan = orchestrator.coordinate_response(alert_response)
        # 紧急事件包含语音确认，所以状态会是AWAITING_CONFIRMATION
        assert response_plan.status in [ResponseStatus.IN_PROGRESS, ResponseStatus.AWAITING_CONFIRMATION]
    
    def test_coordinate_response_executes_protocols(self, orchestrator, fall_incident):
        """测试协调响应执行协议"""
        alert_response = orchestrator.process_incident(fall_incident)
        
        response_plan = orchestrator.coordinate_response(alert_response)
        assert len(response_plan.actions_taken) > 0
    
    def test_voice_confirmation_sets_awaiting_status(self, orchestrator, fall_incident):
        """测试语音确认设置等待状态"""
        alert_response = orchestrator.process_incident(fall_incident)
        response_plan = orchestrator.coordinate_response(alert_response)
        
        # 紧急事件包含语音确认协议
        assert ResponseProtocol.VOICE_CONFIRMATION in response_plan.protocols
        # 状态应该是等待确认
        assert response_plan.status == ResponseStatus.AWAITING_CONFIRMATION


class TestResponseTracking:
    """测试响应跟踪"""
    
    def test_track_response_status(self, orchestrator, fall_incident):
        """测试跟踪响应状态"""
        alert_response = orchestrator.process_incident(fall_incident)
        response_id = alert_response.response_plan.response_id
        
        tracked_response = orchestrator.track_response_status(response_id)
        assert tracked_response is not None
        assert tracked_response.response_id == response_id
    
    def test_track_nonexistent_response(self, orchestrator):
        """测试跟踪不存在的响应"""
        tracked_response = orchestrator.track_response_status("nonexistent_id")
        assert tracked_response is None
    
    def test_update_response_status(self, orchestrator, fall_incident):
        """测试更新响应状态"""
        alert_response = orchestrator.process_incident(fall_incident)
        response_id = alert_response.response_plan.response_id
        
        success = orchestrator.update_response_status(
            response_id,
            ResponseStatus.CONFIRMED,
            {"confirmed_by": "user"}
        )
        assert success is True
        
        tracked_response = orchestrator.track_response_status(response_id)
        assert tracked_response.status == ResponseStatus.CONFIRMED
    
    def test_update_nonexistent_response(self, orchestrator):
        """测试更新不存在的响应"""
        success = orchestrator.update_response_status(
            "nonexistent_id",
            ResponseStatus.CONFIRMED
        )
        assert success is False
    
    def test_resolved_response_removed_from_active(self, orchestrator, fall_incident):
        """测试已解决的响应从活跃列表中移除"""
        alert_response = orchestrator.process_incident(fall_incident)
        response_id = alert_response.response_plan.response_id
        
        orchestrator.update_response_status(response_id, ResponseStatus.RESOLVED)
        
        tracked_response = orchestrator.track_response_status(response_id)
        assert tracked_response is None
    
    def test_cancelled_response_removed_from_active(self, orchestrator, fall_incident):
        """测试已取消的响应从活跃列表中移除"""
        alert_response = orchestrator.process_incident(fall_incident)
        response_id = alert_response.response_plan.response_id
        
        orchestrator.update_response_status(response_id, ResponseStatus.CANCELLED)
        
        tracked_response = orchestrator.track_response_status(response_id)
        assert tracked_response is None


class TestMultipleIncidents:
    """测试多个事件处理"""
    
    def test_get_active_responses(self, orchestrator, fall_incident, medication_incident):
        """测试获取所有活跃响应"""
        orchestrator.process_incident(fall_incident)
        orchestrator.process_incident(medication_incident)
        
        active_responses = orchestrator.get_active_responses()
        assert len(active_responses) == 2
    
    def test_get_response_by_incident(self, orchestrator, fall_incident):
        """测试根据事件ID获取响应"""
        alert_response = orchestrator.process_incident(fall_incident)
        
        response = orchestrator.get_response_by_incident(fall_incident.incident_id)
        assert response is not None
        assert response.incident_id == fall_incident.incident_id
    
    def test_get_response_by_nonexistent_incident(self, orchestrator):
        """测试获取不存在的事件响应"""
        response = orchestrator.get_response_by_incident("nonexistent_incident")
        assert response is None


class TestResponseTimeouts:
    """测试响应超时配置"""
    
    def test_low_severity_timeout(self, orchestrator, medication_incident):
        """测试低级别超时为1小时"""
        alert_response = orchestrator.process_incident(medication_incident)
        response_plan = alert_response.response_plan
        
        time_diff = (response_plan.expected_completion - response_plan.initiated_at).total_seconds()
        assert abs(time_diff - 3600) < 1  # 1小时，允许1秒误差
    
    def test_medium_severity_timeout(self, orchestrator):
        """测试中级别超时为15分钟"""
        incident = IncidentData(
            incident_id="incident_006",
            user_id="user_123",
            incident_type=IncidentType.ABNORMAL_MOVEMENT,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.MEDIUM,
            location=Location(latitude=39.9042, longitude=116.4074),
            sensor_data={},
            verification_status=VerificationStatus.PENDING
        )
        
        alert_response = orchestrator.process_incident(incident)
        response_plan = alert_response.response_plan
        
        time_diff = (response_plan.expected_completion - response_plan.initiated_at).total_seconds()
        assert abs(time_diff - 900) < 1  # 15分钟，允许1秒误差
    
    def test_high_severity_timeout(self, orchestrator):
        """测试高级别超时为5分钟"""
        incident = IncidentData(
            incident_id="incident_007",
            user_id="user_123",
            incident_type=IncidentType.PROLONGED_INACTIVITY,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.HIGH,
            location=Location(latitude=39.9042, longitude=116.4074),
            sensor_data={},
            verification_status=VerificationStatus.PENDING
        )
        
        alert_response = orchestrator.process_incident(incident)
        response_plan = alert_response.response_plan
        
        time_diff = (response_plan.expected_completion - response_plan.initiated_at).total_seconds()
        assert abs(time_diff - 300) < 1  # 5分钟，允许1秒误差
