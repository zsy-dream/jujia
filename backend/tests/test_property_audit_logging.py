"""
Property-Based Tests for Comprehensive Audit Logging

Feature: silver-age-actuary, Property 36: Comprehensive Audit Logging

Property 36: Comprehensive Audit Logging
For any data access and system operation, the system should maintain
comprehensive audit logs for compliance and security monitoring.

Validates: Requirements 10.5
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta

from app.services.audit_service import AuditService
from app.schemas.governance import AuditAction


# Strategy for generating valid user IDs
user_ids = st.text(min_size=1, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters='_-'
))

# Strategy for generating audit actions
audit_actions = st.sampled_from(list(AuditAction))

# Strategy for generating resource types
resource_types = st.sampled_from([
    "health_metrics", "user_profile", "skeleton_data",
    "incident_data", "consent_record", "audit_log"
])

# Strategy for generating resource IDs
resource_ids = st.text(min_size=1, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters='_-'
))

# Strategy for generating IP addresses
ip_addresses = st.one_of(
    st.none(),
    st.text(min_size=7, max_size=15, alphabet='0123456789.')
)

# Strategy for generating success status
success_status = st.booleans()

# Strategy for generating details dictionaries
details_dicts = st.dictionaries(
    keys=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
    values=st.one_of(st.text(max_size=50), st.integers(), st.booleans()),
    min_size=0,
    max_size=5
)


class TestProperty36AuditLogging:
    """
    Property 36: Comprehensive Audit Logging
    
    For any data access and system operation, the system should maintain
    comprehensive audit logs for compliance and security monitoring.
    """
    
    @given(
        user_id=user_ids,
        action=audit_actions,
        resource_type=resource_types,
        resource_id=resource_ids,
        details=details_dicts,
        ip_address=ip_addresses,
        success=success_status
    )
    @settings(max_examples=100, deadline=None)
    def test_all_actions_are_logged(
        self,
        user_id,
        action,
        resource_type,
        resource_id,
        details,
        ip_address,
        success
    ):
        """
        Property: All data access and operations are logged.
        
        For any action performed in the system, an audit log entry
        must be created with complete information.
        """
        audit_service = AuditService()
        
        entry = audit_service.log_action(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            success=success
        )
        
        # Property: Log entry is created
        assert entry is not None
        assert entry.log_id is not None
        
        # Property: All information is preserved
        assert entry.user_id == user_id
        assert entry.action == action
        assert entry.resource_type == resource_type
        assert entry.resource_id == resource_id
        assert entry.details == details
        assert entry.ip_address == ip_address
        assert entry.success == success
        
        # Property: Timestamp is set
        assert entry.timestamp is not None
        assert isinstance(entry.timestamp, datetime)
    
    @given(
        user_id=user_ids,
        action=audit_actions,
        resource_type=resource_types,
        resource_id=resource_ids,
        details=details_dicts
    )
    @settings(max_examples=100, deadline=None)
    def test_user_audit_trail_completeness(
        self,
        user_id,
        action,
        resource_type,
        resource_id,
        details
    ):
        """
        Property: User audit trail contains all user actions.
        
        For any user, retrieving their audit trail must return
        all actions they have performed.
        """
        audit_service = AuditService()
        
        # Log an action
        entry = audit_service.log_action(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
        
        # Property: User audit trail contains the action
        trail = audit_service.get_user_audit_trail(user_id)
        
        assert len(trail) >= 1
        assert any(log.log_id == entry.log_id for log in trail)
        assert all(log.user_id == user_id for log in trail)
    
    @given(
        user_id=user_ids,
        action=audit_actions,
        resource_type=resource_types,
        resource_id=resource_ids,
        details=details_dicts
    )
    @settings(max_examples=100, deadline=None)
    def test_resource_audit_trail_completeness(
        self,
        user_id,
        action,
        resource_type,
        resource_id,
        details
    ):
        """
        Property: Resource audit trail contains all resource operations.
        
        For any resource, retrieving its audit trail must return
        all operations performed on it.
        """
        audit_service = AuditService()
        
        # Log an action on the resource
        entry = audit_service.log_action(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
        
        # Property: Resource audit trail contains the operation
        trail = audit_service.get_resource_audit_trail(resource_type, resource_id)
        
        assert len(trail) >= 1
        assert any(log.log_id == entry.log_id for log in trail)
        assert all(log.resource_type == resource_type for log in trail)
        assert all(log.resource_id == resource_id for log in trail)
    
    @given(
        user_id=user_ids,
        action=audit_actions,
        resource_type=resource_types,
        resource_id=resource_ids,
        details=details_dicts
    )
    @settings(max_examples=100, deadline=None)
    def test_failed_actions_are_tracked(
        self,
        user_id,
        action,
        resource_type,
        resource_id,
        details
    ):
        """
        Property: Failed actions are tracked for security monitoring.
        
        For any failed action, it must be included in the failed
        actions log for security analysis.
        """
        audit_service = AuditService()
        
        # Log a failed action
        entry = audit_service.log_action(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            success=False
        )
        
        # Property: Failed action is tracked
        failed_actions = audit_service.get_failed_actions()
        
        assert len(failed_actions) >= 1
        assert any(log.log_id == entry.log_id for log in failed_actions)
        assert all(not log.success for log in failed_actions)
    
    @given(
        data=st.text(min_size=1, max_size=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_encryption_preserves_data_integrity(self, data):
        """
        Property: Encryption and decryption preserve data integrity.
        
        For any data, encrypting and then decrypting it must
        return the original data unchanged.
        """
        audit_service = AuditService()
        
        encrypted = audit_service.encrypt_data(data)
        decrypted = audit_service.decrypt_data(encrypted)
        
        # Property: Data integrity is preserved
        assert decrypted == data
        
        # Property: Encrypted data is different from original
        assert encrypted != data
    
    @given(
        data=st.text(min_size=1, max_size=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_data_hash_consistency(self, data):
        """
        Property: Data hashing is consistent and deterministic.
        
        For any data, generating its hash multiple times must
        produce the same result.
        """
        audit_service = AuditService()
        
        hash1 = audit_service.generate_data_hash(data)
        hash2 = audit_service.generate_data_hash(data)
        
        # Property: Hash is consistent
        assert hash1 == hash2
        
        # Property: Hash is a valid hex string
        assert len(hash1) == 64  # SHA-256 produces 64 hex characters
        assert all(c in '0123456789abcdef' for c in hash1)
    
    @given(
        data1=st.text(min_size=1, max_size=500),
        data2=st.text(min_size=1, max_size=500)
    )
    @settings(max_examples=100, deadline=None)
    def test_different_data_produces_different_hashes(self, data1, data2):
        """
        Property: Different data produces different hashes.
        
        For any two different pieces of data, their hashes
        should be different (collision resistance).
        """
        assume(data1 != data2)  # Ensure different data
        
        audit_service = AuditService()
        
        hash1 = audit_service.generate_data_hash(data1)
        hash2 = audit_service.generate_data_hash(data2)
        
        # Property: Different data produces different hashes
        assert hash1 != hash2
    
    @given(
        data=st.text(min_size=1, max_size=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_data_integrity_verification(self, data):
        """
        Property: Data integrity verification detects tampering.
        
        For any data, verifying its integrity with the correct hash
        succeeds, and with an incorrect hash fails.
        """
        audit_service = AuditService()
        
        correct_hash = audit_service.generate_data_hash(data)
        
        # Property: Verification succeeds with correct hash
        assert audit_service.verify_data_integrity(data, correct_hash) is True
        
        # Property: Verification fails with incorrect hash
        wrong_hash = "0" * 64  # Invalid hash
        assert audit_service.verify_data_integrity(data, wrong_hash) is False
    
    @given(
        user_id1=user_ids,
        user_id2=user_ids,
        action=audit_actions,
        resource_type=resource_types,
        resource_id=resource_ids,
        details=details_dicts
    )
    @settings(max_examples=100, deadline=None)
    def test_audit_trail_isolation_between_users(
        self,
        user_id1,
        user_id2,
        action,
        resource_type,
        resource_id,
        details
    ):
        """
        Property: Audit trails are isolated between users.
        
        For any two different users, one user's audit trail
        should not contain another user's actions.
        """
        assume(user_id1 != user_id2)  # Ensure different users
        
        audit_service = AuditService()
        
        # Log action for user1
        audit_service.log_action(
            user_id=user_id1,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
        
        # Property: User2's trail does not contain user1's actions
        user2_trail = audit_service.get_user_audit_trail(user_id2)
        
        assert all(log.user_id != user_id1 for log in user2_trail)
    
    @given(
        user_id=user_ids,
        num_actions=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=50, deadline=None)
    def test_compliance_report_accuracy(self, user_id, num_actions):
        """
        Property: Compliance reports accurately reflect logged actions.
        
        For any set of logged actions, the compliance report must
        accurately count and categorize them.
        """
        audit_service = AuditService()
        
        start_time = datetime.utcnow() - timedelta(hours=1)
        
        # Log multiple actions
        for i in range(num_actions):
            audit_service.log_action(
                user_id=user_id,
                action=AuditAction.DATA_ACCESS,
                resource_type="health_metrics",
                resource_id=f"metric_{i}",
                details={"index": i},
                success=True
            )
        
        end_time = datetime.utcnow() + timedelta(hours=1)
        
        # Generate compliance report
        report = audit_service.generate_compliance_report(start_time, end_time)
        
        # Property: Report accurately counts actions
        assert report["summary"]["total_actions"] >= num_actions
        assert report["summary"]["successful_actions"] >= num_actions
        
        # Property: Report structure is complete
        assert "summary" in report
        assert "action_breakdown" in report
        assert "top_users" in report
        assert "security_alerts" in report
    
    @given(
        user_id=user_ids,
        num_failed=st.integers(min_value=11, max_value=20)
    )
    @settings(max_examples=50, deadline=None)
    def test_anomalous_access_detection(self, user_id, num_failed):
        """
        Property: Anomalous access patterns are detected.
        
        For any user with excessive failed actions, the system
        must detect this as anomalous activity.
        """
        audit_service = AuditService()
        
        # Create many failed actions (threshold is 10)
        for i in range(num_failed):
            audit_service.log_action(
                user_id=user_id,
                action=AuditAction.DATA_ACCESS,
                resource_type="health_metrics",
                resource_id=f"metric_{i}",
                details={"error": "Permission denied"},
                success=False
            )
        
        # Property: Anomalous activity is detected
        is_anomalous = audit_service.detect_anomalous_access(user_id, time_window_hours=24)
        
        assert is_anomalous is True
