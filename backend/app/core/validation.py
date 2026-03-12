"""
数据验证工具函数
Data validation utilities for type safety and integrity
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime, UTC

from app.schemas.core import (
    SkeletonData, FrailtyIndex, IncidentData, 
    RiskPrediction, UserProfile, Keypoint, Location
)

def _utc_now_for(dt: datetime) -> datetime:
    """Return current UTC time with tz-awareness matching the provided datetime."""
    now = datetime.now(UTC)
    if dt.tzinfo is None:
        return now.replace(tzinfo=None)
    return now.astimezone(dt.tzinfo)


def validate_skeleton_data(data: SkeletonData) -> Tuple[bool, str]:
    """
    验证骨骼数据的完整性和隐私合规性
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # 检查是否已匿名化
        if not data.anonymized:
            return False, "Skeleton data must be anonymized"
        
        # 检查用户ID
        if not data.user_id or len(data.user_id) == 0:
            return False, "User ID cannot be empty"
        
        # 检查关键点数量
        if len(data.keypoints) == 0:
            return False, "Skeleton data must contain at least one keypoint"
        
        # 检查关键点和置信度分数数量匹配
        if len(data.keypoints) != len(data.confidence_scores):
            return False, "Keypoints and confidence scores count mismatch"
        
        # 检查置信度分数范围
        for i, score in enumerate(data.confidence_scores):
            if not 0.0 <= score <= 1.0:
                return False, f"Confidence score at index {i} out of range [0.0, 1.0]: {score}"
        
        # 检查关键点可见性
        for i, kp in enumerate(data.keypoints):
            if not 0.0 <= kp.visibility <= 1.0:
                return False, f"Keypoint visibility at index {i} out of range [0.0, 1.0]: {kp.visibility}"
        
        return True, ""
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_frailty_index(frailty: FrailtyIndex) -> Tuple[bool, str]:
    """
    验证衰弱指数的数据完整性
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # 检查用户ID
        if not frailty.user_id:
            return False, "User ID cannot be empty"
        
        # 检查分数范围
        if not 0.0 <= frailty.score <= 1.0:
            return False, f"Frailty score out of range [0.0, 1.0]: {frailty.score}"
        
        # 检查置信区间
        lower, upper = frailty.confidence_interval
        if not 0.0 <= lower <= upper <= 1.0:
            return False, f"Invalid confidence interval: ({lower}, {upper})"
        
        # 检查分数在置信区间内
        if not lower <= frailty.score <= upper:
            return False, f"Score {frailty.score} not within confidence interval ({lower}, {upper})"
        
        # 检查组件分数
        if not frailty.components:
            return False, "Frailty components cannot be empty"
        
        for component, value in frailty.components.items():
            if not 0.0 <= value <= 1.0:
                return False, f"Component '{component}' score out of range [0.0, 1.0]: {value}"
        
        return True, ""
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_incident_data(incident: IncidentData) -> Tuple[bool, str]:
    """
    验证事件数据的完整性
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # 检查必填字段
        if not incident.incident_id:
            return False, "Incident ID cannot be empty"
        
        if not incident.user_id:
            return False, "User ID cannot be empty"
        
        # 检查位置数据
        if not isinstance(incident.location, Location):
            return False, "Location must be a valid Location object"
        
        if not -90 <= incident.location.latitude <= 90:
            return False, f"Invalid latitude: {incident.location.latitude}"
        
        if not -180 <= incident.location.longitude <= 180:
            return False, f"Invalid longitude: {incident.location.longitude}"
        
        # 检查传感器数据
        if not isinstance(incident.sensor_data, dict):
            return False, "Sensor data must be a dictionary"
        
        # 检查时间戳
        if incident.timestamp > _utc_now_for(incident.timestamp):
            return False, "Incident timestamp cannot be in the future"
        
        return True, ""
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_risk_prediction(prediction: RiskPrediction) -> Tuple[bool, str]:
    """
    验证风险预测数据的完整性
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # 检查用户ID
        if not prediction.user_id:
            return False, "User ID cannot be empty"
        
        # 检查所有风险分数
        risk_scores = {
            "fall_risk_score": prediction.fall_risk_score,
            "medical_emergency_risk": prediction.medical_emergency_risk,
            "mobility_decline_risk": prediction.mobility_decline_risk,
            "confidence_level": prediction.confidence_level
        }
        
        for name, score in risk_scores.items():
            if not 0.0 <= score <= 1.0:
                return False, f"{name} out of range [0.0, 1.0]: {score}"
        
        # 检查贡献因素
        if not prediction.contributing_factors:
            return False, "Contributing factors cannot be empty"
        
        # 检查预测日期
        if prediction.prediction_date > _utc_now_for(prediction.prediction_date):
            return False, "Prediction date cannot be in the future"
        
        return True, ""
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_user_profile(profile: UserProfile) -> Tuple[bool, str]:
    """
    验证用户档案的完整性
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # 检查用户ID
        if not profile.user_id:
            return False, "User ID cannot be empty"
        
        # 检查年龄
        if not 0 <= profile.age <= 150:
            return False, f"Invalid age: {profile.age}"
        
        # 检查紧急联系人
        if not profile.emergency_contacts:
            return False, "At least one emergency contact is required"
        
        # 检查紧急联系人优先级唯一性
        priorities = [contact.priority for contact in profile.emergency_contacts]
        if len(priorities) != len(set(priorities)):
            return False, "Emergency contact priorities must be unique"
        
        # 验证每个紧急联系人
        for contact in profile.emergency_contacts:
            if not contact.name:
                return False, "Emergency contact name cannot be empty"
            if not contact.phone:
                return False, "Emergency contact phone cannot be empty"
            if contact.priority < 1:
                return False, f"Invalid priority: {contact.priority}"
        
        # 检查基线指标
        if profile.baseline_metrics.average_daily_steps < 0:
            return False, "Average daily steps cannot be negative"
        
        if not 0 <= profile.baseline_metrics.average_sleep_hours <= 24:
            return False, f"Invalid average sleep hours: {profile.baseline_metrics.average_sleep_hours}"
        
        if not 0.0 <= profile.baseline_metrics.baseline_mobility_score <= 1.0:
            return False, f"Invalid baseline mobility score: {profile.baseline_metrics.baseline_mobility_score}"
        
        return True, ""
    
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_privacy_compliance(data: Any) -> Tuple[bool, str]:
    """
    验证数据是否符合隐私保护要求
    
    Returns:
        Tuple[bool, str]: (is_compliant, error_message)
    
    Raises:
        ValueError: When skeleton data is not anonymized (for strict enforcement)
    """
    try:
        # 如果是骨骼数据，必须已匿名化
        if isinstance(data, SkeletonData):
            if not data.anonymized:
                # Raise ValueError for strict enforcement in production code
                raise ValueError("SkeletonData must be anonymized before transmission")
        
        # 检查是否包含敏感的生物识别信息
        if isinstance(data, dict):
            sensitive_keys = ['raw_video', 'facial_features', 'biometric_id', 'face_image']
            for key in sensitive_keys:
                if key in data:
                    return False, f"Data contains sensitive information: {key}"
        
        return True, ""
    
    except ValueError:
        # Re-raise ValueError for privacy violations
        raise
    except Exception as e:
        return False, f"Privacy validation error: {str(e)}"


def validate_data_integrity(data: Any, expected_type: type) -> Tuple[bool, str]:
    """
    验证数据类型和完整性
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # 检查类型
        if not isinstance(data, expected_type):
            return False, f"Expected type {expected_type.__name__}, got {type(data).__name__}"
        
        # 根据类型调用相应的验证函数
        if isinstance(data, SkeletonData):
            return validate_skeleton_data(data)
        elif isinstance(data, FrailtyIndex):
            return validate_frailty_index(data)
        elif isinstance(data, IncidentData):
            return validate_incident_data(data)
        elif isinstance(data, RiskPrediction):
            return validate_risk_prediction(data)
        elif isinstance(data, UserProfile):
            return validate_user_profile(data)
        
        return True, ""
    
    except Exception as e:
        return False, f"Data integrity validation error: {str(e)}"
