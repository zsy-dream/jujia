"""
警报分类与响应的属性测试
Property-Based Tests for Alert Classification and Response

**验证需求：需求4.2**
需求4.2 - 当生成警报时，警报系统应当按严重程度分类（低、中、高、紧急）并配备相应的响应协议

**属性13：警报分类与响应**
对于任何警报生成，系统应当按严重程度分类警报（低、中、高、紧急）并为每个级别实施适当的响应协议
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import datetime, timedelta
from typing import Dict, Any

from app.services.alert_orchestrator import (
    AlertOrchestrator,
    ResponseProtocol,
    ResponseStatus
)
from app.schemas.core import (
    IncidentData,
    IncidentType,
    SeverityLevel,
    VerificationStatus,
    Location
)


# ============================================================================
# 策略定义 - Hypothesis Strategies
# ============================================================================

@st.composite
def location_strategy(draw):
    """生成有效的位置数据"""
    latitude = draw(st.floats(min_value=-90, max_value=90, allow_nan=False, allow_infinity=False))
    longitude = draw(st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False))
    address = draw(st.one_of(
        st.none(),
        st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',)))
    ))
    
    return Location(
        latitude=latitude,
        longitude=longitude,
        address=address
    )


@st.composite
def incident_data_strategy(draw):
    """生成任意有效的事件数据"""
    incident_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'
    )))
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'
    )))
    incident_type = draw(st.sampled_from(list(IncidentType)))
    
    # 生成合理的时间戳（过去30天内）
    days_ago = draw(st.integers(min_value=0, max_value=30))
    hours_ago = draw(st.integers(min_value=0, max_value=23))
    minutes_ago = draw(st.integers(min_value=0, max_value=59))
    timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
    
    severity = draw(st.one_of(st.none(), st.sampled_from(list(SeverityLevel))))
    location = draw(location_strategy())
    
    # 生成传感器数据
    sensor_data = draw(st.dictionaries(
        keys=st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_'
        )),
        values=st.one_of(
            st.booleans(),
            st.integers(min_value=-1000, max_value=1000),
            st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
            st.text(min_size=0, max_size=50)
        ),
        min_size=0,
        max_size=10
    ))
    
    verification_status = draw(st.sampled_from(list(VerificationStatus)))
    
    return IncidentData(
        incident_id=incident_id,
        user_id=user_id,
        incident_type=incident_type,
        timestamp=timestamp,
        severity=severity,
        location=location,
        sensor_data=sensor_data,
        verification_status=verification_status
    )


@st.composite
def context_strategy(draw):
    """生成可选的上下文数据"""
    has_context = draw(st.booleans())
    if not has_context:
        return None
    
    context = {}
    
    # 高风险医疗状况
    if draw(st.booleans()):
        context["high_risk_conditions"] = draw(st.booleans())
    
    # 最近相似事件数量
    if draw(st.booleans()):
        context["recent_similar_incidents"] = draw(st.integers(min_value=0, max_value=10))
    
    # 其他可能的上下文数据
    if draw(st.booleans()):
        context["user_age"] = draw(st.integers(min_value=60, max_value=100))
    
    if draw(st.booleans()):
        context["frailty_score"] = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
    
    return context if context else None


# ============================================================================
# 属性测试
# ============================================================================

class TestProperty13_AlertClassificationAndResponse:
    """
    **属性13：警报分类与响应**
    
    **验证需求：需求4.2**
    
    对于任何警报生成，系统应当按严重程度分类警报（低、中、高、紧急）
    并为每个级别实施适当的响应协议
    """
    
    @given(
        incident=incident_data_strategy(),
        context=context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_all_alerts_have_valid_severity_classification(self, incident, context):
        """
        属性：所有警报必须被分类为有效的严重程度级别
        
        对于任何事件输入，系统必须将其分类为四个严重程度级别之一：
        低、中、高、紧急
        """
        orchestrator = AlertOrchestrator()
        
        # 处理事件生成警报
        alert_response = orchestrator.process_incident(incident, context)
        
        # 验证：警报必须有有效的严重程度分类
        assert alert_response.severity in [
            SeverityLevel.LOW,
            SeverityLevel.MEDIUM,
            SeverityLevel.HIGH,
            SeverityLevel.EMERGENCY
        ], f"警报严重程度必须是有效的级别，但得到: {alert_response.severity}"
        
        # 验证：响应计划的严重程度必须与警报一致
        assert alert_response.response_plan.severity == alert_response.severity, \
            "响应计划的严重程度必须与警报严重程度一致"
    
    @given(
        incident=incident_data_strategy(),
        context=context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_all_severity_levels_have_response_protocols(self, incident, context):
        """
        属性：每个严重程度级别必须配备相应的响应协议
        
        对于任何警报，系统必须为其严重程度级别分配至少一个响应协议
        """
        orchestrator = AlertOrchestrator()
        
        # 处理事件生成警报
        alert_response = orchestrator.process_incident(incident, context)
        
        # 验证：响应计划必须包含至少一个协议
        assert len(alert_response.response_plan.protocols) > 0, \
            f"严重程度 {alert_response.severity} 必须有至少一个响应协议"
        
        # 验证：所有协议必须是有效的ResponseProtocol枚举值
        valid_protocols = set(ResponseProtocol)
        for protocol in alert_response.response_plan.protocols:
            assert protocol in valid_protocols, \
                f"协议 {protocol} 必须是有效的ResponseProtocol"
    
    @given(
        incident=incident_data_strategy(),
        context=context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_emergency_alerts_have_appropriate_protocols(self, incident, context):
        """
        属性：紧急级别警报必须包含紧急响应协议
        
        对于任何被分类为紧急的警报，必须包含语音确认、联系关爱圈和派遣紧急服务
        """
        orchestrator = AlertOrchestrator()
        
        # 处理事件生成警报
        alert_response = orchestrator.process_incident(incident, context)
        
        # 如果是紧急级别，验证必须包含关键协议
        if alert_response.severity == SeverityLevel.EMERGENCY:
            protocols = alert_response.response_plan.protocols
            
            assert ResponseProtocol.VOICE_CONFIRMATION in protocols, \
                "紧急警报必须包含语音确认协议"
            assert ResponseProtocol.CONTACT_CARE_CIRCLE in protocols, \
                "紧急警报必须包含联系关爱圈协议"
            assert ResponseProtocol.DISPATCH_EMERGENCY in protocols, \
                "紧急警报必须包含派遣紧急服务协议"
    
    @given(
        incident=incident_data_strategy(),
        context=context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_high_severity_alerts_have_appropriate_protocols(self, incident, context):
        """
        属性：高级别警报必须包含适当的响应协议
        
        对于任何被分类为高级的警报，必须包含语音确认、通知家属和联系关爱圈
        """
        orchestrator = AlertOrchestrator()
        
        # 处理事件生成警报
        alert_response = orchestrator.process_incident(incident, context)
        
        # 如果是高级别，验证必须包含关键协议
        if alert_response.severity == SeverityLevel.HIGH:
            protocols = alert_response.response_plan.protocols
            
            assert ResponseProtocol.VOICE_CONFIRMATION in protocols, \
                "高级警报必须包含语音确认协议"
            assert ResponseProtocol.NOTIFY_FAMILY in protocols, \
                "高级警报必须包含通知家属协议"
            assert ResponseProtocol.CONTACT_CARE_CIRCLE in protocols, \
                "高级警报必须包含联系关爱圈协议"
    
    @given(
        incident=incident_data_strategy(),
        context=context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_medium_severity_alerts_have_appropriate_protocols(self, incident, context):
        """
        属性：中级别警报必须包含适当的响应协议
        
        对于任何被分类为中级的警报，必须包含监控、通知家属和语音确认
        """
        orchestrator = AlertOrchestrator()
        
        # 处理事件生成警报
        alert_response = orchestrator.process_incident(incident, context)
        
        # 如果是中级别，验证必须包含关键协议
        if alert_response.severity == SeverityLevel.MEDIUM:
            protocols = alert_response.response_plan.protocols
            
            assert ResponseProtocol.MONITOR in protocols, \
                "中级警报必须包含监控协议"
            assert ResponseProtocol.NOTIFY_FAMILY in protocols, \
                "中级警报必须包含通知家属协议"
            assert ResponseProtocol.VOICE_CONFIRMATION in protocols, \
                "中级警报必须包含语音确认协议"
    
    @given(
        incident=incident_data_strategy(),
        context=context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_low_severity_alerts_have_appropriate_protocols(self, incident, context):
        """
        属性：低级别警报必须包含适当的响应协议
        
        对于任何被分类为低级的警报，必须包含监控和通知家属
        """
        orchestrator = AlertOrchestrator()
        
        # 处理事件生成警报
        alert_response = orchestrator.process_incident(incident, context)
        
        # 如果是低级别，验证必须包含关键协议
        if alert_response.severity == SeverityLevel.LOW:
            protocols = alert_response.response_plan.protocols
            
            assert ResponseProtocol.MONITOR in protocols, \
                "低级警报必须包含监控协议"
            assert ResponseProtocol.NOTIFY_FAMILY in protocols, \
                "低级警报必须包含通知家属协议"
    
    @given(
        incident=incident_data_strategy(),
        context=context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_response_plan_has_valid_timeouts(self, incident, context):
        """
        属性：所有响应计划必须有有效的超时时间
        
        对于任何警报，响应计划的预期完成时间必须在启动时间之后，
        并且超时时间必须与严重程度级别相匹配
        """
        orchestrator = AlertOrchestrator()
        
        # 处理事件生成警报
        alert_response = orchestrator.process_incident(incident, context)
        response_plan = alert_response.response_plan
        
        # 验证：预期完成时间必须在启动时间之后
        assert response_plan.expected_completion > response_plan.initiated_at, \
            "预期完成时间必须在启动时间之后"
        
        # 计算超时时间（秒）
        timeout_seconds = (response_plan.expected_completion - response_plan.initiated_at).total_seconds()
        
        # 验证：超时时间必须为正数
        assert timeout_seconds > 0, "超时时间必须为正数"
        
        # 验证：超时时间必须与严重程度匹配
        expected_timeouts = {
            SeverityLevel.LOW: 3600,  # 1小时
            SeverityLevel.MEDIUM: 900,  # 15分钟
            SeverityLevel.HIGH: 300,  # 5分钟
            SeverityLevel.EMERGENCY: 5,  # 5秒
        }
        
        expected_timeout = expected_timeouts[response_plan.severity]
        # 允许2秒的误差（考虑处理时间）
        assert abs(timeout_seconds - expected_timeout) < 2, \
            f"严重程度 {response_plan.severity} 的超时时间应该约为 {expected_timeout} 秒，但得到 {timeout_seconds} 秒"
    
    @given(
        incident=incident_data_strategy(),
        context=context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_response_plan_initialization_is_consistent(self, incident, context):
        """
        属性：响应计划初始化必须一致
        
        对于任何警报，响应计划必须以INITIATED状态开始，
        并且必须有唯一的响应ID和警报ID
        """
        orchestrator = AlertOrchestrator()
        
        # 处理事件生成警报
        alert_response = orchestrator.process_incident(incident, context)
        response_plan = alert_response.response_plan
        
        # 验证：初始状态必须是INITIATED
        assert response_plan.status == ResponseStatus.INITIATED, \
            "响应计划初始状态必须是INITIATED"
        
        # 验证：响应ID和警报ID必须存在且不为空
        assert response_plan.response_id, "响应ID不能为空"
        assert alert_response.alert_id, "警报ID不能为空"
        
        # 验证：响应ID和警报ID必须不同
        assert response_plan.response_id != alert_response.alert_id, \
            "响应ID和警报ID必须不同"
        
        # 验证：事件ID必须匹配
        assert response_plan.incident_id == incident.incident_id, \
            "响应计划的事件ID必须与原始事件ID匹配"
        assert alert_response.incident_id == incident.incident_id, \
            "警报响应的事件ID必须与原始事件ID匹配"
    
    @given(
        incident=incident_data_strategy(),
        context=context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_severity_classification_is_deterministic(self, incident, context):
        """
        属性：严重程度分类必须是确定性的
        
        对于相同的事件和上下文，多次分类应该产生相同的结果
        """
        orchestrator = AlertOrchestrator()
        
        # 第一次分类
        severity1 = orchestrator.classify_severity(incident, context)
        
        # 第二次分类
        severity2 = orchestrator.classify_severity(incident, context)
        
        # 验证：两次分类结果必须相同
        assert severity1 == severity2, \
            "相同的事件和上下文应该产生相同的严重程度分类"
    
    @given(
        incident=incident_data_strategy(),
        context=context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_alert_message_is_generated(self, incident, context):
        """
        属性：所有警报必须生成消息
        
        对于任何警报，必须生成非空的警报消息
        """
        orchestrator = AlertOrchestrator()
        
        # 处理事件生成警报
        alert_response = orchestrator.process_incident(incident, context)
        
        # 验证：警报消息必须存在且不为空
        assert alert_response.message, "警报消息不能为空"
        assert len(alert_response.message) > 0, "警报消息必须包含内容"
        
        # 验证：警报消息必须包含用户ID
        assert incident.user_id in alert_response.message, \
            "警报消息必须包含用户ID"
    
    @given(
        incident=incident_data_strategy(),
        context=context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_response_can_be_tracked(self, incident, context):
        """
        属性：所有响应必须可以被跟踪
        
        对于任何生成的警报，其响应计划必须可以通过响应ID进行跟踪
        """
        orchestrator = AlertOrchestrator()
        
        # 处理事件生成警报
        alert_response = orchestrator.process_incident(incident, context)
        response_id = alert_response.response_plan.response_id
        
        # 验证：可以通过响应ID跟踪响应
        tracked_response = orchestrator.track_response_status(response_id)
        assert tracked_response is not None, "必须能够跟踪响应"
        assert tracked_response.response_id == response_id, \
            "跟踪到的响应ID必须匹配"
        
        # 验证：可以通过事件ID获取响应
        response_by_incident = orchestrator.get_response_by_incident(incident.incident_id)
        assert response_by_incident is not None, "必须能够通过事件ID获取响应"
        assert response_by_incident.incident_id == incident.incident_id, \
            "获取到的响应的事件ID必须匹配"
    
    @given(
        incident=incident_data_strategy(),
        context=context_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_context_affects_severity_appropriately(self, incident, context):
        """
        属性：上下文应该适当地影响严重程度
        
        对于任何事件，有高风险上下文的分类严重程度应该
        大于或等于没有上下文的分类严重程度
        """
        orchestrator = AlertOrchestrator()
        
        # 无上下文的分类
        severity_no_context = orchestrator.classify_severity(incident, None)
        
        # 有上下文的分类
        severity_with_context = orchestrator.classify_severity(incident, context)
        
        # 定义严重程度顺序
        severity_order = {
            SeverityLevel.LOW: 0,
            SeverityLevel.MEDIUM: 1,
            SeverityLevel.HIGH: 2,
            SeverityLevel.EMERGENCY: 3
        }
        
        # 如果上下文包含高风险因素，严重程度应该不会降低
        if context and (
            context.get("high_risk_conditions") or 
            context.get("recent_similar_incidents", 0) > 2
        ):
            assert severity_order[severity_with_context] >= severity_order[severity_no_context], \
                "高风险上下文不应该降低严重程度"


# ============================================================================
# 边缘情况测试
# ============================================================================

class TestAlertClassificationEdgeCases:
    """测试警报分类的边缘情况"""
    
    def test_fall_incident_always_emergency(self):
        """跌倒事件应该始终被分类为紧急"""
        orchestrator = AlertOrchestrator()
        
        incident = IncidentData(
            incident_id="fall_001",
            user_id="user_123",
            incident_type=IncidentType.FALL,
            timestamp=datetime.utcnow(),
            severity=None,  # 即使没有预设严重程度
            location=Location(latitude=0, longitude=0),
            sensor_data={},
            verification_status=VerificationStatus.PENDING
        )
        
        alert_response = orchestrator.process_incident(incident)
        assert alert_response.severity == SeverityLevel.EMERGENCY
    
    def test_medical_emergency_always_emergency(self):
        """医疗紧急情况应该始终被分类为紧急"""
        orchestrator = AlertOrchestrator()
        
        incident = IncidentData(
            incident_id="medical_001",
            user_id="user_123",
            incident_type=IncidentType.MEDICAL_EMERGENCY,
            timestamp=datetime.utcnow(),
            severity=None,
            location=Location(latitude=0, longitude=0),
            sensor_data={},
            verification_status=VerificationStatus.PENDING
        )
        
        alert_response = orchestrator.process_incident(incident)
        assert alert_response.severity == SeverityLevel.EMERGENCY
    
    def test_empty_sensor_data_does_not_break_classification(self):
        """空传感器数据不应该破坏分类"""
        orchestrator = AlertOrchestrator()
        
        incident = IncidentData(
            incident_id="empty_001",
            user_id="user_123",
            incident_type=IncidentType.ABNORMAL_MOVEMENT,
            timestamp=datetime.utcnow(),
            severity=None,
            location=Location(latitude=0, longitude=0),
            sensor_data={},  # 空传感器数据
            verification_status=VerificationStatus.PENDING
        )
        
        alert_response = orchestrator.process_incident(incident)
        assert alert_response.severity in [
            SeverityLevel.LOW, SeverityLevel.MEDIUM, 
            SeverityLevel.HIGH, SeverityLevel.EMERGENCY
        ]
    
    def test_extreme_location_coordinates(self):
        """极端位置坐标不应该破坏分类"""
        orchestrator = AlertOrchestrator()
        
        incident = IncidentData(
            incident_id="location_001",
            user_id="user_123",
            incident_type=IncidentType.FALL,
            timestamp=datetime.utcnow(),
            severity=None,
            location=Location(latitude=90, longitude=180),  # 极端坐标
            sensor_data={},
            verification_status=VerificationStatus.PENDING
        )
        
        alert_response = orchestrator.process_incident(incident)
        assert alert_response.severity == SeverityLevel.EMERGENCY
