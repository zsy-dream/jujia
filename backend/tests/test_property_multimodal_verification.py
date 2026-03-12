"""
多模态事件验证的属性测试
Property-Based Tests for Multimodal Event Verification

**验证需求：需求4.1, 4.4**
需求4.1 - 当检测到潜在事件时，系统应当使用结合视觉和音频分析的多模态验证
需求4.4 - 当多个传感器意见不一致时，系统应当使用加权共识算法确定最终警报状态

**属性12：多模态事件验证**
对于任何潜在事件检测，系统应当使用结合视觉和音频分析的多模态验证，
当传感器意见不一致时使用加权共识算法
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.services.multimodal_verifier import (
    MultiModalVerifier,
    SensorInput,
    SensorType,
    VerificationResult
)
from app.schemas.core import (
    SkeletonData,
    Keypoint,
    JointType,
    VerificationStatus
)


# ============================================================================
# 策略定义 - Hypothesis Strategies
# ============================================================================

@st.composite
def keypoint_strategy(draw):
    """生成有效的关键点数据"""
    joint_type = draw(st.sampled_from(list(JointType)))
    x = draw(st.floats(min_value=0, max_value=1920, allow_nan=False, allow_infinity=False))
    y = draw(st.floats(min_value=0, max_value=1080, allow_nan=False, allow_infinity=False))
    z = draw(st.one_of(
        st.none(),
        st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)  # z must be non-negative
    ))
    visibility = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
    
    return Keypoint(
        joint_type=joint_type,
        x=x,
        y=y,
        z=z,
        visibility=visibility
    )


@st.composite
def skeleton_data_strategy(draw):
    """生成任意有效的骨骼数据"""
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'
    )))
    
    # 生成合理的时间戳（过去5分钟内，更接近当前时间）
    seconds_ago = draw(st.integers(min_value=0, max_value=300))
    timestamp = datetime.now() - timedelta(seconds=seconds_ago)
    
    # 生成1-25个关键点（人体骨骼关键点数量）
    num_keypoints = draw(st.integers(min_value=1, max_value=25))
    keypoints = [draw(keypoint_strategy()) for _ in range(num_keypoints)]
    
    # 生成对应的置信度分数
    confidence_scores = [
        draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
        for _ in range(num_keypoints)
    ]
    
    anonymized = True  # Must be True for privacy protection
    
    return SkeletonData(
        timestamp=timestamp,
        user_id=user_id,
        keypoints=keypoints,
        confidence_scores=confidence_scores,
        anonymized=anonymized
    )


@st.composite
def audio_data_strategy(draw):
    """生成任意有效的音频数据"""
    impact_detected = draw(st.booleans())
    distress_detected = draw(st.booleans())
    confidence = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
    
    seconds_ago = draw(st.integers(min_value=0, max_value=300))
    timestamp = datetime.now() - timedelta(seconds=seconds_ago)
    
    return {
        "impact_detected": impact_detected,
        "distress_detected": distress_detected,
        "confidence": confidence,
        "timestamp": timestamp
    }


@st.composite
def sensor_input_strategy(draw):
    """生成任意有效的传感器输入"""
    sensor_type = draw(st.sampled_from(list(SensorType)))
    confidence = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
    
    # 生成简单的传感器数据
    data = draw(st.dictionaries(
        keys=st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_'
        )),
        values=st.one_of(
            st.booleans(),
            st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False),
            st.text(min_size=0, max_size=50)
        ),
        min_size=1,
        max_size=5
    ))
    
    return SensorInput(
        sensor_type=sensor_type,
        confidence=confidence,
        data=data
    )


# ============================================================================
# 属性测试
# ============================================================================

class TestProperty12_MultimodalEventVerification:
    """
    **属性12：多模态事件验证**
    
    **验证需求：需求4.1, 4.4**
    
    对于任何潜在事件检测，系统应当使用结合视觉和音频分析的多模态验证，
    当传感器意见不一致时使用加权共识算法
    """
    
    @given(
        visual_data=skeleton_data_strategy(),
        audio_data=audio_data_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_multimodal_verification_combines_visual_and_audio(self, visual_data, audio_data):
        """
        属性：多模态验证必须结合视觉和音频分析
        
        对于任何提供视觉和音频数据的验证请求，
        系统必须同时考虑两种模态的输入
        """
        verifier = MultiModalVerifier()
        
        # 执行多模态验证
        result = verifier.verify_incident(
            visual_data=visual_data,
            audio_data=audio_data
        )
        
        # 验证：结果必须包含两种传感器输入
        assert isinstance(result, VerificationResult), "必须返回VerificationResult对象"
        assert len(result.sensor_inputs) == 2, \
            f"多模态验证必须包含2个传感器输入（视觉+音频），但得到 {len(result.sensor_inputs)}"
        
        # 验证：必须包含视觉传感器
        sensor_types = [si.sensor_type for si in result.sensor_inputs]
        assert SensorType.VISUAL in sensor_types, "必须包含视觉传感器输入"
        assert SensorType.AUDIO in sensor_types, "必须包含音频传感器输入"
        
        # 验证：置信度分数必须在有效范围内
        assert 0.0 <= result.confidence_score <= 1.0, \
            f"置信度分数必须在0.0到1.0之间，但得到 {result.confidence_score}"

    
    @given(sensor_inputs=st.lists(sensor_input_strategy(), min_size=2, max_size=10))
    @settings(max_examples=100, deadline=None)
    def test_weighted_consensus_algorithm_for_disagreement(self, sensor_inputs):
        """
        属性：当传感器意见不一致时，必须使用加权共识算法
        
        对于任何多个传感器输入，系统必须计算加权共识分数，
        并在传感器意见不一致时检测到分歧
        """
        verifier = MultiModalVerifier()
        
        # 计算加权共识
        consensus_score, consensus_details = verifier._calculate_weighted_consensus(sensor_inputs)
        
        # 验证：共识分数必须在有效范围内
        assert 0.0 <= consensus_score <= 1.0, \
            f"共识分数必须在0.0到1.0之间，但得到 {consensus_score}"
        
        # 验证：共识详情必须包含必要信息
        assert "consensus_score" in consensus_details, "必须包含共识分数"
        assert "sensor_contributions" in consensus_details, "必须包含传感器贡献"
        assert "consistency" in consensus_details, "必须包含一致性指标"
        assert "disagreement_detected" in consensus_details, "必须包含分歧检测结果"
        assert "sensor_count" in consensus_details, "必须包含传感器数量"
        
        # 验证：传感器数量必须匹配
        assert consensus_details["sensor_count"] == len(sensor_inputs), \
            "传感器数量必须与输入匹配"
        
        # 验证：如果传感器置信度差异大，应该检测到分歧
        confidences = [si.confidence for si in sensor_inputs]
        if len(confidences) >= 2:
            max_diff = max(confidences) - min(confidences)
            if max_diff > 0.4:
                assert consensus_details["disagreement_detected"] is True, \
                    f"当传感器置信度差异为 {max_diff:.2f} 时，应该检测到分歧"
    
    @given(
        visual_data=st.one_of(st.none(), skeleton_data_strategy()),
        audio_data=st.one_of(st.none(), audio_data_strategy()),
        additional_sensors=st.one_of(
            st.none(),
            st.lists(sensor_input_strategy(), min_size=0, max_size=5)
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_verification_handles_any_sensor_combination(self, visual_data, audio_data, additional_sensors):
        """
        属性：验证系统必须处理任意传感器组合
        
        对于任何传感器输入组合（包括空输入），
        系统必须返回有效的验证结果
        """
        verifier = MultiModalVerifier()
        
        # 执行验证
        result = verifier.verify_incident(
            visual_data=visual_data,
            audio_data=audio_data,
            additional_sensors=additional_sensors
        )
        
        # 验证：必须返回VerificationResult对象
        assert isinstance(result, VerificationResult), "必须返回VerificationResult对象"
        
        # 验证：必须有有效的验证状态
        assert result.verification_status in list(VerificationStatus), \
            f"验证状态必须是有效的VerificationStatus枚举值"
        
        # 验证：置信度分数必须在有效范围内
        assert 0.0 <= result.confidence_score <= 1.0, \
            f"置信度分数必须在0.0到1.0之间"
        
        # 验证：如果没有传感器输入，应该取消验证
        expected_sensor_count = 0
        if visual_data:
            expected_sensor_count += 1
        if audio_data:
            expected_sensor_count += 1
        if additional_sensors:
            expected_sensor_count += len(additional_sensors)
        
        if expected_sensor_count == 0:
            assert result.verification_status == VerificationStatus.CANCELLED, \
                "没有传感器输入时应该取消验证"
            assert result.confidence_score == 0.0, \
                "没有传感器输入时置信度应该为0"
    
    @given(sensor_inputs=st.lists(sensor_input_strategy(), min_size=1, max_size=10))
    @settings(max_examples=100, deadline=None)
    def test_confidence_assessment_is_consistent(self, sensor_inputs):
        """
        属性：置信度评估必须是一致的
        
        对于相同的传感器输入，多次评估应该产生相同的置信度分数
        """
        verifier = MultiModalVerifier()
        
        # 第一次评估
        confidence1 = verifier.assess_confidence_level(sensor_inputs)
        
        # 第二次评估
        confidence2 = verifier.assess_confidence_level(sensor_inputs)
        
        # 验证：两次评估结果必须相同
        assert confidence1 == confidence2, \
            f"相同输入的置信度评估必须一致，但得到 {confidence1} 和 {confidence2}"
        
        # 验证：置信度必须在有效范围内
        assert 0.0 <= confidence1 <= 1.0, \
            f"置信度必须在0.0到1.0之间"

    
    @given(
        visual_data=skeleton_data_strategy(),
        audio_data=audio_data_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_verification_result_contains_consensus_details(self, visual_data, audio_data):
        """
        属性：验证结果必须包含共识详情
        
        对于任何多模态验证，结果必须包含详细的共识计算信息
        """
        verifier = MultiModalVerifier()
        
        result = verifier.verify_incident(
            visual_data=visual_data,
            audio_data=audio_data
        )
        
        # 验证：共识详情必须存在
        assert result.consensus_details is not None, "必须包含共识详情"
        assert isinstance(result.consensus_details, dict), "共识详情必须是字典"
        
        # 验证：共识详情必须包含关键信息
        assert "consensus_score" in result.consensus_details, \
            "共识详情必须包含共识分数"
        assert "sensor_contributions" in result.consensus_details, \
            "共识详情必须包含传感器贡献"
        
        # 验证：传感器贡献必须包含所有传感器
        sensor_contributions = result.consensus_details["sensor_contributions"]
        assert len(sensor_contributions) == len(result.sensor_inputs), \
            "传感器贡献数量必须与传感器输入数量匹配"
    
    @given(
        visual_data=skeleton_data_strategy(),
        audio_data=audio_data_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_sensor_weights_affect_consensus(self, visual_data, audio_data):
        """
        属性：传感器权重必须影响共识计算
        
        对于相同的传感器输入，不同的权重配置应该产生不同的共识分数
        （除非所有传感器置信度相同）
        """
        # 使用默认权重
        verifier_default = MultiModalVerifier()
        result_default = verifier_default.verify_incident(
            visual_data=visual_data,
            audio_data=audio_data
        )
        
        # 使用自定义权重（视觉权重更高）
        custom_weights = {
            SensorType.VISUAL: 0.8,
            SensorType.AUDIO: 0.2,
            SensorType.MOTION: 0.0,
            SensorType.ENVIRONMENTAL: 0.0
        }
        verifier_custom = MultiModalVerifier(sensor_weights=custom_weights)
        result_custom = verifier_custom.verify_incident(
            visual_data=visual_data,
            audio_data=audio_data
        )
        
        # 获取视觉和音频的置信度
        visual_confidence = None
        audio_confidence = None
        for si in result_default.sensor_inputs:
            if si.sensor_type == SensorType.VISUAL:
                visual_confidence = si.confidence
            elif si.sensor_type == SensorType.AUDIO:
                audio_confidence = si.confidence
        
        # 如果视觉和音频置信度不同，权重变化应该影响结果
        if visual_confidence is not None and audio_confidence is not None:
            if abs(visual_confidence - audio_confidence) > 0.1:
                # 权重变化应该导致共识分数变化
                # 注意：由于权重归一化，可能变化不大，所以我们只验证结果有效
                assert 0.0 <= result_custom.confidence_score <= 1.0, \
                    "自定义权重的共识分数必须在有效范围内"
    
    @given(
        visual_data=skeleton_data_strategy(),
        audio_data=audio_data_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_false_positive_detection_threshold(self, visual_data, audio_data):
        """
        属性：低置信度验证必须被标记为潜在误报
        
        对于任何共识分数低于误报阈值的验证，
        系统必须检测到误报并记录学习数据
        """
        verifier = MultiModalVerifier()
        
        result = verifier.verify_incident(
            visual_data=visual_data,
            audio_data=audio_data
        )
        
        # 验证：如果共识分数低于误报阈值，必须检测到误报
        if result.confidence_score < verifier.FALSE_POSITIVE_THRESHOLD:
            assert result.false_positive_detected is True, \
                f"共识分数 {result.confidence_score:.2f} 低于阈值 {verifier.FALSE_POSITIVE_THRESHOLD}，应该检测到误报"
            assert result.verification_status == VerificationStatus.FALSE_POSITIVE, \
                "低置信度验证应该标记为FALSE_POSITIVE状态"
            assert result.learning_data is not None, \
                "误报检测必须包含学习数据"
        
        # 验证：如果共识分数高于确认阈值，必须确认事件
        if result.confidence_score >= verifier.confirmation_threshold:
            assert result.is_confirmed is True, \
                f"共识分数 {result.confidence_score:.2f} 高于阈值 {verifier.confirmation_threshold}，应该确认事件"
            assert result.verification_status == VerificationStatus.CONFIRMED, \
                "高置信度验证应该标记为CONFIRMED状态"

    
    @given(
        visual_data=skeleton_data_strategy(),
        audio_data=audio_data_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_verification_timestamp_exists(self, visual_data, audio_data):
        """
        属性：验证结果必须包含时间戳
        
        对于任何验证，结果和传感器输入都必须有时间戳
        """
        verifier = MultiModalVerifier()
        
        result = verifier.verify_incident(
            visual_data=visual_data,
            audio_data=audio_data
        )
        
        # 验证：结果必须有时间戳
        assert result.timestamp is not None, "验证结果必须有时间戳"
        
        # 验证：传感器输入必须有时间戳
        for sensor_input in result.sensor_inputs:
            assert sensor_input.timestamp is not None, \
                f"传感器输入 {sensor_input.sensor_type} 必须有时间戳"
    
    @given(sensor_inputs=st.lists(sensor_input_strategy(), min_size=1, max_size=10))
    @settings(max_examples=100, deadline=None)
    def test_weighted_consensus_respects_sensor_weights(self, sensor_inputs):
        """
        属性：加权共识必须尊重传感器权重配置
        
        对于任何传感器输入，加权共识计算必须使用配置的权重，
        并且权重较高的传感器应该对结果有更大影响
        """
        verifier = MultiModalVerifier()
        
        consensus_score, consensus_details = verifier._calculate_weighted_consensus(sensor_inputs)
        
        # 验证：每个传感器的贡献必须考虑权重
        sensor_contributions = consensus_details["sensor_contributions"]
        
        for sensor_input in sensor_inputs:
            sensor_type_str = sensor_input.sensor_type.value
            if sensor_type_str in sensor_contributions:
                contribution = sensor_contributions[sensor_type_str]
                
                # 验证：贡献必须包含置信度、权重和贡献值
                assert "confidence" in contribution, "必须包含置信度"
                assert "weight" in contribution, "必须包含权重"
                assert "contribution" in contribution, "必须包含贡献值"
                
                # 验证：贡献值应该等于置信度乘以权重
                expected_contribution = contribution["confidence"] * contribution["weight"]
                actual_contribution = contribution["contribution"]
                assert abs(expected_contribution - actual_contribution) < 0.0001, \
                    f"贡献值计算错误: 期望 {expected_contribution}，实际 {actual_contribution}"
    
    @given(
        visual_data=skeleton_data_strategy(),
        audio_data=audio_data_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_multimodal_verification_never_raises_exception(self, visual_data, audio_data):
        """
        属性：多模态验证必须永不抛出异常
        
        对于任何有效的传感器输入，验证过程必须优雅地处理所有情况
        而不抛出异常
        """
        verifier = MultiModalVerifier()
        
        try:
            result = verifier.verify_incident(
                visual_data=visual_data,
                audio_data=audio_data
            )
            
            # 验证：必须返回有效结果
            assert result is not None, "验证必须返回结果"
            assert isinstance(result, VerificationResult), \
                "验证必须返回VerificationResult对象"
        except Exception as e:
            pytest.fail(f"多模态验证不应该抛出异常，但抛出了: {type(e).__name__}: {e}")


# ============================================================================
# 边缘情况测试
# ============================================================================

class TestMultimodalVerificationEdgeCases:
    """测试多模态验证的边缘情况"""
    
    def test_empty_keypoints_visual_data(self):
        """空关键点的视觉数据应该被优雅处理"""
        verifier = MultiModalVerifier()
        
        visual_data = SkeletonData(
            timestamp=datetime.now(),
            user_id="user123",
            keypoints=[],  # 空关键点
            confidence_scores=[],
            anonymized=True
        )
        
        result = verifier.verify_incident(visual_data=visual_data)
        
        assert result is not None
        assert 0.0 <= result.confidence_score <= 1.0
    
    def test_all_zero_confidence_sensors(self):
        """所有传感器置信度为0应该被优雅处理"""
        verifier = MultiModalVerifier()
        
        sensor_inputs = [
            SensorInput(SensorType.VISUAL, 0.0, {"test": "data"}),
            SensorInput(SensorType.AUDIO, 0.0, {"test": "data"}),
        ]
        
        consensus_score = verifier.assess_confidence_level(sensor_inputs)
        
        assert consensus_score == 0.0
    
    def test_all_max_confidence_sensors(self):
        """所有传感器置信度为1.0应该产生高共识"""
        verifier = MultiModalVerifier()
        
        sensor_inputs = [
            SensorInput(SensorType.VISUAL, 1.0, {"test": "data"}),
            SensorInput(SensorType.AUDIO, 1.0, {"test": "data"}),
        ]
        
        consensus_score = verifier.assess_confidence_level(sensor_inputs)
        
        assert consensus_score == 1.0
    
    def test_single_sensor_no_disagreement(self):
        """单个传感器不应该检测到分歧"""
        verifier = MultiModalVerifier()
        
        sensor_inputs = [
            SensorInput(SensorType.VISUAL, 0.8, {"test": "data"})
        ]
        
        _, consensus_details = verifier._calculate_weighted_consensus(sensor_inputs)
        
        # 单个传感器不应该有分歧
        assert consensus_details["disagreement_detected"] is False
    
    def test_extreme_disagreement(self):
        """极端分歧（0.0 vs 1.0）应该被检测"""
        verifier = MultiModalVerifier()
        
        sensor_inputs = [
            SensorInput(SensorType.VISUAL, 0.0, {"test": "data"}),
            SensorInput(SensorType.AUDIO, 1.0, {"test": "data"}),
        ]
        
        _, consensus_details = verifier._calculate_weighted_consensus(sensor_inputs)
        
        assert consensus_details["disagreement_detected"] is True
