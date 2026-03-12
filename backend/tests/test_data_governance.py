"""
Unit tests for Data Governance Service

Tests consent management, retention policies, and breach detection.
"""

import pytest
from datetime import datetime, timedelta

from app.services.data_governance import DataGovernanceService
from app.schemas.governance import (
    ConsentRequest, ConsentRevocation, ConsentType, ConsentStatus,
    DataCategory, BreachSeverity
)


@pytest.fixture
def governance_service():
    """Create a fresh governance service for each test"""
    return DataGovernanceService()


class TestConsentManagement:
    """Test consent collection and management"""
    
    def test_collect_consent_creates_record(self, governance_service):
        """Test that consent collection creates a valid record"""
        request = ConsentRequest(
            user_id="user_123",
            consent_type=ConsentType.MONITORING,
            purpose_description="24/7 health monitoring",
            data_usage_details="Video processing for skeleton extraction"
        )
        
        consent = governance_service.collect_consent(request)
        
        assert consent.user_id == "user_123"
        assert consent.consent_type == ConsentType.MONITORING
        assert consent.status == ConsentStatus.GRANTED
        assert consent.purpose_description == "24/7 health monitoring"
        assert consent.granted_at is not None
    
    def test_collect_consent_with_expiration(self, governance_service):
        """Test consent with expiration date"""
        request = ConsentRequest(
            user_id="user_123",
            consent_type=ConsentType.RESEARCH,
            purpose_description="Research study participation",
            data_usage_details="Anonymized data for research",
            expires_in_days=30
        )
        
        consent = governance_service.collect_consent(request)
        
        assert consent.expires_at is not None
        expected_expiry = datetime.utcnow() + timedelta(days=30)
        assert abs((consent.expires_at - expected_expiry).total_seconds()) < 5
    
    def test_revoke_consent(self, governance_service):
        """Test consent revocation"""
        # First grant consent
        request = ConsentRequest(
            user_id="user_123",
            consent_type=ConsentType.INSURANCE_SHARING,
            purpose_description="Insurance risk assessment",
            data_usage_details="Anonymized health data sharing"
        )
        consent = governance_service.collect_consent(request)
        
        # Then revoke it
        revocation = ConsentRevocation(
            consent_id=consent.consent_id,
            user_id="user_123",
            reason="No longer needed"
        )
        
        revoked_consent = governance_service.revoke_consent(revocation)
        
        assert revoked_consent.status == ConsentStatus.REVOKED
        assert revoked_consent.revoked_at is not None
    
    def test_revoke_consent_wrong_user(self, governance_service):
        """Test that users cannot revoke other users' consents"""
        # Grant consent to user_123
        request = ConsentRequest(
            user_id="user_123",
            consent_type=ConsentType.MONITORING,
            purpose_description="Monitoring",
            data_usage_details="Data usage"
        )
        consent = governance_service.collect_consent(request)
        
        # Try to revoke as user_456
        revocation = ConsentRevocation(
            consent_id=consent.consent_id,
            user_id="user_456"
        )
        
        with pytest.raises(ValueError, match="does not have permission"):
            governance_service.revoke_consent(revocation)
    
    def test_check_consent_valid(self, governance_service):
        """Test checking valid consent"""
        request = ConsentRequest(
            user_id="user_123",
            consent_type=ConsentType.MONITORING,
            purpose_description="Monitoring",
            data_usage_details="Data usage"
        )
        governance_service.collect_consent(request)
        
        has_consent = governance_service.check_consent("user_123", ConsentType.MONITORING)
        
        assert has_consent is True
    
    def test_check_consent_expired(self, governance_service):
        """Test that expired consent is detected"""
        # Create consent that expired 1 day ago
        request = ConsentRequest(
            user_id="user_123",
            consent_type=ConsentType.RESEARCH,
            purpose_description="Research",
            data_usage_details="Data usage",
            expires_in_days=-1  # Already expired
        )
        consent = governance_service.collect_consent(request)
        
        # Manually set expiration to past
        consent.expires_at = datetime.utcnow() - timedelta(days=1)
        
        has_consent = governance_service.check_consent("user_123", ConsentType.RESEARCH)
        
        assert has_consent is False
        assert consent.status == ConsentStatus.EXPIRED


