"""
独立单元测试 - 精算风险引擎
Standalone unit tests for Actuarial Risk Engine (no conftest dependencies)
"""
import os
import sys

# 设置测试环境变量
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/test_db"
os.environ["SECRET_KEY"] = "test_secret"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

from datetime import datetime, timedelta
from app.services.actuarial_risk_engine import (
    ActuarialRiskEngine,
    FrailtyCalculator,
    TemporalAnalyzer,
    ActivityData,
    TimeSeriesData,
    MobilityScore,
    ActivityScore,
    SleepScore
)
from app.schemas.core import (
    SkeletonData,
    Keypoint,
    JointType,
    FrailtyIndex
)


def test_frailty_calculator_empty_data():
    """测试空数据的移动性评估"""
    calculator = FrailtyCalculator()
    result = calculator.assess_mobility_patterns([])
    
    assert isinstance(result, MobilityScore)
    assert result.score == 0.5
    print("✓ 空数据移动性评估测试通过")


def test_frailty_calculator_with_skeleton_data():
    """测试有骨骼数据的移动性评估"""
    calculator = FrailtyCalculator()
    
    # 创建测试骨骼数据
    skeleton_data = []
    for i in range(10):
        keypoints = [
            Keypoint(JointType.LEFT_HIP, 100 + i, 200 + i, visibility=0.9),
            Keypoint(JointType.RIGHT_HIP, 120 + i, 200 + i, visibility=0.9),
            Keypoint(JointType.LEFT_KNEE, 100 + i, 250 + i, visibility=0.85),
            Keypoint(JointType.RIGHT_KNEE, 120 + i, 250 + i, visibility=0.85),
        ]
        skeleton_data.append(SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="test_user",
            keypoints=keypoints,
            confidence_scores=[0.9, 0.9, 0.85, 0.85],
            anonymized=True
        ))
    
    result = calculator.assess_mobility_patterns(skeleton_data)
    
    assert isinstance(result, MobilityScore)
    assert 0.0 <= result.score <= 1.0
    assert 0.0 <= result.gait_stability <= 1.0
    print("✓ 骨骼数据移动性评估测试通过")


def test_activity_analysis():
    """测试活动水平分析"""
    calculator = FrailtyCalculator(baseline_steps=5000)
    
    activity_data = [
        ActivityData("user1", datetime.utcnow(), 6000, 60, 7.5),
        ActivityData("user1", datetime.utcnow(), 5500, 55, 7.0),
        ActivityData("user1", datetime.utcnow(), 5800, 58, 7.2),
    ]
    
    result = calculator.analyze_activity_levels(activity_data)
    
    assert isinstance(result, ActivityScore)
    assert 0.0 <= result.score <= 1.0
    assert result.daily_steps_ratio > 0.5  # Above baseline
    print("✓ 活动水平分析测试通过")


def test_sleep_quality_analysis():
    """测试睡眠质量分析"""
    calculator = FrailtyCalculator()
    
    # 最佳睡眠
    activity_data = [
        ActivityData("user1", datetime.utcnow(), 5000, 60, 7.5),
        ActivityData("user1", datetime.utcnow(), 5000, 60, 8.0),
        ActivityData("user1", datetime.utcnow(), 5000, 60, 7.8),
    ]
    
    result = calculator.analyze_sleep_quality(activity_data)
    
    assert isinstance(result, SleepScore)
    assert result.score > 0.7  # Good sleep should score high
    print("✓ 睡眠质量分析测试通过")


def test_composite_score():
    """测试综合评分计算"""
    calculator = FrailtyCalculator()
    
    mobility = MobilityScore(0.8, 0.8, 0.8, 0.8)
    activity = ActivityScore(0.7, 0.7, 0.7, 0.7)
    sleep = SleepScore(0.9, 0.9, 0.9, 0.9)
    
    result = calculator.compute_composite_score(mobility, activity, sleep)
    
    assert 0.0 <= result <= 1.0
    # Should be weighted average: 0.4*0.8 + 0.35*0.7 + 0.25*0.9
    expected = 0.4 * 0.8 + 0.35 * 0.7 + 0.25 * 0.9
    assert abs(result - expected) < 0.01
    print("✓ 综合评分计算测试通过")


