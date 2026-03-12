"""
Unit tests for health recommendation service
Tests pattern detection, recommendation generation, and weekly report generation
"""
import pytest
from datetime import datetime, timedelta
from typing import List

from app.services.health_recommendation import (
    HealthPatternDetector,
    RecommendationEngine,
    WeeklyReportGenerator,
    HealthRecommendationService,
    HealthPattern,
    HealthRecommendation,
    RecommendationType,
    InterventionUrgency
)
from app.schemas.core import (
    FrailtyIndex,
    RiskPrediction
)


class TestHealthPatternDetector:
    """Test health pattern detection"""
    
    def test_detect_mobility_decline_severe(self):
        """Test detection of severe mobility decline"""
        detector = HealthPatternDetector(mobility_threshold=0.5)
        
        # Create frailty history with declining mobility
        frailty_history = [
            FrailtyIndex(
                user_id="test_user",
                score=0.6,
                components={"mobility": 0.25},
                calculation_date=datetime.now() - timedelta(days=i),
                confidence_interval=(0.55, 0.65)
            )
            for i in range(7, 0, -1)
        ]
        
        patterns = detector.detect_patterns(frailty_history, [], [])
        
        assert len(patterns) > 0
        mobility_patterns = [p for p in patterns if p.pattern_type == "declining_mobility"]
        assert len(mobility_patterns) == 1
        assert mobility_patterns[0].severity == "severe"
    
    def test_detect_low_activity_moderate(self):
        """Test detection of moderate low activity"""
        detector = HealthPatternDetector(activity_threshold=3000)
        
        activity_history = [
            {"steps_count": 2200, "sleep_hours": 7.0}
            for _ in range(7)
        ]
        
        patterns = detector.detect_patterns([], activity_history, [])
        
        assert len(patterns) > 0
        activity_patterns = [p for p in patterns if p.pattern_type == "low_activity"]
        assert len(activity_patterns) == 1
        assert activity_patterns[0].severity == "moderate"
    
    def test_detect_sleep_issues_insufficient(self):
        """Test detection of insufficient sleep"""
        detector = HealthPatternDetector(sleep_min=6.0)
        
        activity_history = [
            {"steps_count": 5000, "sleep_hours": 5.2}
            for _ in range(7)
        ]
        
        patterns = detector.detect_patterns([], activity_history, [])
        
        assert len(patterns) > 0
        sleep_patterns = [p for p in patterns if p.pattern_type == "sleep_issues"]
        assert len(sleep_patterns) == 1
        assert "睡眠不足" in sleep_patterns[0].description
    
    def test_detect_rising_risk(self):
        """Test detection of rising risk"""
        detector = HealthPatternDetector()
        
        # Create risk history with rising trend
        risk_history = [
            RiskPrediction(
                user_id="test_user",
                prediction_date=datetime.now() - timedelta(days=i),
                fall_risk_score=0.3 + (0.05 * (7-i)),
                medical_emergency_risk=0.3 + (0.05 * (7-i)),
                mobility_decline_risk=0.3 + (0.05 * (7-i)),
                confidence_level=0.8,
                contributing_factors=["低移动性"]
            )
            for i in range(7, 0, -1)
        ]
        
        patterns = detector.detect_patterns([], [], risk_history)
        
        assert len(patterns) > 0
        risk_patterns = [p for p in patterns if p.pattern_type == "rising_risk"]
        assert len(risk_patterns) == 1
        assert risk_patterns[0].trend == "worsening"
    
    def test_no_patterns_detected_healthy(self):
        """Test that no patterns are detected for healthy metrics"""
        detector = HealthPatternDetector()
        
        frailty_history = [
            FrailtyIndex(
                user_id="test_user",
                score=0.85,
                components={"mobility": 0.85, "activity": 0.85, "sleep": 0.85},
                calculation_date=datetime.now() - timedelta(days=i),
                confidence_interval=(0.80, 0.90)
            )
            for i in range(7, 0, -1)
        ]
        
        activity_history = [
            {"steps_count": 6000, "sleep_hours": 7.5}
            for _ in range(7)
        ]
        
        risk_history = [
            RiskPrediction(
                user_id="test_user",
                prediction_date=datetime.now() - timedelta(days=i),
                fall_risk_score=0.2,
                medical_emergency_risk=0.2,
                mobility_decline_risk=0.2,
                confidence_level=0.8,
                contributing_factors=[]
            )
            for i in range(7, 0, -1)
        ]
        
        patterns = detector.detect_patterns(frailty_history, activity_history, risk_history)
        
        # Should have no concerning patterns
        assert len(patterns) == 0


