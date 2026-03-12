# -*- coding: utf-8 -*-
"""
Property-Based Tests for Insurance Report Anonymization
属性11：保险报告匿名化

**Validates: Requirements 3.5, 8.1, 8.5**

Property 11: Insurance Report Anonymization
对于任何保险集成场景，系统应当在维护严格隐私控制的同时为精算分析生成匿名化风险报告

This test validates that:
1. All insurance reports are properly anonymized
2. No personally identifiable information (PII) is exposed
3. Privacy controls are enforced
4. Audit trails are maintained
5. K-anonymity guarantees are met
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta
from typing import List, Tuple

from app.services.insurance_service import (
    InsuranceIntegrationService,
    DataAnonymizer,
    AuditLogger,
    PrivacyController,
    InsuranceAccessLevel,
    DataAnonymizationLevel,
    AnonymizedRiskProfile,
)
from app.schemas.core import FrailtyIndex, RiskPrediction


# Strategy for generating valid ages (elderly population)
age_strategy = st.integers(min_value=65, max_value=100)

# Strategy for generating risk scores (0.0 to 1.0)
risk_score_strategy = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)

# Strategy for generating component scores
component_strategy = st.dictionaries(
    keys=st.sampled_from(["mobility", "activity", "sleep", "cognition"]),
    values=risk_score_strategy,
    min_size=1,
    max_size=4
)

# Strategy for generating user IDs
user_id_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
    min_size=5,
    max_size=20
)


def generate_frailty_index(user_id: str, score: float, components: dict) -> FrailtyIndex:
    """Generate a FrailtyIndex for testing"""
    return FrailtyIndex(
        user_id=user_id,
        score=score,
        components=components,
        calculation_date=datetime.utcnow(),
        confidence_interval=(max(0.0, score - 0.1), min(1.0, score + 0.1))
    )


def generate_risk_prediction(
    user_id: str,
    fall_risk: float,
    emergency_risk: float,
    decline_risk: float,
    confidence: float
) -> RiskPrediction:
    """Generate a RiskPrediction for testing"""
    return RiskPrediction(
        user_id=user_id,
        prediction_date=datetime.utcnow(),
        fall_risk_score=fall_risk,
        medical_emergency_risk=emergency_risk,
        mobility_decline_risk=decline_risk,
        confidence_level=confidence,
        contributing_factors=["test_factor"]
    )


@given(
    user_id=user_id_strategy,
    age=age_strategy,
    frailty_score=risk_score_strategy,
    components=component_strategy,
    fall_risk=risk_score_strategy,
    emergency_risk=risk_score_strategy,
    decline_risk=risk_score_strategy,
    confidence=risk_score_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_anonymized_user_id_no_pii(
    user_id: str,
    age: int,
    frailty_score: float,
    components: dict,
    fall_risk: float,
    emergency_risk: float,
    decline_risk: float,
    confidence: float
):
    """
    Property: Anonymized user IDs must not contain original PII
    
    For any user ID, the anonymized version should:
    - Not contain the original user ID
    - Be deterministic (same input -> same output with same salt)
    - Be irreversible (one-way transformation)
    """
    anonymizer = DataAnonymizer()
    frailty = generate_frailty_index(user_id, frailty_score, components)
    risk_pred = generate_risk_prediction(
        user_id, fall_risk, emergency_risk, decline_risk, confidence
    )
    
    # Anonymize the profile
    anon_profile = anonymizer.anonymize_risk_profile(user_id, age, frailty, risk_pred)
    
    # Property 1: Anonymized ID should not contain original user ID
    assert user_id not in anon_profile.anonymous_id, \
        "Anonymized ID contains original user ID"
    
    # Property 2: Anonymized ID should have consistent format
    assert anon_profile.anonymous_id.startswith("anon_"), \
        "Anonymized ID should have 'anon_' prefix"
    
    # Property 3: Anonymized ID should be non-empty
    assert len(anon_profile.anonymous_id) > 5, \
        "Anonymized ID is too short"


@given(
    ages=st.lists(age_strategy, min_size=1, max_size=50),
    frailty_scores=st.lists(risk_score_strategy, min_size=1, max_size=50),
    risk_scores=st.lists(risk_score_strategy, min_size=1, max_size=50)
)
@settings(max_examples=100, deadline=None)
def test_property_age_generalization_privacy(
    ages: List[int],
    frailty_scores: List[float],
    risk_scores: List[float]
):
    """
    Property: Age generalization must protect individual privacy
    
    For any set of ages, generalization should:
    - Group ages into ranges (not exact ages)
    - Use consistent bin sizes
    - Prevent re-identification through age
    """
    # Ensure lists are same length
    min_len = min(len(ages), len(frailty_scores), len(risk_scores))
    assume(min_len > 0)
    
    ages = ages[:min_len]
    frailty_scores = frailty_scores[:min_len]
    risk_scores = risk_scores[:min_len]
    
    anonymizer = DataAnonymizer(age_bin_size=5)
    
    for age in ages:
        age_range = anonymizer.generalize_age(age)
        
        # Property 1: Age range should be a range, not exact age
        assert "-" in age_range, "Age should be generalized to a range"
        
        # Property 2: Age range should follow format "X-Y"
        parts = age_range.split("-")
        assert len(parts) == 2, "Age range should have two parts"
        
        lower, upper = int(parts[0]), int(parts[1])
        
        # Property 3: Range should be consistent with bin size
        assert upper - lower == 5, "Age range should match bin size"
        
        # Property 4: Original age should fall within the range
        assert lower <= age < upper, "Original age should be within generalized range"


@given(
    user_data=st.lists(
        st.tuples(
            user_id_strategy,
            age_strategy,
            risk_score_strategy,
            component_strategy,
            risk_score_strategy,
            risk_score_strategy,
            risk_score_strategy,
            risk_score_strategy
        ),
        min_size=5,  # Minimum for k-anonymity
        max_size=20
    )
)
@settings(max_examples=50, deadline=None)
def test_property_k_anonymity_guarantee(user_data):
    """
    Property: K-anonymity must be maintained for all anonymized reports
    
    For any set of user data, anonymized profiles should:
    - Meet k-anonymity requirements (k=5 by default)
    - Have at least k records with same quasi-identifiers
    - Reject reports that don't meet k-anonymity
    """
    assume(len(user_data) >= 5)  # Need at least k records
    
    anonymizer = DataAnonymizer(k_anonymity=5)
    service = InsuranceIntegrationService(anonymizer=anonymizer)
    
    # Generate anonymized profiles
    anonymized_profiles = []
    for user_id, age, frailty_score, components, fall_risk, emergency_risk, decline_risk, confidence in user_data:
        frailty = generate_frailty_index(user_id, frailty_score, components)
        risk_pred = generate_risk_prediction(
            user_id, fall_risk, emergency_risk, decline_risk, confidence
        )
        
        anon_profile = anonymizer.anonymize_risk_profile(user_id, age, frailty, risk_pred)
        anonymized_profiles.append(anon_profile)
    
    # Check k-anonymity
    k_anonymity_satisfied = anonymizer.check_k_anonymity(anonymized_profiles)
    
    # Property: If k-anonymity is satisfied, each quasi-identifier group has >= k members
    if k_anonymity_satisfied:
        groups = {}
        for profile in anonymized_profiles:
            key = (profile.age_range, profile.risk_category)
            groups[key] = groups.get(key, 0) + 1
        
        for count in groups.values():
            assert count >= 5, f"Group has {count} members, less than k=5"


@given(
    accessor_id=st.text(min_size=5, max_size=20),
    access_level=st.sampled_from(list(InsuranceAccessLevel)),
    num_assessments=st.integers(min_value=1, max_value=30)
)
@settings(max_examples=100, deadline=None)
def test_property_privacy_controls_enforced(
    accessor_id: str,
    access_level: InsuranceAccessLevel,
    num_assessments: int
):
    """
    Property: Privacy controls must be enforced for all data access
    
    For any accessor and access level:
    - Access should be denied without proper permissions
    - Access should be granted only with appropriate permissions
    - All access attempts should be audited
    """
    service = InsuranceIntegrationService()
    
    # Generate test data
    test_data = []
    for i in range(num_assessments):
        age = 70 + (i % 20)
        frailty = generate_frailty_index(f"user_{i}", 0.5, {"mobility": 0.5})
        risk_pred = generate_risk_prediction(f"user_{i}", 0.3, 0.2, 0.25, 0.8)
        test_data.append((age, frailty, risk_pred))
    
    # Property 1: Access denied without permission
    report = service.generate_population_risk_report(
        accessor_id=accessor_id,
        risk_assessments=test_data,
        reporting_period_start=datetime.utcnow() - timedelta(days=30),
        reporting_period_end=datetime.utcnow()
    )
    
    assert report is None, "Access should be denied without permission"
    
    # Property 2: Access granted with permission
    service.privacy_controller.grant_access(accessor_id, access_level)
    
    report = service.generate_population_risk_report(
        accessor_id=accessor_id,
        risk_assessments=test_data,
        reporting_period_start=datetime.utcnow() - timedelta(days=30),
        reporting_period_end=datetime.utcnow()
    )
    
    if access_level in [InsuranceAccessLevel.POPULATION_ONLY, 
                        InsuranceAccessLevel.ANONYMIZED_INDIVIDUAL,
                        InsuranceAccessLevel.CONSENTED_INDIVIDUAL]:
        assert report is not None, "Access should be granted with proper permission"
    
    # Property 3: All access attempts are audited
    audit_trail = service.get_audit_trail(accessor_id=accessor_id)
    assert len(audit_trail) >= 1, "All access attempts should be audited"


@given(
    user_data=st.lists(
        st.tuples(
            user_id_strategy,
            age_strategy,
            risk_score_strategy,
            component_strategy,
            risk_score_strategy,
            risk_score_strategy,
            risk_score_strategy,
            risk_score_strategy
        ),
        min_size=1,
        max_size=20
    )
)
@settings(max_examples=100, deadline=None)
def test_property_audit_trail_completeness(user_data):
    """
    Property: Complete audit trail must be maintained for all operations
    
    For any insurance data access:
    - Every access attempt should be logged
    - Audit entries should contain all required information
    - Audit trail should be retrievable
    """
    assume(len(user_data) >= 1)
    
    service = InsuranceIntegrationService()
    accessor_id = "test_accessor"
    
    # Grant access
    service.privacy_controller.grant_access(
        accessor_id,
        InsuranceAccessLevel.POPULATION_ONLY
    )
    
    # Generate test data
    test_data = []
    for user_id, age, frailty_score, components, fall_risk, emergency_risk, decline_risk, confidence in user_data:
        frailty = generate_frailty_index(user_id, frailty_score, components)
        risk_pred = generate_risk_prediction(
            user_id, fall_risk, emergency_risk, decline_risk, confidence
        )
        test_data.append((age, frailty, risk_pred))
    
    # Generate report
    report = service.generate_population_risk_report(
        accessor_id=accessor_id,
        risk_assessments=test_data,
        reporting_period_start=datetime.utcnow() - timedelta(days=30),
        reporting_period_end=datetime.utcnow()
    )
    
    # Property 1: Audit trail exists
    audit_trail = service.get_audit_trail(accessor_id=accessor_id)
    assert len(audit_trail) > 0, "Audit trail should exist"
    
    # Property 2: Audit entries contain required fields
    for entry in audit_trail:
        assert entry.audit_id is not None, "Audit entry should have ID"
        assert entry.timestamp is not None, "Audit entry should have timestamp"
        assert entry.accessor_id == accessor_id, "Audit entry should record accessor"
        assert entry.access_level is not None, "Audit entry should record access level"
        assert entry.action is not None, "Audit entry should record action"
        assert isinstance(entry.success, bool), "Audit entry should record success status"


@given(
    user_data=st.lists(
        st.tuples(
            user_id_strategy,
            age_strategy,
            risk_score_strategy,
            component_strategy,
            risk_score_strategy,
            risk_score_strategy,
            risk_score_strategy,
            risk_score_strategy
        ),
        min_size=1,
        max_size=30
    )
)
@settings(max_examples=100, deadline=None)
def test_property_no_pii_in_population_reports(user_data):
    """
    Property: Population reports must not contain any PII
    
    For any population report:
    - No individual user IDs should be present
    - Only aggregated statistics should be included
    - No individual-level data should be identifiable
    """
    assume(len(user_data) >= 1)
    
    service = InsuranceIntegrationService()
    accessor_id = "test_accessor"
    
    service.privacy_controller.grant_access(
        accessor_id,
        InsuranceAccessLevel.POPULATION_ONLY
    )
    
    # Generate test data and track original user IDs
    test_data = []
    original_user_ids = []
    for user_id, age, frailty_score, components, fall_risk, emergency_risk, decline_risk, confidence in user_data:
        original_user_ids.append(user_id)
        frailty = generate_frailty_index(user_id, frailty_score, components)
        risk_pred = generate_risk_prediction(
            user_id, fall_risk, emergency_risk, decline_risk, confidence
        )
        test_data.append((age, frailty, risk_pred))
    
    # Generate report
    report = service.generate_population_risk_report(
        accessor_id=accessor_id,
        risk_assessments=test_data,
        reporting_period_start=datetime.utcnow() - timedelta(days=30),
        reporting_period_end=datetime.utcnow()
    )
    
    assert report is not None, "Report should be generated"
    
    # Property 1: No individual profiles in population report
    assert report.anonymized_profiles is None, \
        "Population report should not contain individual profiles"
    
    # Property 2: Population statistics should be aggregated
    assert report.population_statistics is not None, \
        "Population report should contain aggregated statistics"
    
    # Property 3: Report should indicate aggregation anonymization
    assert report.anonymization_method == "aggregation", \
        "Population report should use aggregation anonymization"
    
    # Property 4: Privacy guarantees should be documented
    assert "anonymization_level" in report.privacy_guarantees, \
        "Report should document anonymization level"


@given(
    risk_score=risk_score_strategy
)
@settings(max_examples=100, deadline=None)
def test_property_risk_categorization_consistency(risk_score: float):
    """
    Property: Risk categorization must be consistent and deterministic
    
    For any risk score:
    - Categorization should be deterministic
    - Categories should be mutually exclusive
    - Boundaries should be clear and consistent
    """
    anonymizer = DataAnonymizer()
    
    category = anonymizer.categorize_risk_score(risk_score)
    
    # Property 1: Category should be one of the valid values
    assert category in ["low", "medium", "high"], \
        f"Invalid risk category: {category}"
    
    # Property 2: Categorization should be deterministic
    category2 = anonymizer.categorize_risk_score(risk_score)
    assert category == category2, "Risk categorization should be deterministic"
    
    # Property 3: Boundaries should be consistent
    if risk_score < 0.3:
        assert category == "low", "Score < 0.3 should be low risk"
    elif risk_score < 0.6:
        assert category == "medium", "Score 0.3-0.6 should be medium risk"
    else:
        assert category == "high", "Score >= 0.6 should be high risk"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
