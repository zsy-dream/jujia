"""
属性测试：衰弱指数计算
Property-Based Tests for Frailty Index Calculation

**验证属性：衰弱指数计算**
**Validates: Requirements 3.1, 3.3**

属性描述：
对于任何日常活动数据收集，风险引擎应当使用经过验证的精算模型计算更新的衰弱指数分数，
并纳入移动模式、睡眠质量和活动水平。
"""
import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime, timedelta
from typing import List

from app.schemas.core import (
    Keypoint, SkeletonData, JointType, FrailtyIndex
)
from app.services.actuarial_risk_engine import (
    ActuarialRiskEngine, FrailtyCalculator, ActivityData
)


# ============================================================================
# 策略定义 - Hypothesis Strategies
# ============================================================================

@st.composite
def valid_keypoint_strategy(draw):
    """生成有效的关键点数据"""
    joint_type = draw(st.sampled_from(list(JointType)))
    x = draw(st.floats(min_value=0.0, max_value=1920.0, allow_nan=False, allow_infinity=False))
    y = draw(st.floats(min_value=0.0, max_value=1080.0, allow_nan=False, allow_infinity=False))
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
    """Generate valid skeleton data"""
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        min_codepoint=48, max_codepoint=122
    )))
    
    days_ago = draw(st.integers(min_value=0, max_value=30))
    timestamp = datetime.utcnow() - timedelta(days=days_ago)
    
    # Generate 17 keypoints (standard human skeleton)
    num_keypoints = 17
    keypoints = draw(st.lists(
        valid_keypoint_strategy(),
        min_size=num_keypoints,
        max_size=num_keypoints
    ))
    
    confidence_scores = draw(st.lists(
        st.floats(min_value=0.0, max_value=1.0),
        min_size=num_keypoints,
        max_size=num_keypoints
    ))
    
    return SkeletonData(
        timestamp=timestamp,
        user_id=user_id,
        keypoints=keypoints,
        confidence_scores=confidence_scores,
        anonymized=True
    )


@st.composite
def valid_activity_data_strategy(draw):
    """Generate valid activity data"""
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        min_codepoint=48, max_codepoint=122
    )))
    
    days_ago = draw(st.integers(min_value=0, max_value=30))
    date = datetime.utcnow() - timedelta(days=days_ago)
    
    # Generate reasonable activity data
    steps_count = draw(st.integers(min_value=0, max_value=20000))
    active_minutes = draw(st.integers(min_value=0, max_value=300))
    sleep_hours = draw(st.floats(min_value=0.0, max_value=14.0))
    
    return ActivityData(
        user_id=user_id,
        date=date,
        steps_count=steps_count,
        active_minutes=active_minutes,
        sleep_hours=sleep_hours
    )


# ============================================================================
# 属性：衰弱指数计算
# Property 8: Frailty Index Calculation
# ============================================================================

