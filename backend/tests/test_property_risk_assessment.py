"""
属性测试：风险评估完整性
Property-Based Tests for Risk Assessment Integrity

**验证属性：风险评估完整性**
**Validates: Requirements 3.4**

属性描述：
对于任何风险评估生成，系统应当提供30天期间的置信区间和趋势分析，并进行统计验证。
"""
import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime, timedelta
from typing import List

from app.schemas.core import (
    Keypoint, SkeletonData, JointType, RiskAssessmentReport
)
from app.services.actuarial_risk_engine import (
    ActuarialRiskEngine, ActivityData, TimeSeriesData
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
    """生成有效的骨骼数据"""
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        min_codepoint=48, max_codepoint=122
    )))
    
    days_ago = draw(st.integers(min_value=0, max_value=30))
    timestamp = datetime.utcnow() - timedelta(days=days_ago)
    
    # 生成17个关键点（标准人体骨骼）
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
    
    # 生成合理范围的活动数据
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


@st.composite
def valid_time_series_data_strategy(draw):
    """生成有效的时序数据（30天期间）"""
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        min_codepoint=48, max_codepoint=122
    )))
    
    # 生成30天的活动数据
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # 生成至少10天的数据点
    num_days = draw(st.integers(min_value=10, max_value=30))
    data_points = []
    
    for i in range(num_days):
        date = start_date + timedelta(days=i)
        steps_count = draw(st.integers(min_value=0, max_value=20000))
        active_minutes = draw(st.integers(min_value=0, max_value=300))
        sleep_hours = draw(st.floats(min_value=0.0, max_value=14.0))
        
        data_points.append(ActivityData(
            user_id=user_id,
            date=date,
            steps_count=steps_count,
            active_minutes=active_minutes,
            sleep_hours=sleep_hours
        ))
    
    return TimeSeriesData(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        data_points=data_points
    )


# ============================================================================
# 属性10：风险评估完整性
# Property 10: Risk Assessment Integrity
# ============================================================================