class TestRetentionPolicies:
    """Test data retention policies"""
    
    def test_default_policies_initialized(self, governance_service):
        """Test that default retention policies are created"""
        skeleton_policy = governance_service.get_retention_policy(DataCategory.SKELETON_DATA)
        
        assert skeleton_policy is not None
        assert skeleton_policy.retention_days == 90
        assert skeleton_policy.auto_delete is True
    
    def test_apply_retention_policy_should_delete(self, governance_service):
        """Test that old data is marked for deletion"""
        old_timestamp = datetime.utcnow() - timedelta(days=100)
        
        should_delete = governance_service.apply_retention_policy(
            DataCategory.SKELETON_DATA,
            old_timestamp
        )
        
        assert should_delete is True
    
    def test_apply_retention_policy_should_keep(self, governance_service):
        """Test that recent data is kept"""
        recent_timestamp = datetime.utcnow() - timedelta(days=30)
        
        should_delete = governance_service.apply_retention_policy(
            DataCategory.SKELETON_DATA,
            recent_timestamp
        )
        
        assert should_delete is False
    
    def test_retention_policy_different_categories(self, governance_service):
        """Test different retention periods for different data categories"""
        # Health metrics: 365 days
        health_policy = governance_service.get_retention_policy(DataCategory.HEALTH_METRICS)
        assert health_policy.retention_days == 365
        
        # Audit logs: 7 years
        audit_policy = governance_service.get_retention_policy(DataCategory.AUDIT_LOGS)
        assert audit_policy.retention_days == 2555


class TestBreachDetection:
    """Test data breach detection and response"""
    
    def test_detect_breach_creates_incident(self, governance_service):
        """Test breach detection creates incident record"""
        incident = governance_service.detect_breach(
            severity=BreachSeverity.HIGH,
            affected_users=["user_123", "user_456"],
            data_categories=[DataCategory.HEALTH_METRICS],
            description="Unauthorized access attempt",
            containment_actions=["Account locked", "Password reset required"]
        )
        
        assert incident.incident_id is not None
        assert incident.severity == BreachSeverity.HIGH
        assert len(incident.affected_users) == 2
        assert incident.notification_sent is False
        assert incident.resolved is False
    
    def test_notify_breach_victims(self, governance_service):
        """Test breach victim notification"""
        incident = governance_service.detect_breach(
            severity=BreachSeverity.MEDIUM,
            affected_users=["user_123"],
            data_categories=[DataCategory.USER_PROFILE],
            description="Data exposure",
            containment_actions=["System patched"]
        )
        
        success = governance_service.notify_breach_victims(incident.incident_id)
        
        assert success is True
        assert incident.notification_sent is True
        assert incident.notification_sent_at is not None
    
    def test_notify_breach_within_72_hours(self, governance_service):
        """Test that breach notification timing is tracked"""
        incident = governance_service.detect_breach(
            severity=BreachSeverity.CRITICAL,
            affected_users=["user_123"],
            data_categories=[DataCategory.HEALTH_METRICS],
            description="Critical breach",
            containment_actions=["Emergency response"]
        )
        
        # Notify immediately
        governance_service.notify_breach_victims(incident.incident_id)
        
        # Check notification was within 72 hours
        hours_elapsed = (incident.notification_sent_at - incident.detected_at).total_seconds() / 3600
        assert hours_elapsed < 72
    
    def test_resolve_breach(self, governance_service):
        """Test breach resolution"""
        incident = governance_service.detect_breach(
            severity=BreachSeverity.LOW,
            affected_users=["user_123"],
            data_categories=[DataCategory.SKELETON_DATA],
            description="Minor incident",
            containment_actions=["Fixed"]
        )
        
        resolved_incident = governance_service.resolve_breach(incident.incident_id)
        
        assert resolved_incident.resolved is True
        assert resolved_incident.resolved_at is not None
    
    def test_get_unresolved_breaches(self, governance_service):
        """Test filtering unresolved breaches"""
        # Create resolved breach
        incident1 = governance_service.detect_breach(
            severity=BreachSeverity.LOW,
            affected_users=["user_1"],
            data_categories=[DataCategory.SKELETON_DATA],
            description="Resolved",
            containment_actions=["Fixed"]
        )
        governance_service.resolve_breach(incident1.incident_id)
        
        # Create unresolved breach
        incident2 = governance_service.detect_breach(
            severity=BreachSeverity.HIGH,
            affected_users=["user_2"],
            data_categories=[DataCategory.HEALTH_METRICS],
            description="Unresolved",
            containment_actions=["In progress"]
        )
        
        unresolved = governance_service.get_breach_incidents(resolved=False)
        
        assert len(unresolved) == 1
        assert unresolved[0].incident_id == incident2.incident_id
