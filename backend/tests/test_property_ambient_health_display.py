"""
属性测试：环境健康状态显示
Property Test: Ambient Health Status Display

属性15：环境健康状态显示
*对于任何*健康状态变化，环境界面应当显示适当的灯光模式：
正常范围显示蓝色，风险增加显示琥珀色，需要立即关注时显示脉冲红光配合音频
**验证需求：需求5.1, 5.2, 5.3**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime

from app.schemas.ambient import (
    HealthStatus, RiskLevel, LightingPattern,
    LightingConfig, AudioConfig, UserPreferences
)
from app.services.ambient_controller import AmbientController
from app.services.lighting_orchestrator import LightingOrchestrator


# 策略：生成健康状态
health_status_strategy = st.sampled_from([
    HealthStatus.EXCELLENT,
    HealthStatus.GOOD,
    HealthStatus.FAIR,
    HealthStatus.POOR,
    HealthStatus.CRITICAL
])

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
    enabled=st.booleans(),
    volume_day=st.floats(min_value=0.5, max_value=1.0),
    volume_night=st.floats(min_value=0.2, max_value=0.5),
    voice_enabled=st.booleans(),
    preferred_voice=st.sampled_from(["zh-CN-female", "zh-CN-male", "en-US-female"])
)


@given(
    health_status=health_status_strategy,
    lighting_config=lighting_config_strategy,
    audio_config=audio_config_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_ambient_health_status_display(
    health_status: HealthStatus,
    lighting_config: LightingConfig,
    audio_config: AudioConfig
):
    """
    属性15：环境健康状态显示
    
    验证：对于任何健康状态变化，环境界面应当显示适当的灯光模式
    """
    # 创建环境控制器
    controller = AmbientController(lighting_config, audio_config)
    
    # 更新健康状态显示
    feedback = controller.update_health_status_display(health_status)
    
    # 验证反馈已生成
    assert feedback is not None
    assert feedback.health_status == health_status
    assert feedback.timestamp is not None
    
    # 验证灯光模式映射正确性
    # 需求5.1: 正常范围显示蓝色
    if health_status in [HealthStatus.EXCELLENT, HealthStatus.GOOD]:
        assert feedback.risk_level == RiskLevel.NORMAL
        assert feedback.lighting_pattern == LightingPattern.CALM_BLUE
    
    # 需求5.2: 风险增加显示琥珀色
    elif health_status == HealthStatus.FAIR:
        assert feedback.risk_level == RiskLevel.CAUTION
        assert feedback.lighting_pattern == LightingPattern.AMBER_CAUTION
    
    # 需求5.3: 需要立即关注时显示脉冲红光
    elif health_status in [HealthStatus.POOR, HealthStatus.CRITICAL]:
        assert feedback.risk_level in [RiskLevel.ATTENTION_NEEDED, RiskLevel.EMERGENCY]
        assert feedback.lighting_pattern == LightingPattern.PULSING_RED
    
    # 验证亮度在有效范围内
    assert 0.0 <= feedback.brightness <= 1.0
    
    # 验证亮度根据配置调整
    # 亮度应该在配置的日间或夜间范围内
    assert (
        lighting_config.brightness_night <= feedback.brightness <= lighting_config.brightness_day or
        feedback.brightness == lighting_config.brightness_night or
        feedback.brightness == lighting_config.brightness_day
    )



@given(
    risk_level=st.sampled_from([RiskLevel.NORMAL, RiskLevel.CAUTION, RiskLevel.ATTENTION_NEEDED, RiskLevel.EMERGENCY]),
    lighting_config=lighting_config_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_lighting_orchestrator_health_indicators(
    risk_level: RiskLevel,
    lighting_config: LightingConfig
):
    """
    属性15：灯光编排器健康指示
    
    验证：灯光编排器正确设置健康指示灯光
    """
    orchestrator = LightingOrchestrator(lighting_config)
    
    # 设置健康指示灯光
    result = orchestrator.set_health_indicator_lights(risk_level)
    
    # 验证结果
    assert result["success"] == True
    assert result["risk_level"] == risk_level.value
    assert result["devices_updated"] == len(lighting_config.device_ids)
    
    # 验证颜色映射
    if risk_level == RiskLevel.NORMAL:
        assert result["color"] == "blue"
        assert result["pattern"] == LightingPattern.CALM_BLUE.value
    elif risk_level == RiskLevel.CAUTION:
        assert result["color"] == "amber"
        assert result["pattern"] == LightingPattern.AMBER_CAUTION.value
    elif risk_level in [RiskLevel.ATTENTION_NEEDED, RiskLevel.EMERGENCY]:
        assert result["color"] == "red"
        assert result["pattern"] == LightingPattern.PULSING_RED.value
    
    # 验证亮度
    assert 0.0 <= result["brightness"] <= 1.0
    
    # 验证所有设备都已更新
    for device_id in lighting_config.device_ids:
        pattern = orchestrator.get_current_pattern(device_id)
        assert pattern is not None


@given(
    lighting_config=lighting_config_strategy,
    user_preferences=st.builds(
        UserPreferences,
        user_id=st.text(min_size=5, max_size=20),
        lighting_config=lighting_config_strategy,
        audio_config=audio_config_strategy,
        quiet_hours_start=st.integers(min_value=20, max_value=23),
        quiet_hours_end=st.integers(min_value=5, max_value=9),
        medication_reminder_advance=st.integers(min_value=5, max_value=30)
    )
)
@settings(max_examples=100, deadline=None)
def test_property_adaptive_brightness_and_intensity(
    lighting_config: LightingConfig,
    user_preferences: UserPreferences
):
    """
    属性17：自适应环境亮度
    
    验证：环境界面根据时间和用户偏好调整亮度和强度
    """
    orchestrator = LightingOrchestrator(lighting_config)
    
    # 创建平静灯光模式
    result = orchestrator.create_calming_patterns(user_preferences)
    
    # 验证结果
    assert result["success"] == True
    assert result["pattern"] == "calming"
    assert result["devices_updated"] == len(lighting_config.device_ids)
    
    # 验证亮度在有效范围内
    assert 0.0 <= result["brightness"] <= 1.0
    
    # 验证亮度根据时间调整
    # 如果在安静时段，应该使用夜间亮度
    if result["is_quiet_hours"]:
        assert result["brightness"] == user_preferences.lighting_config.brightness_night
    else:
        assert result["brightness"] == user_preferences.lighting_config.brightness_day


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
