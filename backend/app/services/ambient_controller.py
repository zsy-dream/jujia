"""
环境交互控制器
Ambient Controller for environmental feedback through lighting and audio
"""
from datetime import datetime, time
from typing import Optional, Dict, Any
import logging

from app.schemas.ambient import (
    HealthStatus, RiskLevel, LightingPattern, EmergencyType,
    ReminderType, LightingConfig, AudioConfig, UserPreferences,
    SystemHealth, MedicationReminder, AmbientFeedback
)

logger = logging.getLogger(__name__)


class AmbientController:
    """
    环境交互控制器 - 通过灯光和音频提供环境反馈
    Ambient Controller for providing environmental feedback through lighting and audio
    """
    
    def __init__(self, lighting_config: LightingConfig, audio_config: AudioConfig):
        """
        初始化环境控制器
        
        Args:
            lighting_config: 灯光配置
            audio_config: 音频配置
        """
        self.lighting_config = lighting_config
        self.audio_config = audio_config
        self.current_pattern: Optional[LightingPattern] = None
        self.current_brightness: float = 0.8
        
        logger.info(
            f"AmbientController initialized with lighting={lighting_config.enabled}, "
            f"audio={audio_config.enabled}"
        )
    
    def update_health_status_display(self, health_status: HealthStatus) -> AmbientFeedback:
        """
        更新健康状态显示
        Update health status display based on current health metrics
        
        Args:
            health_status: 当前健康状态
            
        Returns:
            AmbientFeedback: 环境反馈状态
        """
        # 根据健康状态映射到风险级别和灯光模式
        status_mapping = {
            HealthStatus.EXCELLENT: (RiskLevel.NORMAL, LightingPattern.CALM_BLUE),
            HealthStatus.GOOD: (RiskLevel.NORMAL, LightingPattern.CALM_BLUE),
            HealthStatus.FAIR: (RiskLevel.CAUTION, LightingPattern.AMBER_CAUTION),
            HealthStatus.POOR: (RiskLevel.ATTENTION_NEEDED, LightingPattern.PULSING_RED),
            HealthStatus.CRITICAL: (RiskLevel.EMERGENCY, LightingPattern.PULSING_RED)
        }
        
        risk_level, lighting_pattern = status_mapping[health_status]
        
        # 调整亮度基于时间
        brightness = self._get_adaptive_brightness()
        
        # 更新灯光显示
        if self.lighting_config.enabled:
            self._set_lighting_pattern(lighting_pattern, brightness)
        
        feedback = AmbientFeedback(
            timestamp=datetime.utcnow(),
            user_id="system",  # Default system user
            health_status=health_status,
            risk_level=risk_level,
            lighting_pattern=lighting_pattern,
            brightness=brightness
        )
        
        logger.info(
            f"Health status display updated: {health_status.value} -> "
            f"{lighting_pattern.value} at brightness {brightness:.2f}"
        )
        
        return feedback
    
    def provide_medication_reminder(self, medication_schedule: MedicationReminder) -> Dict[str, Any]:
        """
        提供药物提醒
        Provide medication reminder through lighting and audio
        
        Args:
            medication_schedule: 药物提醒计划
            
        Returns:
            Dict: 提醒执行结果
        """
        result = {
            "reminder_sent": False,
            "lighting_activated": False,
            "audio_played": False,
            "timestamp": datetime.utcnow()
        }
        
        # 设置药物提醒灯光模式
        if self.lighting_config.enabled:
            brightness = self._get_adaptive_brightness()
            self._set_lighting_pattern(LightingPattern.MEDICATION_REMINDER, brightness)
            result["lighting_activated"] = True
            logger.info(f"Medication reminder lighting activated for {medication_schedule.medication_name}")
        
        # 播放温和的音频提醒
        if self.audio_config.enabled:
            message = f"提醒：该服用{medication_schedule.medication_name}了，剂量{medication_schedule.dosage}"
            if medication_schedule.instructions:
                message += f"。{medication_schedule.instructions}"
            
            self._play_gentle_reminder(message, ReminderType.MEDICATION)
            result["audio_played"] = True
            logger.info(f"Medication reminder audio played for {medication_schedule.medication_name}")
        
        result["reminder_sent"] = True
        return result
    
    def indicate_system_status(self, system_health: SystemHealth) -> Dict[str, Any]:
        """
        指示系统状态
        Indicate system health status through ambient feedback
        
        Args:
            system_health: 系统健康状态
            
        Returns:
            Dict: 状态指示结果
        """
        result = {
            "status_indicated": False,
            "pattern": None,
            "timestamp": datetime.utcnow()
        }
        
        if not self.lighting_config.enabled:
            return result
        
        # 根据系统状态选择灯光模式
        if system_health.overall_status == "healthy":
            # 正常状态 - 不需要特殊指示
            result["status_indicated"] = True
            result["pattern"] = "normal"
        elif system_health.overall_status == "degraded":
            # 降级模式 - 使用琥珀色警告
            brightness = self._get_adaptive_brightness() * 0.5  # 降低亮度
            self._set_lighting_pattern(LightingPattern.SYSTEM_STATUS, brightness)
            result["status_indicated"] = True
            result["pattern"] = "degraded"
            logger.warning(f"System degraded mode indicated via ambient lighting")
        else:  # offline
            # 离线状态 - 关闭灯光或使用最小亮度
            self._set_lighting_pattern(LightingPattern.OFF, 0.0)
            result["status_indicated"] = True
            result["pattern"] = "offline"
            logger.error(f"System offline status indicated")
        
        return result
    
    def _get_adaptive_brightness(self) -> float:
        """
        获取自适应亮度
        Get adaptive brightness based on time of day
        
        Returns:
            float: 亮度值 (0.0 to 1.0)
        """
        current_hour = datetime.now().hour
        
        # 夜间时段 (22:00 - 07:00) 使用较低亮度
        if current_hour >= 22 or current_hour < 7:
            return self.lighting_config.brightness_night
        else:
            return self.lighting_config.brightness_day
    
    def _set_lighting_pattern(self, pattern: LightingPattern, brightness: float) -> None:
        """
        设置灯光模式
        Set lighting pattern with specified brightness
        
        Args:
            pattern: 灯光模式
            brightness: 亮度值
        """
        self.current_pattern = pattern
        self.current_brightness = brightness
        
        # 这里应该调用实际的智能家居API
        # 目前只记录日志
        logger.debug(
            f"Lighting pattern set: {pattern.value} at brightness {brightness:.2f}"
        )
        
        # TODO: 实际集成智能家居系统
        # if self.lighting_config.smart_home_integration == "philips_hue":
        #     self._control_philips_hue(pattern, brightness)
        # elif self.lighting_config.smart_home_integration == "lifx":
        #     self._control_lifx(pattern, brightness)
    
    def _play_gentle_reminder(self, message: str, reminder_type: ReminderType) -> None:
        """
        播放温和提醒
        Play gentle audio reminder
        
        Args:
            message: 提醒消息
            reminder_type: 提醒类型
        """
        volume = self._get_adaptive_volume()
        
        logger.debug(
            f"Playing gentle reminder: type={reminder_type.value}, "
            f"volume={volume:.2f}, message='{message}'"
        )
        
        # TODO: 实际集成音频系统
        # 这里应该调用TTS服务和音频播放API
    
    def _get_adaptive_volume(self) -> float:
        """
        获取自适应音量
        Get adaptive volume based on time of day
        
        Returns:
            float: 音量值 (0.0 to 1.0)
        """
        current_hour = datetime.now().hour
        
        # 夜间时段使用较低音量
        if current_hour >= 22 or current_hour < 7:
            return self.audio_config.volume_night
        else:
            return self.audio_config.volume_day
