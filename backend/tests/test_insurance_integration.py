# -*- coding: utf-8 -*-
"""
Insurance Integration Service Unit Tests
Tests for anonymization, privacy controls, and audit trails
"""
import pytest
from datetime import datetime, timedelta
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


def test_anonymize_user_id():
    """Test user ID anonymization"""
    anonymizer = DataAnonymizer()
    user_id = "user_12345"
    
    anon_id = anonymizer.anonymize_user_id(user_id)
    
    assert anon_id.startswith("anon_")
    assert len(anon_id) > 10
    assert anon_id != user_id


def test_generalize_age():
    """Test age generalization"""
    anonymizer = DataAnonymizer(age_bin_size=5)
    
    assert anonymizer.generalize_age(67) == "65-70"
    assert anonymizer.generalize_age(72) == "70-75"
    assert anonymizer.generalize_age(85) == "85-90"


def test_categorize_risk_score():
    """Test risk score categorization"""
    anonymizer = DataAnonymizer()
    
    assert anonymizer.categorize_risk_score(0.2) == "low"
    assert anonymizer.categorize_risk_score(0.45) == "medium"
    assert anonymizer.categorize_risk_score(0.75) == "high"


def test_audit_logger():
    """Test audit logging"""
    logger = AuditLogger()
    
    entry = logger.log_access(
        accessor_id="insurance_company_1",
        access_level=InsuranceAccessLevel.POPULATION_ONLY,
        data_type="population_risk_report",
        action="generate_report",
        success=True,
        details={"report_id": "test_123"}
    )
    
    assert entry.accessor_id == "insurance_company_1"
    assert entry.success is True
    assert len(entry.audit_id) > 0


def test_privacy_controller_access():
    """Test privacy controller access management"""
    controller = PrivacyController()
    
    controller.grant_access("accessor_1", InsuranceAccessLevel.POPULATION_ONLY)
    
    assert controller.check_access_permission("accessor_1", InsuranceAccessLevel.POPULATION_ONLY) is True
    assert controller.check_access_permission("accessor_2", InsuranceAccessLevel.POPULATION_ONLY) is False


def test_generate_population_risk_report():
    """Test population risk report generation"""
    service = InsuranceIntegrationService()
    service.privacy_controller.grant_access("insurance_1", InsuranceAccessLevel.POPULATION_ONLY)
    
    # Create test data
    test_data = []
    for i in range(10):
        age = 65 + (i % 25)
        
        frailty = FrailtyIndex(
            user_id=f"user_{i}",
            score=0.5,
            components={"mobility": 0.5, "activity": 0.5, "sleep": 0.5},
            calculation_date=datetime.utcnow(),
            confidence_interval=(0.4, 0.6)
        )
        
        risk_pred = RiskPrediction(
            user_id=f"user_{i}",
            prediction_date=datetime.utcnow(),
            fall_risk_score=0.3,
            medical_emergency_risk=0.2,
            mobility_decline_risk=0.25,
            confidence_level=0.8,
            contributing_factors=["test"]
        )
        
        test_data.append((age, frailty, risk_pred))
    
    report = service.generate_population_risk_report(
        accessor_id="insurance_1",
        risk_assessments=test_data,
        reporting_period_start=datetime.utcnow() - timedelta(days=30),
        reporting_period_end=datetime.utcnow()
    )
    
    assert report is not None
    assert report.report_type == "population"
    assert report.population_statistics.population_size == 10
    assert report.anonymization_method == "aggregation"
