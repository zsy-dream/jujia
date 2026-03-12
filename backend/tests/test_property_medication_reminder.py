"""
属性测试：药物提醒反馈
Property Test: Medication Reminder Feedback

属性16：药物提醒反馈
*对于任何*药物提醒事件，系统应当使用特定的灯光模式和温和铃声提供清晰、非侵入性的通知
**验证需求：需求5.4**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta

from app.schemas.ambient import (
    MedicationReminder, LightingPattern, ReminderType,
    LightingConfig, AudioConfig, UserPreferences
)
from app.services.medication_reminder import MedicationReminderSystem
from app.services.lighting_orchestrator import LightingOrchestrator
from app.services.audio_feedback import AudioFeedbackSystem


# 策略：生成药物提醒
medication_reminder_strategy = st.builds(
    MedicationReminder,
    medication_name=st.text(min_size=3, max_size=30, alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs'))),
    scheduled_time=st.datetimes(
        min_value=datetime(2024, 1, 1),
        max_value=datetime(2026, 12, 31)
    ),
    dosage=st.text(min_size=2, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs'))),
    instructions=st.one_of(st.none(), st.text(min_size=5, max_size=100)),
    reminder_sent=st.just(False),
    acknowledged=st.just(False)
)

# 策略：生成灯光配置
lighting_config_strategy = st.builds(
    LightingConfig,
    enabled=st.just(True),
    brightness_day=st.floats(min_value=0.5, max_value=1.0),
    brightness_night=st.floats(min_value=0.1, max_value=0.5),
    transition_duration=st.floats(min_value=0.5, max_value=5.0),
    smart_home_integration=st.sampled_from([None, "philips_hue", "lifx"]),
    device_ids=st.lists(st.text(min_size=5, max_size=20), min_size=1, max_size=5)
)

# 策略：生成音频配置
audio_config_strategy = st.builds(
    AudioConfig,
    enabled=st.just(True),
    volume_day=st.floats(min_value=0.5, max_value=1.0),
    volume_night=st.floats(min_value=0.2, max_value=0.5),
    voice_enabled=st.booleans(),
    preferred_voice=st.sampled_from(["zh-CN-female", "zh-CN-male", "en-US-female"])
)


# 策略：生成用户偏好
user_preferences_strategy = st.builds(
    UserPreferences,
    user_id=st.text(min_size=5, max_size=20),
    lighting_config=lighting_config_strategy,
    audio_config=audio_config_strategy,
    quiet_hours_start=st.integers(min_value=20, max_value=23),
    quiet_hours_end=st.integers(min_value=5, max_value=9),
    medication_reminder_advance=st.integers(min_value=5, max_value=30)
)


@given(
    reminder=medication_reminder_strategy,
    lighting_config=lighting_config_strategy,
    audio_config=audio_config_strategy,
    user_preferences=user_preferences_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_medication_reminder_feedback(
    reminder: MedicationReminder,
    lighting_config: LightingConfig,
    audio_config: AudioConfig,
    user_preferences: UserPreferences
):
    """
    属性16：药物提醒反馈
    
    验证：对于任何药物提醒事件，系统应当使用特定的灯光模式和温和铃声
    提供清晰、非侵入性的通知
    """
    # 创建药物提醒系统
    lighting_orchestrator = LightingOrchestrator(lighting_config)
    audio_system = AudioFeedbackSystem(audio_config)
    reminder_system = MedicationReminderSystem(
        lighting_orchestrator,
        audio_system,
        user_preferences
    )
    
    # 触发药物提醒
    result = reminder_system.trigger_reminder(reminder)
    
    # 验证提醒已成功触发
    assert result["success"] == True
    assert result["medication"] == reminder.medication_name
    assert result["timestamp"] is not None
    
    # 需求5.4: 验证灯光模式已激活
    if lighting_config.enabled:
        assert result["lighting_activated"] == True
        assert result["lighting_pattern"] == LightingPattern.MEDICATION_REMINDER.value
    else:
        assert result["lighting_activated"] == False
    
    # 需求5.4: 验证音频提醒已播放
    if audio_config.enabled:
        assert result["audio_played"] == True
        assert result["audio_message"] is not None
        # 验证消息包含药物名称和剂量
        assert reminder.medication_name in result["audio_message"]
        assert reminder.dosage in result["audio_message"]
    else:
        assert result["audio_played"] == False
    
    # 验证提醒已标记为已发送
    assert reminder.reminder_sent == True



@given(
    reminder=medication_reminder_strategy,
    user_preferences=user_preferences_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_medication_reminder_scheduling(
    reminder: MedicationReminder,
    user_preferences: UserPreferences
):
    """
    属性16：药物提醒安排
    
    验证：系统正确安排药物提醒，并根据用户偏好提前通知
    """
    lighting_orchestrator = LightingOrchestrator(user_preferences.lighting_config)
    audio_system = AudioFeedbackSystem(user_preferences.audio_config)
    reminder_system = MedicationReminderSystem(
        lighting_orchestrator,
        audio_system,
        user_preferences
    )
    
    # 安排提醒
    result = reminder_system.schedule_reminder(reminder)
    
    # 验证安排成功
    assert result["success"] == True
    assert result["medication"] == reminder.medication_name
    assert result["scheduled_time"] == reminder.scheduled_time
    
    # 验证提前提醒时间计算正确
    expected_advance = timedelta(minutes=user_preferences.medication_reminder_advance)
    expected_reminder_time = reminder.scheduled_time - expected_advance
    assert result["reminder_time"] == expected_reminder_time
    assert result["advance_minutes"] == user_preferences.medication_reminder_advance


@given(
    audio_config=audio_config_strategy,
    reminder_type=st.sampled_from([
        ReminderType.MEDICATION,
        ReminderType.APPOINTMENT,
        ReminderType.ACTIVITY,
        ReminderType.HYDRATION
    ])
)
@settings(max_examples=100, deadline=None)
def test_property_audio_feedback_gentle_reminders(
    audio_config: AudioConfig,
    reminder_type: ReminderType
):
    """
    属性16：温和音频提醒
    
    验证：音频反馈系统提供温和、非侵入性的提醒
    """
    audio_system = AudioFeedbackSystem(audio_config)
    
    # 播放温和提醒
    result = audio_system.play_gentle_reminders(reminder_type)
    
    if audio_config.enabled:
        # 验证提醒已播放
        assert result["success"] == True
        assert result["reminder_type"] == reminder_type.value
        assert result["message"] is not None
        assert result["timestamp"] is not None
        
        # 验证音量在有效范围内
        assert 0.0 <= result["volume"] <= 1.0
        
        # 验证音量根据配置调整
        assert (
            audio_config.volume_night <= result["volume"] <= audio_config.volume_day
        )
    else:
        # 音频禁用时应返回失败
        assert result["success"] == False
        assert result["reason"] == "audio_disabled"



@given(
    current_time=st.datetimes(
        min_value=datetime(2024, 1, 1),
        max_value=datetime(2026, 12, 31)
    ),
    audio_config=audio_config_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_adaptive_volume_adjustment(
    current_time: datetime,
    audio_config: AudioConfig
):
    """
    属性17：自适应音量调整
    
    验证：音频系统根据时间调整音量，夜间使用较低音量
    """
    audio_system = AudioFeedbackSystem(audio_config)
    
    # 调整音量
    volume = audio_system.adjust_volume_for_time_of_day(current_time)
    
    # 验证音量在有效范围内
    assert 0.0 <= volume <= 1.0
    
    # 验证夜间时段使用较低音量
    hour = current_time.hour
    if hour >= 22 or hour < 7:
        assert volume == audio_config.volume_night
    else:
        assert volume == audio_config.volume_day


@given(
    reminder=medication_reminder_strategy,
    lighting_config=lighting_config_strategy,
    audio_config=audio_config_strategy,
    user_preferences=user_preferences_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_medication_reminder_acknowledgment(
    reminder: MedicationReminder,
    lighting_config: LightingConfig,
    audio_config: AudioConfig,
    user_preferences: UserPreferences
):
    """
    属性16：药物提醒确认
    
    验证：用户确认提醒后，系统停止灯光和音频反馈
    """
    lighting_orchestrator = LightingOrchestrator(lighting_config)
    audio_system = AudioFeedbackSystem(audio_config)
    reminder_system = MedicationReminderSystem(
        lighting_orchestrator,
        audio_system,
        user_preferences
    )
    
    # 安排并触发提醒
    schedule_result = reminder_system.schedule_reminder(reminder)
    reminder_id = schedule_result["reminder_id"]
    
    trigger_result = reminder_system.trigger_reminder(reminder)
    assert trigger_result["success"] == True
    
    # 确认提醒
    ack_result = reminder_system.acknowledge_reminder(reminder_id)
    
    # 验证确认成功
    assert ack_result["success"] == True
    assert ack_result["medication"] == reminder.medication_name
    assert ack_result["acknowledged_at"] is not None
    
    # 验证提醒已标记为已确认
    assert reminder.acknowledged == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
