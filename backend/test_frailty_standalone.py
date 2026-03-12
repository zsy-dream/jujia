"""
独立衰弱指数计算测试 - 不依赖conftest
Standalone frailty calculation test without conftest dependencies
"""
import sys
import os

# 添加app目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck

from app.schemas.core import Keypoint, SkeletonData, JointType
from app.services.actuarial_risk_engine import ActuarialRiskEngine, ActivityData


# 策略定义
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
    """生成有效的骨骼数据"""
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        min_codepoint=48, max_codepoint=122
    )))
    
    days_ago = draw(st.integers(min_value=0, max_value=30))
    timestamp = datetime.utcnow() - timedelta(days=days_ago)
    
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
    """生成有效的活动数据"""
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        min_codepoint=48, max_codepoint=122
    )))
    
    days_ago = draw(st.integers(min_value=0, max_value=30))
    date = datetime.utcnow() - timedelta(days=days_ago)
    
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


# 测试函数
@given(
    skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=1, max_size=10),
    activity_data=st.lists(valid_activity_data_strategy(), min_size=1, max_size=10)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_frailty_index_in_valid_range(skeleton_data, activity_data):
    """
    属性：衰弱指数必须在[0.0, 1.0]范围内
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
    
    # 验证：衰弱指数分数在有效范围内
    assert 0.0 <= frailty_index.score <= 1.0, \
        f"Frailty index score must be in [0.0, 1.0], got {frailty_index.score}"
    
    # 验证：置信区间边界也在有效范围内
    lower, upper = frailty_index.confidence_interval
    assert 0.0 <= lower <= 1.0, \
        f"Confidence interval lower bound must be in [0.0, 1.0], got {lower}"
    assert 0.0 <= upper <= 1.0, \
        f"Confidence interval upper bound must be in [0.0, 1.0], got {upper}"
    
    print(f"✓ Test passed: score={frailty_index.score:.3f}, CI=[{lower:.3f}, {upper:.3f}]")


@given(
    skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=1, max_size=10),
    activity_data=st.lists(valid_activity_data_strategy(), min_size=1, max_size=10)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_frailty_index_incorporates_all_components(skeleton_data, activity_data):
    """
    属性：衰弱指数必须纳入移动模式、睡眠质量和活动水平
    **Validates: Requirements 3.1, 3.3**
    """
    user_id = skeleton_data[0].user_id
    for data in skeleton_data:
        data.user_id = user_id
    for data in activity_data:
        data.user_id = user_id
    
    engine = ActuarialRiskEngine()
    frailty_index = engine.calculate_frailty_index(
        user_id=user_id,
        skeleton_data=skeleton_data,
        activity_data=activity_data
    )
    
    # 验证：必须包含所有核心组件
    assert "mobility" in frailty_index.components
    assert "activity" in frailty_index.components
    assert "sleep" in frailty_index.components
    
    # 验证：所有组件分数在有效范围内
    assert 0.0 <= frailty_index.components["mobility"] <= 1.0
    assert 0.0 <= frailty_index.components["activity"] <= 1.0
    assert 0.0 <= frailty_index.components["sleep"] <= 1.0
    
    print(f"✓ Test passed: mobility={frailty_index.components['mobility']:.3f}, "
          f"activity={frailty_index.components['activity']:.3f}, "
          f"sleep={frailty_index.components['sleep']:.3f}")


if __name__ == "__main__":
    print("运行衰弱指数计算属性测试...")
    print("=" * 70)
    
    print("\n测试1: 衰弱指数必须在有效范围内")
    print("-" * 70)
    test_frailty_index_in_valid_range()
    
    print("\n测试2: 衰弱指数必须纳入所有组件")
    print("-" * 70)
    test_frailty_index_incorporates_all_components()
    
    print("\n" + "=" * 70)
    print("所有测试通过！✓")