class TestRecommendationEngine:
    """Test recommendation generation"""
    
    def test_generate_mobility_recommendation_severe(self):
        """Test generation of severe mobility recommendation"""
        engine = RecommendationEngine()
        
        pattern = HealthPattern(
            pattern_type="declining_mobility",
            severity="severe",
            detected_date=datetime.now(),
            description="移动能力严重下降",
            metrics={"average_mobility": 0.25},
            trend="worsening"
        )
        
        frailty = FrailtyIndex(
            user_id="test_user",
            score=0.4,
            components={"mobility": 0.25},
            calculation_date=datetime.now(),
            confidence_interval=(0.35, 0.45)
        )
        
        risk = RiskPrediction(
            user_id="test_user",
            prediction_date=datetime.now(),
            fall_risk_score=0.7,
            medical_emergency_risk=0.5,
            mobility_decline_risk=0.8,
            confidence_level=0.8,
            contributing_factors=["低移动性"]
        )
        
        recommendations = engine.generate_recommendations("test_user", [pattern], frailty, risk)
        
        assert len(recommendations) > 0
        mobility_recs = [r for r in recommendations if "移动" in r.title]
        assert len(mobility_recs) > 0
        assert mobility_recs[0].urgency == InterventionUrgency.URGENT
        assert mobility_recs[0].recommendation_type == RecommendationType.PHYSICAL_THERAPY
    
    def test_generate_activity_recommendation(self):
        """Test generation of activity recommendation"""
        engine = RecommendationEngine()
        
        pattern = HealthPattern(
            pattern_type="low_activity",
            severity="moderate",
            detected_date=datetime.now(),
            description="活动量偏低",
            metrics={"average_steps": 2200, "threshold": 3000},
            trend="stable"
        )
        
        frailty = FrailtyIndex(
            user_id="test_user",
            score=0.6,
            components={"activity": 0.5},
            calculation_date=datetime.now(),
            confidence_interval=(0.55, 0.65)
        )
        
        risk = RiskPrediction(
            user_id="test_user",
            prediction_date=datetime.now(),
            fall_risk_score=0.4,
            medical_emergency_risk=0.3,
            mobility_decline_risk=0.4,
            confidence_level=0.8,
            contributing_factors=["活动水平不足"]
        )
        
        recommendations = engine.generate_recommendations("test_user", [pattern], frailty, risk)
        
        assert len(recommendations) > 0
        activity_recs = [r for r in recommendations if "活动" in r.title]
        assert len(activity_recs) > 0
        assert activity_recs[0].recommendation_type == RecommendationType.LIFESTYLE_CHANGE
    
    def test_generate_sleep_recommendation(self):
        """Test generation of sleep recommendation"""
        engine = RecommendationEngine()
        
        pattern = HealthPattern(
            pattern_type="sleep_issues",
            severity="moderate",
            detected_date=datetime.now(),
            description="睡眠不足",
            metrics={"average_sleep": 5.5, "min_threshold": 6.0},
            trend="stable"
        )
        
        frailty = FrailtyIndex(
            user_id="test_user",
            score=0.6,
            components={"sleep": 0.5},
            calculation_date=datetime.now(),
            confidence_interval=(0.55, 0.65)
        )
        
        risk = RiskPrediction(
            user_id="test_user",
            prediction_date=datetime.now(),
            fall_risk_score=0.4,
            medical_emergency_risk=0.4,
            mobility_decline_risk=0.3,
            confidence_level=0.8,
            contributing_factors=["睡眠质量差"]
        )
        
        recommendations = engine.generate_recommendations("test_user", [pattern], frailty, risk)
        
        assert len(recommendations) > 0
        sleep_recs = [r for r in recommendations if "睡眠" in r.title]
        assert len(sleep_recs) > 0
        assert len(sleep_recs[0].specific_actions) > 0
    
    def test_generate_risk_management_recommendation(self):
        """Test generation of risk management recommendation"""
        engine = RecommendationEngine()
        
        pattern = HealthPattern(
            pattern_type="rising_risk",
            severity="severe",
            detected_date=datetime.now(),
            description="健康风险持续上升",
            metrics={"average_risk": 0.75},
            trend="worsening"
        )
        
        frailty = FrailtyIndex(
            user_id="test_user",
            score=0.3,
            components={"mobility": 0.3},
            calculation_date=datetime.now(),
            confidence_interval=(0.25, 0.35)
        )
        
        risk = RiskPrediction(
            user_id="test_user",
            prediction_date=datetime.now(),
            fall_risk_score=0.8,
            medical_emergency_risk=0.7,
            mobility_decline_risk=0.75,
            confidence_level=0.8,
            contributing_factors=["低移动性", "活动水平不足", "步态不稳定"]
        )
        
        recommendations = engine.generate_recommendations("test_user", [pattern], frailty, risk)
        
        assert len(recommendations) > 0
        risk_recs = [r for r in recommendations if "风险" in r.title]
        assert len(risk_recs) > 0
        assert risk_recs[0].urgency == InterventionUrgency.IMMEDIATE
        assert risk_recs[0].recommendation_type == RecommendationType.MEDICAL_CONSULTATION
    
    def test_generate_preventive_recommendations_no_patterns(self):
        """Test generation of preventive recommendations when no patterns detected"""
        engine = RecommendationEngine()
        
        frailty = FrailtyIndex(
            user_id="test_user",
            score=0.7,
            components={"mobility": 0.7},
            calculation_date=datetime.now(),
            confidence_interval=(0.65, 0.75)
        )
        
        risk = RiskPrediction(
            user_id="test_user",
            prediction_date=datetime.now(),
            fall_risk_score=0.6,  # High enough to trigger prevention
            medical_emergency_risk=0.3,
            mobility_decline_risk=0.4,
            confidence_level=0.8,
            contributing_factors=[]
        )
        
        recommendations = engine.generate_recommendations("test_user", [], frailty, risk)
        
        # Should generate preventive recommendations
        assert len(recommendations) > 0
        assert any("跌倒" in r.title for r in recommendations)


