"""
药物提醒系统
Medication Reminder System with lighting patterns and audio alerts
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from app.schemas.ambient import (
    MedicationReminder, LightingPattern, ReminderType,
    LightingConfig, AudioConfig, UserPreferences
)
from app.services.lighting_orchestrator import LightingOrchestrator
from app.services.audio_feedback import AudioFeedbackSystem

logger = logging.getLogger(__name__)


class MedicationReminderSystem:
    """
    药物提醒系统 - 具有灯光模式和铃声的药物提醒
    Medication Reminder System with lighting patterns and audio alerts
    """
    
    def __init__(
        self,
        lighting_orchestrator: LightingOrchestrator,
        audio_system: AudioFeedbackSystem,
        user_preferences: UserPreferences
    ):
        """
        初始化药物提醒系统
        
        Args:
            lighting_orchestrator: 灯光编排器
            audio_system: 音频反馈系统
            user_preferences: 用户偏好
        """
        self.lighting = lighting_orchestrator
        self.audio = audio_system
        self.preferences = user_preferences
        self.active_reminders: Dict[str, MedicationReminder] = {}
        
        logger.info("MedicationReminderSystem initialized")

    def schedule_reminder(self, reminder: MedicationReminder) -> Dict[str, Any]:
        """
        安排药物提醒
        Schedule a medication reminder
        
        Args:
            reminder: 药物提醒
            
        Returns:
            Dict: 安排结果
        """
        reminder_id = f"{reminder.medication_name}_{reminder.scheduled_time.isoformat()}"
        self.active_reminders[reminder_id] = reminder
        
        # 计算提前提醒时间
        advance_time = timedelta(minutes=self.preferences.medication_reminder_advance)
        reminder_time = reminder.scheduled_time - advance_time
        
        result = {
            "success": True,
            "reminder_id": reminder_id,
            "medication": reminder.medication_name,
            "scheduled_time": reminder.scheduled_time,
            "reminder_time": reminder_time,
            "advance_minutes": self.preferences.medication_reminder_advance
        }
        
        logger.info(
            f"Medication reminder scheduled: {reminder.medication_name} "
            f"at {reminder.scheduled_time}, reminder at {reminder_time}"
        )
        
        return result
    
    def trigger_reminder(self, reminder: MedicationReminder) -> Dict[str, Any]:
        """
        触发药物提醒
        Trigger medication reminder with lighting and audio
        
        Args:
            reminder: 药物提醒
            
        Returns:
            Dict: 提醒触发结果
        """
        result = {
            "success": False,
            "medication": reminder.medication_name,
            "lighting_activated": False,
            "audio_played": False,
            "timestamp": datetime.utcnow()
        }
        
        # 激活药物提醒灯光模式
        if self.lighting.config.enabled:
            lighting_result = self._activate_medication_lighting()
            result["lighting_activated"] = lighting_result["success"]
            result["lighting_pattern"] = lighting_result.get("pattern")
        
        # 播放音频提醒
        if self.audio.config.enabled:
            audio_result = self._play_medication_audio(reminder)
            result["audio_played"] = audio_result["success"]
            result["audio_message"] = audio_result.get("message")
        
        # 标记提醒已发送
        reminder.reminder_sent = True
        result["success"] = True
        
        logger.info(
            f"Medication reminder triggered: {reminder.medication_name}, "
            f"lighting={result['lighting_activated']}, audio={result['audio_played']}"
        )
        
        return result

    def acknowledge_reminder(self, reminder_id: str) -> Dict[str, Any]:
        """
        确认药物提醒
        Acknowledge medication reminder
        
        Args:
            reminder_id: 提醒ID
            
        Returns:
            Dict: 确认结果
        """
        if reminder_id not in self.active_reminders:
            return {
                "success": False,
                "reason": "reminder_not_found",
                "reminder_id": reminder_id
            }
        
        reminder = self.active_reminders[reminder_id]
        reminder.acknowledged = True
        
        # 停止灯光和音频提醒
        self._deactivate_medication_feedback()
        
        result = {
            "success": True,
            "reminder_id": reminder_id,
            "medication": reminder.medication_name,
            "acknowledged_at": datetime.utcnow()
        }
        
        logger.info(f"Medication reminder acknowledged: {reminder.medication_name}")
        
        return result
    
    def _activate_medication_lighting(self) -> Dict[str, Any]:
        """
        激活药物提醒灯光
        Activate medication reminder lighting pattern
        
        Returns:
            Dict: 激活结果
        """
        # 使用特定的药物提醒灯光模式
        # 通常是温和的脉冲绿色或蓝色
        medication_pattern = {
            "color": "soft_green",
            "pattern": LightingPattern.MEDICATION_REMINDER,
            "brightness": self._get_adaptive_brightness(),
            "transition": "gentle_pulse"
        }
        
        for device_id in self.lighting.config.device_ids:
            self.lighting._apply_pattern_to_device(device_id, medication_pattern)
        
        return {
            "success": True,
            "pattern": LightingPattern.MEDICATION_REMINDER.value,
            "devices_activated": len(self.lighting.config.device_ids)
        }
    
    def _play_medication_audio(self, reminder: MedicationReminder) -> Dict[str, Any]:
        """
        播放药物提醒音频
        Play medication reminder audio
        
        Args:
            reminder: 药物提醒
            
        Returns:
            Dict: 播放结果
        """
        # 构建提醒消息
        message = f"温馨提醒：该服用{reminder.medication_name}了，剂量{reminder.dosage}"
        if reminder.instructions:
            message += f"。{reminder.instructions}"
        
        # 播放温和的铃声后跟语音消息
        volume = self.audio._get_adaptive_volume()
        
        # 先播放铃声
        self.audio._play_audio("medication_chime", volume, gentle=True)
        
        # 然后播放语音消息
        self.audio._play_audio(message, volume, gentle=True)
        
        return {
            "success": True,
            "message": message,
            "volume": volume
        }

    def _deactivate_medication_feedback(self) -> None:
        """
        停用药物提醒反馈
        Deactivate medication reminder feedback
        """
        # 重置灯光到正常状态
        if self.lighting.config.enabled:
            self.lighting.reset_all_lights()
        
        # 停止音频
        if self.audio.config.enabled:
            self.audio.stop_all_audio()
        
        logger.debug("Medication reminder feedback deactivated")
    
    def _get_adaptive_brightness(self) -> float:
        """
        获取自适应亮度
        Get adaptive brightness based on time and preferences
        
        Returns:
            float: 亮度值 (0.0 to 1.0)
        """
        current_hour = datetime.now().hour
        
        is_quiet_hours = (
            current_hour >= self.preferences.quiet_hours_start or
            current_hour < self.preferences.quiet_hours_end
        )
        
        if is_quiet_hours:
            return self.preferences.lighting_config.brightness_night
        else:
            return self.preferences.lighting_config.brightness_day
    
    def get_pending_reminders(self) -> List[MedicationReminder]:
        """
        获取待处理提醒
        Get pending medication reminders
        
        Returns:
            List[MedicationReminder]: 待处理提醒列表
        """
        pending = [
            reminder for reminder in self.active_reminders.values()
            if reminder.reminder_sent and not reminder.acknowledged
        ]
        
        return pending
    
    def clear_old_reminders(self, hours: int = 24) -> int:
        """
        清除旧提醒
        Clear old reminders
        
        Args:
            hours: 清除多少小时前的提醒
            
        Returns:
            int: 清除的提醒数量
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        old_reminder_ids = [
            rid for rid, reminder in self.active_reminders.items()
            if reminder.scheduled_time < cutoff_time
        ]
        
        for rid in old_reminder_ids:
            del self.active_reminders[rid]
        
        logger.info(f"Cleared {len(old_reminder_ids)} old reminders")
        
        return len(old_reminder_ids)
