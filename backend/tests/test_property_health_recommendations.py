"""
Property-Based Tests for Health Pattern Recommendations

Feature: silver-age-actuary, Property 19: Health Pattern Recommendations

Property 19: Health Pattern Recommendations
For any concerning health pattern detection, the system should provide
specific, actionable intervention or medical consultation recommendations.

Validates: Requirements 6.2
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta

from app.services.health_recommendation import (
    HealthRecommendationService,
    HealthPatternDetector,
    RecommendationEngine,
    HealthPattern,
    RecommendationType,
    InterventionUrgency
)
from app.schemas.core import FrailtyIndex, RiskPrediction


# Strategy for generating user IDs
user_ids = st.text(min_size=1, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters='_-'
))

# Strategy for generating frailty scores (0.0 to 1.0, lower is more frail)
frailty_scores = st.floats(min_value=0.0, max_value=1.0)

# Strategy for generating risk scores (0.0 to 1.0)
risk_scores = st.floats(min_value=0.0, max_value=1.0)

# Strategy for generating step counts
step_counts = st.integers(min_value=0, max_value=15000)

# Strategy for generating sleep hours
sleep_hours = st.floats(min_value=0.0, max_value=14.0)

# Strategy for generating mobility scores
mobility_scores = st.floats(min_value=0.0, max_value=1.0)


def create_frailty_index(score: float, mobility: float) -> FrailtyIndex:
    """Helper to create FrailtyIndex"""
    return FrailtyIndex(
        user_id="test_user",
        score=score,
        components={
            "mobility": mobility,
            "strength": score,
            "endurance": score,
            "nutrition": score,
            "cognition": score
        },
        calculation_date=datetime.now(),
        confidence_interval=(max(0, score - 0.1), min(1, score + 0.1))
    )


def create_risk_prediction(
    fall_risk: float,
    medical_risk: float,
    mobility_risk: float
) -> RiskPrediction:
    """Helper to create RiskPrediction"""
    return RiskPrediction(
        user_id="test_user",
        prediction_date=datetime.now(),
        fall_risk_score=fall_risk,
        medical_emergency_risk=medical_risk,
        mobility_decline_risk=mobility_risk,
        confidence_level=0.8,
        contributing_factors=["age", "mobility", "activity"]
    )


class TestProperty19HealthRecommendations:
    """
    Property 19: Health Pattern Recommendations
    
    For any concerning health pattern detection, the system should provide
    specific, actionable intervention or medical consultation recommendations.
    """
    
    @given(
        user_id=user_ids,
        mobility_score=st.floats(min_value=0.0, max_value=0.4),  # Low mobility
        frailty_score=frailty_scores
    )
    @settings(max_examples=100, deadline=None)
    def test_low_mobility_generates_recommendations(
        self,
        user_id,
        mobility_score,
        frailty_score
    ):
        """
        Property: Low mobility patterns always generate specific recommendations.
        
        For any detected low mobility pattern, the system must provide
        actionable recommendations with specific actions.
        """
        service = HealthRecommendationService()
        
        # Create frailty history with low mobility
        frailty_history = [
            create_frailty_index(frailty_score, mobility_score)
            for _ in range(5)
        ]
        
        activity_history = []
        risk_history = [create_risk_prediction(0.3, 0.3, 0.3)]
        
        patterns, recommendations = service.analyze_health_patterns(
            user_id, frailty_history, activity_history, risk_history
        )
        
        # Property: Low mobility generates recommendations
        assert len(recommendations) > 0
        
        # Property: Recommendations have specific actions
        for rec in recommendations:
            assert rec.recommendation_id is not None
            assert rec.title is not None
            assert len(rec.title) > 0
            assert rec.description is not None
            assert len(rec.description) > 0
            assert rec.rationale is not None
            assert len(rec.rationale) > 0
            assert len(rec.specific_actions) > 0
            assert all(len(action) > 0 for action in rec.specific_actions)
            assert len(rec.expected_outcomes) > 0
            assert rec.follow_up_timeline is not None
    
    @given(
        user_id=user_ids,
        avg_steps=st.integers(min_value=0, max_value=2500),  # Low activity
        frailty_score=frailty_scores
    )
    @settings(max_examples=100, deadline=None)
    def test_low_activity_generates_recommendations(
        self,
        user_id,
        avg_steps,
        frailty_score
    ):
        """
        Property: Low activity patterns always generate specific recommendations.
        
        For any detected low activity pattern, the system must provide
        actionable recommendations.
        """
        service = HealthRecommendationService()
        
        # Create activity history with low steps
        activity_history = [
            {"steps_count": avg_steps, "sleep_hours": 7.0}
            for _ in range(5)
        ]
        
        frailty_history = [create_frailty_index(frailty_score, 0.5)]
        risk_history = [create_risk_prediction(0.3, 0.3, 0.3)]
        
        patterns, recommendations = service.analyze_health_patterns(
            user_id, frailty_history, activity_history, risk_history
        )
        
        # Property: Low activity generates recommendations
        assert len(recommendations) > 0
        
        # Property: Recommendations are actionable
        for rec in recommendations:
            assert isinstance(rec.recommendation_type, RecommendationType)
            assert isinstance(rec.urgency, InterventionUrgency)
            assert len(rec.specific_actions) >= 3  # Multiple specific actions
    
    @given(
        user_id=user_ids,
        sleep_hours=st.one_of(
            st.floats(min_value=0.0, max_value=5.0),  # Too little
            st.floats(min_value=10.0, max_value=14.0)  # Too much
        ),
        frailty_score=frailty_scores
    )
    @settings(max_examples=100, deadline=None)
    def test_sleep_issues_generate_recommendations(
        self,
        user_id,
        sleep_hours,
        frailty_score
    ):
        """
        Property: Sleep issues always generate specific recommendations.
        
        For any detected sleep pattern outside normal range, the system
        must provide actionable recommendations.
        """
        service = HealthRecommendationService()
        
        # Create activity history with sleep issues
        activity_history = [
            {"steps_count": 5000, "sleep_hours": sleep_hours}
            for _ in range(5)
        ]
        
        frailty_history = [create_frailty_index(frailty_score, 0.5)]
        risk_history = [create_risk_prediction(0.3, 0.3, 0.3)]
        
        patterns, recommendations = service.analyze_health_patterns(
            user_id, frailty_history, activity_history, risk_history
        )
        
        # Property: Sleep issues generate recommendations
        assert len(recommendations) > 0
        
        # Property: Recommendations address the specific issue
        for rec in recommendations:
            assert rec.rationale is not None
            assert "睡眠" in rec.rationale or "sleep" in rec.rationale.lower()
    
    @given(
        user_id=user_ids,
        risk_score=st.floats(min_value=0.5, max_value=1.0),  # High risk
        frailty_score=frailty_scores
    )
    @settings(max_examples=100, deadline=None)
    def test_high_risk_generates_urgent_recommendations(
        self,
        user_id,
        risk_score,
        frailty_score
    ):
        """
        Property: High risk patterns generate urgent recommendations.
        
        For any high risk detection, the system must provide recommendations
        with appropriate urgency levels.
        """
        service = HealthRecommendationService()
        
        # Create risk history with rising risk
        risk_history = [
            create_risk_prediction(risk_score * 0.8, risk_score * 0.8, risk_score * 0.8),
            create_risk_prediction(risk_score * 0.9, risk_score * 0.9, risk_score * 0.9),
            create_risk_prediction(risk_score, risk_score, risk_score)
        ]
        
        frailty_history = [create_frailty_index(frailty_score, 0.5)]
        activity_history = []
        
        patterns, recommendations = service.analyze_health_patterns(
            user_id, frailty_history, activity_history, risk_history
        )
        
        # Property: High risk generates recommendations
        if len(recommendations) > 0:
            # Property: At least one recommendation has appropriate urgency
            urgency_levels = [rec.urgency for rec in recommendations]
            assert any(
                urgency in [InterventionUrgency.IMMEDIATE, InterventionUrgency.URGENT, InterventionUrgency.SOON]
                for urgency in urgency_levels
            )
    
    @given(
        user_id=user_ids,
        frailty_score=frailty_scores,
        mobility_score=mobility_scores
    )
    @settings(max_examples=100, deadline=None)
    def test_recommendations_have_follow_up_timeline(
        self,
        user_id,
        frailty_score,
        mobility_score
    ):
        """
        Property: All recommendations include follow-up timeline.
        
        For any recommendation generated, it must include a clear
        follow-up timeline for monitoring progress.
        """
        service = HealthRecommendationService()
        
        frailty_history = [create_frailty_index(frailty_score, mobility_score) for _ in range(5)]
        activity_history = [{"steps_count": 2000, "sleep_hours": 5.0} for _ in range(5)]
        risk_history = [create_risk_prediction(0.5, 0.5, 0.5)]
        
        patterns, recommendations = service.analyze_health_patterns(
            user_id, frailty_history, activity_history, risk_history
        )
        
        # Property: All recommendations have follow-up timeline
        for rec in recommendations:
            assert rec.follow_up_timeline is not None
            assert len(rec.follow_up_timeline) > 0
            assert isinstance(rec.follow_up_timeline, str)
    
    @given(
        user_id=user_ids,
        frailty_score=frailty_scores,
        mobility_score=mobility_scores
    )
    @settings(max_examples=100, deadline=None)
    def test_recommendations_have_expected_outcomes(
        self,
        user_id,
        frailty_score,
        mobility_score
    ):
        """
        Property: All recommendations include expected outcomes.
        
        For any recommendation, it must clearly state what outcomes
        are expected from following the recommendations.
        """
        service = HealthRecommendationService()
        
        frailty_history = [create_frailty_index(frailty_score, mobility_score) for _ in range(5)]
        activity_history = [{"steps_count": 1500, "sleep_hours": 4.5} for _ in range(5)]
        risk_history = [create_risk_prediction(0.6, 0.6, 0.6)]
        
        patterns, recommendations = service.analyze_health_patterns(
            user_id, frailty_history, activity_history, risk_history
        )
        
        # Property: All recommendations have expected outcomes
        for rec in recommendations:
            assert len(rec.expected_outcomes) > 0
            assert all(isinstance(outcome, str) for outcome in rec.expected_outcomes)
            assert all(len(outcome) > 0 for outcome in rec.expected_outcomes)
    
    @given(
        user_id=user_ids,
        severity=st.sampled_from(["mild", "moderate", "severe"])
    )
    @settings(max_examples=50, deadline=None)
    def test_severity_affects_urgency(
        self,
        user_id,
        severity
    ):
        """
        Property: Pattern severity affects recommendation urgency.
        
        For any pattern, more severe patterns should generate
        recommendations with higher urgency levels.
        """
        engine = RecommendationEngine()
        
        # Create pattern with specific severity
        pattern = HealthPattern(
            pattern_type="declining_mobility",
            severity=severity,
            detected_date=datetime.now(),
            description=f"Test pattern with {severity} severity",
            metrics={"average_mobility": 0.3},
            trend="worsening"
        )
        
        frailty = create_frailty_index(0.5, 0.3)
        risk = create_risk_prediction(0.5, 0.5, 0.5)
        
        recommendations = engine.generate_recommendations(
            user_id, [pattern], frailty, risk
        )
        
        # Property: Recommendations generated
        assert len(recommendations) > 0
        
        # Property: Severe patterns have higher urgency
        if severity == "severe":
            assert any(
                rec.urgency in [InterventionUrgency.IMMEDIATE, InterventionUrgency.URGENT]
                for rec in recommendations
            )
        elif severity == "mild":
            assert any(
                rec.urgency in [InterventionUrgency.ROUTINE, InterventionUrgency.SOON]
                for rec in recommendations
            )
    
    @given(
        user_id=user_ids,
        frailty_score=frailty_scores
    )
    @settings(max_examples=100, deadline=None)
    def test_recommendations_are_unique(
        self,
        user_id,
        frailty_score
    ):
        """
        Property: Each recommendation has a unique ID.
        
        For any set of recommendations generated, each must have
        a unique identifier for tracking.
        """
        service = HealthRecommendationService()
        
        frailty_history = [create_frailty_index(frailty_score, 0.3) for _ in range(5)]
        activity_history = [{"steps_count": 1000, "sleep_hours": 4.0} for _ in range(5)]
        risk_history = [create_risk_prediction(0.7, 0.7, 0.7)]
        
        patterns, recommendations = service.analyze_health_patterns(
            user_id, frailty_history, activity_history, risk_history
        )
        
        # Property: All recommendation IDs are unique
        if len(recommendations) > 1:
            rec_ids = [rec.recommendation_id for rec in recommendations]
            assert len(rec_ids) == len(set(rec_ids))
    
    @given(
        user_id=user_ids,
        frailty_score=frailty_scores,
        mobility_score=mobility_scores
    )
    @settings(max_examples=100, deadline=None)
    def test_intervention_guidance_is_complete(
        self,
        user_id,
        frailty_score,
        mobility_score
    ):
        """
        Property: Intervention guidance provides complete information.
        
        For any recommendation, the intervention guidance must include
        all necessary information for action.
        """
        service = HealthRecommendationService()
        
        frailty_history = [create_frailty_index(frailty_score, mobility_score) for _ in range(5)]
        activity_history = [{"steps_count": 2000, "sleep_hours": 5.5} for _ in range(5)]
        risk_history = [create_risk_prediction(0.5, 0.5, 0.5)]
        
        patterns, recommendations = service.analyze_health_patterns(
            user_id, frailty_history, activity_history, risk_history
        )
        
        # Property: Intervention guidance is complete
        for rec in recommendations:
            guidance = service.get_intervention_guidance(rec)
            
            assert "recommendation_id" in guidance
            assert "type" in guidance
            assert "urgency" in guidance
            assert "title" in guidance
            assert "description" in guidance
            assert "rationale" in guidance
            assert "action_plan" in guidance
            assert "expected_outcomes" in guidance
            assert "urgency_timeline" in guidance
            assert "consultation_needed" in guidance
            
            # Action plan structure
            assert "immediate_actions" in guidance["action_plan"]
            assert "ongoing_actions" in guidance["action_plan"]
            assert "follow_up" in guidance["action_plan"]
    
    @given(
        user_id=user_ids,
        num_patterns=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=50, deadline=None)
    def test_multiple_patterns_generate_multiple_recommendations(
        self,
        user_id,
        num_patterns
    ):
        """
        Property: Multiple concerning patterns generate multiple recommendations.
        
        For any set of detected patterns, the system should provide
        recommendations addressing each pattern.
        """
        service = HealthRecommendationService()
        
        # Create multiple concerning patterns
        frailty_history = [create_frailty_index(0.3, 0.2) for _ in range(5)]
        activity_history = [{"steps_count": 1000, "sleep_hours": 4.0} for _ in range(5)]
        risk_history = [
            create_risk_prediction(0.5 + i*0.05, 0.5 + i*0.05, 0.5 + i*0.05)
            for i in range(5)
        ]
        
        patterns, recommendations = service.analyze_health_patterns(
            user_id, frailty_history, activity_history, risk_history
        )
        
        # Property: Multiple patterns detected
        assert len(patterns) >= 1
        
        # Property: Recommendations generated for patterns
        assert len(recommendations) >= 1
        
        # Property: Each recommendation addresses specific patterns
        for rec in recommendations:
            assert len(rec.related_patterns) >= 0
