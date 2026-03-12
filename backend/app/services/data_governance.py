"""
Data Governance Service

Implements comprehensive data consent management, retention policies,
and breach detection protocols.

Requirements: 10.2, 10.3, 10.4
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
import logging

from app.schemas.governance import (
    ConsentRecord, ConsentType, ConsentStatus,
    RetentionPolicy, DataCategory,
    BreachIncident, BreachSeverity,
    ConsentRequest, ConsentRevocation
)


logger = logging.getLogger(__name__)


class DataGovernanceService:
    """
    Service for managing data consent, retention policies, and breach detection.
    
    Implements:
    - Explicit consent collection with clear usage explanations
    - Automatic data retention policies with scheduled deletion
    - Data breach detection and incident response protocols
    """
    
    def __init__(self):
        # In-memory storage for demonstration (would use database in production)
        self.consents: Dict[str, ConsentRecord] = {}
        self.retention_policies: Dict[str, RetentionPolicy] = {}
        self.breach_incidents: Dict[str, BreachIncident] = {}
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default retention policies"""
        default_policies = [
            RetentionPolicy(
                policy_id="policy_skeleton",
                data_category=DataCategory.SKELETON_DATA,
                retention_days=90,
                auto_delete=True,
                description="Skeleton data retained for 90 days for trend analysis"
            ),
            RetentionPolicy(
                policy_id="policy_health",
                data_category=DataCategory.HEALTH_METRICS,
                retention_days=365,
                auto_delete=True,
                description="Health metrics retained for 1 year for long-term analysis"
            ),
            RetentionPolicy(
                policy_id="policy_incidents",
                data_category=DataCategory.INCIDENT_DATA,
                retention_days=730,
                auto_delete=True,
                description="Incident data retained for 2 years for safety analysis"
            ),
            RetentionPolicy(
                policy_id="policy_audit",
                data_category=DataCategory.AUDIT_LOGS,
                retention_days=2555,
                auto_delete=True,
                description="Audit logs retained for 7 years for compliance"
            )
        ]
        
        for policy in default_policies:
            self.retention_policies[policy.policy_id] = policy
    
    def collect_consent(self, request: ConsentRequest) -> ConsentRecord:
        """
        Collect explicit consent from user with clear usage explanations.
        
        Args:
            request: Consent request with purpose and data usage details
            
        Returns:
            ConsentRecord with granted status
            
        Requirement 10.2: Explicit consent collection with clear data usage explanations
        """
        consent_id = f"consent_{uuid.uuid4().hex[:12]}"
        
        expires_at = None
        if request.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
        
        consent = ConsentRecord(
            consent_id=consent_id,
            user_id=request.user_id,
            consent_type=request.consent_type,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.utcnow(),
            expires_at=expires_at,
            purpose_description=request.purpose_description,
            data_usage_details=request.data_usage_details
        )
        
        self.consents[consent_id] = consent
        logger.info(f"Consent granted: {consent_id} for user {request.user_id}, type {request.consent_type}")
        
        return consent
    
    def revoke_consent(self, revocation: ConsentRevocation) -> ConsentRecord:
        """
        Revoke previously granted consent.
        
        Args:
            revocation: Consent revocation request
            
        Returns:
            Updated ConsentRecord with revoked status
            
        Requirement 10.2: User control over consent
        """
        if revocation.consent_id not in self.consents:
            raise ValueError(f"Consent {revocation.consent_id} not found")
        
        consent = self.consents[revocation.consent_id]
        
        if consent.user_id != revocation.user_id:
            raise ValueError("User does not have permission to revoke this consent")
        
        consent.status = ConsentStatus.REVOKED
        consent.revoked_at = datetime.utcnow()
        
        logger.info(f"Consent revoked: {revocation.consent_id} by user {revocation.user_id}")
        
        return consent
    
    def check_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """
        Check if user has valid consent for a specific type.
        
        Args:
            user_id: User identifier
            consent_type: Type of consent to check
            
        Returns:
            True if valid consent exists, False otherwise
        """
        for consent in self.consents.values():
            if (consent.user_id == user_id and 
                consent.consent_type == consent_type and
                consent.status == ConsentStatus.GRANTED):
                
                # Check expiration
                if consent.expires_at and consent.expires_at < datetime.utcnow():
                    consent.status = ConsentStatus.EXPIRED
                    return False
                
                return True
        
        return False
    
    def get_user_consents(self, user_id: str) -> List[ConsentRecord]:
        """Get all consents for a user"""
        return [c for c in self.consents.values() if c.user_id == user_id]
    
    def apply_retention_policy(self, data_category: DataCategory, data_timestamp: datetime) -> bool:
        """
        Check if data should be deleted based on retention policy.
        
        Args:
            data_category: Category of data
            data_timestamp: When the data was created
            
        Returns:
            True if data should be deleted, False otherwise
            
        Requirement 10.3: Automatic data retention with scheduled deletion
        """
        # Find applicable policy
        policy = None
        for p in self.retention_policies.values():
            if p.data_category == data_category:
                policy = p
                break
        
        if not policy:
            logger.warning(f"No retention policy found for {data_category}")
            return False
        
        if not policy.auto_delete:
            return False
        
        # Calculate age
        age_days = (datetime.utcnow() - data_timestamp).days
        
        should_delete = age_days > policy.retention_days
        
        if should_delete:
            logger.info(f"Data deletion triggered: {data_category}, age {age_days} days > {policy.retention_days} days")
        
        return should_delete
    
    def get_retention_policy(self, data_category: DataCategory) -> Optional[RetentionPolicy]:
        """Get retention policy for a data category"""
        for policy in self.retention_policies.values():
            if policy.data_category == data_category:
                return policy
        return None
    
    def detect_breach(
        self,
        severity: BreachSeverity,
        affected_users: List[str],
        data_categories: List[DataCategory],
        description: str,
        containment_actions: List[str]
    ) -> BreachIncident:
        """
        Detect and record a data breach incident.
        
        Args:
            severity: Severity level of the breach
            affected_users: List of affected user IDs
            data_categories: Categories of data affected
            description: Description of the breach
            containment_actions: Actions taken to contain the breach
            
        Returns:
            BreachIncident record
            
        Requirement 10.4: Data breach detection and incident response
        """
        incident_id = f"breach_{uuid.uuid4().hex[:12]}"
        
        incident = BreachIncident(
            incident_id=incident_id,
            detected_at=datetime.utcnow(),
            severity=severity,
            affected_users=affected_users,
            data_categories_affected=data_categories,
            description=description,
            containment_actions=containment_actions,
            notification_sent=False,
            resolved=False
        )
        
        self.breach_incidents[incident_id] = incident
        
        logger.error(f"Data breach detected: {incident_id}, severity {severity}, {len(affected_users)} users affected")
        
        return incident
    
    def notify_breach_victims(self, incident_id: str) -> bool:
        """
        Notify affected users of a data breach.
        
        Args:
            incident_id: Breach incident identifier
            
        Returns:
            True if notifications sent successfully
            
        Requirement 10.4: Notify affected users within 72 hours
        """
        if incident_id not in self.breach_incidents:
            raise ValueError(f"Breach incident {incident_id} not found")
        
        incident = self.breach_incidents[incident_id]
        
        # Check 72-hour window
        hours_since_detection = (datetime.utcnow() - incident.detected_at).total_seconds() / 3600
        
        if hours_since_detection > 72:
            logger.warning(f"Breach notification delayed beyond 72 hours: {incident_id}")
        
        # In production, this would send actual notifications
        # For now, just mark as sent
        incident.notification_sent = True
        incident.notification_sent_at = datetime.utcnow()
        
        logger.info(f"Breach notifications sent for incident {incident_id} to {len(incident.affected_users)} users")
        
        return True
    
    def resolve_breach(self, incident_id: str) -> BreachIncident:
        """Mark a breach incident as resolved"""
        if incident_id not in self.breach_incidents:
            raise ValueError(f"Breach incident {incident_id} not found")
        
        incident = self.breach_incidents[incident_id]
        incident.resolved = True
        incident.resolved_at = datetime.utcnow()
        
        logger.info(f"Breach incident resolved: {incident_id}")
        
        return incident
    
    def get_breach_incidents(self, resolved: Optional[bool] = None) -> List[BreachIncident]:
        """
        Get breach incidents, optionally filtered by resolution status.
        
        Args:
            resolved: If True, return only resolved incidents; if False, only unresolved; if None, return all
            
        Returns:
            List of breach incidents
        """
        incidents = list(self.breach_incidents.values())
        
        if resolved is not None:
            incidents = [i for i in incidents if i.resolved == resolved]
        
        return incidents