class TestFrailtyIndexCalculation:
    """
    **验证属性：衰弱指数计算**
    **Validates: Requirements 3.1, 3.3**
    
    验证风险引擎对所有活动数据正确计算衰弱指数：
    1. 衰弱指数必须在有效范围[0.0, 1.0]内
    2. 必须纳入移动模式、睡眠质量和活动水平
    3. 必须提供置信区间
    4. 计算必须使用经过验证的精算模型
    """
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=1, max_size=10),
        activity_data=st.lists(valid_activity_data_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_frailty_index_in_valid_range(
        self,
        skeleton_data: List[SkeletonData],
        activity_data: List[ActivityData]
    ):
        """
        属性：衰弱指数必须在[0.0, 1.0]范围内
        
        对于任何有效的骨骼数据和活动数据，计算的衰弱指数分数
        必须在有效范围内（0.0表示最衰弱，1.0表示最健康）。
        """
        # 确保所有数据使用相同的user_id
        user_id = skeleton_data[0].user_id
        for data in skeleton_data:
            data.user_id = user_id
        for data in activity_data:
            data.user_id = user_id
        
        # 创建风险引擎并计算衰弱指数
        engine = ActuarialRiskEngine()
        frailty_index = engine.calculate_frailty_index(
            user_id=user_id,
            skeleton_data=skeleton_data,
            activity_data=activity_data
        )
        
        # 验证：衰弱指数分数在有效范围内
        assert 0.0 <= frailty_index.score <= 1.0, \
            f"Frailty index score must be in [0.0, 1.0], got {frailty_index.score}"
        
        # 验证：置信区间边界也在有效范围内
        lower, upper = frailty_index.confidence_interval
        assert 0.0 <= lower <= 1.0, \
            f"Confidence interval lower bound must be in [0.0, 1.0], got {lower}"
        assert 0.0 <= upper <= 1.0, \
            f"Confidence interval upper bound must be in [0.0, 1.0], got {upper}"
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=1, max_size=10),
        activity_data=st.lists(valid_activity_data_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_frailty_index_incorporates_all_components(
        self,
        skeleton_data: List[SkeletonData],
        activity_data: List[ActivityData]
    ):
        """
        属性：衰弱指数必须纳入移动模式、睡眠质量和活动水平
        
        对于任何活动数据，计算的衰弱指数必须包含所有三个核心组件：
        - 移动性评分（mobility）
        - 活动水平评分（activity）
        - 睡眠质量评分（sleep）
        
        **Validates: Requirements 3.1, 3.3**
        """
        # 确保所有数据使用相同的user_id
        user_id = skeleton_data[0].user_id
        for data in skeleton_data:
            data.user_id = user_id
        for data in activity_data:
            data.user_id = user_id
        
        # 创建风险引擎并计算衰弱指数
        engine = ActuarialRiskEngine()
        frailty_index = engine.calculate_frailty_index(
            user_id=user_id,
            skeleton_data=skeleton_data,
            activity_data=activity_data
        )
        
        # 验证：必须包含所有核心组件
        assert "mobility" in frailty_index.components, \
            "Frailty index must include mobility component"
        assert "activity" in frailty_index.components, \
            "Frailty index must include activity component"
        assert "sleep" in frailty_index.components, \
            "Frailty index must include sleep component"
        
        # 验证：所有组件分数在有效范围内
        assert 0.0 <= frailty_index.components["mobility"] <= 1.0, \
            f"Mobility score must be in [0.0, 1.0], got {frailty_index.components['mobility']}"
        assert 0.0 <= frailty_index.components["activity"] <= 1.0, \
            f"Activity score must be in [0.0, 1.0], got {frailty_index.components['activity']}"
        assert 0.0 <= frailty_index.components["sleep"] <= 1.0, \
            f"Sleep score must be in [0.0, 1.0], got {frailty_index.components['sleep']}"
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=1, max_size=10),
        activity_data=st.lists(valid_activity_data_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_frailty_index_includes_mobility_patterns(
        self,
        skeleton_data: List[SkeletonData],
        activity_data: List[ActivityData]
    ):
        """
        属性：衰弱指数必须包含移动模式分析
        
        对于任何骨骼数据，衰弱指数必须包含详细的移动模式组件：
        - 步态稳定性（gait_stability）
        - 运动范围（movement_range）
        - 平衡质量（balance_quality）
        
        **Validates: Requirements 3.3**
        """
        # 确保所有数据使用相同的user_id
        user_id = skeleton_data[0].user_id
        for data in skeleton_data:
            data.user_id = user_id
        for data in activity_data:
            data.user_id = user_id
        
        # 创建风险引擎并计算衰弱指数
        engine = ActuarialRiskEngine()
        frailty_index = engine.calculate_frailty_index(
            user_id=user_id,
            skeleton_data=skeleton_data,
            activity_data=activity_data
        )
        
        # 验证：必须包含移动模式组件
        assert "gait_stability" in frailty_index.components, \
            "Frailty index must include gait stability"
        assert "movement_range" in frailty_index.components, \
            "Frailty index must include movement range"
        assert "balance_quality" in frailty_index.components, \
            "Frailty index must include balance quality"
        
        # 验证：所有移动模式组件在有效范围内
        assert 0.0 <= frailty_index.components["gait_stability"] <= 1.0
        assert 0.0 <= frailty_index.components["movement_range"] <= 1.0
        assert 0.0 <= frailty_index.components["balance_quality"] <= 1.0
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=1, max_size=10),
        activity_data=st.lists(valid_activity_data_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_frailty_index_includes_activity_levels(
        self,
        skeleton_data: List[SkeletonData],
        activity_data: List[ActivityData]
    ):
        """
        属性：衰弱指数必须包含活动水平分析
        
        对于任何活动数据，衰弱指数必须包含详细的活动水平组件：
        - 每日步数比率（daily_steps_ratio）
        - 活动时间比率（active_time_ratio）
        
        **Validates: Requirements 3.3**
        """
        # 确保所有数据使用相同的user_id
        user_id = skeleton_data[0].user_id
        for data in skeleton_data:
            data.user_id = user_id
        for data in activity_data:
            data.user_id = user_id
        
        # 创建风险引擎并计算衰弱指数
        engine = ActuarialRiskEngine()
        frailty_index = engine.calculate_frailty_index(
            user_id=user_id,
            skeleton_data=skeleton_data,
            activity_data=activity_data
        )
        
        # 验证：必须包含活动水平组件
        assert "daily_steps_ratio" in frailty_index.components, \
            "Frailty index must include daily steps ratio"
        assert "active_time_ratio" in frailty_index.components, \
            "Frailty index must include active time ratio"
        
        # 验证：活动水平组件在有效范围内
        assert 0.0 <= frailty_index.components["daily_steps_ratio"] <= 1.0
        assert 0.0 <= frailty_index.components["active_time_ratio"] <= 1.0
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=1, max_size=10),
        activity_data=st.lists(valid_activity_data_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_frailty_index_includes_sleep_quality(
        self,
        skeleton_data: List[SkeletonData],
        activity_data: List[ActivityData]
    ):
        """
        属性：衰弱指数必须包含睡眠质量分析
        
        对于任何活动数据，衰弱指数必须包含详细的睡眠质量组件：
        - 睡眠时长评分（sleep_duration）
        - 睡眠规律性（sleep_regularity）
        
        **Validates: Requirements 3.3**
        """
        # 确保所有数据使用相同的user_id
        user_id = skeleton_data[0].user_id
        for data in skeleton_data:
            data.user_id = user_id
        for data in activity_data:
            data.user_id = user_id
        
        # 创建风险引擎并计算衰弱指数
        engine = ActuarialRiskEngine()
        frailty_index = engine.calculate_frailty_index(
            user_id=user_id,
            skeleton_data=skeleton_data,
            activity_data=activity_data
        )
        
        # 验证：必须包含睡眠质量组件
        assert "sleep_duration" in frailty_index.components, \
            "Frailty index must include sleep duration score"
        assert "sleep_regularity" in frailty_index.components, \
            "Frailty index must include sleep regularity"
        
        # 验证：睡眠质量组件在有效范围内
        assert 0.0 <= frailty_index.components["sleep_duration"] <= 1.0
        assert 0.0 <= frailty_index.components["sleep_regularity"] <= 1.0
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=1, max_size=10),
        activity_data=st.lists(valid_activity_data_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_frailty_index_provides_confidence_interval(
        self,
        skeleton_data: List[SkeletonData],
        activity_data: List[ActivityData]
    ):
        """
        属性：衰弱指数必须提供置信区间
        
        对于任何活动数据，计算的衰弱指数必须包含置信区间，
        且置信区间必须合理（下界 <= 分数 <= 上界）。
        
        **Validates: Requirements 3.1**
        """
        # 确保所有数据使用相同的user_id
        user_id = skeleton_data[0].user_id
        for data in skeleton_data:
            data.user_id = user_id
        for data in activity_data:
            data.user_id = user_id
        
        # 创建风险引擎并计算衰弱指数
        engine = ActuarialRiskEngine()
        frailty_index = engine.calculate_frailty_index(
            user_id=user_id,
            skeleton_data=skeleton_data,
            activity_data=activity_data
        )
        
        # 验证：必须提供置信区间
        assert frailty_index.confidence_interval is not None, \
            "Frailty index must provide confidence interval"
        
        lower, upper = frailty_index.confidence_interval
        
        # 验证：置信区间必须合理
        assert lower <= frailty_index.score <= upper, \
            f"Score {frailty_index.score} must be within confidence interval [{lower}, {upper}]"
        
        # 验证：置信区间宽度合理（不能太宽）
        ci_width = upper - lower
        assert ci_width <= 0.5, \
            f"Confidence interval width {ci_width} is too large (max 0.5)"
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=1, max_size=10),
        activity_data=st.lists(valid_activity_data_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_frailty_index_user_id_matches(
        self,
        skeleton_data: List[SkeletonData],
        activity_data: List[ActivityData]
    ):
        """
        属性：衰弱指数的用户ID必须匹配输入
        
        对于任何活动数据，计算的衰弱指数必须包含正确的用户ID。
        """
        # 确保所有数据使用相同的user_id
        user_id = skeleton_data[0].user_id
        for data in skeleton_data:
            data.user_id = user_id
        for data in activity_data:
            data.user_id = user_id
        
        # 创建风险引擎并计算衰弱指数
        engine = ActuarialRiskEngine()
        frailty_index = engine.calculate_frailty_index(
            user_id=user_id,
            skeleton_data=skeleton_data,
            activity_data=activity_data
        )
        
        # 验证：用户ID匹配
        assert frailty_index.user_id == user_id, \
            f"Frailty index user_id {frailty_index.user_id} must match input {user_id}"
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=1, max_size=10),
        activity_data=st.lists(valid_activity_data_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_frailty_index_calculation_date_reasonable(
        self,
        skeleton_data: List[SkeletonData],
        activity_data: List[ActivityData]
    ):
        """
        属性：衰弱指数的计算日期必须合理
        
        对于任何活动数据，计算的衰弱指数的计算日期应该是当前时间或最近时间。
        """
        # 确保所有数据使用相同的user_id
        user_id = skeleton_data[0].user_id
        for data in skeleton_data:
            data.user_id = user_id
        for data in activity_data:
            data.user_id = user_id
        
        # 记录计算前的时间
        before_calculation = datetime.utcnow()
        
        # 创建风险引擎并计算衰弱指数
        engine = ActuarialRiskEngine()
        frailty_index = engine.calculate_frailty_index(
            user_id=user_id,
            skeleton_data=skeleton_data,
            activity_data=activity_data
        )
        
        # 记录计算后的时间
        after_calculation = datetime.utcnow()
        
        # 验证：计算日期在合理范围内（允许1秒的时钟偏差）
        assert before_calculation - timedelta(seconds=1) <= frailty_index.calculation_date <= after_calculation + timedelta(seconds=1), \
            f"Calculation date {frailty_index.calculation_date} must be between {before_calculation} and {after_calculation}"
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=8, max_size=12),
        activity_data=st.lists(valid_activity_data_strategy(), min_size=8, max_size=12)
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow, HealthCheck.large_base_example, HealthCheck.data_too_large])
    def test_more_data_yields_narrower_confidence_interval(
        self,
        skeleton_data: List[SkeletonData],
        activity_data: List[ActivityData]
    ):
        """
        属性：更多数据应产生更窄的置信区间
        
        对于更多的活动数据，计算的衰弱指数应该有更窄的置信区间，
        反映更高的统计置信度。
        """
        # 确保所有数据使用相同的user_id
        user_id = skeleton_data[0].user_id
        for data in skeleton_data:
            data.user_id = user_id
        for data in activity_data:
            data.user_id = user_id
        
        # 使用少量数据计算
        engine = ActuarialRiskEngine()
        frailty_few = engine.calculate_frailty_index(
            user_id=user_id,
            skeleton_data=skeleton_data[:5],
            activity_data=activity_data[:5]
        )
        
        # 使用更多数据计算
        frailty_many = engine.calculate_frailty_index(
            user_id=user_id,
            skeleton_data=skeleton_data,
            activity_data=activity_data
        )
        
        # 计算置信区间宽度
        ci_width_few = frailty_few.confidence_interval[1] - frailty_few.confidence_interval[0]
        ci_width_many = frailty_many.confidence_interval[1] - frailty_many.confidence_interval[0]
        
        # 验证：更多数据产生更窄或相同的置信区间
        assert ci_width_many <= ci_width_few + 1e-9, \
            f"More data should yield narrower confidence interval: {ci_width_many} <= {ci_width_few}"