class TestWeeklyReportGenerator:
    """Test weekly report generation"""
    
    def test_generate_weekly_report_basic(self):
        """Test basic weekly report generation"""
        generator = WeeklyReportGenerator()
        
        week_start = datetime.now() - timedelta(days=7)
        week_end = datetime.now()
        
        current_week_data = {
            "average_daily_steps": 5000,
            "average_sleep_hours": 7.5,
            "average_mobility_score": 0.75,
            "average_frailty_score": 0.25,
            "daily_steps_list": [4800, 5000, 5200, 5100, 4900, 5000, 5000],
            "daily_sleep_list": [7.5, 7.0, 8.0, 7.5, 7.5, 7.0, 8.0],
            "daily_mobility_list": [0.75, 0.75, 0.76, 0.74, 0.75, 0.76, 0.75],
            "activity_history": []
        }
        
        baseline_data = {
            "average_daily_steps": 5000,
            "average_sleep_hours": 7.0,
            "baseline_mobility_score": 0.7
        }
        
        frailty_history = [
            FrailtyIndex(
                user_id="test_user",
                score=0.75,
                components={"mobility": 0.75},
                calculation_date=datetime.now() - timedelta(days=i),
                confidence_interval=(0.70, 0.80)
            )
            for i in range(7, 0, -1)
        ]
        
        risk_history = [
            RiskPrediction(
                user_id="test_user",
                prediction_date=datetime.now() - timedelta(days=i),
                fall_risk_score=0.3,
                medical_emergency_risk=0.3,
                mobility_decline_risk=0.3,
                confidence_level=0.8,
                contributing_factors=[]
            )
            for i in range(7, 0, -1)
        ]
        
        report = generator.generate_weekly_report(
            "test_user", week_start, week_end,
            current_week_data, None, baseline_data,
            frailty_history, risk_history
        )
        
        assert report.user_id == "test_user"
        assert report.average_daily_steps == 5000
        assert report.average_sleep_hours == 7.5
        assert report.average_mobility_score == 0.75
        assert 0.0 <= report.overall_health_score <= 1.0
        assert report.activity_trend in ["improving", "stable", "declining"]
        assert report.sleep_trend in ["improving", "stable", "declining"]
        assert report.mobility_trend in ["improving", "stable", "declining"]
        assert len(report.highlights) > 0
    
    def test_generate_weekly_report_with_last_week(self):
        """Test weekly report generation with last week comparison"""
        generator = WeeklyReportGenerator()
        
        week_start = datetime.now() - timedelta(days=7)
        week_end = datetime.now()
        
        current_week_data = {
            "average_daily_steps": 5500,
            "average_sleep_hours": 7.5,
            "average_mobility_score": 0.80,
            "average_frailty_score": 0.20,
            "daily_steps_list": [5400, 5500, 5600, 5500, 5400, 5500, 5500],
            "daily_sleep_list": [7.5] * 7,
            "daily_mobility_list": [0.80] * 7,
            "activity_history": []
        }
        
        last_week_data = {
            "average_daily_steps": 5000,
            "average_sleep_hours": 7.0,
            "average_mobility_score": 0.75,
            "average_frailty_score": 0.25
        }
        
        baseline_data = {
            "average_daily_steps": 5000,
            "average_sleep_hours": 7.0,
            "baseline_mobility_score": 0.7
        }
        
        frailty_history = [
            FrailtyIndex(
                user_id="test_user",
                score=0.80,
                components={"mobility": 0.80},
                calculation_date=datetime.now() - timedelta(days=i),
                confidence_interval=(0.75, 0.85)
            )
            for i in range(7, 0, -1)
        ]
        
        risk_history = [
            RiskPrediction(
                user_id="test_user",
                prediction_date=datetime.now() - timedelta(days=i),
                fall_risk_score=0.2,
                medical_emergency_risk=0.2,
                mobility_decline_risk=0.2,
                confidence_level=0.8,
                contributing_factors=[]
            )
            for i in range(7, 0, -1)
        ]
        
        report = generator.generate_weekly_report(
            "test_user", week_start, week_end,
            current_week_data, last_week_data, baseline_data,
            frailty_history, risk_history
        )
        
        # Should show improvement
        assert report.steps_vs_last_week > 0
        assert report.mobility_vs_last_week > 0
        assert report.week_over_week_change > 0
        assert len(report.highlights) > 0
    
    def test_generate_weekly_report_with_concerns(self):
        """Test weekly report generation with health concerns"""
        generator = WeeklyReportGenerator()
        
        week_start = datetime.now() - timedelta(days=7)
        week_end = datetime.now()
        
        current_week_data = {
            "average_daily_steps": 1800,  # Very low
            "average_sleep_hours": 4.5,  # Insufficient
            "average_mobility_score": 0.35,  # Low
            "average_frailty_score": 0.65,  # High frailty
            "daily_steps_list": [1800] * 7,
            "daily_sleep_list": [4.5] * 7,
            "daily_mobility_list": [0.35] * 7,
            "activity_history": [
                {"steps_count": 1800, "sleep_hours": 4.5}
                for _ in range(7)
            ]
        }
        
        baseline_data = {
            "average_daily_steps": 5000,
            "average_sleep_hours": 7.0,
            "baseline_mobility_score": 0.7
        }
        
        frailty_history = [
            FrailtyIndex(
                user_id="test_user",
                score=0.35,
                components={"mobility": 0.35, "activity": 0.3, "sleep": 0.4},
                calculation_date=datetime.now() - timedelta(days=i),
                confidence_interval=(0.30, 0.40)
            )
            for i in range(7, 0, -1)
        ]
        
        risk_history = [
            RiskPrediction(
                user_id="test_user",
                prediction_date=datetime.now() - timedelta(days=i),
                fall_risk_score=0.7,
                medical_emergency_risk=0.6,
                mobility_decline_risk=0.7,
                confidence_level=0.8,
                contributing_factors=["低移动性", "活动水平不足"]
            )
            for i in range(7, 0, -1)
        ]
        
        report = generator.generate_weekly_report(
            "test_user", week_start, week_end,
            current_week_data, None, baseline_data,
            frailty_history, risk_history
        )
        
        # Should have concerns
        assert len(report.concerns) > 0
        assert len(report.detected_patterns) > 0
        assert len(report.recommendations) > 0
    
    def test_weekly_report_to_dict(self):
        """Test weekly report serialization to dict"""
        generator = WeeklyReportGenerator()
        
        week_start = datetime.now() - timedelta(days=7)
        week_end = datetime.now()
        
        current_week_data = {
            "average_daily_steps": 5000,
            "average_sleep_hours": 7.5,
            "average_mobility_score": 0.75,
            "average_frailty_score": 0.25,
            "daily_steps_list": [5000] * 7,
            "daily_sleep_list": [7.5] * 7,
            "daily_mobility_list": [0.75] * 7,
            "activity_history": []
        }
        
        baseline_data = {
            "average_daily_steps": 5000,
            "average_sleep_hours": 7.0,
            "baseline_mobility_score": 0.7
        }
        
        report = generator.generate_weekly_report(
            "test_user", week_start, week_end,
            current_week_data, None, baseline_data, [], []
        )
        
        report_dict = report.to_dict()
        
        assert "user_id" in report_dict
        assert "report_id" in report_dict
        assert "key_metrics" in report_dict
        assert "trends" in report_dict
        assert "comparisons" in report_dict
        assert "detected_patterns" in report_dict
        assert "recommendations" in report_dict
        assert "highlights" in report_dict
        assert "concerns" in report_dict


