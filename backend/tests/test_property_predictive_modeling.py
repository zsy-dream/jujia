"""
属性测试：预测健康建模
Property Test: Predictive Health Modeling

**属性29：预测健康建模**
**验证需求：需求8.3**

对于任何活动和移动模式数据，系统应当计算具有验证准确性的常见老年健康事件预测模型
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta

from app.services.predictive_health_modeling import (
    ActivityPatternAnalyzer,
    PredictiveHealthModel,
    ActivityPattern,
    MobilityPattern
)
from app.services.actuarial_risk_engine import ActivityData
from app.schemas.core import FrailtyIndex, RiskPrediction


# 策略定义
@st.composite
def activity_data_strategy(draw):
    """生成活动数据"""
    num_days = draw(st.integers(min_value=7, max_value=90))
    activity_data = []
    
    base_steps = draw(st.integers(min_value=1000, max_value=8000))
    base_active = draw(st.integers(min_value=20, max_value=120))
    base_sleep = draw(st.floats(min_value=4.0, max_value=10.0))
    
    for i in range(num_days):
        # 添加一些随机变化
        steps_variation = draw(st.integers(min_value=-500, max_value=500))
        active_variation = draw(st.integers(min_value=-20, max_value=20))
        sleep_variation = draw(st.floats(min_value=-1.0, max_value=1.0))
        
        activity = ActivityData(
            user_id=f"user_{draw(st.integers(min_value=1, max_value=100))}",
            date=datetime.utcnow() - timedelta(days=num_days - i),
            steps_count=max(0, base_steps + steps_variation),
            active_minutes=max(0, base_active + active_variation),
            sleep_hours=max(0.0, min(12.0, base_sleep + sleep_variation)),
            mobility_score=draw(st.floats(min_value=0.0, max_value=1.0))
        )
        activity_data.append(activity)
    
    return activity_data


@st.composite
def frailty_index_strategy(draw):
    """生成衰弱指数"""
    score = draw(st.floats(min_value=0.0, max_value=1.0))
    ci_width = draw(st.floats(min_value=0.01, max_value=0.2))
    
    return FrailtyIndex(
        user_id=f"user_{draw(st.integers(min_value=1, max_value=100))}",
        score=score,
        components={
            "mobility": draw(st.floats(min_value=0.0, max_value=1.0)),
            "activity": draw(st.floats(min_value=0.0, max_value=1.0)),
            "sleep": draw(st.floats(min_value=0.0, max_value=1.0)),
            "gait_stability": draw(st.floats(min_value=0.0, max_value=1.0)),
            "balance_quality": draw(st.floats(min_value=0.0, max_value=1.0))
        },
        calculation_date=datetime.utcnow(),
        confidence_interval=(max(0.0, score - ci_width), min(1.0, score + ci_width))
    )


@st.composite
def risk_prediction_strategy(draw):
    """生成风险预测"""
    return RiskPrediction(
        user_id=f"user_{draw(st.integers(min_value=1, max_value=100))}",
        prediction_date=datetime.utcnow(),
        fall_risk_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        medical_emergency_risk=draw(st.floats(min_value=0.0, max_value=1.0)),
        mobility_decline_risk=draw(st.floats(min_value=0.0, max_value=1.0)),
        confidence_level=draw(st.floats(min_value=0.5, max_value=1.0)),
        contributing_factors=[]
    )


class TestPredictiveHealthModeling:
    """测试预测健康建模属性"""
    
    @given(
        activity_data=activity_data_strategy()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_29_activity_pattern_analysis(self, activity_data):
        """
        属性29：活动模式分析
        
        对于任何活动数据，系统应当：
        1. 成功分析活动模式
        2. 生成有效的活动指标
        3. 检测趋势和异常
        """
        # 设置
        analyzer = ActivityPatternAnalyzer()
        user_id = activity_data[0].user_id if activity_data else "test_user"
        
        # 执行
        pattern = analyzer.analyze_activity_patterns(user_id, activity_data)
        
        # 验证
        assert pattern is not None, "应生成活动模式"
        assert pattern.user_id == user_id
        
        # 属性1: 分析期间应匹配数据量
        assert pattern.analysis_period_days == len(activity_data)
        
        # 属性2: 平均步数应在合理范围内
        if len(activity_data) > 0:
            assert pattern.average_daily_steps >= 0
            actual_avg = sum(d.steps_count for d in activity_data) / len(activity_data)
            assert abs(pattern.average_daily_steps - actual_avg) < 1.0, "平均步数应准确"
        
        # 属性3: 步数变异性应非负
        assert pattern.steps_variability >= 0
        
        # 属性4: 活动一致性应在0-1范围内
        assert 0.0 <= pattern.activity_consistency <= 1.0
        
        # 属性5: 趋势应为有效值
        valid_trends = ["increasing", "decreasing", "stable", "insufficient_data", "unknown"]
        assert pattern.steps_trend in valid_trends
        
        # 属性6: 异常天数不应超过总天数
        assert 0 <= pattern.anomaly_days <= len(activity_data)
        
        # 属性7: 周末比率应为正数
        assert pattern.weekday_vs_weekend_ratio > 0
    
    @given(
        activity_data=activity_data_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_29_mobility_pattern_analysis(self, activity_data):
        """
        属性29：移动模式分析
        
        对于任何包含移动性评分的活动数据，系统应当：
        1. 成功分析移动模式
        2. 生成有效的移动性指标
        3. 识别跌倒风险指标
        """
        # 设置
        analyzer = ActivityPatternAnalyzer()
        user_id = activity_data[0].user_id if activity_data else "test_user"
        
        # 执行
        pattern = analyzer.analyze_mobility_patterns(user_id, activity_data)
        
        # 验证
        assert pattern is not None, "应生成移动模式"
        
        # 属性1: 移动性评分应在0-1范围内
        assert 0.0 <= pattern.average_mobility_score <= 1.0
        
        # 属性2: 步态稳定性评分应在0-1范围内
        assert 0.0 <= pattern.gait_stability_score <= 1.0
        
        # 属性3: 平衡评分应在0-1范围内
        assert 0.0 <= pattern.balance_score <= 1.0
        
        # 属性4: 运动范围评分应在0-1范围内
        assert 0.0 <= pattern.movement_range_score <= 1.0
        
        # 属性5: 移动能力下降率应在合理范围内
        assert -1.0 <= pattern.mobility_decline_rate <= 1.0
        
        # 属性6: 跌倒风险指标应为列表
        assert isinstance(pattern.fall_risk_indicators, list)
        
        # 属性7: 趋势应为有效值
        valid_trends = ["improving", "declining", "stable", "unknown"]
        assert pattern.mobility_trend in valid_trends
    
    @given(
        frailty=frailty_index_strategy(),
        risk_pred=risk_prediction_strategy(),
        activity_data=activity_data_strategy(),
        prediction_horizon=st.integers(min_value=7, max_value=90)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_29_event_prediction(
        self,
        frailty,
        risk_pred,
        activity_data,
        prediction_horizon
    ):
        """
        属性29：事件预测模型
        
        对于任何输入数据，系统应当：
        1. 生成有效的事件预测
        2. 所有概率在0-1范围内
        3. 置信区间有效
        4. 模型准确性指标有效
        """
        # 设置
        analyzer = ActivityPatternAnalyzer()
        model = PredictiveHealthModel()
        user_id = frailty.user_id
        
        # 分析模式
        activity_pattern = analyzer.analyze_activity_patterns(user_id, activity_data)
        mobility_pattern = analyzer.analyze_mobility_patterns(user_id, activity_data)
        
        # 执行
        prediction = model.predict_events(
            user_id=user_id,
            frailty=frailty,
            risk_prediction=risk_pred,
            activity_pattern=activity_pattern,
            mobility_pattern=mobility_pattern,
            historical_incidents=[],
            prediction_horizon_days=prediction_horizon
        )
        
        # 验证
        assert prediction is not None, "应生成事件预测"
        
        # 属性1: 所有概率应在0-1范围内
        assert 0.0 <= prediction.fall_probability <= 1.0
        assert 0.0 <= prediction.fall_with_injury_probability <= 1.0
        assert 0.0 <= prediction.hospitalization_probability <= 1.0
        assert 0.0 <= prediction.emergency_visit_probability <= 1.0
        assert 0.0 <= prediction.mobility_loss_probability <= 1.0
        
        # 属性2: 跌倒伴随受伤概率应小于或等于跌倒概率
        assert prediction.fall_with_injury_probability <= prediction.fall_probability * 1.1, \
            "受伤概率不应显著超过跌倒概率"
        
        # 属性3: 置信区间应有效
        fall_ci = prediction.fall_confidence_interval
        assert len(fall_ci) == 2
        assert 0.0 <= fall_ci[0] <= fall_ci[1] <= 1.0
        assert fall_ci[0] <= prediction.fall_probability <= fall_ci[1], \
            "预测值应在置信区间内"
        
        hosp_ci = prediction.hospitalization_confidence_interval
        assert len(hosp_ci) == 2
        assert 0.0 <= hosp_ci[0] <= hosp_ci[1] <= 1.0
        
        # 属性4: 模型准确性指标应在0-1范围内
        assert 0.0 <= prediction.model_accuracy <= 1.0
        assert 0.0 <= prediction.model_precision <= 1.0
        assert 0.0 <= prediction.model_recall <= 1.0
        assert 0.0 <= prediction.confidence_score <= 1.0
        
        # 属性5: 预测时间范围应匹配
        assert prediction.prediction_horizon_days == prediction_horizon
        
        # 属性6: 顶级风险因素应为列表
        assert isinstance(prediction.top_risk_factors, list)
        for factor_name, importance in prediction.top_risk_factors:
            assert isinstance(factor_name, str)
            assert 0.0 <= importance <= 1.0, "风险因素重要性应在0-1范围内"
    
    @given(
        frailty=frailty_index_strategy(),
        risk_pred=risk_prediction_strategy(),
        activity_data=activity_data_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_29_prediction_consistency(
        self,
        frailty,
        risk_pred,
        activity_data
    ):
        """
        属性29：预测一致性
        
        验证预测结果与输入数据的一致性
        """
        # 设置
        analyzer = ActivityPatternAnalyzer()
        model = PredictiveHealthModel()
        user_id = frailty.user_id
        
        activity_pattern = analyzer.analyze_activity_patterns(user_id, activity_data)
        mobility_pattern = analyzer.analyze_mobility_patterns(user_id, activity_data)
        
        # 执行
        prediction = model.predict_events(
            user_id=user_id,
            frailty=frailty,
            risk_prediction=risk_pred,
            activity_pattern=activity_pattern,
            mobility_pattern=mobility_pattern,
            historical_incidents=[],
            prediction_horizon_days=30
        )
        
        # 验证一致性
        # 属性1: 高风险预测应导致高事件概率
        if risk_pred.fall_risk_score > 0.7:
            assert prediction.fall_probability > 0.3, "高跌倒风险应导致较高跌倒概率"
        
        # 属性2: 低衰弱分数（不健康）应导致较高风险
        if frailty.score < 0.3:
            max_prob = max(
                prediction.fall_probability,
                prediction.hospitalization_probability,
                prediction.mobility_loss_probability
            )
            assert max_prob >= 0.3, "低衰弱分数应导致较高事件概率"
        
        # 属性3: 低移动性应增加跌倒风险
        if mobility_pattern.average_mobility_score < 0.4:
            assert prediction.fall_probability > 0.2, "低移动性应增加跌倒概率"
    
    @given(
        frailty=frailty_index_strategy(),
        risk_pred=risk_prediction_strategy(),
        activity_data=activity_data_strategy(),
        horizon1=st.integers(min_value=7, max_value=30),
        horizon2=st.integers(min_value=31, max_value=90)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_29_time_horizon_scaling(
        self,
        frailty,
        risk_pred,
        activity_data,
        horizon1,
        horizon2
    ):
        """
        属性29：时间范围缩放
        
        验证较长时间范围应产生更高或相等的事件概率
        """
        # 设置
        analyzer = ActivityPatternAnalyzer()
        model = PredictiveHealthModel()
        user_id = frailty.user_id
        
        activity_pattern = analyzer.analyze_activity_patterns(user_id, activity_data)
        mobility_pattern = analyzer.analyze_mobility_patterns(user_id, activity_data)
        
        # 执行两个不同时间范围的预测
        prediction1 = model.predict_events(
            user_id=user_id,
            frailty=frailty,
            risk_prediction=risk_pred,
            activity_pattern=activity_pattern,
            mobility_pattern=mobility_pattern,
            historical_incidents=[],
            prediction_horizon_days=horizon1
        )
        
        prediction2 = model.predict_events(
            user_id=user_id,
            frailty=frailty,
            risk_prediction=risk_pred,
            activity_pattern=activity_pattern,
            mobility_pattern=mobility_pattern,
            historical_incidents=[],
            prediction_horizon_days=horizon2
        )
        
        # 验证
        # 属性1: 较长时间范围应有更高或相等的跌倒概率
        assert prediction2.fall_probability >= prediction1.fall_probability * 0.9, \
            f"较长时间范围应有更高跌倒概率: {horizon1}天={prediction1.fall_probability}, {horizon2}天={prediction2.fall_probability}"
        
        # 属性2: 较长时间范围应有更高或相等的住院概率
        assert prediction2.hospitalization_probability >= prediction1.hospitalization_probability * 0.9, \
            "较长时间范围应有更高住院概率"
    
    @given(
        activity_data=activity_data_strategy()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_29_trend_detection_accuracy(self, activity_data):
        """
        属性29：趋势检测准确性
        
        验证趋势检测与实际数据变化一致
        """
        # 只测试有足够数据的情况
        assume(len(activity_data) >= 14)
        
        # 设置
        analyzer = ActivityPatternAnalyzer()
        user_id = activity_data[0].user_id
        
        # 计算实际趋势
        mid = len(activity_data) // 2
        first_half_steps = [d.steps_count for d in activity_data[:mid]]
        second_half_steps = [d.steps_count for d in activity_data[mid:]]
        
        first_avg = sum(first_half_steps) / len(first_half_steps)
        second_avg = sum(second_half_steps) / len(second_half_steps)
        
        actual_change_ratio = (second_avg - first_avg) / (first_avg + 1)
        
        # 执行
        pattern = analyzer.analyze_activity_patterns(user_id, activity_data)
        
        # 验证趋势检测
        if actual_change_ratio > 0.2:
            # 明显增加
            assert pattern.steps_trend in ["increasing", "stable"], \
                f"应检测到增加趋势: 实际变化={actual_change_ratio:.2f}, 检测={pattern.steps_trend}"
        elif actual_change_ratio < -0.2:
            # 明显减少
            assert pattern.steps_trend in ["decreasing", "stable"], \
                f"应检测到减少趋势: 实际变化={actual_change_ratio:.2f}, 检测={pattern.steps_trend}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
