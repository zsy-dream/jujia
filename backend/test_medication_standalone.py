"""
独立药物提醒属性测试
Standalone Medication Reminder Property Test
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta

from app.schemas.ambient import (
    MedicationReminder, LightingPattern, ReminderType,
    LightingConfig, AudioConfig, UserPreferences
)
from app.services.medication_reminder import MedicationReminderSystem
from app.services.lighting_orchestrator import LightingOrchestrator
from app.services.audio_feedback import AudioFeedbackSystem


# 策略定义
medication_reminder_strategy = st.builds(
    MedicationReminder,
    medication_name=st.text(min_size=3, max_size=30, alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs'))),
    scheduled_time=st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2026, 12, 31)),
    dosage=st.text(min_size=2, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N', 'Zs'))),
    instructions=st.one_of(st.none(), st.text(min_size=5, max_size=100)),
    reminder_sent=st.just(False),
    acknowledged=st.just(False)
)

lighting_config_strategy = st.builds(
    LightingConfig,
    enabled=st.just(True),
    brightness_day=st.floats(min_value=0.5, max_value=1.0),
    brightness_night=st.floats(min_value=0.1, max_value=0.5),
    transition_duration=st.floats(min_value=0.5, max_value=5.0),
    device_ids=st.lists(st.text(min_size=5, max_size=20), min_size=1, max_size=3)
)

audio_config_strategy = st.builds(
    AudioConfig,
    enabled=st.just(True),
    volume_day=st.floats(min_value=0.5, max_value=1.0),
    volume_night=st.floats(min_value=0.2, max_value=0.5)
)

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
@settings(max_examples=50, deadline=None)
def test_medication_reminder_feedback(reminder, lighting_config, audio_config, user_preferences):
    """属性16：药物提醒反馈"""
    lighting_orchestrator = LightingOrchestrator(lighting_config)
    audio_system = AudioFeedbackSystem(audio_config)
    reminder_system = MedicationReminderSystem(lighting_orchestrator, audio_system, user_preferences)
    
    result = reminder_system.trigger_reminder(reminder)
    
    assert result["success"] == True
    assert result["medication"] == reminder.medication_name
    
    if lighting_config.enabled:
        assert result["lighting_activated"] == True
        assert result["lighting_pattern"] == LightingPattern.MEDICATION_REMINDER.value
    
    if audio_config.enabled:
        assert result["audio_played"] == True
        assert reminder.medication_name in result["audio_message"]
        assert reminder.dosage in result["audio_message"]
    
    assert reminder.reminder_sent == True
    print(f"✓ Test passed for medication: {reminder.medication_name}")


if __name__ == "__main__":
    print("Running medication reminder property tests...")
    test_medication_reminder_feedback()
    print("\n✓ All tests passed!")