def test_temporal_analyzer_declining_trend():
    """测试下降趋势检测"""
    analyzer = TemporalAnalyzer()
    
    # 创建下降趋势数据
    data_points = []
    for i in range(14):
        steps = 5000 - (i * 200)  # Declining steps
        data_points.append(
            ActivityData("user1", datetime.utcnow() - timedelta(days=13-i), 
                       steps, 60, 7.0)
        )
    
    time_series = TimeSeriesData(
        user_id="user1",
        data_points=data_points,
        start_date=datetime.utcnow() - timedelta(days=14),
        end_date=datetime.utcnow()
    )
    
    result = analyzer.detect_risk_patterns(time_series)
    
    assert result["trend"] == "declining"
    assert result["risk_level"] in ["medium", "high"]
    print("✓ 下降趋势检测测试通过")


def test_actuarial_risk_engine_frailty_calculation():
    """测试精算风险引擎的衰弱指数计算"""
    engine = ActuarialRiskEngine()
    
    # 创建测试数据
    skeleton_data = []
    for i in range(5):
        keypoints = [
            Keypoint(JointType.LEFT_HIP, 100, 200, visibility=0.9),
            Keypoint(JointType.RIGHT_HIP, 120, 200, visibility=0.9),
        ]
        skeleton_data.append(SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="test_user",
            keypoints=keypoints,
            confidence_scores=[0.9, 0.9],
            anonymized=True
        ))
    
    activity_data = [
        ActivityData("test_user", datetime.utcnow(), 5000, 60, 7.5),
        ActivityData("test_user", datetime.utcnow(), 5200, 62, 7.8),
    ]
    
    result = engine.calculate_frailty_index("test_user", skeleton_data, activity_data)
    
    assert isinstance(result, FrailtyIndex)
    assert result.user_id == "test_user"
    assert 0.0 <= result.score <= 1.0
    assert len(result.components) > 0
    assert result.confidence_interval[0] <= result.score <= result.confidence_interval[1]
    
    # 验证所有必需组件存在
    assert "mobility" in result.components
    assert "activity" in result.components
    assert "sleep" in result.components
    print("✓ 衰弱指数计算测试通过")


def test_risk_prediction():
    """测试风险预测"""
    engine = ActuarialRiskEngine()
    
    # 创建历史数据
    data_points = []
    for i in range(30):
        data_points.append(
            ActivityData("test_user", datetime.utcnow() - timedelta(days=29-i), 
                       5000, 60, 7.5)
        )
    
    time_series = TimeSeriesData(
        user_id="test_user",
        data_points=data_points,
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow()
    )
    
    frailty = FrailtyIndex(
        user_id="test_user",
        score=0.7,
        components={"mobility": 0.7, "activity": 0.7, "sleep": 0.7},
        calculation_date=datetime.utcnow(),
        confidence_interval=(0.65, 0.75)
    )
    
    result = engine.predict_incident_probability("test_user", time_series, frailty)
    
    assert result.user_id == "test_user"
    assert 0.0 <= result.fall_risk_score <= 1.0
    assert 0.0 <= result.medical_emergency_risk <= 1.0
    assert 0.0 <= result.mobility_decline_risk <= 1.0
    assert 0.0 <= result.confidence_level <= 1.0
    assert len(result.contributing_factors) > 0
    print("✓ 风险预测测试通过")


def test_high_risk_scenario():
    """测试高风险场景"""
    engine = ActuarialRiskEngine()
    
    # 创建高风险历史数据 (下降趋势)
    data_points = []
    for i in range(30):
        steps = 5000 - (i * 100)  # Declining
        data_points.append(
            ActivityData("test_user", datetime.utcnow() - timedelta(days=29-i), 
                       max(steps, 1000), 30, 5.0)
        )
    
    time_series = TimeSeriesData(
        user_id="test_user",
        data_points=data_points,
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow()
    )
    
    # 低衰弱指数 (高风险)
    frailty = FrailtyIndex(
        user_id="test_user",
        score=0.3,
        components={"mobility": 0.3, "activity": 0.3, "sleep": 0.3},
        calculation_date=datetime.utcnow(),
        confidence_interval=(0.25, 0.35)
    )
    
    result = engine.predict_incident_probability("test_user", time_series, frailty)
    
    # 高风险场景应该有较高的风险分数
    assert result.fall_risk_score > 0.5
    print("✓ 高风险场景测试通过")


if __name__ == "__main__":
    print("\n=== 运行精算风险引擎单元测试 ===\n")
    
    try:
        test_frailty_calculator_empty_data()
        test_frailty_calculator_with_skeleton_data()
        test_activity_analysis()
        test_sleep_quality_analysis()
        test_composite_score()
        test_temporal_analyzer_declining_trend()
        test_actuarial_risk_engine_frailty_calculation()
        test_risk_prediction()
        test_high_risk_scenario()
        
        print("\n=== ✓ 所有测试通过! ===\n")
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试错误: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
