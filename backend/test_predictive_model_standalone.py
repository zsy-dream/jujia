"""
独立单元测试 - 预测模型
Standalone unit tests for Predictive Model (no conftest dependencies)
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
    PredictiveModel,
    ActivityData,
    TimeSeriesData
)
from app.schemas.core import (
    SkeletonData,
    Keypoint,
    JointType,
    FrailtyIndex,
    RiskAssessmentReport
)


def test_predict_fall_risk_basic():
    """测试基本跌倒风险预测"""
    model = PredictiveModel()
    
    frailty = FrailtyIndex(
        user_id="test_user",
        score=0.7,
        components={
            "mobility": 0.7,
            "balance_quality": 0.7,
            "gait_stability": 0.7
        },
        calculation_date=datetime.utcnow(),
        confidence_interval=(0.65, 0.75)
    )
    
    data_points = [
        ActivityData("test_user", datetime.utcnow() - timedelta(days=i), 
                   5000, 60, 7.5)
        for i in range(30)
    ]
    
    time_series = TimeSeriesData(
        user_id="test_user",
        data_points=data_points,
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow()
    )
    
    risk_score, confidence_interval = model.predict_fall_risk(frailty, time_series)
    
    print(f"Fall risk score: {risk_score:.3f}")
    print(f"Confidence interval: ({confidence_interval[0]:.3f}, {confidence_interval[1]:.3f})")
    
    assert 0.0 <= risk_score <= 1.0
    assert 0.0 <= confidence_interval[0] <= confidence_interval[1] <= 1.0
    assert confidence_interval[0] <= risk_score <= confidence_interval[1]
    print("✓ Test passed: predict_fall_risk_basic")


def test_predict_fall_risk_high_risk():
    """测试高跌倒风险场景"""
    model = PredictiveModel()
    
    # 低移动性和平衡分数
    frailty = FrailtyIndex(
        user_id="test_user",
        score=0.3,
        components={
            "mobility": 0.2,
            "balance_quality": 0.3,
            "gait_stability": 0.3
        },
        calculation_date=datetime.utcnow(),
        confidence_interval=(0.25, 0.35)
    )
    
    # 低活动数据
    data_points = [
        ActivityData("test_user", datetime.utcnow() - timedelta(days=i), 
                   1500, 20, 6.0)
        for i in range(30)
    ]
    
    time_series = TimeSeriesData(
        user_id="test_user",
        data_points=data_points,
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow()
    )
    
    risk_score, confidence_interval = model.predict_fall_risk(frailty, time_series)
    
    print(f"High risk fall score: {risk_score:.3f}")
    
    # 高风险场景应该有高风险分数
    assert risk_score > 0.6
    print("✓ Test passed: predict_fall_risk_high_risk")


def test_analyze_trends_improving():
    """测试改善趋势分析"""
    model = PredictiveModel()
    
    # 创建改善趋势数据
    data_points = []
    for i in range(30):
        steps = 3000 + (i * 100)  # 逐渐改善
        data_points.append(
            ActivityData("test_user", datetime.utcnow() - timedelta(days=29-i), 
                       steps, 50 + i, 7.0 + (i * 0.01), mobility_score=0.5 + (i * 0.01))
        )
    
    time_series = TimeSeriesData(
        user_id="test_user",
        data_points=data_points,
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow()
    )
    
    result = model.analyze_trends(time_series)
    
    print(f"Overall trend: {result['overall_trend']}")
    print(f"Activity trend: {result['activity_trend']}")
    print(f"Trend confidence: {result['trend_confidence']:.3f}")
    
    assert result["overall_trend"] == "improving"
    assert result["activity_trend"] == "improving"
    assert result["trend_confidence"] == 1.0
    print("✓ Test passed: analyze_trends_improving")


def test_generate_risk_report_basic():
    """测试基本风险报告生成"""
    engine = ActuarialRiskEngine()
    
    # 创建测试数据
    skeleton_data = []
    for i in range(10):
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
    
    data_points = []
    for i in range(30):
        data_points.append(
            ActivityData("test_user", datetime.utcnow() - timedelta(days=29-i), 
                       5000, 60, 7.5, mobility_score=0.7)
        )
    
    time_series = TimeSeriesData(
        user_id="test_user",
        data_points=data_points,
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow()
    )
    
    report = engine.generate_risk_report("test_user", skeleton_data, time_series)
    
    print(f"\n=== Risk Assessment Report ===")
    print(f"User ID: {report.user_id}")
    print(f"Alert Level: {report.alert_level}")
    print(f"Frailty Score: {report.current_frailty.score:.3f}")
    print(f"Fall Risk: {report.risk_prediction.fall_risk_score:.3f}")
    print(f"Medical Emergency Risk: {report.risk_prediction.medical_emergency_risk:.3f}")
    print(f"Mobility Decline Risk: {report.risk_prediction.mobility_decline_risk:.3f}")
    print(f"Overall Trend: {report.trend_analysis['overall_trend']}")
    print(f"Recommendations: {len(report.recommendations)}")
    for i, rec in enumerate(report.recommendations[:3], 1):
        print(f"  {i}. {rec}")
    
    assert isinstance(report, RiskAssessmentReport)
    assert report.user_id == "test_user"
    assert report.alert_level in ["low", "medium", "high", "emergency"]
    assert len(report.recommendations) > 0
    assert "fall_risk" in report.confidence_intervals
    assert "medical_emergency_risk" in report.confidence_intervals
    assert "mobility_decline_risk" in report.confidence_intervals
    print("✓ Test passed: generate_risk_report_basic")


def test_generate_risk_report_high_risk():
    """测试高风险场景报告生成"""
    engine = ActuarialRiskEngine()
    
    # 创建低质量骨骼数据
    skeleton_data = []
    for i in range(5):
        keypoints = [
            Keypoint(JointType.LEFT_HIP, 100, 200, visibility=0.5),
            Keypoint(JointType.RIGHT_HIP, 120, 200, visibility=0.5),
        ]
        skeleton_data.append(SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="test_user",
            keypoints=keypoints,
            confidence_scores=[0.5, 0.5],
            anonymized=True
        ))
    
    # 创建高风险活动数据
    data_points = []
    for i in range(30):
        steps = 5000 - (i * 100)  # 下降趋势
        data_points.append(
            ActivityData("test_user", datetime.utcnow() - timedelta(days=29-i), 
                       max(steps, 1500), 30, 5.0, mobility_score=max(0.5 - (i * 0.01), 0.2))
        )
    
    time_series = TimeSeriesData(
        user_id="test_user",
        data_points=data_points,
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow()
    )
    
    report = engine.generate_risk_report("test_user", skeleton_data, time_series)
    
    print(f"\n=== High Risk Report ===")
    print(f"Alert Level: {report.alert_level}")
    print(f"Fall Risk: {report.risk_prediction.fall_risk_score:.3f}")
    print(f"Overall Trend: {report.trend_analysis['overall_trend']}")
    
    # 高风险场景应该有高警报级别
    assert report.alert_level in ["medium", "high", "emergency"]
    assert report.risk_prediction.fall_risk_score > 0.3
    
    # 应该有相关建议
    recommendations_text = " ".join(report.recommendations)
    assert "风险" in recommendations_text or "建议" in recommendations_text
    print("✓ Test passed: generate_risk_report_high_risk")


def test_confidence_intervals_in_report():
    """测试报告中的置信区间"""
    engine = ActuarialRiskEngine()
    
    skeleton_data = [
        SkeletonData(
            timestamp=datetime.utcnow(),
            user_id="test_user",
            keypoints=[Keypoint(JointType.LEFT_HIP, 100, 200, visibility=0.9)],
            confidence_scores=[0.9],
            anonymized=True
        )
    ]
    
    data_points = [
        ActivityData("test_user", datetime.utcnow() - timedelta(days=i), 
                   5000, 60, 7.5)
        for i in range(30)
    ]
    
    time_series = TimeSeriesData(
        user_id="test_user",
        data_points=data_points,
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow()
    )
    
    report = engine.generate_risk_report("test_user", skeleton_data, time_series)
    
    print(f"\n=== Confidence Intervals ===")
    for risk_type, (lower, upper) in report.confidence_intervals.items():
        print(f"{risk_type}: ({lower:.3f}, {upper:.3f})")
        assert 0.0 <= lower <= upper <= 1.0, f"Invalid CI for {risk_type}: ({lower}, {upper})"
    
    print("✓ Test passed: confidence_intervals_in_report")


if __name__ == "__main__":
    print("Running Predictive Model Tests...\n")
    
    try:
        test_predict_fall_risk_basic()
        test_predict_fall_risk_high_risk()
        test_analyze_trends_improving()
        test_generate_risk_report_basic()
        test_generate_risk_report_high_risk()
        test_confidence_intervals_in_report()
        
        print("\n" + "="*50)
        print("All tests passed! ✓")
        print("="*50)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
