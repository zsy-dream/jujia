"""
Unit tests for Audit Service

Tests audit logging, encryption, and security monitoring.
"""

import pytest
from datetime import datetime, timedelta

from app.services.audit_service import AuditService
from app.schemas.governance import AuditAction


@pytest.fixture
def audit_service():
    """Create a fresh audit service for each test"""
    return AuditService()


class TestAuditLogging:
    """Test audit log creation and retrieval"""
    
    def test_log_action_creates_entry(self, audit_service):
        """Test that logging an action creates an audit entry"""
        entry = audit_service.log_action(
            user_id="user_123",
            action=AuditAction.DATA_ACCESS,
            resource_type="health_metrics",
            resource_id="metric_456",
            details={"operation": "read", "fields": ["frailty_score"]},
            ip_address="192.168.1.1",
            success=True
        )
        
        assert entry.log_id is not None
        assert entry.user_id == "user_123"
        assert entry.action == AuditAction.DATA_ACCESS
        assert entry.resource_type == "health_metrics"
        assert entry.success is True
    
    def test_log_failed_action(self, audit_service):
        """Test logging failed actions"""
        entry = audit_service.log_action(
            user_id="user_123",
            action=AuditAction.DATA_MODIFICATION,
            resource_type="user_profile",
            resource_id="profile_789",
            details={"error": "Permission denied"},
            success=False
        )
        
        assert entry.success is False
        assert "error" in entry.details
    
    def test_get_user_audit_trail(self, audit_service):
        """Test retrieving audit trail for a user"""
        # Create multiple log entries
        audit_service.log_action(
            user_id="user_123",
            action=AuditAction.DATA_ACCESS,
            resource_type="health_metrics",
            resource_id="metric_1",
            details={}
        )
        audit_service.log_action(
            user_id="user_123",
            action=AuditAction.DATA_MODIFICATION,
            resource_type="user_profile",
            resource_id="profile_1",
            details={}
        )
        audit_service.log_action(
            user_id="user_456",
            action=AuditAction.DATA_ACCESS,
            resource_type="health_metrics",
            resource_id="metric_2",
            details={}
        )
        
        trail = audit_service.get_user_audit_trail("user_123")
        
        assert len(trail) == 2
        assert all(log.user_id == "user_123" for log in trail)
    
    def test_get_user_audit_trail_with_time_filter(self, audit_service):
        """Test filtering audit trail by time"""
        # Create log entry
        entry = audit_service.log_action(
            user_id="user_123",
            action=AuditAction.DATA_ACCESS,
            resource_type="health_metrics",
            resource_id="metric_1",
            details={}
        )
        
        # Filter with time range that includes the entry
        start_time = datetime.utcnow() - timedelta(hours=1)
        end_time = datetime.utcnow() + timedelta(hours=1)
        
        trail = audit_service.get_user_audit_trail("user_123", start_time, end_time)
        
        assert len(trail) == 1
        
        # Filter with time range that excludes the entry
        old_start = datetime.utcnow() - timedelta(days=2)
        old_end = datetime.utcnow() - timedelta(days=1)
        
        trail = audit_service.get_user_audit_trail("user_123", old_start, old_end)
        
        assert len(trail) == 0
    
    def test_get_resource_audit_trail(self, audit_service):
        """Test retrieving audit trail for a resource"""
        # Create logs for same resource
        audit_service.log_action(
            user_id="user_123",
            action=AuditAction.DATA_ACCESS,
            resource_type="health_metrics",
            resource_id="metric_1",
            details={"operation": "read"}
        )
        audit_service.log_action(
            user_id="user_456",
            action=AuditAction.DATA_MODIFICATION,
            resource_type="health_metrics",
            resource_id="metric_1",
            details={"operation": "update"}
        )
        
        trail = audit_service.get_resource_audit_trail("health_metrics", "metric_1")
        
        assert len(trail) == 2
        assert all(log.resource_id == "metric_1" for log in trail)
    
    def test_get_failed_actions(self, audit_service):
        """Test retrieving failed actions for security monitoring"""
        # Create successful and failed actions
        audit_service.log_action(
            user_id="user_123",
            action=AuditAction.DATA_ACCESS,
            resource_type="health_metrics",
            resource_id="metric_1",
            details={},
            success=True
        )
        audit_service.log_action(
            user_id="user_123",
            action=AuditAction.DATA_MODIFICATION,
            resource_type="user_profile",
            resource_id="profile_1",
            details={"error": "Permission denied"},
            success=False
        )
        audit_service.log_action(
            user_id="user_456",
            action=AuditAction.DATA_DELETION,
            resource_type="health_metrics",
            resource_id="metric_2",
            details={"error": "Not found"},
            success=False
        )
        
        failed = audit_service.get_failed_actions()
        
        assert len(failed) == 2
        assert all(not log.success for log in failed)


