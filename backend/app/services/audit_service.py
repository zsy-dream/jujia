"""
Audit Logging and Security Monitoring Service

Implements comprehensive audit logging for all data access and operations,
end-to-end encryption, and security monitoring.

Requirements: 10.5, 9.5
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
import logging
import hashlib
import json
from cryptography.fernet import Fernet

from app.schemas.governance import AuditLogEntry, AuditAction


logger = logging.getLogger(__name__)


class AuditService:
    """
    Service for comprehensive audit logging and security monitoring.
    
    Implements:
    - Comprehensive audit logs for all data access and operations
    - End-to-end encryption for data transmission and storage
    - Security monitoring and compliance reporting
    """
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        # In-memory storage for demonstration (would use database in production)
        self.audit_logs: Dict[str, AuditLogEntry] = {}
        
        # Initialize encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            # Generate a key for demonstration (in production, use secure key management)
            self.cipher = Fernet(Fernet.generate_key())
    
    def log_action(
        self,
        user_id: str,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        success: bool = True
    ) -> AuditLogEntry:
        """
        Log an auditable action.
        
        Args:
            user_id: User performing the action
            action: Type of action
            resource_type: Type of resource accessed
            resource_id: Identifier of the resource
            details: Additional details about the action
            ip_address: IP address of the request
            success: Whether the action succeeded
            
        Returns:
            AuditLogEntry record
            
        Requirement 10.5: Comprehensive audit logs for all data access and operations
        """
        log_id = f"log_{uuid.uuid4().hex[:12]}"
        
        entry = AuditLogEntry(
            log_id=log_id,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            success=success
        )
        
        self.audit_logs[log_id] = entry
        
        logger.info(f"Audit log created: {log_id}, user {user_id}, action {action}, resource {resource_type}/{resource_id}")
        
        return entry
    
    def get_user_audit_trail(
        self,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditLogEntry]:
        """
        Get audit trail for a specific user.
        
        Args:
            user_id: User identifier
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            List of audit log entries
        """
        logs = [log for log in self.audit_logs.values() if log.user_id == user_id]
        
        if start_time:
            logs = [log for log in logs if log.timestamp >= start_time]
        
        if end_time:
            logs = [log for log in logs if log.timestamp <= end_time]
        
        # Sort by timestamp descending
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return logs
    
    def get_resource_audit_trail(
        self,
        resource_type: str,
        resource_id: str
    ) -> List[AuditLogEntry]:
        """
        Get audit trail for a specific resource.
        
        Args:
            resource_type: Type of resource
            resource_id: Resource identifier
            
        Returns:
            List of audit log entries
        """
        logs = [
            log for log in self.audit_logs.values()
            if log.resource_type == resource_type and log.resource_id == resource_id
        ]
        
        # Sort by timestamp descending
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return logs
    
    def get_failed_actions(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditLogEntry]:
        """
        Get all failed actions for security monitoring.
        
        Args:
            start_time: Optional start time filter
            end_time: Optional end time filter
            
        Returns:
            List of failed audit log entries
        """
        logs = [log for log in self.audit_logs.values() if not log.success]
        
        if start_time:
            logs = [log for log in logs if log.timestamp >= start_time]
        
        if end_time:
            logs = [log for log in logs if log.timestamp <= end_time]
        
        # Sort by timestamp descending
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return logs
    
    def encrypt_data(self, data: str) -> str:
        """
        Encrypt data for secure transmission or storage.
        
        Args:
            data: Plain text data to encrypt
            
        Returns:
            Encrypted data as base64 string
            
        Requirement 9.5: End-to-end encryption for data transmission and storage
        """
        encrypted = self.cipher.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data.
        
        Args:
            encrypted_data: Encrypted data as base64 string
            
        Returns:
            Decrypted plain text data
            
        Requirement 9.5: End-to-end encryption for data transmission and storage
        """
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
    
    def generate_data_hash(self, data: str) -> str:
        """
        Generate a hash of data for integrity verification.
        
        Args:
            data: Data to hash
            
        Returns:
            SHA-256 hash of the data
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_data_integrity(self, data: str, expected_hash: str) -> bool:
        """
        Verify data integrity using hash comparison.
        
        Args:
            data: Data to verify
            expected_hash: Expected hash value
            
        Returns:
            True if data integrity is verified, False otherwise
        """
        actual_hash = self.generate_data_hash(data)
        return actual_hash == expected_hash
    
    def generate_compliance_report(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """
        Generate a compliance report for a time period.
        
        Args:
            start_time: Start of reporting period
            end_time: End of reporting period
            
        Returns:
            Compliance report with statistics and summaries
            
        Requirement 10.5: Compliance reporting
        """
        # Filter logs by time period
        logs = [
            log for log in self.audit_logs.values()
            if start_time <= log.timestamp <= end_time
        ]
        
        # Calculate statistics
        total_actions = len(logs)
        failed_actions = len([log for log in logs if not log.success])
        
        # Count by action type
        action_counts = {}
        for log in logs:
            action_type = log.action.value
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        # Count by user
        user_counts = {}
        for log in logs:
            user_counts[log.user_id] = user_counts.get(log.user_id, 0) + 1
        
        # Identify suspicious activity (multiple failed actions)
        suspicious_users = []
        for user_id in user_counts:
            user_logs = [log for log in logs if log.user_id == user_id]
            failed_count = len([log for log in user_logs if not log.success])
            if failed_count > 5:  # Threshold for suspicious activity
                suspicious_users.append({
                    "user_id": user_id,
                    "failed_actions": failed_count,
                    "total_actions": len(user_logs)
                })
        
        report = {
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "summary": {
                "total_actions": total_actions,
                "successful_actions": total_actions - failed_actions,
                "failed_actions": failed_actions,
                "success_rate": (total_actions - failed_actions) / total_actions if total_actions > 0 else 0
            },
            "action_breakdown": action_counts,
            "top_users": sorted(
                [{"user_id": k, "action_count": v} for k, v in user_counts.items()],
                key=lambda x: x["action_count"],
                reverse=True
            )[:10],
            "security_alerts": {
                "suspicious_users": suspicious_users
            }
        }
        
        return report
    
    def detect_anomalous_access(
        self,
        user_id: str,
        time_window_hours: int = 24
    ) -> bool:
        """
        Detect anomalous access patterns for security monitoring.
        
        Args:
            user_id: User to check
            time_window_hours: Time window for analysis
            
        Returns:
            True if anomalous activity detected, False otherwise
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        recent_logs = [
            log for log in self.audit_logs.values()
            if log.user_id == user_id and log.timestamp >= cutoff_time
        ]
        
        if not recent_logs:
            return False
        
        # Check for anomalies
        failed_count = len([log for log in recent_logs if not log.success])
        
        # Anomaly: More than 10 failed actions in time window
        if failed_count > 10:
            logger.warning(f"Anomalous activity detected for user {user_id}: {failed_count} failed actions")
            return True
        
        # Anomaly: Excessive access (more than 100 actions in time window)
        if len(recent_logs) > 100:
            logger.warning(f"Anomalous activity detected for user {user_id}: {len(recent_logs)} actions")
            return True
        
        return False


from datetime import timedelta
