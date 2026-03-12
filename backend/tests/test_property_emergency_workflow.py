"""
紧急响应工作流的属性测试
Property-Based Tests for Emergency Response Workflow

**验证需求：需求2.1, 2.2, 2.3**
需求2.1 - 当通过骨骼分析检测到跌倒时，系统应当在5秒内触发紧急协议
需求2.2 - 当检测到紧急情况时，警报系统应当在升级前尝试与用户进行AI语音确认
需求2.3 - 如果用户在30秒内未响应语音确认,那么系统应当自动联系关爱圈

**属性5：紧急响应工作流**
对于任何跌倒检测事件，系统应当在5秒内触发紧急协议，尝试AI语音确认，
如果30秒内未收到响应则升级联系关爱圈
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import datetime, timedelta
from typing import Dict, Any, List
import time

from app.services.emergency_dispatcher import (
    EmergencyDispatcher,
    DispatchStatus,
    ContactMethod,
    VoiceConfirmationRequest,
    ContactResult,
    EmergencyPackage,
    DispatchResult
)
from app.services.alert_orchestrator import AlertOrchestrator
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
def emergency_contact_strategy(draw):
    """生成有效的紧急联系人"""
    name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'), whitelist_characters=' '
    )))
    relationship = draw(st.sampled_from(["儿子", "女儿", "配偶", "护理人员", "朋友", "邻居"]))
    phone = draw(st.text(min_size=11, max_size=11, alphabet=st.characters(whitelist_categories=('Nd',))))
    email = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='@._-'
    )))
    priority = draw(st.integers(min_value=1, max_value=10))
    
    return EmergencyContact(
        name=name,
        relationship=relationship,
        phone=phone,
        email=email,
        priority=priority
    )


@st.composite
def medical_condition_strategy(draw):
    """生成有效的医疗状况"""
    condition_name = draw(st.sampled_from([
        "高血压", "糖尿病", "心脏病", "骨质疏松", "关节炎", "阿尔茨海默病"
    ]))
    days_ago = draw(st.integers(min_value=30, max_value=3650))
    diagnosed_date = datetime.utcnow() - timedelta(days=days_ago)
    severity = draw(st.sampled_from(["mild", "moderate", "severe"]))
    notes = draw(st.text(min_size=0, max_size=100))
    
    return MedicalCondition(
        condition_name=condition_name,
        diagnosed_date=diagnosed_date,
        severity=severity,
        notes=notes
    )


@st.composite
def user_profile_strategy(draw):
    """生成任意有效的用户档案"""
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'
    )))
    age = draw(st.integers(min_value=60, max_value=100))
    
    # 生成1-5个医疗状况
    num_conditions = draw(st.integers(min_value=0, max_value=5))
    medical_conditions = [draw(medical_condition_strategy()) for _ in range(num_conditions)]
    
    # 生成0-2个移动辅助设备
    num_aids = draw(st.integers(min_value=0, max_value=2))
    mobility_aids = []
    for _ in range(num_aids):
        aid_type = draw(st.sampled_from(["walker", "cane", "wheelchair"]))
        days_ago = draw(st.integers(min_value=1, max_value=1825))
        start_date = datetime.utcnow() - timedelta(days=days_ago)
        mobility_aids.append(MobilityAid(aid_type=aid_type, start_date=start_date, notes=""))
    
    # 生成1-5个紧急联系人
    num_contacts = draw(st.integers(min_value=1, max_value=5))
    emergency_contacts = [draw(emergency_contact_strategy()) for _ in range(num_contacts)]
    
    # 确保优先级唯一
    for i, contact in enumerate(emergency_contacts):
        contact.priority = i + 1
    
    care_preferences = CarePreferences(
        preferred_language="zh-CN",
        voice_confirmation_enabled=True,
        emergency_auto_escalation=draw(st.booleans())
    )
    
    baseline_metrics = BaselineMetrics(
        average_daily_steps=draw(st.integers(min_value=500, max_value=10000)),
        average_sleep_hours=draw(st.floats(min_value=4.0, max_value=12.0, allow_nan=False, allow_infinity=False)),
        typical_activity_periods=[(8, 12), (14, 18)],
        baseline_mobility_score=draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
    )
    
    return UserProfile(
        user_id=user_id,
        age=age,
        medical_conditions=medical_conditions,
        mobility_aids=mobility_aids,
        emergency_contacts=emergency_contacts,
        care_preferences=care_preferences,
        baseline_metrics=baseline_metrics
    )


@st.composite
def fall_incident_strategy(draw):
    """生成任意有效的跌倒事件"""
    incident_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'
    )))
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'
    )))
    
    # 跌倒事件应该是最近发生的（过去5分钟内）
    seconds_ago = draw(st.integers(min_value=0, max_value=300))
    timestamp = datetime.utcnow() - timedelta(seconds=seconds_ago)
    
    location = draw(location_strategy())
    
    # 跌倒事件的传感器数据
    sensor_data = {
        "fall_detected": True,
        "impact_force": draw(st.floats(min_value=5.0, max_value=15.0, allow_nan=False, allow_infinity=False)),
        "user_immobile": draw(st.booleans())
    }
    
    verification_status = draw(st.sampled_from([
        VerificationStatus.PENDING,
        VerificationStatus.CONFIRMED
    ]))
    
    return IncidentData(
        incident_id=incident_id,
        user_id=user_id,
        incident_type=IncidentType.FALL,
        timestamp=timestamp,
        severity=SeverityLevel.EMERGENCY,  # 跌倒总是紧急
        location=location,
        sensor_data=sensor_data,
        verification_status=verification_status
    )


# ============================================================================
# 属性测试
# ============================================================================

class TestProperty5_EmergencyResponseWorkflow:
    """
    **属性5：紧急响应工作流**
    
    **验证需求：需求2.1, 2.2, 2.3**
    
    对于任何跌倒检测事件，系统应当在5秒内触发紧急协议，
    尝试AI语音确认，如果30秒内未收到响应则升级联系关爱圈
    """
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_emergency_protocol_triggered_within_5_seconds(self, fall_incident, user_profile):
        """
        属性：跌倒检测必须在5秒内触发紧急协议（需求2.1）
        
        对于任何跌倒事件，系统必须在5秒内启动紧急响应工作流
        """
        dispatcher = EmergencyDispatcher()
        
        # 记录开始时间
        start_time = time.time()
        
        # 启动紧急响应
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        # 记录结束时间
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 验证：必须在5秒内完成（需求2.1）
        assert elapsed_time < 5.0, \
            f"紧急协议必须在5秒内触发，但用时 {elapsed_time:.2f} 秒"
        
        # 验证：调度已启动
        assert dispatch_result is not None, "必须返回调度结果"
        assert dispatch_result.status == DispatchStatus.INITIATED, \
            "调度状态必须是INITIATED"
        assert dispatch_result.incident_id == fall_incident.incident_id, \
            "调度的事件ID必须匹配"
        
        # 验证：监控已激活（需求2.5）
        assert dispatch_result.monitoring_active is True, \
            "紧急响应期间必须激活持续监控"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_voice_confirmation_sent_for_all_emergencies(self, fall_incident, user_profile):
        """
        属性：所有紧急情况必须发送AI语音确认（需求2.2）
        
        对于任何跌倒事件，系统必须尝试与用户进行AI语音确认
        """
        dispatcher = EmergencyDispatcher()
        
        # 启动紧急响应
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        # 发送语音确认
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        # 验证：语音确认已发送
        assert voice_confirmation is not None, "必须发送语音确认"
        assert voice_confirmation.user_id == user_profile.user_id, \
            "语音确认的用户ID必须匹配"
        assert voice_confirmation.incident_id == fall_incident.incident_id, \
            "语音确认的事件ID必须匹配"
        
        # 验证：语音确认消息已生成
        assert voice_confirmation.message, "必须生成语音确认消息"
        assert len(voice_confirmation.message) > 0, "语音确认消息不能为空"
        
        # 验证：调度状态已更新
        assert dispatch_result.status == DispatchStatus.VOICE_CONFIRMATION_SENT, \
            "发送语音确认后状态必须更新为VOICE_CONFIRMATION_SENT"
        assert dispatch_result.voice_confirmation is not None, \
            "调度结果必须包含语音确认对象"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_voice_confirmation_timeout_is_30_seconds(self, fall_incident, user_profile):
        """
        属性：语音确认超时必须是30秒（需求2.2）
        
        对于任何语音确认请求，超时时间必须设置为30秒
        """
        dispatcher = EmergencyDispatcher()
        
        # 启动紧急响应并发送语音确认
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        # 验证：超时时间必须是30秒（需求2.2）
        assert voice_confirmation.timeout_seconds == 30, \
            f"语音确认超时必须是30秒，但得到 {voice_confirmation.timeout_seconds} 秒"
        
        # 验证：过期时间计算正确
        expected_expires_at = voice_confirmation.initiated_at + timedelta(seconds=30)
        time_diff = abs((voice_confirmation.expires_at - expected_expires_at).total_seconds())
        assert time_diff < 1, \
            f"过期时间计算错误，差异 {time_diff:.2f} 秒"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_care_circle_contacted_after_no_response(self, fall_incident, user_profile):
        """
        属性：30秒无响应后必须联系关爱圈（需求2.3）
        
        对于任何语音确认超时的情况，系统必须自动联系关爱圈
        """
        dispatcher = EmergencyDispatcher()
        
        # 启动紧急响应并发送语音确认
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        # 模拟30秒超时（手动设置过期时间为过去）
        voice_confirmation.expires_at = datetime.utcnow() - timedelta(seconds=1)
        
        # 检查超时
        is_timeout = dispatcher.check_voice_confirmation_timeout(voice_confirmation.request_id)
        assert is_timeout is True, "30秒后必须检测到超时"
        
        # 联系关爱圈
        contact_results = dispatcher.contact_care_circle(
            dispatch_result.dispatch_id,
            user_profile.emergency_contacts,
            fall_incident
        )
        
        # 验证：关爱圈已联系（需求2.3）
        assert len(contact_results) > 0, "必须尝试联系关爱圈"
        assert dispatch_result.status == DispatchStatus.CARE_CIRCLE_CONTACTED, \
            "联系关爱圈后状态必须更新为CARE_CIRCLE_CONTACTED"
        
        # 验证：至少尝试联系一个紧急联系人
        assert len(contact_results) >= len(user_profile.emergency_contacts), \
            "必须尝试联系所有紧急联系人"
        
        # 验证：联系结果已存储
        assert dispatch_result.care_circle_contacts == contact_results, \
            "联系结果必须存储在调度结果中"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_care_circle_contacted_by_priority(self, fall_incident, user_profile):
        """
        属性：关爱圈必须按优先级联系
        
        对于任何关爱圈联系请求，必须按照优先级顺序联系紧急联系人
        """
        # 确保有多个联系人
        assume(len(user_profile.emergency_contacts) >= 2)
        
        dispatcher = EmergencyDispatcher()
        
        # 启动紧急响应
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        # 联系关爱圈
        contact_results = dispatcher.contact_care_circle(
            dispatch_result.dispatch_id,
            user_profile.emergency_contacts,
            fall_incident
        )
        
        # 验证：联系顺序按优先级
        # 获取第一个被联系的人的名字
        first_contact_name = contact_results[0].contact_name
        
        # 找到优先级最高的联系人（优先级数字最小）
        highest_priority_contact = min(user_profile.emergency_contacts, key=lambda c: c.priority)
        
        # 验证：第一个被联系的应该是优先级最高的
        assert first_contact_name == highest_priority_contact.name, \
            f"应该首先联系优先级最高的联系人 {highest_priority_contact.name}，但首先联系了 {first_contact_name}"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_user_response_prevents_escalation(self, fall_incident, user_profile):
        """
        属性：用户响应必须阻止升级
        
        对于任何在30秒内收到用户响应的情况，不应该自动联系关爱圈
        """
        dispatcher = EmergencyDispatcher()
        
        # 启动紧急响应并发送语音确认
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        # 用户在超时前响应
        success = dispatcher.record_voice_response(
            voice_confirmation.request_id,
            "我很好"
        )
        
        # 验证：响应已记录
        assert success is True, "必须成功记录用户响应"
        assert voice_confirmation.response_received is True, \
            "语音确认必须标记为已收到响应"
        assert voice_confirmation.response_text == "我很好", \
            "响应文本必须匹配"
        
        # 验证：调度状态已更新
        assert dispatch_result.status == DispatchStatus.USER_RESPONDED, \
            "收到用户响应后状态必须更新为USER_RESPONDED"
        
        # 验证：即使过期时间已过，因为已收到响应，不应该超时
        voice_confirmation.expires_at = datetime.utcnow() - timedelta(seconds=1)
        is_timeout = dispatcher.check_voice_confirmation_timeout(voice_confirmation.request_id)
        assert is_timeout is False, \
            "收到用户响应后，即使过期时间已过也不应该超时"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_emergency_package_created_with_complete_info(self, fall_incident, user_profile):
        """
        属性：紧急信息包必须包含完整信息（需求2.4）
        
        对于任何紧急情况，必须创建包含位置、病史和事件详情的完整信息包
        """
        dispatcher = EmergencyDispatcher()
        
        # 确保事件的user_id与用户档案匹配
        fall_incident.user_id = user_profile.user_id
        
        # 创建紧急信息包
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        # 验证：信息包已创建
        assert package is not None, "必须创建紧急信息包"
        assert package.user_id == user_profile.user_id, "用户ID必须匹配"
        assert package.incident == fall_incident, "事件必须匹配"
        
        # 验证：位置信息完整（需求2.4）
        assert package.location == fall_incident.location, "位置信息必须匹配"
        assert package.location.latitude == fall_incident.location.latitude, \
            "纬度必须匹配"
        assert package.location.longitude == fall_incident.location.longitude, \
            "经度必须匹配"
        
        # 验证：病史信息完整（需求2.4）
        assert "medical_conditions" in package.medical_history, \
            "必须包含医疗状况"
        assert "age" in package.medical_history, "必须包含年龄"
        assert package.medical_history["age"] == user_profile.age, \
            "年龄必须匹配"
        assert len(package.medical_history["medical_conditions"]) == len(user_profile.medical_conditions), \
            "医疗状况数量必须匹配"
        
        # 验证：事件详情完整（需求2.4）
        assert "incident_type" in package.event_details, "必须包含事件类型"
        assert "severity" in package.event_details, "必须包含严重程度"
        assert "timestamp" in package.event_details, "必须包含时间戳"
        assert "sensor_data" in package.event_details, "必须包含传感器数据"
        assert package.event_details["incident_type"] == fall_incident.incident_type.value, \
            "事件类型必须匹配"
        
        # 验证：紧急联系人完整
        assert len(package.emergency_contacts) == len(user_profile.emergency_contacts), \
            "紧急联系人数量必须匹配"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_emergency_package_serializable(self, fall_incident, user_profile):
        """
        属性：紧急信息包必须可序列化
        
        对于任何紧急信息包，必须能够转换为字典格式用于传输
        """
        dispatcher = EmergencyDispatcher()
        
        # 创建紧急信息包
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        # 转换为字典
        package_dict = package.to_dict()
        
        # 验证：所有必需字段存在
        required_fields = [
            "package_id", "user_id", "incident", "location",
            "medical_history", "event_details", "emergency_contacts", "created_at"
        ]
        for field in required_fields:
            assert field in package_dict, f"紧急信息包必须包含字段: {field}"
        
        # 验证：字段类型正确
        assert isinstance(package_dict["incident"], dict), "事件必须是字典"
        assert isinstance(package_dict["location"], dict), "位置必须是字典"
        assert isinstance(package_dict["medical_history"], dict), "病史必须是字典"
        assert isinstance(package_dict["event_details"], dict), "事件详情必须是字典"
        assert isinstance(package_dict["emergency_contacts"], list), "紧急联系人必须是列表"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_monitoring_active_throughout_emergency(self, fall_incident, user_profile):
        """
        属性：紧急响应期间必须保持持续监控（需求2.5）
        
        对于任何紧急响应，从启动到解决期间必须保持监控激活
        """
        dispatcher = EmergencyDispatcher()
        
        # 启动紧急响应
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        # 验证：监控已激活
        assert dispatch_result.monitoring_active is True, \
            "启动紧急响应时必须激活监控"
        
        # 发送语音确认
        dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        # 验证：监控仍然激活
        assert dispatch_result.monitoring_active is True, \
            "发送语音确认后监控必须保持激活"
        
        # 更新监控状态
        success = dispatcher.update_monitoring_status(
            dispatch_result.dispatch_id,
            {"status": "monitoring", "vital_signs": "stable"}
        )
        
        # 验证：监控状态更新成功
        assert success is True, "必须能够更新监控状态"
        assert dispatch_result.status == DispatchStatus.MONITORING, \
            "更新监控状态后状态必须是MONITORING"
        assert dispatch_result.monitoring_active is True, \
            "更新监控状态后监控必须保持激活"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_monitoring_stops_on_resolution(self, fall_incident, user_profile):
        """
        属性：解决调度时监控必须停止
        
        对于任何解决的紧急响应，监控必须停止
        """
        dispatcher = EmergencyDispatcher()
        
        # 启动紧急响应
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        
        # 验证：监控已激活
        assert dispatch_result.monitoring_active is True
        
        # 解决调度
        success = dispatcher.resolve_dispatch(
            dispatch_result.dispatch_id,
            {"resolution": "user_confirmed_safe"}
        )
        
        # 验证：解决成功
        assert success is True, "必须能够解决调度"
        assert dispatch_result.status == DispatchStatus.RESOLVED, \
            "解决后状态必须是RESOLVED"
        
        # 验证：监控已停止
        assert dispatch_result.monitoring_active is False, \
            "解决调度后监控必须停止"
        
        # 验证：调度已从活跃列表中移除
        retrieved = dispatcher.get_dispatch_status(dispatch_result.dispatch_id)
        assert retrieved is None, \
            "解决的调度必须从活跃列表中移除"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_complete_workflow_no_response_scenario(self, fall_incident, user_profile):
        """
        属性：完整工作流（无响应场景）必须正确执行
        
        对于任何跌倒事件，如果用户未响应，必须完整执行：
        1. 5秒内触发紧急协议
        2. 发送语音确认（30秒超时）
        3. 超时后联系关爱圈
        4. 保持持续监控
        """
        dispatcher = EmergencyDispatcher()
        
        # 步骤1：启动紧急响应（必须在5秒内）
        start_time = time.time()
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        elapsed = time.time() - start_time
        
        assert elapsed < 5.0, f"必须在5秒内触发，但用时 {elapsed:.2f} 秒"
        assert dispatch_result.status == DispatchStatus.INITIATED
        assert dispatch_result.monitoring_active is True
        
        # 步骤2：发送语音确认（30秒超时）
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        assert voice_confirmation.timeout_seconds == 30
        assert dispatch_result.status == DispatchStatus.VOICE_CONFIRMATION_SENT
        
        # 步骤3：模拟30秒超时
        voice_confirmation.expires_at = datetime.utcnow() - timedelta(seconds=1)
        is_timeout = dispatcher.check_voice_confirmation_timeout(voice_confirmation.request_id)
        assert is_timeout is True
        
        # 步骤4：联系关爱圈
        contact_results = dispatcher.contact_care_circle(
            dispatch_result.dispatch_id,
            user_profile.emergency_contacts,
            fall_incident
        )
        
        assert len(contact_results) > 0
        assert dispatch_result.status == DispatchStatus.CARE_CIRCLE_CONTACTED
        
        # 步骤5：验证持续监控
        assert dispatch_result.monitoring_active is True
        
        # 验证：所有状态更新已记录
        assert len(dispatch_result.status_updates) >= 3, \
            "必须记录所有关键状态更新"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_complete_workflow_user_response_scenario(self, fall_incident, user_profile):
        """
        属性：完整工作流（用户响应场景）必须正确执行
        
        对于任何跌倒事件，如果用户响应，必须：
        1. 触发紧急协议
        2. 发送语音确认
        3. 记录用户响应
        4. 不升级到关爱圈
        5. 可以取消调度
        """
        dispatcher = EmergencyDispatcher()
        
        # 步骤1：启动紧急响应
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        assert dispatch_result.status == DispatchStatus.INITIATED
        
        # 步骤2：发送语音确认
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        assert dispatch_result.status == DispatchStatus.VOICE_CONFIRMATION_SENT
        
        # 步骤3：用户响应
        success = dispatcher.record_voice_response(
            voice_confirmation.request_id,
            "我很好"
        )
        
        assert success is True
        assert voice_confirmation.response_received is True
        assert dispatch_result.status == DispatchStatus.USER_RESPONDED
        
        # 步骤4：验证不会超时（即使过期时间已过）
        voice_confirmation.expires_at = datetime.utcnow() - timedelta(seconds=1)
        is_timeout = dispatcher.check_voice_confirmation_timeout(voice_confirmation.request_id)
        assert is_timeout is False, "用户响应后不应该超时"
        
        # 步骤5：取消调度
        cancel_success = dispatcher.cancel_dispatch(
            dispatch_result.dispatch_id,
            "user_confirmed_safe"
        )
        
        assert cancel_success is True
        assert dispatch_result.status == DispatchStatus.CANCELLED
        assert dispatch_result.monitoring_active is False
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_dispatch_has_unique_identifiers(self, fall_incident, user_profile):
        """
        属性：每个调度必须有唯一标识符
        
        对于任何紧急响应，调度ID、语音确认ID和信息包ID必须唯一
        """
        dispatcher = EmergencyDispatcher()
        
        # 创建第一个调度
        dispatch1 = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        voice1 = dispatcher.send_voice_confirmation(
            dispatch1.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        package1 = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        # 创建第二个调度（使用不同的事件ID）
        fall_incident2 = IncidentData(
            incident_id=fall_incident.incident_id + "_2",
            user_id=fall_incident.user_id,
            incident_type=IncidentType.FALL,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.EMERGENCY,
            location=fall_incident.location,
            sensor_data=fall_incident.sensor_data,
            verification_status=fall_incident.verification_status
        )
        
        dispatch2 = dispatcher.initiate_emergency_response(fall_incident2, user_profile)
        voice2 = dispatcher.send_voice_confirmation(
            dispatch2.dispatch_id,
            user_profile.user_id,
            fall_incident2
        )
        package2 = dispatcher.create_emergency_package(fall_incident2, user_profile)
        
        # 验证：所有ID必须唯一
        assert dispatch1.dispatch_id != dispatch2.dispatch_id, \
            "调度ID必须唯一"
        assert voice1.request_id != voice2.request_id, \
            "语音确认ID必须唯一"
        assert package1.package_id != package2.package_id, \
            "信息包ID必须唯一"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_status_updates_recorded_chronologically(self, fall_incident, user_profile):
        """
        属性：状态更新必须按时间顺序记录
        
        对于任何紧急响应，所有状态更新必须按时间顺序记录
        """
        dispatcher = EmergencyDispatcher()
        
        # 执行工作流
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        dispatcher.update_monitoring_status(
            dispatch_result.dispatch_id,
            {"status": "monitoring"}
        )
        
        # 验证：状态更新已记录
        assert len(dispatch_result.status_updates) >= 3, \
            "必须记录所有状态更新"
        
        # 验证：时间戳按顺序递增
        timestamps = [update["timestamp"] for update in dispatch_result.status_updates]
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i + 1], \
                "状态更新时间戳必须按时间顺序递增"
    
    @given(
        fall_incident=fall_incident_strategy(),
        user_profile=user_profile_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_emergency_workflow_never_raises_exception(self, fall_incident, user_profile):
        """
        属性：紧急工作流必须永不抛出异常
        
        对于任何有效的输入，紧急响应工作流必须优雅地处理所有情况
        """
        dispatcher = EmergencyDispatcher()
        
        try:
            # 执行完整工作流
            dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
            assert dispatch_result is not None
            
            voice_confirmation = dispatcher.send_voice_confirmation(
                dispatch_result.dispatch_id,
                user_profile.user_id,
                fall_incident
            )
            assert voice_confirmation is not None
            
            package = dispatcher.create_emergency_package(fall_incident, user_profile)
            assert package is not None
            
            contact_results = dispatcher.contact_care_circle(
                dispatch_result.dispatch_id,
                user_profile.emergency_contacts,
                fall_incident
            )
            assert contact_results is not None
            
        except Exception as e:
            pytest.fail(f"紧急工作流不应该抛出异常，但抛出了: {type(e).__name__}: {e}")


# ============================================================================
# 边缘情况测试
# ============================================================================

class TestEmergencyWorkflowEdgeCases:
    """测试紧急响应工作流的边缘情况"""
    
    def test_single_emergency_contact(self):
        """只有一个紧急联系人的情况"""
        dispatcher = EmergencyDispatcher()
        
        user_profile = UserProfile(
            user_id="user123",
            age=75,
            medical_conditions=[],
            mobility_aids=[],
            emergency_contacts=[
                EmergencyContact(
                    name="张三",
                    relationship="儿子",
                    phone="13800138000",
                    email="zhangsan@example.com",
                    priority=1
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
        
        fall_incident = IncidentData(
            incident_id="fall_001",
            user_id="user123",
            incident_type=IncidentType.FALL,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.EMERGENCY,
            location=Location(latitude=39.9042, longitude=116.4074),
            sensor_data={"fall_detected": True},
            verification_status=VerificationStatus.CONFIRMED
        )
        
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        contact_results = dispatcher.contact_care_circle(
            dispatch_result.dispatch_id,
            user_profile.emergency_contacts,
            fall_incident
        )
        
        # 验证：至少尝试联系一次
        assert len(contact_results) >= 1
    
    def test_no_medical_conditions(self):
        """没有医疗状况的用户"""
        dispatcher = EmergencyDispatcher()
        
        user_profile = UserProfile(
            user_id="user123",
            age=75,
            medical_conditions=[],  # 没有医疗状况
            mobility_aids=[],
            emergency_contacts=[
                EmergencyContact(
                    name="张三",
                    relationship="儿子",
                    phone="13800138000",
                    email="zhangsan@example.com",
                    priority=1
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
        
        fall_incident = IncidentData(
            incident_id="fall_001",
            user_id="user123",
            incident_type=IncidentType.FALL,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.EMERGENCY,
            location=Location(latitude=39.9042, longitude=116.4074),
            sensor_data={"fall_detected": True},
            verification_status=VerificationStatus.CONFIRMED
        )
        
        # 创建紧急信息包
        package = dispatcher.create_emergency_package(fall_incident, user_profile)
        
        # 验证：即使没有医疗状况，信息包也应该正常创建
        assert package is not None
        assert "medical_conditions" in package.medical_history
        assert len(package.medical_history["medical_conditions"]) == 0
    
    def test_immediate_user_response(self):
        """用户立即响应的情况"""
        dispatcher = EmergencyDispatcher()
        
        user_profile = UserProfile(
            user_id="user123",
            age=75,
            medical_conditions=[],
            mobility_aids=[],
            emergency_contacts=[
                EmergencyContact(
                    name="张三",
                    relationship="儿子",
                    phone="13800138000",
                    email="zhangsan@example.com",
                    priority=1
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
        
        fall_incident = IncidentData(
            incident_id="fall_001",
            user_id="user123",
            incident_type=IncidentType.FALL,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.EMERGENCY,
            location=Location(latitude=39.9042, longitude=116.4074),
            sensor_data={"fall_detected": True},
            verification_status=VerificationStatus.CONFIRMED
        )
        
        # 启动紧急响应
        dispatch_result = dispatcher.initiate_emergency_response(fall_incident, user_profile)
        voice_confirmation = dispatcher.send_voice_confirmation(
            dispatch_result.dispatch_id,
            user_profile.user_id,
            fall_incident
        )
        
        # 用户立即响应（在1秒内）
        dispatcher.record_voice_response(voice_confirmation.request_id, "我很好")
        
        # 验证：响应已记录
        assert voice_confirmation.response_received is True
        assert dispatch_result.status == DispatchStatus.USER_RESPONDED
        
        # 验证：不应该超时
        is_timeout = dispatcher.check_voice_confirmation_timeout(voice_confirmation.request_id)
        assert is_timeout is False
    
    def test_multiple_simultaneous_emergencies(self):
        """多个同时发生的紧急情况"""
        dispatcher = EmergencyDispatcher()
        
        user_profile = UserProfile(
            user_id="user123",
            age=75,
            medical_conditions=[],
            mobility_aids=[],
            emergency_contacts=[
                EmergencyContact(
                    name="张三",
                    relationship="儿子",
                    phone="13800138000",
                    email="zhangsan@example.com",
                    priority=1
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
        
        # 创建两个不同的跌倒事件
        fall1 = IncidentData(
            incident_id="fall_001",
            user_id="user123",
            incident_type=IncidentType.FALL,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.EMERGENCY,
            location=Location(latitude=39.9042, longitude=116.4074),
            sensor_data={"fall_detected": True},
            verification_status=VerificationStatus.CONFIRMED
        )
        
        fall2 = IncidentData(
            incident_id="fall_002",
            user_id="user456",
            incident_type=IncidentType.FALL,
            timestamp=datetime.utcnow(),
            severity=SeverityLevel.EMERGENCY,
            location=Location(latitude=31.2304, longitude=121.4737),
            sensor_data={"fall_detected": True},
            verification_status=VerificationStatus.CONFIRMED
        )
        
        # 启动两个紧急响应
        dispatch1 = dispatcher.initiate_emergency_response(fall1, user_profile)
        dispatch2 = dispatcher.initiate_emergency_response(fall2, user_profile)
        
        # 验证：两个调度都已创建
        assert dispatch1.dispatch_id != dispatch2.dispatch_id
        
        # 验证：两个调度都是活跃的
        active_dispatches = dispatcher.get_active_dispatches()
        assert len(active_dispatches) == 2
        
        dispatch_ids = [d.dispatch_id for d in active_dispatches]
        assert dispatch1.dispatch_id in dispatch_ids
        assert dispatch2.dispatch_id in dispatch_ids
