"""
多模态验证系统单元测试
Unit tests for Multi-Modal Verification System
"""
import pytest
from datetime import datetime
from app.services.multimodal_verifier import (
    MultiModalVerifier, SensorInput, SensorType, VerificationResult
)
from app.schemas.core import (
    SkeletonData, Keypoint, JointType, VerificationStatus
)


class TestMultiModalVerifier:
    """测试多模态验证器"""
    
    def test_verify_incident_with_visual_only(self):
        """测试仅使用视觉数据验证事件"""
        verifier = MultiModalVerifier()
        
        # 创建高置信度的视觉数据
        visual_data = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="user123",
            keypoints=[
                Keypoint(JointType.NOSE, 100, 100, visibility=0.9),
                Keypoint(JointType.LEFT_SHOULDER, 80, 120, visibility=0.85),
                Keypoint(JointType.RIGHT_SHOULDER, 120, 120, visibility=0.85),
            ],
            confidence_scores=[0.9, 0.85, 0.85],
            anonymized=True
        )
        
        result = verifier.verify_incident(visual_data=visual_data)
        
        assert isinstance(result, VerificationResult)
        assert result.confidence_score > 0.0
        assert len(result.sensor_inputs) == 1
        assert result.sensor_inputs[0].sensor_type == SensorType.VISUAL
    
    def test_verify_incident_with_audio_only(self):
        """测试仅使用音频数据验证事件"""
        verifier = MultiModalVerifier()
        
        # 创建音频数据
        audio_data = {
            "impact_detected": True,
            "distress_detected": False,
            "confidence": 0.8,
            "timestamp": datetime.utcnow()
        }
        
        result = verifier.verify_incident(audio_data=audio_data)
        
        assert isinstance(result, VerificationResult)
        assert result.confidence_score > 0.0
        assert len(result.sensor_inputs) == 1
        assert result.sensor_inputs[0].sensor_type == SensorType.AUDIO
    
    def test_verify_incident_multimodal(self):
        """测试多模态验证（视觉+音频）"""
        verifier = MultiModalVerifier()
        
        # 创建视觉数据
        visual_data = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="user123",
            keypoints=[
                Keypoint(JointType.NOSE, 100, 100, visibility=0.9),
                Keypoint(JointType.LEFT_SHOULDER, 80, 120, visibility=0.85),
            ],
            confidence_scores=[0.9, 0.85],
            anonymized=True
        )
        
        # 创建音频数据
        audio_data = {
            "impact_detected": True,
            "distress_detected": True,
            "confidence": 0.85,
            "timestamp": datetime.utcnow()
        }
        
        result = verifier.verify_incident(
            visual_data=visual_data,
            audio_data=audio_data
        )
        
        assert isinstance(result, VerificationResult)
        assert len(result.sensor_inputs) == 2
        assert result.confidence_score > 0.0
        # 多模态应该有更高的置信度
        assert result.consensus_details["sensor_count"] == 2
    
    def test_weighted_consensus_algorithm(self):
        """测试加权共识算法"""
        verifier = MultiModalVerifier()
        
        # 创建多个传感器输入
        sensor_inputs = [
            SensorInput(
                sensor_type=SensorType.VISUAL,
                confidence=0.9,
                data={"test": "visual"}
            ),
            SensorInput(
                sensor_type=SensorType.AUDIO,
                confidence=0.8,
                data={"test": "audio"}
            ),
            SensorInput(
                sensor_type=SensorType.MOTION,
                confidence=0.7,
                data={"test": "motion"}
            )
        ]
        
        consensus_score = verifier.assess_confidence_level(sensor_inputs)
        
        assert 0.0 <= consensus_score <= 1.0
        # 加权共识应该接近高置信度传感器
        assert consensus_score > 0.7
    
    def test_sensor_disagreement_detection(self):
        """测试传感器分歧检测"""
        verifier = MultiModalVerifier()
        
        # 创建有分歧的传感器输入
        sensor_inputs = [
            SensorInput(
                sensor_type=SensorType.VISUAL,
                confidence=0.9,  # 高置信度
                data={"test": "visual"}
            ),
            SensorInput(
                sensor_type=SensorType.AUDIO,
                confidence=0.2,  # 低置信度 - 分歧
                data={"test": "audio"}
            )
        ]
        
        consensus_score, details = verifier._calculate_weighted_consensus(sensor_inputs)
        
        assert details["disagreement_detected"] is True
        assert "consistency" in details
    
    def test_false_positive_detection(self):
        """测试误报检测"""
        verifier = MultiModalVerifier()
        
        # 创建低置信度数据（应该被识别为误报）
        visual_data = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="user123",
            keypoints=[
                Keypoint(JointType.NOSE, 100, 100, visibility=0.2),  # 低可见性
            ],
            confidence_scores=[0.2],  # 低置信度
            anonymized=True
        )
        
        audio_data = {
            "impact_detected": False,
            "distress_detected": False,
            "confidence": 0.1,
            "timestamp": datetime.utcnow()
        }
        
        result = verifier.verify_incident(
            visual_data=visual_data,
            audio_data=audio_data
        )
        
        assert result.false_positive_detected is True
        assert result.verification_status == VerificationStatus.FALSE_POSITIVE
        assert result.learning_data is not None
    
    def test_false_positive_learning(self):
        """测试误报学习机制"""
        verifier = MultiModalVerifier()
        
        # 记录多个误报
        for i in range(3):
            visual_data = SkeletonData(
                timestamp=datetime.utcnow(),
                user_id=f"user{i}",
                keypoints=[Keypoint(JointType.NOSE, 100, 100, visibility=0.2)],
                confidence_scores=[0.2],
                anonymized=True
            )
            
            result = verifier.verify_incident(visual_data=visual_data)
            assert result.false_positive_detected is True
        
        # 检查误报历史
        history = verifier.get_false_positive_history()
        assert len(history) == 3
        
        # 测试基于历史的误报减少
        historical_patterns = {"total_verifications": 10}
        adjustments = verifier.reduce_false_positives(historical_patterns)
        
        assert "adjusted_threshold" in adjustments
        assert "sensor_weights" in adjustments
        assert "false_positive_rate" in adjustments
        assert adjustments["false_positive_rate"] == 0.3  # 3/10
    
    def test_high_confidence_confirmation(self):
        """测试高置信度事件确认"""
        verifier = MultiModalVerifier()
        
        # 创建高置信度的多模态数据
        visual_data = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="user123",
            keypoints=[
                Keypoint(JointType.NOSE, 100, 100, visibility=0.95),
                Keypoint(JointType.LEFT_SHOULDER, 80, 120, visibility=0.9),
                Keypoint(JointType.RIGHT_SHOULDER, 120, 120, visibility=0.9),
            ],
            confidence_scores=[0.95, 0.9, 0.9],
            anonymized=True
        )
        
        audio_data = {
            "impact_detected": True,
            "distress_detected": True,
            "confidence": 0.9,
            "timestamp": datetime.utcnow()
        }
        
        result = verifier.verify_incident(
            visual_data=visual_data,
            audio_data=audio_data
        )
        
        assert result.is_confirmed is True
        assert result.verification_status == VerificationStatus.CONFIRMED
        assert result.confidence_score >= verifier.confirmation_threshold
    
    def test_custom_sensor_weights(self):
        """测试自定义传感器权重"""
        custom_weights = {
            SensorType.VISUAL: 0.5,
            SensorType.AUDIO: 0.5,
            SensorType.MOTION: 0.0,
            SensorType.ENVIRONMENTAL: 0.0
        }
        
        verifier = MultiModalVerifier(sensor_weights=custom_weights)
        
        assert verifier.sensor_weights == custom_weights
    
    def test_custom_confirmation_threshold(self):
        """测试自定义确认阈值"""
        custom_threshold = 0.8
        verifier = MultiModalVerifier(confirmation_threshold=custom_threshold)
        
        assert verifier.confirmation_threshold == custom_threshold
    
    def test_no_sensor_inputs(self):
        """测试没有传感器输入的情况"""
        verifier = MultiModalVerifier()
        
        result = verifier.verify_incident()
        
        assert result.is_confirmed is False
        assert result.verification_status == VerificationStatus.CANCELLED
        assert len(result.sensor_inputs) == 0
    
    def test_additional_sensors(self):
        """测试额外传感器输入"""
        verifier = MultiModalVerifier()
        
        additional_sensors = [
            SensorInput(
                sensor_type=SensorType.MOTION,
                confidence=0.75,
                data={"acceleration": "high"}
            ),
            SensorInput(
                sensor_type=SensorType.ENVIRONMENTAL,
                confidence=0.6,
                data={"temperature": "normal"}
            )
        ]
        
        result = verifier.verify_incident(additional_sensors=additional_sensors)
        
        assert len(result.sensor_inputs) == 2
        assert result.confidence_score > 0.0
    
    def test_visual_data_analysis(self):
        """测试视觉数据分析"""
        verifier = MultiModalVerifier()
        
        # 测试高可见性数据
        high_visibility_data = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="user123",
            keypoints=[
                Keypoint(JointType.NOSE, 100, 100, visibility=0.9),
                Keypoint(JointType.LEFT_SHOULDER, 80, 120, visibility=0.9),
            ],
            confidence_scores=[0.9, 0.9],
            anonymized=True
        )
        
        high_confidence = verifier._analyze_visual_data(high_visibility_data)
        
        # 测试低可见性数据
        low_visibility_data = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="user123",
            keypoints=[
                Keypoint(JointType.NOSE, 100, 100, visibility=0.2),
                Keypoint(JointType.LEFT_SHOULDER, 80, 120, visibility=0.2),
            ],
            confidence_scores=[0.9, 0.9],
            anonymized=True
        )
        
        low_confidence = verifier._analyze_visual_data(low_visibility_data)
        
        assert high_confidence > low_confidence
    
    def test_audio_data_analysis(self):
        """测试音频数据分析"""
        verifier = MultiModalVerifier()
        
        # 测试有冲击和求救声音
        high_confidence_audio = {
            "impact_detected": True,
            "distress_detected": True,
            "confidence": 0.7
        }
        
        high_confidence = verifier._analyze_audio_data(high_confidence_audio)
        
        # 测试无特殊声音
        low_confidence_audio = {
            "impact_detected": False,
            "distress_detected": False,
            "confidence": 0.5
        }
        
        low_confidence = verifier._analyze_audio_data(low_confidence_audio)
        
        assert high_confidence > low_confidence
    
    def test_sensor_weight_adjustment_after_false_positives(self):
        """测试误报后的传感器权重调整"""
        verifier = MultiModalVerifier()
        
        # 模拟多次视觉传感器误报
        for _ in range(5):
            sensor_inputs = [
                SensorInput(
                    sensor_type=SensorType.VISUAL,
                    confidence=0.2,
                    data={"test": "visual"}
                )
            ]
            verifier._record_false_positive(sensor_inputs, 0.2)
        
        historical_patterns = {"total_verifications": 10}
        adjustments = verifier.reduce_false_positives(historical_patterns)
        
        # 视觉传感器权重应该被降低
        original_visual_weight = verifier.DEFAULT_SENSOR_WEIGHTS[SensorType.VISUAL]
        adjusted_visual_weight = adjustments["sensor_weights"][SensorType.VISUAL]
        
        assert adjusted_visual_weight < original_visual_weight
        assert len(adjustments["recommendations"]) > 0
    
    def test_clear_false_positive_history(self):
        """测试清除误报历史"""
        verifier = MultiModalVerifier()
        
        # 添加一些误报记录
        sensor_inputs = [
            SensorInput(
                sensor_type=SensorType.VISUAL,
                confidence=0.2,
                data={"test": "visual"}
            )
        ]
        verifier._record_false_positive(sensor_inputs, 0.2)
        
        assert len(verifier.get_false_positive_history()) == 1
        
        verifier.clear_false_positive_history()
        
        assert len(verifier.get_false_positive_history()) == 0


class TestSensorInput:
    """测试传感器输入数据类"""
    
    def test_valid_sensor_input(self):
        """测试有效的传感器输入"""
        sensor_input = SensorInput(
            sensor_type=SensorType.VISUAL,
            confidence=0.8,
            data={"test": "data"}
        )
        
        assert sensor_input.sensor_type == SensorType.VISUAL
        assert sensor_input.confidence == 0.8
        assert sensor_input.data == {"test": "data"}
        assert isinstance(sensor_input.timestamp, datetime)
    
    def test_invalid_confidence_range(self):
        """测试无效的置信度范围"""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            SensorInput(
                sensor_type=SensorType.VISUAL,
                confidence=1.5,  # 超出范围
                data={"test": "data"}
            )
        
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            SensorInput(
                sensor_type=SensorType.VISUAL,
                confidence=-0.1,  # 负数
                data={"test": "data"}
            )
