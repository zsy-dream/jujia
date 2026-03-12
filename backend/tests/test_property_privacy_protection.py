"""
属性测试：隐私保护视频处理
Property-Based Tests for Privacy-Preserving Video Processing

**验证属性1：隐私保护视频处理**
**Validates: Requirements 1.1, 1.2**

属性描述：
对于任何监控设备捕获的视频输入，系统应当仅提取骨骼姿态数据，
匿名化所有生物识别标识符，并且永不存储或传输原始视频数据。
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.schemas.core import (
    Keypoint, SkeletonData, JointType
)
from app.core.validation import (
    validate_skeleton_data, validate_privacy_compliance
)


# ============================================================================
# 策略定义 - Hypothesis Strategies
# ============================================================================

@st.composite
def valid_joint_type_strategy(draw):
    """生成有效的关节类型"""
    return draw(st.sampled_from(list(JointType)))


@st.composite
def valid_keypoint_strategy(draw):
    """生成有效的关键点数据"""
    joint_type = draw(valid_joint_type_strategy())
    x = draw(st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False))
    y = draw(st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False))
    z = draw(st.one_of(
        st.none(),
        st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
    ))
    visibility = draw(st.floats(min_value=0.0, max_value=1.0))
    
    return Keypoint(
        joint_type=joint_type,
        x=x,
        y=y,
        z=z,
        visibility=visibility
    )


@st.composite
def valid_skeleton_data_strategy(draw):
    """生成有效的骨骼数据（已匿名化）"""
    # 生成用户ID（非空字符串）
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        min_codepoint=48, max_codepoint=122
    )))
    
    # 生成时间戳（过去30天内）
    days_ago = draw(st.integers(min_value=0, max_value=30))
    timestamp = datetime.utcnow() - timedelta(days=days_ago)
    
    # 生成关键点列表（1-17个关键点，对应人体骨骼）
    num_keypoints = draw(st.integers(min_value=1, max_value=17))
    keypoints = draw(st.lists(
        valid_keypoint_strategy(),
        min_size=num_keypoints,
        max_size=num_keypoints
    ))
    
    # 生成匹配数量的置信度分数
    confidence_scores = draw(st.lists(
        st.floats(min_value=0.0, max_value=1.0),
        min_size=num_keypoints,
        max_size=num_keypoints
    ))
    
    # 必须已匿名化
    anonymized = True
    
    return SkeletonData(
        timestamp=timestamp,
        user_id=user_id,
        keypoints=keypoints,
        confidence_scores=confidence_scores,
        anonymized=anonymized
    )


@st.composite
def sensitive_data_dict_strategy(draw):
    """生成包含敏感信息的字典（用于测试隐私违规检测）"""
    sensitive_keys = ['raw_video', 'facial_features', 'biometric_id', 'face_image']
    selected_key = draw(st.sampled_from(sensitive_keys))
    
    data = {
        "user_id": draw(st.text(min_size=1, max_size=20)),
        selected_key: draw(st.text(min_size=10, max_size=100))
    }
    
    return data


# ============================================================================
# 属性1：隐私保护视频处理
# Property 1: Privacy-Preserving Video Processing
# ============================================================================

class TestPrivacyPreservingVideoProcessing:
    """
    **验证属性1：隐私保护视频处理**
    **Validates: Requirements 1.1, 1.2**
    
    验证系统对所有骨骼数据强制执行隐私保护：
    1. 所有骨骼数据必须已匿名化
    2. 不得包含原始视频或生物识别信息
    3. 数据验证必须通过
    """
    
    @given(skeleton_data=valid_skeleton_data_strategy())
    @settings(max_examples=100)
    def test_skeleton_data_must_be_anonymized(self, skeleton_data: SkeletonData):
        """
        属性：所有骨骼数据必须已匿名化
        
        对于任何有效的骨骼数据，anonymized标志必须为True。
        这确保系统永不传输未匿名化的数据。
        """
        # 验证：骨骼数据必须已匿名化
        assert skeleton_data.anonymized is True, \
            "All skeleton data must be anonymized before transmission"
        
        # 验证：隐私合规性检查必须通过
        is_compliant, error = validate_privacy_compliance(skeleton_data)
        assert is_compliant, f"Privacy compliance check failed: {error}"
    
    @given(skeleton_data=valid_skeleton_data_strategy())
    @settings(max_examples=100)
    def test_skeleton_data_validation_passes(self, skeleton_data: SkeletonData):
        """
        属性：所有有效的骨骼数据必须通过验证
        
        对于任何生成的有效骨骼数据，数据验证必须成功。
        这确保数据完整性和类型安全。
        """
        # 验证：数据验证必须通过
        is_valid, error = validate_skeleton_data(skeleton_data)
        assert is_valid, f"Skeleton data validation failed: {error}"
        
        # 验证：关键点和置信度分数数量匹配
        assert len(skeleton_data.keypoints) == len(skeleton_data.confidence_scores), \
            "Keypoints and confidence scores count must match"
        
        # 验证：所有置信度分数在有效范围内
        for i, score in enumerate(skeleton_data.confidence_scores):
            assert 0.0 <= score <= 1.0, \
                f"Confidence score at index {i} out of range: {score}"
    
    @given(skeleton_data=valid_skeleton_data_strategy())
    @settings(max_examples=100)
    def test_no_biometric_identifiers_in_skeleton_data(self, skeleton_data: SkeletonData):
        """
        属性：骨骼数据不得包含生物识别标识符
        
        对于任何骨骼数据，不应包含可识别个人身份的生物识别信息。
        骨骼数据仅包含关键点坐标和置信度分数。
        """
        # 验证：骨骼数据结构不包含敏感字段
        # SkeletonData只包含：timestamp, user_id, keypoints, confidence_scores, anonymized
        # 不包含：raw_video, facial_features, biometric_id, face_image等
        
        # 检查关键点数据
        for keypoint in skeleton_data.keypoints:
            # 关键点只包含位置和可见性信息
            assert hasattr(keypoint, 'joint_type')
            assert hasattr(keypoint, 'x')
            assert hasattr(keypoint, 'y')
            assert hasattr(keypoint, 'visibility')
            
            # 不应包含面部特征或其他生物识别信息
            assert not hasattr(keypoint, 'facial_features')
            assert not hasattr(keypoint, 'biometric_id')
            assert not hasattr(keypoint, 'face_image')
    
    @given(sensitive_data=sensitive_data_dict_strategy())
    @settings(max_examples=50)
    def test_sensitive_data_detection(self, sensitive_data: Dict[str, Any]):
        """
        属性：系统必须检测并拒绝包含敏感信息的数据
        
        对于任何包含敏感信息（raw_video, facial_features等）的数据，
        隐私合规性检查必须失败。
        """
        # 验证：包含敏感信息的数据必须被拒绝
        is_compliant, error = validate_privacy_compliance(sensitive_data)
        assert not is_compliant, \
            f"Privacy compliance should reject data with sensitive information: {sensitive_data}"
        assert "sensitive information" in error.lower(), \
            f"Error message should mention sensitive information: {error}"
    
    @given(
        user_id=st.text(min_size=1, max_size=50),
        num_keypoints=st.integers(min_value=1, max_value=17)
    )
    @settings(max_examples=100)
    def test_keypoints_and_scores_count_must_match(self, user_id: str, num_keypoints: int):
        """
        属性：关键点和置信度分数数量必须匹配
        
        对于任何骨骼数据，关键点列表和置信度分数列表的长度必须相同。
        不匹配的数据应在创建时被拒绝。
        """
        # 生成匹配数量的关键点和分数
        keypoints = [
            Keypoint(JointType.NOSE, 100.0 + i, 200.0 + i, visibility=0.9)
            for i in range(num_keypoints)
        ]
        confidence_scores = [0.9] * num_keypoints
        
        # 验证：匹配数量的数据应成功创建
        skeleton = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            keypoints=keypoints,
            confidence_scores=confidence_scores,
            anonymized=True
        )
        assert len(skeleton.keypoints) == len(skeleton.confidence_scores)
        
        # 验证：不匹配数量的数据应被拒绝
        mismatched_scores = [0.9] * (num_keypoints + 1)
        with pytest.raises(ValueError, match="must match"):
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id=user_id,
                keypoints=keypoints,
                confidence_scores=mismatched_scores,
                anonymized=True
            )
    
    @given(skeleton_data=valid_skeleton_data_strategy())
    @settings(max_examples=100)
    def test_confidence_scores_in_valid_range(self, skeleton_data: SkeletonData):
        """
        属性：所有置信度分数必须在[0.0, 1.0]范围内
        
        对于任何骨骼数据，所有置信度分数必须是有效的概率值。
        """
        # 验证：所有置信度分数在有效范围内
        for i, score in enumerate(skeleton_data.confidence_scores):
            assert 0.0 <= score <= 1.0, \
                f"Confidence score at index {i} must be in [0.0, 1.0], got {score}"
    
    @given(skeleton_data=valid_skeleton_data_strategy())
    @settings(max_examples=100)
    def test_keypoint_visibility_in_valid_range(self, skeleton_data: SkeletonData):
        """
        属性：所有关键点可见性必须在[0.0, 1.0]范围内
        
        对于任何骨骼数据，所有关键点的可见性值必须是有效的概率值。
        """
        # 验证：所有关键点可见性在有效范围内
        for i, keypoint in enumerate(skeleton_data.keypoints):
            assert 0.0 <= keypoint.visibility <= 1.0, \
                f"Keypoint visibility at index {i} must be in [0.0, 1.0], got {keypoint.visibility}"
    
    @given(
        user_id=st.text(min_size=1, max_size=50),
        num_keypoints=st.integers(min_value=1, max_value=17)
    )
    @settings(max_examples=50)
    def test_non_anonymized_data_rejected(self, user_id: str, num_keypoints: int):
        """
        属性：未匿名化的数据必须被拒绝
        
        对于任何尝试创建未匿名化骨骼数据的操作，系统必须拒绝。
        这是隐私保护的核心要求。
        """
        # 生成关键点和分数
        keypoints = [
            Keypoint(JointType.NOSE, 100.0 + i, 200.0 + i, visibility=0.9)
            for i in range(num_keypoints)
        ]
        confidence_scores = [0.9] * num_keypoints
        
        # 验证：尝试创建未匿名化数据应被拒绝
        with pytest.raises(ValueError, match="must be anonymized"):
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id=user_id,
                keypoints=keypoints,
                confidence_scores=confidence_scores,
                anonymized=False  # 未匿名化
            )
    
    @given(skeleton_data=valid_skeleton_data_strategy())
    @settings(max_examples=100)
    def test_user_id_not_empty(self, skeleton_data: SkeletonData):
        """
        属性：用户ID不能为空
        
        对于任何骨骼数据，必须包含有效的用户ID以进行数据关联。
        """
        # 验证：用户ID不为空
        assert skeleton_data.user_id, "User ID cannot be empty"
        assert len(skeleton_data.user_id) > 0, "User ID must have non-zero length"
    
    @given(skeleton_data=valid_skeleton_data_strategy())
    @settings(max_examples=100)
    def test_timestamp_not_in_future(self, skeleton_data: SkeletonData):
        """
        属性：时间戳不能在未来
        
        对于任何骨骼数据，时间戳应该是过去或当前时间，不能是未来时间。
        """
        # 验证：时间戳不在未来（允许1秒的时钟偏差）
        now = datetime.utcnow()
        assert skeleton_data.timestamp <= now + timedelta(seconds=1), \
            f"Timestamp cannot be in the future: {skeleton_data.timestamp} > {now}"


# ============================================================================
# 边界条件和错误处理测试
# Edge Cases and Error Handling Tests
# ============================================================================

class TestPrivacyProtectionEdgeCases:
    """
    测试隐私保护的边界条件和错误处理
    """
    
    def test_empty_user_id_rejected(self):
        """测试空用户ID被拒绝"""
        keypoints = [Keypoint(JointType.NOSE, 100.0, 200.0)]
        
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="",
                keypoints=keypoints,
                confidence_scores=[0.9],
                anonymized=True
            )
    
    def test_empty_keypoints_list(self):
        """测试空关键点列表"""
        skeleton = SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="user123",
            keypoints=[],
            confidence_scores=[],
            anonymized=True
        )
        
        # 验证会失败，因为没有关键点
        is_valid, error = validate_skeleton_data(skeleton)
        assert not is_valid
        assert "at least one keypoint" in error.lower()
    
    def test_invalid_confidence_score_rejected(self):
        """测试无效的置信度分数被拒绝"""
        keypoints = [Keypoint(JointType.NOSE, 100.0, 200.0)]
        
        # 置信度分数超出范围
        with pytest.raises(ValueError, match="Confidence score must be between"):
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="user123",
                keypoints=keypoints,
                confidence_scores=[1.5],  # 超出范围
                anonymized=True
            )
    
    def test_negative_z_coordinate_rejected(self):
        """测试负Z坐标被拒绝"""
        with pytest.raises(ValueError, match="Z coordinate cannot be negative"):
            Keypoint(
                joint_type=JointType.NOSE,
                x=100.0,
                y=200.0,
                z=-10.0  # 负值
            )
    
    def test_invalid_visibility_rejected(self):
        """测试无效的可见性值被拒绝"""
        with pytest.raises(ValueError, match="Visibility must be between"):
            Keypoint(
                joint_type=JointType.NOSE,
                x=100.0,
                y=200.0,
                visibility=1.5  # 超出范围
            )
