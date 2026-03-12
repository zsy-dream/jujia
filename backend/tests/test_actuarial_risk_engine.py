"""
单元测试 - 精算风险引擎
Unit tests for Actuarial Risk Engine
"""
import os
import sys

# 设置测试环境变量
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/test_db"
os.environ["SECRET_KEY"] = "test_secret"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

import pytest
from datetime import datetime, timedelta
from app.services.actuarial_risk_engine import (
    ActuarialRiskEngine,
    FrailtyCalculator,
    TemporalAnalyzer,
    PredictiveModel,
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


class TestFrailtyCalculator:
    """测试衰弱计算器"""
    
    def test_assess_mobility_patterns_empty_data(self):
        """测试空数据的移动性评估"""
        calculator = FrailtyCalculator()
        result = calculator.assess_mobility_patterns([])
        
        assert isinstance(result, MobilityScore)
        assert result.score == 0.5
        assert result.gait_stability == 0.5
        assert result.movement_range == 0.5
        assert result.balance_quality == 0.5
    
    def test_assess_mobility_patterns_with_data(self):
        """测试有数据的移动性评估"""
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
        assert 0.0 <= result.movement_range <= 1.0
        assert 0.0 <= result.balance_quality <= 1.0
    
    def test_analyze_activity_levels_empty_data(self):
        """测试空数据的活动水平分析"""
        calculator = FrailtyCalculator()
        result = calculator.analyze_activity_levels([])
        
        assert isinstance(result, ActivityScore)
        assert result.score == 0.5
    
    def test_analyze_activity_levels_with_data(self):
        """测试有数据的活动水平分析"""
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
        assert result.active_time_ratio > 0.5
    
    def test_analyze_sleep_quality_optimal_sleep(self):
        """测试最佳睡眠质量分析"""
        calculator = FrailtyCalculator()
        
        activity_data = [
            ActivityData("user1", datetime.utcnow(), 5000, 60, 7.5),
            ActivityData("user1", datetime.utcnow(), 5000, 60, 8.0),
            ActivityData("user1", datetime.utcnow(), 5000, 60, 7.8),
        ]
        
        result = calculator.analyze_sleep_quality(activity_data)
        
        assert isinstance(result, SleepScore)
        assert result.score > 0.7  # Good sleep should score high
        assert result.sleep_duration_score >= 0.8
    
    def test_analyze_sleep_quality_poor_sleep(self):
        """测试差睡眠质量分析"""
        calculator = FrailtyCalculator()
        
        activity_data = [
            ActivityData("user1", datetime.utcnow(), 5000, 60, 4.5),
            ActivityData("user1", datetime.utcnow(), 5000, 60, 5.0),
            ActivityData("user1", datetime.utcnow(), 5000, 60, 4.0),
        ]
        
        result = calculator.analyze_sleep_quality(activity_data)
        
        assert isinstance(result, SleepScore)
        assert result.score < 0.7  # Poor sleep should score low
    
    def test_compute_composite_score(self):
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


class TestTemporalAnalyzer:
    """测试时序分析器"""
    
    def test_detect_risk_patterns_insufficient_data(self):
        """测试数据不足的风险模式检测"""
        analyzer = TemporalAnalyzer()
        
        data_points = [
            ActivityData("user1", datetime.utcnow(), 5000, 60, 7.0)
        ]
        
        time_series = TimeSeriesData(
            user_id="user1",
            data_points=data_points,
            start_date=datetime.utcnow() - timedelta(days=1),
            end_date=datetime.utcnow()
        )
        
        result = analyzer.detect_risk_patterns(time_series)
        
        assert result["trend"] == "insufficient_data"
        assert result["change_detected"] is False
        assert result["risk_level"] == "unknown"
    
    def test_detect_risk_patterns_declining_trend(self):
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
    
    def test_detect_risk_patterns_improving_trend(self):
        """测试改善趋势检测"""
        analyzer = TemporalAnalyzer()
        
        # 创建改善趋势数据
        data_points = []
        for i in range(14):
            steps = 3000 + (i * 200)  # Improving steps
            data_points.append(
                ActivityData("user1", datetime.utcnow() - timedelta(days=13-i), 
                           steps, 60, 7.5)
            )
        
        time_series = TimeSeriesData(
            user_id="user1",
            data_points=data_points,
            start_date=datetime.utcnow() - timedelta(days=14),
            end_date=datetime.utcnow()
        )
        
        result = analyzer.detect_risk_patterns(time_series)
        
        assert result["trend"] == "improving"
        assert result["risk_level"] in ["low", "medium"]
    
    def test_detect_significant_change(self):
        """测试显著变化检测"""
        analyzer = TemporalAnalyzer()
        
        # 创建有显著变化的数据
        data_points = []
        # 前10天正常
        for i in range(10):
            data_points.append(
                ActivityData("user1", datetime.utcnow() - timedelta(days=12-i), 
                           5000, 60, 7.0)
            )
        # 最后3天显著下降
        for i in range(3):
            data_points.append(
                ActivityData("user1", datetime.utcnow() - timedelta(days=2-i), 
                           1000, 20, 5.0)
            )
        
        time_series = TimeSeriesData(
            user_id="user1",
            data_points=data_points,
            start_date=datetime.utcnow() - timedelta(days=13),
            end_date=datetime.utcnow()
        )
        
        result = analyzer.detect_risk_patterns(time_series)
        
        assert result["change_detected"] is True


class TestActuarialRiskEngine:
    """测试精算风险引擎"""
    
    def test_calculate_frailty_index(self):
        """测试衰弱指数计算"""
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
    
    def test_calculate_frailty_index_components(self):
        """测试衰弱指数组件"""
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
        
        activity_data = [
            ActivityData("test_user", datetime.utcnow(), 5000, 60, 7.5)
        ]
        
        result = engine.calculate_frailty_index("test_user", skeleton_data, activity_data)
        
        # 验证所有必需组件存在
        assert "mobility" in result.components
        assert "activity" in result.components
        assert "sleep" in result.components
        assert "gait_stability" in result.components
        assert "movement_range" in result.components
        assert "balance_quality" in result.components
    
    def test_predict_incident_probability(self):
        """测试事件概率预测"""
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
    
    def test_predict_high_risk_scenario(self):
        """测试高风险场景预测"""
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
        assert "下降趋势" in "".join(result.contributing_factors) or \
               "低移动性" in "".join(result.contributing_factors) or \
               "活动水平不足" in "".join(result.contributing_factors)
    
    def test_confidence_interval_calculation(self):
        """测试置信区间计算"""
        engine = ActuarialRiskEngine()
        
        # 少量数据应该有更宽的置信区间
        skeleton_data_small = [
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id="test_user",
                keypoints=[Keypoint(JointType.LEFT_HIP, 100, 200, visibility=0.9)],
                confidence_scores=[0.9],
                anonymized=True
            )
        ]
        activity_data_small = [
            ActivityData("test_user", datetime.utcnow(), 5000, 60, 7.5)
        ]
        
        result_small = engine.calculate_frailty_index(
            "test_user", skeleton_data_small, activity_data_small
        )
        
        # 大量数据应该有更窄的置信区间
        skeleton_data_large = skeleton_data_small * 50
        activity_data_large = activity_data_small * 50
        
        result_large = engine.calculate_frailty_index(
            "test_user", skeleton_data_large, activity_data_large
        )
        
        ci_width_small = result_small.confidence_interval[1] - result_small.confidence_interval[0]
        ci_width_large = result_large.confidence_interval[1] - result_large.confidence_interval[0]
        
        assert ci_width_small > ci_width_large


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestPredictiveModel:
    """测试预测模型"""
    
    def test_predict_fall_risk_basic(self):
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
        
        assert 0.0 <= risk_score <= 1.0
        assert 0.0 <= confidence_interval[0] <= confidence_interval[1] <= 1.0
        assert confidence_interval[0] <= risk_score <= confidence_interval[1]
    
    def test_predict_fall_risk_high_risk(self):
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
        
        # 高风险场景应该有高风险分数
        assert risk_score > 0.6
    
    def test_predict_medical_emergency_risk(self):
        """测试医疗紧急事件风险预测"""
        model = PredictiveModel()
        
        frailty = FrailtyIndex(
            user_id="test_user",
            score=0.6,
            components={
                "sleep": 0.5,
                "activity": 0.6
            },
            calculation_date=datetime.utcnow(),
            confidence_interval=(0.55, 0.65)
        )
        
        data_points = [
            ActivityData("test_user", datetime.utcnow() - timedelta(days=i), 
                       4000, 50, 7.0)
            for i in range(30)
        ]
        
        time_series = TimeSeriesData(
            user_id="test_user",
            data_points=data_points,
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow()
        )
        
        risk_score, confidence_interval = model.predict_medical_emergency_risk(frailty, time_series)
        
        assert 0.0 <= risk_score <= 1.0
        assert 0.0 <= confidence_interval[0] <= confidence_interval[1] <= 1.0
    
    def test_predict_medical_emergency_risk_poor_sleep(self):
        """测试睡眠不良的医疗紧急风险"""
        model = PredictiveModel()
        
        frailty = FrailtyIndex(
            user_id="test_user",
            score=0.5,
            components={
                "sleep": 0.3,
                "activity": 0.5
            },
            calculation_date=datetime.utcnow(),
            confidence_interval=(0.45, 0.55)
        )
        
        # 睡眠不足数据
        data_points = [
            ActivityData("test_user", datetime.utcnow() - timedelta(days=i), 
                       4000, 50, 4.5)
            for i in range(30)
        ]
        
        time_series = TimeSeriesData(
            user_id="test_user",
            data_points=data_points,
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow()
        )
        
        risk_score, confidence_interval = model.predict_medical_emergency_risk(frailty, time_series)
        
        # 睡眠不良应该增加风险
        assert risk_score > 0.4
    
    def test_predict_mobility_decline_risk(self):
        """测试移动能力下降风险预测"""
        model = PredictiveModel()
        
        frailty = FrailtyIndex(
            user_id="test_user",
            score=0.6,
            components={
                "mobility": 0.6,
                "activity": 0.6,
                "movement_range": 0.6
            },
            calculation_date=datetime.utcnow(),
            confidence_interval=(0.55, 0.65)
        )
        
        data_points = [
            ActivityData("test_user", datetime.utcnow() - timedelta(days=i), 
                       4500, 55, 7.0)
            for i in range(30)
        ]
        
        time_series = TimeSeriesData(
            user_id="test_user",
            data_points=data_points,
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow()
        )
        
        risk_score, confidence_interval = model.predict_mobility_decline_risk(frailty, time_series)
        
        assert 0.0 <= risk_score <= 1.0
        assert 0.0 <= confidence_interval[0] <= confidence_interval[1] <= 1.0
    
    def test_predict_mobility_decline_with_declining_trend(self):
        """测试下降趋势的移动能力风险"""
        model = PredictiveModel()
        
        frailty = FrailtyIndex(
            user_id="test_user",
            score=0.5,
            components={
                "mobility": 0.4,
                "activity": 0.5,
                "movement_range": 0.5
            },
            calculation_date=datetime.utcnow(),
            confidence_interval=(0.45, 0.55)
        )
        
        # 创建下降趋势数据
        data_points = []
        for i in range(30):
            steps = 5000 - (i * 100)  # 逐渐下降
            data_points.append(
                ActivityData("test_user", datetime.utcnow() - timedelta(days=29-i), 
                           max(steps, 2000), 50, 7.0)
            )
        
        time_series = TimeSeriesData(
            user_id="test_user",
            data_points=data_points,
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow()
        )
        
        risk_score, confidence_interval = model.predict_mobility_decline_risk(frailty, time_series)
        
        # 下降趋势应该增加风险
        assert risk_score > 0.5
    
    def test_analyze_trends_insufficient_data(self):
        """测试数据不足的趋势分析"""
        model = PredictiveModel()
        
        data_points = [
            ActivityData("test_user", datetime.utcnow(), 5000, 60, 7.0)
        ]
        
        time_series = TimeSeriesData(
            user_id="test_user",
            data_points=data_points,
            start_date=datetime.utcnow() - timedelta(days=1),
            end_date=datetime.utcnow()
        )
        
        result = model.analyze_trends(time_series)
        
        assert result["overall_trend"] == "insufficient_data"
        assert result["trend_confidence"] == 0.0
    
    def test_analyze_trends_improving(self):
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
        
        assert result["overall_trend"] == "improving"
        assert result["activity_trend"] == "improving"
        assert result["trend_confidence"] == 1.0
    
    def test_analyze_trends_declining(self):
        """测试下降趋势分析"""
        model = PredictiveModel()
        
        # 创建下降趋势数据
        data_points = []
        for i in range(30):
            steps = 5000 - (i * 100)  # 逐渐下降
            data_points.append(
                ActivityData("test_user", datetime.utcnow() - timedelta(days=29-i), 
                           max(steps, 2000), max(60 - i, 20), 7.0, mobility_score=max(0.7 - (i * 0.01), 0.3))
            )
        
        time_series = TimeSeriesData(
            user_id="test_user",
            data_points=data_points,
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow()
        )
        
        result = model.analyze_trends(time_series)
        
        assert result["overall_trend"] == "declining"
        assert result["activity_trend"] == "declining"