# ============================================================================
# 边界条件和错误处理测试
# Edge Cases and Error Handling Tests
# ============================================================================

class TestFrailtyCalculationEdgeCases:
    """
    测试衰弱指数计算的边界条件和错误处理
    """
    
    def test_empty_skeleton_data_handled_gracefully(self):
        """测试空骨骼数据被优雅处理"""
        engine = ActuarialRiskEngine()
        activity_data = [
            ActivityData(
                user_id="user123",
                date=datetime.utcnow(),
                steps_count=5000,
                active_minutes=60,
                sleep_hours=7.5
            )
        ]
        
        # 空骨骼数据应该使用默认移动性评分
        frailty_index = engine.calculate_frailty_index(
            user_id="user123",
            skeleton_data=[],
            activity_data=activity_data
        )
        
        assert 0.0 <= frailty_index.score <= 1.0
        assert "mobility" in frailty_index.components
    
    def test_empty_activity_data_handled_gracefully(self):
        """测试空活动数据被优雅处理"""
        engine = ActuarialRiskEngine()
        skeleton_data = [
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="user123",
                keypoints=[Keypoint(JointType.NOSE, 100.0, 200.0)],
                confidence_scores=[0.9],
                anonymized=True
            )
        ]
        
        # 空活动数据应该使用默认活动和睡眠评分
        frailty_index = engine.calculate_frailty_index(
            user_id="user123",
            skeleton_data=skeleton_data,
            activity_data=[]
        )
        
        assert 0.0 <= frailty_index.score <= 1.0
        assert "activity" in frailty_index.components
        assert "sleep" in frailty_index.components
    
    def test_extreme_low_activity_yields_low_score(self):
        """测试极低活动产生低分数"""
        engine = ActuarialRiskEngine()
        
        # 极低活动数据
        activity_data = [
            ActivityData(
                user_id="user123",
                date=datetime.utcnow() - timedelta(days=i),
                steps_count=100,  # 极低步数
                active_minutes=5,  # 极低活动时间
                sleep_hours=3.0  # 极少睡眠
            )
            for i in range(7)
        ]
        
        skeleton_data = [
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="user123",
                keypoints=[Keypoint(JointType.NOSE, 100.0, 200.0)],
                confidence_scores=[0.5],  # 低置信度
                anonymized=True
            )
        ]
        
        frailty_index = engine.calculate_frailty_index(
            user_id="user123",
            skeleton_data=skeleton_data,
            activity_data=activity_data
        )
        
        # 极低活动应产生较低的衰弱指数分数
        assert frailty_index.score < 0.7, \
            f"Extreme low activity should yield low frailty score, got {frailty_index.score}"
    
    def test_high_activity_yields_high_score(self):
        """测试高活动产生高分数"""
        engine = ActuarialRiskEngine()
        
        # 高活动数据
        activity_data = [
            ActivityData(
                user_id="user123",
                date=datetime.utcnow() - timedelta(days=i),
                steps_count=10000,  # 高步数
                active_minutes=120,  # 高活动时间
                sleep_hours=8.0  # 良好睡眠
            )
            for i in range(7)
        ]
        
        skeleton_data = [
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="user123",
                keypoints=[Keypoint(JointType.NOSE, 100.0, 200.0)],
                confidence_scores=[0.95],  # 高置信度
                anonymized=True
            )
        ]
        
        frailty_index = engine.calculate_frailty_index(
            user_id="user123",
            skeleton_data=skeleton_data,
            activity_data=activity_data
        )
        
        # 高活动应产生较高的衰弱指数分数
        assert frailty_index.score > 0.3, \
            f"High activity should yield high frailty score, got {frailty_index.score}"