class TestRiskAssessmentIntegrity:
    """
    **验证属性：风险评估完整性**
    **Validates: Requirements 3.4**
    
    验证风险评估生成对所有输入提供完整的30天分析：
    1. 必须提供30天期间的置信区间
    2. 必须包含趋势分析
    3. 置信区间必须进行统计验证
    4. 报告必须包含所有必需的风险评估组件
    """
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=5, max_size=15),
        historical_data=valid_time_series_data_strategy()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_risk_assessment_provides_confidence_intervals(
        self,
        skeleton_data: List[SkeletonData],
        historical_data: TimeSeriesData
    ):
        """
        属性：风险评估必须提供置信区间
        
        对于任何风险评估生成，系统必须为所有风险类型提供置信区间：
        - 跌倒风险置信区间
        - 医疗紧急风险置信区间
        - 移动性下降风险置信区间
        - 衰弱指数置信区间
        
        **Validates: Requirements 3.4**
        """
        # 确保所有数据使用相同的user_id
        user_id = historical_data.user_id
        for data in skeleton_data:
            data.user_id = user_id
        
        # 创建风险引擎并生成风险报告
        engine = ActuarialRiskEngine()
        report = engine.generate_risk_report(
            user_id=user_id,
            skeleton_data=skeleton_data,
            historical_data=historical_data
        )
        
        # 验证：必须包含置信区间字典
        assert report.confidence_intervals is not None, \
            "Risk assessment must provide confidence intervals"
        
        # 验证：必须包含所有风险类型的置信区间
        required_intervals = [
            "fall_risk",
            "medical_emergency_risk",
            "mobility_decline_risk",
            "frailty_index"
        ]
        
        for risk_type in required_intervals:
            assert risk_type in report.confidence_intervals, \
                f"Risk assessment must include {risk_type} confidence interval"
            
            lower, upper = report.confidence_intervals[risk_type]
            
            # 验证：置信区间边界在有效范围内
            assert 0.0 <= lower <= 1.0, \
                f"{risk_type} confidence interval lower bound must be in [0.0, 1.0], got {lower}"
            assert 0.0 <= upper <= 1.0, \
                f"{risk_type} confidence interval upper bound must be in [0.0, 1.0], got {upper}"
            
            # 验证：下界 <= 上界
            assert lower <= upper, \
                f"{risk_type} confidence interval lower bound {lower} must be <= upper bound {upper}"

    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=5, max_size=15),
        historical_data=valid_time_series_data_strategy()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_risk_assessment_includes_trend_analysis(
        self,
        skeleton_data: List[SkeletonData],
        historical_data: TimeSeriesData
    ):
        """
        属性：风险评估必须包含趋势分析
        
        对于任何风险评估生成，系统必须提供详细的趋势分析，包括：
        - 趋势方向（improving, stable, declining）
        - 趋势置信度
        - 各项指标的趋势
        
        **Validates: Requirements 3.4**
        """
        # 确保所有数据使用相同的user_id
        user_id = historical_data.user_id
        for data in skeleton_data:
            data.user_id = user_id
        
        # 创建风险引擎并生成风险报告
        engine = ActuarialRiskEngine()
        report = engine.generate_risk_report(
            user_id=user_id,
            skeleton_data=skeleton_data,
            historical_data=historical_data
        )
        
        # 验证：必须包含趋势分析
        assert report.trend_analysis is not None, \
            "Risk assessment must include trend analysis"
        
        # 验证：趋势分析必须包含关键字段
        assert "overall_trend" in report.trend_analysis, \
            "Trend analysis must include overall_trend"
        assert "trend_confidence" in report.trend_analysis, \
            "Trend analysis must include trend_confidence"
        
        # 验证：趋势方向必须是有效值
        valid_trends = ["improving", "stable", "declining"]
        assert report.trend_analysis["overall_trend"] in valid_trends, \
            f"Overall trend must be one of {valid_trends}, got {report.trend_analysis['overall_trend']}"
        
        # 验证：趋势置信度在有效范围内
        trend_confidence = report.trend_analysis["trend_confidence"]
        assert 0.0 <= trend_confidence <= 1.0, \
            f"Trend confidence must be in [0.0, 1.0], got {trend_confidence}"
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=5, max_size=15),
        historical_data=valid_time_series_data_strategy()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_risk_assessment_covers_30_day_period(
        self,
        skeleton_data: List[SkeletonData],
        historical_data: TimeSeriesData
    ):
        """
        属性：风险评估必须覆盖30天期间
        
        对于任何风险评估生成，报告的时间范围必须覆盖30天期间。
        
        **Validates: Requirements 3.4**
        """
        # 确保所有数据使用相同的user_id
        user_id = historical_data.user_id
        for data in skeleton_data:
            data.user_id = user_id
        
        # 创建风险引擎并生成风险报告
        engine = ActuarialRiskEngine()
        report = engine.generate_risk_report(
            user_id=user_id,
            skeleton_data=skeleton_data,
            historical_data=historical_data
        )
        
        # 验证：报告必须包含时间范围
        assert report.period_start is not None, \
            "Risk assessment must include period_start"
        assert report.period_end is not None, \
            "Risk assessment must include period_end"
        
        # 验证：时间范围必须合理
        assert report.period_start <= report.period_end, \
            f"period_start {report.period_start} must be before period_end {report.period_end}"
        
        # 验证：时间范围应该接近30天（允许一些灵活性）
        period_days = (report.period_end - report.period_start).days
        assert 10 <= period_days <= 35, \
            f"Risk assessment period should be approximately 30 days, got {period_days} days"
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=5, max_size=15),
        historical_data=valid_time_series_data_strategy()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_risk_assessment_confidence_intervals_statistically_valid(
        self,
        skeleton_data: List[SkeletonData],
        historical_data: TimeSeriesData
    ):
        """
        属性：风险评估置信区间必须进行统计验证
        
        对于任何风险评估生成，置信区间必须：
        1. 包含对应的风险分数
        2. 宽度合理（不能太宽或太窄）
        3. 反映数据的不确定性
        
        **Validates: Requirements 3.4**
        """
        # 确保所有数据使用相同的user_id
        user_id = historical_data.user_id
        for data in skeleton_data:
            data.user_id = user_id
        
        # 创建风险引擎并生成风险报告
        engine = ActuarialRiskEngine()
        report = engine.generate_risk_report(
            user_id=user_id,
            skeleton_data=skeleton_data,
            historical_data=historical_data
        )
        
        # 验证：跌倒风险置信区间包含风险分数
        fall_lower, fall_upper = report.confidence_intervals["fall_risk"]
        assert fall_lower <= report.risk_prediction.fall_risk_score <= fall_upper, \
            f"Fall risk score {report.risk_prediction.fall_risk_score} must be within CI [{fall_lower}, {fall_upper}]"
        
        # 验证：医疗紧急风险置信区间包含风险分数
        emergency_lower, emergency_upper = report.confidence_intervals["medical_emergency_risk"]
        assert emergency_lower <= report.risk_prediction.medical_emergency_risk <= emergency_upper, \
            f"Emergency risk score {report.risk_prediction.medical_emergency_risk} must be within CI [{emergency_lower}, {emergency_upper}]"
        
        # 验证：移动性下降风险置信区间包含风险分数
        decline_lower, decline_upper = report.confidence_intervals["mobility_decline_risk"]
        assert decline_lower <= report.risk_prediction.mobility_decline_risk <= decline_upper, \
            f"Decline risk score {report.risk_prediction.mobility_decline_risk} must be within CI [{decline_lower}, {decline_upper}]"
        
        # 验证：衰弱指数置信区间包含衰弱指数分数
        frailty_lower, frailty_upper = report.confidence_intervals["frailty_index"]
        assert frailty_lower <= report.current_frailty.score <= frailty_upper, \
            f"Frailty score {report.current_frailty.score} must be within CI [{frailty_lower}, {frailty_upper}]"
        
        # 验证：置信区间宽度合理（不能太宽）
        for risk_type, (lower, upper) in report.confidence_intervals.items():
            ci_width = upper - lower
            assert ci_width <= 0.6, \
                f"{risk_type} confidence interval width {ci_width} is too large (max 0.6)"
            assert ci_width >= 0.0, \
                f"{risk_type} confidence interval width {ci_width} must be non-negative"

    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=5, max_size=15),
        historical_data=valid_time_series_data_strategy()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_risk_assessment_includes_all_required_components(
        self,
        skeleton_data: List[SkeletonData],
        historical_data: TimeSeriesData
    ):
        """
        属性：风险评估必须包含所有必需组件
        
        对于任何风险评估生成，报告必须包含：
        - 用户ID
        - 报告日期
        - 时间范围（开始和结束）
        - 当前衰弱指数
        - 风险预测
        - 趋势分析
        - 置信区间
        - 建议
        - 警报级别
        
        **Validates: Requirements 3.4**
        """
        # 确保所有数据使用相同的user_id
        user_id = historical_data.user_id
        for data in skeleton_data:
            data.user_id = user_id
        
        # 创建风险引擎并生成风险报告
        engine = ActuarialRiskEngine()
        report = engine.generate_risk_report(
            user_id=user_id,
            skeleton_data=skeleton_data,
            historical_data=historical_data
        )
        
        # 验证：必须包含用户ID
        assert report.user_id == user_id, \
            f"Report user_id {report.user_id} must match input {user_id}"
        
        # 验证：必须包含报告日期
        assert report.report_date is not None, \
            "Risk assessment must include report_date"
        
        # 验证：必须包含时间范围
        assert report.period_start is not None, \
            "Risk assessment must include period_start"
        assert report.period_end is not None, \
            "Risk assessment must include period_end"
        
        # 验证：必须包含当前衰弱指数
        assert report.current_frailty is not None, \
            "Risk assessment must include current_frailty"
        assert 0.0 <= report.current_frailty.score <= 1.0, \
            f"Frailty score must be in [0.0, 1.0], got {report.current_frailty.score}"
        
        # 验证：必须包含风险预测
        assert report.risk_prediction is not None, \
            "Risk assessment must include risk_prediction"
        assert 0.0 <= report.risk_prediction.fall_risk_score <= 1.0
        assert 0.0 <= report.risk_prediction.medical_emergency_risk <= 1.0
        assert 0.0 <= report.risk_prediction.mobility_decline_risk <= 1.0
        
        # 验证：必须包含趋势分析
        assert report.trend_analysis is not None, \
            "Risk assessment must include trend_analysis"
        
        # 验证：必须包含置信区间
        assert report.confidence_intervals is not None, \
            "Risk assessment must include confidence_intervals"
        
        # 验证：必须包含建议
        assert report.recommendations is not None, \
            "Risk assessment must include recommendations"
        assert isinstance(report.recommendations, list), \
            "Recommendations must be a list"
        
        # 验证：必须包含警报级别
        assert report.alert_level is not None, \
            "Risk assessment must include alert_level"
        valid_alert_levels = ["low", "medium", "high", "emergency"]
        assert report.alert_level in valid_alert_levels, \
            f"Alert level must be one of {valid_alert_levels}, got {report.alert_level}"
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=5, max_size=15),
        historical_data=valid_time_series_data_strategy()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_risk_assessment_report_date_reasonable(
        self,
        skeleton_data: List[SkeletonData],
        historical_data: TimeSeriesData
    ):
        """
        属性：风险评估报告日期必须合理
        
        对于任何风险评估生成，报告日期应该是当前时间或最近时间。
        
        **Validates: Requirements 3.4**
        """
        # 确保所有数据使用相同的user_id
        user_id = historical_data.user_id
        for data in skeleton_data:
            data.user_id = user_id
        
        # 记录生成前的时间
        before_generation = datetime.utcnow()
        
        # 创建风险引擎并生成风险报告
        engine = ActuarialRiskEngine()
        report = engine.generate_risk_report(
            user_id=user_id,
            skeleton_data=skeleton_data,
            historical_data=historical_data
        )
        
        # 记录生成后的时间
        after_generation = datetime.utcnow()
        
        # 验证：报告日期在合理范围内（允许1秒的时钟偏差）
        assert before_generation - timedelta(seconds=1) <= report.report_date <= after_generation + timedelta(seconds=1), \
            f"Report date {report.report_date} must be between {before_generation} and {after_generation}"
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=5, max_size=15),
        historical_data=valid_time_series_data_strategy()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_risk_assessment_provides_actionable_recommendations(
        self,
        skeleton_data: List[SkeletonData],
        historical_data: TimeSeriesData
    ):
        """
        属性：风险评估必须提供可操作的建议
        
        对于任何风险评估生成，系统必须提供至少一条建议，
        帮助用户或护理人员采取行动。
        
        **Validates: Requirements 3.4**
        """
        # 确保所有数据使用相同的user_id
        user_id = historical_data.user_id
        for data in skeleton_data:
            data.user_id = user_id
        
        # 创建风险引擎并生成风险报告
        engine = ActuarialRiskEngine()
        report = engine.generate_risk_report(
            user_id=user_id,
            skeleton_data=skeleton_data,
            historical_data=historical_data
        )
        
        # 验证：必须提供至少一条建议
        assert len(report.recommendations) > 0, \
            "Risk assessment must provide at least one recommendation"
        
        # 验证：所有建议都是非空字符串
        for recommendation in report.recommendations:
            assert isinstance(recommendation, str), \
                "Each recommendation must be a string"
            assert len(recommendation) > 0, \
                "Each recommendation must be non-empty"
    
    @given(
        skeleton_data=st.lists(valid_skeleton_data_strategy(), min_size=5, max_size=15),
        historical_data=valid_time_series_data_strategy()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_risk_assessment_alert_level_matches_risk_scores(
        self,
        skeleton_data: List[SkeletonData],
        historical_data: TimeSeriesData
    ):
        """
        属性：风险评估警报级别必须与风险分数匹配
        
        对于任何风险评估生成，警报级别应该反映风险分数的严重程度：
        - 高风险分数应产生更高的警报级别
        - 低风险分数应产生较低的警报级别
        
        **Validates: Requirements 3.4**
        """
        # 确保所有数据使用相同的user_id
        user_id = historical_data.user_id
        for data in skeleton_data:
            data.user_id = user_id
        
        # 创建风险引擎并生成风险报告
        engine = ActuarialRiskEngine()
        report = engine.generate_risk_report(
            user_id=user_id,
            skeleton_data=skeleton_data,
            historical_data=historical_data
        )
        
        # 计算最大风险分数
        max_risk = max(
            report.risk_prediction.fall_risk_score,
            report.risk_prediction.medical_emergency_risk,
            report.risk_prediction.mobility_decline_risk
        )
        
        # 验证：警报级别与风险分数一致
        if max_risk >= 0.8:
            # 高风险应该是high或emergency
            assert report.alert_level in ["high", "emergency"], \
                f"High risk score {max_risk} should yield high or emergency alert, got {report.alert_level}"
        elif max_risk <= 0.3:
            # 低风险应该是low或medium
            assert report.alert_level in ["low", "medium"], \
                f"Low risk score {max_risk} should yield low or medium alert, got {report.alert_level}"


# ============================================================================
# 边界条件和错误处理测试
# Edge Cases and Error Handling Tests
# ============================================================================

class TestRiskAssessmentEdgeCases:
    """
    测试风险评估的边界条件和错误处理
    """
    
    def test_risk_assessment_with_minimal_data(self):
        """测试最少数据生成风险评估"""
        engine = ActuarialRiskEngine()
        
        user_id = "user123"
        
        # 最少的骨骼数据
        skeleton_data = [
            SkeletonData(
                timestamp=datetime.utcnow(),
                user_id=user_id,
                keypoints=[Keypoint(JointType.NOSE, 100.0, 200.0)],
                confidence_scores=[0.9],
                anonymized=True
            )
        ]
        
        # 最少的历史数据（10天）
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        data_points = [
            ActivityData(
                user_id=user_id,
                date=start_date + timedelta(days=i),
                steps_count=5000,
                active_minutes=60,
                sleep_hours=7.0
            )
            for i in range(10)
        ]
        
        historical_data = TimeSeriesData(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            data_points=data_points
        )
        
        # 生成风险报告
        report = engine.generate_risk_report(
            user_id=user_id,
            skeleton_data=skeleton_data,
            historical_data=historical_data
        )
        
        # 验证：即使数据最少，也应该生成完整报告
        assert report is not None
        assert report.confidence_intervals is not None
        assert report.trend_analysis is not None
        assert len(report.recommendations) > 0