class TestHealthRecommendationService:
    """Test main health recommendation service"""
    
    def test_analyze_health_patterns(self):
        """Test health pattern analysis"""
        service = HealthRecommendationService()
        
        frailty_history = [
            FrailtyIndex(
                user_id="test_user",
                score=0.4,
                components={"mobility": 0.35},
                calculation_date=datetime.now() - timedelta(days=i),
                confidence_interval=(0.35, 0.45)
            )
            for i in range(7, 0, -1)
        ]
        
        activity_history = [
            {"steps_count": 2000, "sleep_hours": 5.5}
            for _ in range(7)
        ]
        
        risk_history = [
            RiskPrediction(
                user_id="test_user",
                prediction_date=datetime.now() - timedelta(days=i),
                fall_risk_score=0.6,
                medical_emergency_risk=0.5,
                mobility_decline_risk=0.6,
                confidence_level=0.8,
                contributing_factors=["低移动性"]
            )
            for i in range(7, 0, -1)
        ]
        
        patterns, recommendations = service.analyze_health_patterns(
            "test_user", frailty_history, activity_history, risk_history
        )
        
        assert len(patterns) > 0
        assert len(recommendations) > 0
    
    def test_get_intervention_guidance(self):
        """Test getting intervention guidance details"""
        service = HealthRecommendationService()
        
        recommendation = HealthRecommendation(
            recommendation_id="test-rec-1",
            recommendation_type=RecommendationType.PHYSICAL_THERAPY,
            urgency=InterventionUrgency.URGENT,
            title="测试建议",
            description="测试描述",
            rationale="测试理由",
            specific_actions=["行动1", "行动2", "行动3"],
            expected_outcomes=["结果1", "结果2"],
            follow_up_timeline="1周后",
            related_patterns=["test_pattern"]
        )
        
        guidance = service.get_intervention_guidance(recommendation)
        
        assert "recommendation_id" in guidance
        assert "action_plan" in guidance
        assert "immediate_actions" in guidance["action_plan"]
        assert "ongoing_actions" in guidance["action_plan"]
        assert "urgency_timeline" in guidance
        assert "consultation_needed" in guidance