class TestEncryption:
    """Test data encryption and decryption"""
    
    def test_encrypt_decrypt_data(self, audit_service):
        """Test that data can be encrypted and decrypted"""
        original_data = "Sensitive health information"
        
        encrypted = audit_service.encrypt_data(original_data)
        decrypted = audit_service.decrypt_data(encrypted)
        
        assert encrypted != original_data
        assert decrypted == original_data
    
    def test_encrypted_data_is_different(self, audit_service):
        """Test that encrypted data is not readable"""
        original_data = "Secret data"
        
        encrypted = audit_service.encrypt_data(original_data)
        
        assert encrypted != original_data
        assert "Secret" not in encrypted
    
    def test_generate_data_hash(self, audit_service):
        """Test data hash generation"""
        data = "Test data"
        
        hash1 = audit_service.generate_data_hash(data)
        hash2 = audit_service.generate_data_hash(data)
        
        # Same data should produce same hash
        assert hash1 == hash2
        
        # Different data should produce different hash
        hash3 = audit_service.generate_data_hash("Different data")
        assert hash1 != hash3
    
    def test_verify_data_integrity(self, audit_service):
        """Test data integrity verification"""
        data = "Important data"
        expected_hash = audit_service.generate_data_hash(data)
        
        # Verify with correct hash
        is_valid = audit_service.verify_data_integrity(data, expected_hash)
        assert is_valid is True
        
        # Verify with incorrect hash
        wrong_hash = audit_service.generate_data_hash("Wrong data")
        is_valid = audit_service.verify_data_integrity(data, wrong_hash)
        assert is_valid is False


class TestComplianceReporting:
    """Test compliance report generation"""
    
    def test_generate_compliance_report(self, audit_service):
        """Test compliance report generation"""
        start_time = datetime.utcnow() - timedelta(hours=1)
        
        # Create various log entries
        audit_service.log_action(
            user_id="user_123",
            action=AuditAction.DATA_ACCESS,
            resource_type="health_metrics",
            resource_id="metric_1",
            details={},
            success=True
        )
        audit_service.log_action(
            user_id="user_123",
            action=AuditAction.DATA_MODIFICATION,
            resource_type="user_profile",
            resource_id="profile_1",
            details={},
            success=False
        )
        audit_service.log_action(
            user_id="user_456",
            action=AuditAction.DATA_ACCESS,
            resource_type="health_metrics",
            resource_id="metric_2",
            details={},
            success=True
        )
        
        end_time = datetime.utcnow() + timedelta(hours=1)
        
        report = audit_service.generate_compliance_report(start_time, end_time)
        
        assert "summary" in report
        assert report["summary"]["total_actions"] == 3
        assert report["summary"]["successful_actions"] == 2
        assert report["summary"]["failed_actions"] == 1
        assert "action_breakdown" in report
        assert "top_users" in report
    
    def test_compliance_report_action_breakdown(self, audit_service):
        """Test action breakdown in compliance report"""
        start_time = datetime.utcnow() - timedelta(hours=1)
        
        # Create multiple access actions
        for i in range(3):
            audit_service.log_action(
                user_id=f"user_{i}",
                action=AuditAction.DATA_ACCESS,
                resource_type="health_metrics",
                resource_id=f"metric_{i}",
                details={}
            )
        
        # Create one modification action
        audit_service.log_action(
            user_id="user_1",
            action=AuditAction.DATA_MODIFICATION,
            resource_type="user_profile",
            resource_id="profile_1",
            details={}
        )
        
        end_time = datetime.utcnow() + timedelta(hours=1)
        
        report = audit_service.generate_compliance_report(start_time, end_time)
        
        assert report["action_breakdown"]["data_access"] == 3
        assert report["action_breakdown"]["data_modification"] == 1


class TestSecurityMonitoring:
    """Test security monitoring and anomaly detection"""
    
    def test_detect_anomalous_access_excessive_failures(self, audit_service):
        """Test detection of excessive failed actions"""
        # Create many failed actions
        for i in range(15):
            audit_service.log_action(
                user_id="user_123",
                action=AuditAction.DATA_ACCESS,
                resource_type="health_metrics",
                resource_id=f"metric_{i}",
                details={"error": "Permission denied"},
                success=False
            )
        
        is_anomalous = audit_service.detect_anomalous_access("user_123", time_window_hours=24)
        
        assert is_anomalous is True
    
    def test_detect_anomalous_access_excessive_volume(self, audit_service):
        """Test detection of excessive access volume"""
        # Create many successful actions
        for i in range(150):
            audit_service.log_action(
                user_id="user_123",
                action=AuditAction.DATA_ACCESS,
                resource_type="health_metrics",
                resource_id=f"metric_{i}",
                details={},
                success=True
            )
        
        is_anomalous = audit_service.detect_anomalous_access("user_123", time_window_hours=24)
        
        assert is_anomalous is True
    
    def test_normal_access_not_anomalous(self, audit_service):
        """Test that normal access patterns are not flagged"""
        # Create normal amount of actions
        for i in range(5):
            audit_service.log_action(
                user_id="user_123",
                action=AuditAction.DATA_ACCESS,
                resource_type="health_metrics",
                resource_id=f"metric_{i}",
                details={},
                success=True
            )
        
        is_anomalous = audit_service.detect_anomalous_access("user_123", time_window_hours=24)
        
        assert is_anomalous is False