class TestRiskAssessmentReport:
    """测试风险评估报告生成"""
    
    def test_generate_risk_report_basic(self):
        """测试基本风险报告生成"""
        from app.services.actuarial_risk_engine import ActuarialRiskEngine
        from app.schemas.core import RiskAssessmentReport
        
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
        
        assert isinstance(report, RiskAssessmentReport)
        assert report.user_id == "test_user"
        assert report.alert_level in ["low", "medium", "high", "emergency"]
        assert len(report.recommendations) > 0
        assert "fall_risk" in report.confidence_intervals
        assert "medical_emergency_risk" in report.confidence_intervals
        assert "mobility_decline_risk" in report.confidence_intervals
    
    def test_generate_risk_report_high_risk(self):
        """测试高风险场景报告生成"""
        from app.services.actuarial_risk_engine import ActuarialRiskEngine
        
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
        
        # 高风险场景应该有高警报级别
        assert report.alert_level in ["high", "emergency"]
        
        # 至少一个风险分数应该较高（fall_risk, medical_emergency, or mobility_decline）
        assert (report.risk_prediction.fall_risk_score > 0.3 or 
                report.risk_prediction.medical_emergency_risk > 0.3 or
                report.risk_prediction.mobility_decline_risk > 0.5), \
            "High risk scenario should have elevated risk scores"
        
        # 应该有相关建议
        recommendations_text = " ".join(report.recommendations)
        assert "风险" in recommendations_text or "建议" in recommendations_text
    
    def test_generate_risk_report_confidence_intervals(self):
        """测试报告中的置信区间"""
        from app.services.actuarial_risk_engine import ActuarialRiskEngine
        
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
        
        # 验证所有置信区间
        for risk_type, (lower, upper) in report.confidence_intervals.items():
            assert 0.0 <= lower <= upper <= 1.0, f"Invalid CI for {risk_type}: ({lower}, {upper})"
    
    def test_generate_risk_report_trend_analysis(self):
        """测试报告中的趋势分析"""
        from app.services.actuarial_risk_engine import ActuarialRiskEngine
        
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
        
        # 验证趋势分析存在
        assert "overall_trend" in report.trend_analysis
        assert "activity_trend" in report.trend_analysis
        assert "sleep_trend" in report.trend_analysis
        assert "trend_confidence" in report.trend_analysis
        assert 0.0 <= report.trend_analysis["trend_confidence"] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
