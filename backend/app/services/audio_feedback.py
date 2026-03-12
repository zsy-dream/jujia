"""
音频反馈系统
Audio Feedback System for gentle reminders and voice confirmation
"""
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from app.schemas.ambient import (
    ReminderType, AudioConfig, VoiceResponse,
    MedicationReminder, UserPreferences
)
from app.schemas.core import IncidentData

logger = logging.getLogger(__name__)


class AudioFeedbackSystem:
    """
    音频反馈系统 - 用于温和提醒和语音确认
    Audio Feedback System for gentle reminders and voice confirmation
    """
    
    def __init__(self, config: AudioConfig):
        """
        初始化音频反馈系统
        
        Args:
            config: 音频配置
        """
        self.config = config
        self.active_reminders: Dict[str, datetime] = {}
        logger.info(
            f"AudioFeedbackSystem initialized: enabled={config.enabled}, "
            f"voice={config.voice_enabled}"
        )

    def play_gentle_reminders(self, reminder_type: ReminderType) -> Dict[str, Any]:
        """
        播放温和提醒
        Play gentle audio reminders
        
        Args:
            reminder_type: 提醒类型
            
        Returns:
            Dict: 播放结果
        """
        if not self.config.enabled:
            return {"success": False, "reason": "audio_disabled"}
        
        # 根据提醒类型生成消息
        messages = {
            ReminderType.MEDICATION: "温馨提醒：该服药了",
            ReminderType.APPOINTMENT: "温馨提醒：您有一个预约",
            ReminderType.ACTIVITY: "温馨提醒：该活动一下了",
            ReminderType.HYDRATION: "温馨提醒：记得喝水"
        }
        
        message = messages.get(reminder_type, "温馨提醒")
        volume = self._get_adaptive_volume()
        
        result = {
            "success": True,
            "reminder_type": reminder_type.value,
            "message": message,
            "volume": volume,
            "timestamp": datetime.utcnow()
        }
        
        # 播放音频
        self._play_audio(message, volume, gentle=True)
        
        # 记录活跃提醒
        self.active_reminders[reminder_type.value] = datetime.utcnow()
        
        logger.info(f"Gentle reminder played: {reminder_type.value} at volume {volume:.2f}")
        
        return result

    def provide_voice_confirmation(self, incident: IncidentData) -> VoiceResponse:
        """
        提供语音确认
        Provide voice confirmation for incident verification
        
        Args:
            incident: 事件数据
            
        Returns:
            VoiceResponse: 语音响应
        """
        if not self.config.voice_enabled:
            logger.warning("Voice confirmation requested but voice is disabled")
            return VoiceResponse(
                message="Voice confirmation disabled",
                urgency="normal"
            )
        
        # 根据事件类型生成确认消息
        incident_messages = {
            "fall": "检测到跌倒。您还好吗？请回答是或否。",
            "fall_detected": "检测到跌倒。您还好吗？请回答是或否。",
            "medical_emergency": "检测到医疗紧急情况。您需要帮助吗？",
            "prolonged_inactivity": "您已经很长时间没有活动了。您还好吗？",
            "abnormal_movement": "检测到异常活动。您需要帮助吗？"
        }
        
        message = incident_messages.get(
            incident.incident_type.value,
            "检测到异常情况。您还好吗？"
        )
        
        # 根据严重程度确定紧急程度
        urgency_mapping = {
            "low": "low",
            "medium": "normal",
            "high": "high",
            "emergency": "emergency"
        }
        urgency = urgency_mapping.get(incident.severity.value, "normal")
        
        voice_response = VoiceResponse(
            message=message,
            language=self.config.preferred_voice.split("-")[0] + "-" + self.config.preferred_voice.split("-")[1],
            voice_type=self.config.preferred_voice.split("-")[-1] if "-" in self.config.preferred_voice else "female",
            urgency=urgency
        )
        
        # 播放语音确认
        volume = self._get_adaptive_volume()
        if urgency == "emergency":
            volume = min(volume * 1.5, 1.0)  # 紧急情况提高音量
        
        self._play_audio(message, volume, gentle=False)
        
        logger.info(
            f"Voice confirmation provided for incident {incident.incident_id}: "
            f"type={incident.incident_type.value}, urgency={urgency}"
        )
        
        return voice_response

    def adjust_volume_for_time_of_day(self, current_time: datetime) -> float:
        """
        根据时间调整音量
        Adjust volume based on time of day
        
        Args:
            current_time: 当前时间
            
        Returns:
            float: 调整后的音量 (0.0 to 1.0)
        """
        hour = current_time.hour
        
        # 夜间时段 (22:00 - 07:00) 使用较低音量
        if hour >= 22 or hour < 7:
            volume = self.config.volume_night
            logger.debug(f"Night time volume: {volume:.2f}")
        else:
            volume = self.config.volume_day
            logger.debug(f"Day time volume: {volume:.2f}")
        
        return volume
    
    def _get_adaptive_volume(self) -> float:
        """
        获取自适应音量
        Get adaptive volume based on current time
        
        Returns:
            float: 音量值 (0.0 to 1.0)
        """
        return self.adjust_volume_for_time_of_day(datetime.now())
    
    def _play_audio(self, message: str, volume: float, gentle: bool = True) -> None:
        """
        播放音频
        Play audio message
        
        Args:
            message: 消息内容
            volume: 音量
            gentle: 是否使用温和模式
        """
        logger.debug(
            f"Playing audio: message='{message}', volume={volume:.2f}, gentle={gentle}"
        )
        
        # TODO: 实际集成TTS和音频播放
        # 这里应该调用文本转语音服务和音频播放API
        # 
        # if self.config.voice_enabled:
        #     tts_audio = self._text_to_speech(message, self.config.preferred_voice)
        #     self._play_audio_file(tts_audio, volume, gentle)
        # else:
        #     self._play_tone(volume, gentle)
    
    def stop_all_audio(self) -> Dict[str, Any]:
        """
        停止所有音频播放
        Stop all audio playback
        
        Returns:
            Dict: 停止结果
        """
        self.active_reminders.clear()
        
        logger.info("All audio playback stopped")
        
        return {
            "success": True,
            "timestamp": datetime.utcnow()
        }
