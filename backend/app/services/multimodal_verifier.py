"""
多模态验证系统
Multi-Modal Verification System

实现需求4.1, 4.4, 4.3：
- 使用结合视觉和音频分析的多模态验证
- 当多个传感器意见不一致时使用加权共识算法
- 检测误报并记录事件以改进模型
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import statistics

from app.schemas.core import (
    SkeletonData, IncidentData, VerificationStatus
)


class SensorType(str, Enum):
    """传感器类型"""
    VISUAL = "visual"  # 视觉传感器（骨骼数据）
    AUDIO = "audio"  # 音频传感器
    MOTION = "motion"  # 运动传感器
    ENVIRONMENTAL = "environmental"  # 环境传感器


@dataclass
class SensorInput:
    """传感器输入数据"""
    sensor_type: SensorType
    confidence: float  # 0.0 到 1.0
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """验证传感器输入"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass
class VerificationResult:
    """验证结果"""
    is_confirmed: bool
    confidence_score: float
    verification_status: VerificationStatus
    sensor_inputs: List[SensorInput]
    consensus_details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    false_positive_detected: bool = False
    learning_data: Optional[Dict[str, Any]] = None


class MultiModalVerifier:
    """
    多模态验证器 - 结合多个传感器数据进行事件验证
    
    核心功能：
    1. 结合视觉和音频分析进行多模态验证
    2. 使用加权共识算法处理传感器分歧
    3. 检测误报并记录用于模型改进
    """
    
    # 传感器权重配置 - 不同传感器的可信度权重
    DEFAULT_SENSOR_WEIGHTS = {
        SensorType.VISUAL: 0.4,  # 视觉数据权重最高
        SensorType.AUDIO: 0.3,   # 音频数据次之
        SensorType.MOTION: 0.2,  # 运动传感器
        SensorType.ENVIRONMENTAL: 0.1  # 环境传感器权重最低
    }
    
    # 确认阈值 - 加权共识分数需要超过此值才能确认事件
    CONFIRMATION_THRESHOLD = 0.6
    
    # 误报检测阈值 - 低于此值认为是误报
    FALSE_POSITIVE_THRESHOLD = 0.3
    
    def __init__(
        self, 
        sensor_weights: Optional[Dict[SensorType, float]] = None,
        confirmation_threshold: float = CONFIRMATION_THRESHOLD
    ):
        """
        初始化多模态验证器
        
        Args:
            sensor_weights: 自定义传感器权重（可选）
            confirmation_threshold: 确认阈值（可选）
        """
        self.sensor_weights = sensor_weights or self.DEFAULT_SENSOR_WEIGHTS
        self.confirmation_threshold = confirmation_threshold
        self._false_positive_history: List[Dict[str, Any]] = []
    
    def verify_incident(
        self, 
        visual_data: Optional[SkeletonData] = None,
        audio_data: Optional[Dict[str, Any]] = None,
        additional_sensors: Optional[List[SensorInput]] = None
    ) -> VerificationResult:
        """
        验证事件 - 使用多模态数据进行验证
        
        Args:
            visual_data: 视觉骨骼数据（可选）
            audio_data: 音频分析数据（可选）
            additional_sensors: 其他传感器输入（可选）
            
        Returns:
            VerificationResult: 验证结果
        """
        sensor_inputs = []
        
        # 处理视觉数据
        if visual_data:
            visual_confidence = self._analyze_visual_data(visual_data)
            sensor_inputs.append(SensorInput(
                sensor_type=SensorType.VISUAL,
                confidence=visual_confidence,
                data={"skeleton_data": visual_data},
                timestamp=visual_data.timestamp
            ))
        
        # 处理音频数据
        if audio_data:
            audio_confidence = self._analyze_audio_data(audio_data)
            sensor_inputs.append(SensorInput(
                sensor_type=SensorType.AUDIO,
                confidence=audio_confidence,
                data=audio_data,
                timestamp=audio_data.get("timestamp", datetime.utcnow())
            ))
        
        # 添加其他传感器
        if additional_sensors:
            sensor_inputs.extend(additional_sensors)
        
        # 如果没有传感器输入，无法验证
        if not sensor_inputs:
            return VerificationResult(
                is_confirmed=False,
                confidence_score=0.0,
                verification_status=VerificationStatus.CANCELLED,
                sensor_inputs=[],
                consensus_details={"error": "No sensor inputs provided"}
            )
        
        # 计算加权共识
        consensus_score, consensus_details = self._calculate_weighted_consensus(sensor_inputs)
        
        # 确定验证状态
        is_confirmed = consensus_score >= self.confirmation_threshold
        false_positive_detected = consensus_score < self.FALSE_POSITIVE_THRESHOLD
        
        if false_positive_detected:
            verification_status = VerificationStatus.FALSE_POSITIVE
            learning_data = self._record_false_positive(sensor_inputs, consensus_score)
        elif is_confirmed:
            verification_status = VerificationStatus.CONFIRMED
            learning_data = None
        else:
            verification_status = VerificationStatus.PENDING
            learning_data = None
        
        return VerificationResult(
            is_confirmed=is_confirmed,
            confidence_score=consensus_score,
            verification_status=verification_status,
            sensor_inputs=sensor_inputs,
            consensus_details=consensus_details,
            false_positive_detected=false_positive_detected,
            learning_data=learning_data
        )
    
    def assess_confidence_level(
        self, 
        sensor_inputs: List[SensorInput]
    ) -> float:
        """
        评估传感器输入的置信度水平
        
        Args:
            sensor_inputs: 传感器输入列表
            
        Returns:
            float: 综合置信度分数（0.0 到 1.0）
        """
        if not sensor_inputs:
            return 0.0
        
        consensus_score, _ = self._calculate_weighted_consensus(sensor_inputs)
        return consensus_score
    
    def reduce_false_positives(
        self, 
        historical_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        基于历史模式减少误报
        
        Args:
            historical_patterns: 历史模式数据
            
        Returns:
            Dict[str, Any]: 调整后的验证参数
        """
        # 分析误报历史
        if not self._false_positive_history:
            return {
                "adjusted_threshold": self.confirmation_threshold,
                "sensor_weights": self.sensor_weights,
                "recommendations": []
            }
        
        # 计算误报率
        total_verifications = historical_patterns.get("total_verifications", 0)
        false_positive_count = len(self._false_positive_history)
        false_positive_rate = (
            false_positive_count / total_verifications 
            if total_verifications > 0 
            else 0.0
        )
        
        recommendations = []
        adjusted_threshold = self.confirmation_threshold
        adjusted_weights = self.sensor_weights.copy()
        
        # 如果误报率过高（>10%），提高确认阈值
        if false_positive_rate > 0.1:
            adjusted_threshold = min(0.8, self.confirmation_threshold + 0.1)
            recommendations.append(
                f"High false positive rate ({false_positive_rate:.2%}). "
                f"Increased confirmation threshold to {adjusted_threshold}"
            )
        
        # 分析哪些传感器导致误报
        sensor_false_positive_counts = {}
        for fp_record in self._false_positive_history:
            for sensor_input in fp_record.get("sensor_inputs", []):
                sensor_type = sensor_input.sensor_type
                sensor_false_positive_counts[sensor_type] = (
                    sensor_false_positive_counts.get(sensor_type, 0) + 1
                )
        
        # 降低频繁误报传感器的权重
        for sensor_type, fp_count in sensor_false_positive_counts.items():
            if fp_count > false_positive_count * 0.5:  # 超过50%的误报涉及此传感器
                if sensor_type in adjusted_weights:
                    adjusted_weights[sensor_type] *= 0.9  # 降低10%权重
                    recommendations.append(
                        f"Reduced weight for {sensor_type.value} sensor due to high false positive involvement"
                    )
        
        # 重新归一化权重
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            adjusted_weights = {
                k: v / total_weight 
                for k, v in adjusted_weights.items()
            }
        
        return {
            "adjusted_threshold": adjusted_threshold,
            "sensor_weights": adjusted_weights,
            "false_positive_rate": false_positive_rate,
            "recommendations": recommendations
        }
    
    def _calculate_weighted_consensus(
        self, 
        sensor_inputs: List[SensorInput]
    ) -> tuple[float, Dict[str, Any]]:
        """
        计算加权共识算法
        
        Args:
            sensor_inputs: 传感器输入列表
            
        Returns:
            tuple: (共识分数, 详细信息)
        """
        if not sensor_inputs:
            return 0.0, {"error": "No sensor inputs"}
        
        # 计算加权平均
        weighted_sum = 0.0
        total_weight = 0.0
        sensor_contributions = {}
        
        for sensor_input in sensor_inputs:
            weight = self.sensor_weights.get(sensor_input.sensor_type, 0.1)
            contribution = sensor_input.confidence * weight
            weighted_sum += contribution
            total_weight += weight
            
            sensor_contributions[sensor_input.sensor_type.value] = {
                "confidence": sensor_input.confidence,
                "weight": weight,
                "contribution": contribution
            }
        
        # 归一化共识分数
        consensus_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # 计算传感器一致性（标准差）
        confidences = [si.confidence for si in sensor_inputs]
        consistency = 1.0 - statistics.stdev(confidences) if len(confidences) > 1 else 1.0
        
        # 检测传感器分歧
        disagreement_detected = False
        if len(confidences) >= 2:
            max_diff = max(confidences) - min(confidences)
            if max_diff > 0.4:  # 如果最大差异超过0.4，认为存在分歧
                disagreement_detected = True
        
        consensus_details = {
            "consensus_score": consensus_score,
            "sensor_contributions": sensor_contributions,
            "consistency": consistency,
            "disagreement_detected": disagreement_detected,
            "sensor_count": len(sensor_inputs)
        }
        
        return consensus_score, consensus_details
    
    def _analyze_visual_data(self, visual_data: SkeletonData) -> float:
        """
        分析视觉骨骼数据
        
        Args:
            visual_data: 骨骼数据
            
        Returns:
            float: 视觉数据置信度
        """
        # 计算平均置信度分数
        if not visual_data.confidence_scores:
            return 0.0
        
        avg_confidence = statistics.mean(visual_data.confidence_scores)
        
        # 检查关键点可见性
        visible_keypoints = sum(
            1 for kp in visual_data.keypoints 
            if kp.visibility > 0.5
        )
        visibility_ratio = visible_keypoints / len(visual_data.keypoints) if visual_data.keypoints else 0.0
        
        # 综合置信度 = 平均置信度 * 可见性比例
        visual_confidence = avg_confidence * visibility_ratio
        
        return visual_confidence
    
    def _analyze_audio_data(self, audio_data: Dict[str, Any]) -> float:
        """
        分析音频数据
        
        Args:
            audio_data: 音频分析数据
            
        Returns:
            float: 音频数据置信度
        """
        # 从音频数据中提取置信度
        # 这里假设音频数据包含一些分析结果
        
        # 检查是否有跌倒相关的音频特征
        has_impact_sound = audio_data.get("impact_detected", False)
        has_distress_sound = audio_data.get("distress_detected", False)
        audio_confidence_raw = audio_data.get("confidence", 0.5)
        
        # 根据音频特征调整置信度
        confidence_boost = 0.0
        if has_impact_sound:
            confidence_boost += 0.2
        if has_distress_sound:
            confidence_boost += 0.2
        
        audio_confidence = min(1.0, audio_confidence_raw + confidence_boost)
        
        return audio_confidence
    
    def _record_false_positive(
        self, 
        sensor_inputs: List[SensorInput],
        consensus_score: float
    ) -> Dict[str, Any]:
        """
        记录误报事件用于模型改进
        
        Args:
            sensor_inputs: 传感器输入
            consensus_score: 共识分数
            
        Returns:
            Dict[str, Any]: 学习数据
        """
        learning_data = {
            "timestamp": datetime.utcnow(),
            "consensus_score": consensus_score,
            "sensor_inputs": sensor_inputs,
            "sensor_types": [si.sensor_type.value for si in sensor_inputs],
            "confidences": [si.confidence for si in sensor_inputs]
        }
        
        self._false_positive_history.append(learning_data)
        
        return learning_data
    
    def get_false_positive_history(self) -> List[Dict[str, Any]]:
        """获取误报历史记录"""
        return self._false_positive_history.copy()
    
    def clear_false_positive_history(self) -> None:
        """清除误报历史记录"""
        self._false_positive_history.clear()
