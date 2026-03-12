"""
灯光编排器
Lighting Orchestrator for health status indication and smart home integration
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

from app.schemas.ambient import (
    RiskLevel, LightingPattern, EmergencyType,
    LightingConfig, UserPreferences
)

logger = logging.getLogger(__name__)


class LightingOrchestrator:
    """
    灯光编排器 - 用于健康状态指示的智能灯光控制
    Lighting Orchestrator for health status indication
    """
    
    def __init__(self, config: LightingConfig):
        """
        初始化灯光编排器
        
        Args:
            config: 灯光配置
        """
        self.config = config
        self.active_patterns: Dict[str, LightingPattern] = {}
        logger.info(f"LightingOrchestrator initialized with {len(config.device_ids)} devices")

    def set_health_indicator_lights(self, risk_level: RiskLevel) -> Dict[str, Any]:
        """
        设置健康指示灯光
        Set health indicator lights based on risk level
        
        Args:
            risk_level: 风险级别
            
        Returns:
            Dict: 灯光设置结果
        """
        if not self.config.enabled:
            return {"success": False, "reason": "lighting_disabled"}
        
        # 根据风险级别映射颜色和模式
        risk_to_pattern = {
            RiskLevel.NORMAL: {
                "color": "blue",
                "pattern": LightingPattern.CALM_BLUE,
                "brightness": 0.6,
                "transition": "smooth"
            },
            RiskLevel.CAUTION: {
                "color": "amber",
                "pattern": LightingPattern.AMBER_CAUTION,
                "brightness": 0.7,
                "transition": "gradual"
            },
            RiskLevel.ATTENTION_NEEDED: {
                "color": "red",
                "pattern": LightingPattern.PULSING_RED,
                "brightness": 0.8,
                "transition": "pulse"
            },
            RiskLevel.EMERGENCY: {
                "color": "red",
                "pattern": LightingPattern.PULSING_RED,
                "brightness": 1.0,
                "transition": "rapid_pulse"
            }
        }
        
        pattern_config = risk_to_pattern[risk_level]
        
        result = {
            "success": True,
            "risk_level": risk_level.value,
            "pattern": pattern_config["pattern"].value,
            "color": pattern_config["color"],
            "brightness": pattern_config["brightness"],
            "devices_updated": len(self.config.device_ids),
            "timestamp": datetime.utcnow()
        }
        
        # 应用灯光模式到所有设备
        for device_id in self.config.device_ids:
            self._apply_pattern_to_device(device_id, pattern_config)
            self.active_patterns[device_id] = pattern_config["pattern"]
        
        logger.info(
            f"Health indicator lights set: {risk_level.value} -> "
            f"{pattern_config['color']} ({pattern_config['brightness']:.1f})"
        )
        
        return result

    def create_calming_patterns(self, user_preferences: UserPreferences) -> Dict[str, Any]:
        """
        创建平静灯光模式
        Create calming lighting patterns based on user preferences
        
        Args:
            user_preferences: 用户偏好
            
        Returns:
            Dict: 模式创建结果
        """
        if not self.config.enabled:
            return {"success": False, "reason": "lighting_disabled"}
        
        # 根据时间调整亮度
        current_hour = datetime.now().hour
        is_quiet_hours = (
            current_hour >= user_preferences.quiet_hours_start or
            current_hour < user_preferences.quiet_hours_end
        )
        
        brightness = (
            user_preferences.lighting_config.brightness_night if is_quiet_hours
            else user_preferences.lighting_config.brightness_day
        )
        
        calming_config = {
            "color": "soft_blue",
            "pattern": LightingPattern.CALM_BLUE,
            "brightness": brightness,
            "transition": self.config.transition_duration
        }
        
        result = {
            "success": True,
            "pattern": "calming",
            "brightness": brightness,
            "is_quiet_hours": is_quiet_hours,
            "devices_updated": len(self.config.device_ids),
            "timestamp": datetime.utcnow()
        }
        
        for device_id in self.config.device_ids:
            self._apply_pattern_to_device(device_id, calming_config)
        
        logger.info(f"Calming patterns created with brightness {brightness:.2f}")
        
        return result

    def emergency_lighting_protocol(self, emergency_type: EmergencyType) -> Dict[str, Any]:
        """
        紧急灯光协议
        Emergency lighting protocol for critical situations
        
        Args:
            emergency_type: 紧急类型
            
        Returns:
            Dict: 紧急灯光激活结果
        """
        if not self.config.enabled:
            logger.warning("Emergency lighting protocol called but lighting is disabled")
            return {"success": False, "reason": "lighting_disabled"}
        
        # 紧急类型到灯光配置的映射
        emergency_patterns = {
            EmergencyType.FALL: {
                "color": "red",
                "pattern": LightingPattern.PULSING_RED,
                "brightness": 1.0,
                "pulse_rate": "fast"
            },
            EmergencyType.MEDICAL: {
                "color": "red",
                "pattern": LightingPattern.PULSING_RED,
                "brightness": 1.0,
                "pulse_rate": "medium"
            },
            EmergencyType.FIRE: {
                "color": "red",
                "pattern": LightingPattern.PULSING_RED,
                "brightness": 1.0,
                "pulse_rate": "very_fast"
            },
            EmergencyType.INTRUSION: {
                "color": "red",
                "pattern": LightingPattern.PULSING_RED,
                "brightness": 1.0,
                "pulse_rate": "fast"
            }
        }
        
        pattern_config = emergency_patterns[emergency_type]
        
        result = {
            "success": True,
            "emergency_type": emergency_type.value,
            "pattern": pattern_config["pattern"].value,
            "brightness": pattern_config["brightness"],
            "devices_activated": len(self.config.device_ids),
            "timestamp": datetime.utcnow()
        }
        
        # 立即激活所有设备的紧急灯光
        for device_id in self.config.device_ids:
            self._apply_pattern_to_device(device_id, pattern_config, immediate=True)
            self.active_patterns[device_id] = pattern_config["pattern"]
        
        logger.critical(
            f"Emergency lighting protocol activated: {emergency_type.value} -> "
            f"{pattern_config['color']} pulsing at {pattern_config['pulse_rate']}"
        )
        
        return result

    def _apply_pattern_to_device(
        self, 
        device_id: str, 
        pattern_config: Dict[str, Any],
        immediate: bool = False
    ) -> None:
        """
        应用灯光模式到设备
        Apply lighting pattern to specific device
        
        Args:
            device_id: 设备ID
            pattern_config: 模式配置
            immediate: 是否立即应用（跳过过渡）
        """
        transition = 0 if immediate else self.config.transition_duration
        
        logger.debug(
            f"Applying pattern to device {device_id}: "
            f"color={pattern_config.get('color')}, "
            f"brightness={pattern_config.get('brightness'):.2f}, "
            f"transition={transition}s"
        )
        
        # TODO: 实际智能家居集成
        # 根据 self.config.smart_home_integration 调用相应的API
        # 
        # if self.config.smart_home_integration == "philips_hue":
        #     self._control_philips_hue_device(device_id, pattern_config, transition)
        # elif self.config.smart_home_integration == "lifx":
        #     self._control_lifx_device(device_id, pattern_config, transition)
        # else:
        #     logger.warning(f"Unknown smart home integration: {self.config.smart_home_integration}")
    
    def get_current_pattern(self, device_id: str) -> Optional[LightingPattern]:
        """
        获取设备当前灯光模式
        Get current lighting pattern for device
        
        Args:
            device_id: 设备ID
            
        Returns:
            Optional[LightingPattern]: 当前灯光模式
        """
        return self.active_patterns.get(device_id)
    
    def reset_all_lights(self) -> Dict[str, Any]:
        """
        重置所有灯光到默认状态
        Reset all lights to default state
        
        Returns:
            Dict: 重置结果
        """
        default_config = {
            "color": "blue",
            "pattern": LightingPattern.CALM_BLUE,
            "brightness": self.config.brightness_day,
            "transition": self.config.transition_duration
        }
        
        for device_id in self.config.device_ids:
            self._apply_pattern_to_device(device_id, default_config)
            self.active_patterns[device_id] = LightingPattern.CALM_BLUE
        
        logger.info("All lights reset to default state")
        
        return {
            "success": True,
            "devices_reset": len(self.config.device_ids),
            "timestamp": datetime.utcnow()
        }
