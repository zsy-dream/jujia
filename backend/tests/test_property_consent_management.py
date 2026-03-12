"""
Property-Based Tests for Data Consent Management

Feature: silver-age-actuary, Property 33: Data Consent Management

Property 33: Data Consent Management
For any user data collection, the system should obtain explicit consent
and provide clear, comprehensive data usage explanations.

Validates: Requirements 10.2
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta

from app.services.data_governance import DataGovernanceService
from app.schemas.governance import (
    ConsentRequest, ConsentRevocation, ConsentType, ConsentStatus
)


# Strategy for generating valid user IDs
user_ids = st.text(min_size=1, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters='_-'
))

# Strategy for generating consent types
consent_types = st.sampled_from(list(ConsentType))

# Strategy for generating purpose descriptions
purpose_descriptions = st.text(min_size=10, max_size=200)

# Strategy for generating data usage details
data_usage_details = st.text(min_size=10, max_size=500)

# Strategy for generating expiration days (0 to 365)
expiration_days = st.one_of(st.none(), st.integers(min_value=1, max_value=365))


class TestProperty33ConsentManagement:
    """
    Property 33: Data Consent Management
    
    For any user data collection, the system should obtain explicit consent
    and provide clear, comprehensive data usage explanations.
    """
    
    @given(
        user_id=user_ids,
        consent_type=consent_types,
        purpose_description=purpose_descriptions,
        data_usage_details=data_usage_details,
        expires_in_days=expiration_days
    )
    @settings(max_examples=100, deadline=None)
    def test_consent_collection_always_creates_valid_record(
        self,
        user_id,
        consent_type,
        purpose_description,
        data_usage_details,
        expires_in_days
    ):
        """
        Property: Consent collection always creates a valid record with
        explicit consent status and clear usage explanations.
        
        For any valid consent request, the system must:
        1. Create a consent record with GRANTED status
        2. Store the user ID correctly
        3. Store the consent type correctly
        4. Include the purpose description
        5. Include the data usage details
        6. Set granted_at timestamp
        7. Handle expiration if specified
        """
        governance_service = DataGovernanceService()
        
        request = ConsentRequest(
            user_id=user_id,
            consent_type=consent_type,
            purpose_description=purpose_description,
            data_usage_details=data_usage_details,
            expires_in_days=expires_in_days
        )
        
        consent = governance_service.collect_consent(request)
        
        # Property: Consent is always granted initially
        assert consent.status == ConsentStatus.GRANTED
        
        # Property: User ID is preserved
        assert consent.user_id == user_id
        
        # Property: Consent type is preserved
        assert consent.consent_type == consent_type
        
        # Property: Purpose description is stored (clear explanation)
        assert consent.purpose_description == purpose_description
        assert len(consent.purpose_description) >= 10  # Meaningful description
        
        # Property: Data usage details are stored (comprehensive explanation)
        assert consent.data_usage_details == data_usage_details
        assert len(consent.data_usage_details) >= 10  # Meaningful details
        
        # Property: Granted timestamp is set
        assert consent.granted_at is not None
        assert isinstance(consent.granted_at, datetime)
        
        # Property: Expiration is handled correctly
        if expires_in_days:
            assert consent.expires_at is not None
            # Expiration should be in the future
            assert consent.expires_at > consent.granted_at
        else:
            # No expiration if not specified
            assert consent.expires_at is None
        
        # Property: Consent ID is generated
        assert consent.consent_id is not None
        assert len(consent.consent_id) > 0
    
    @given(
        user_id=user_ids,
        consent_type=consent_types,
        purpose_description=purpose_descriptions,
        data_usage_details=data_usage_details
    )
    @settings(max_examples=100, deadline=None)
    def test_consent_check_reflects_granted_status(
        self,
        user_id,
        consent_type,
        purpose_description,
        data_usage_details
    ):
        """
        Property: After granting consent, check_consent returns True
        for that user and consent type.
        
        For any granted consent, the system must correctly identify
        that the user has valid consent.
        """
        governance_service = DataGovernanceService()
        
        request = ConsentRequest(
            user_id=user_id,
            consent_type=consent_type,
            purpose_description=purpose_description,
            data_usage_details=data_usage_details
        )
        
        governance_service.collect_consent(request)
        
        # Property: Consent check returns True after granting
        has_consent = governance_service.check_consent(user_id, consent_type)
        assert has_consent is True
    
    @given(
        user_id=user_ids,
        consent_type=consent_types,
        purpose_description=purpose_descriptions,
        data_usage_details=data_usage_details
    )
    @settings(max_examples=100, deadline=None)
    def test_revoked_consent_cannot_be_used(
        self,
        user_id,
        consent_type,
        purpose_description,
        data_usage_details
    ):
        """
        Property: After revoking consent, check_consent returns False
        for that user and consent type.
        
        For any revoked consent, the system must correctly identify
        that the user no longer has valid consent.
        """
        governance_service = DataGovernanceService()
        
        # Grant consent
        request = ConsentRequest(
            user_id=user_id,
            consent_type=consent_type,
            purpose_description=purpose_description,
            data_usage_details=data_usage_details
        )
        consent = governance_service.collect_consent(request)
        
        # Revoke consent
        revocation = ConsentRevocation(
            consent_id=consent.consent_id,
            user_id=user_id
        )
        governance_service.revoke_consent(revocation)
        
        # Property: Consent check returns False after revocation
        has_consent = governance_service.check_consent(user_id, consent_type)
        assert has_consent is False
    
    @given(
        user_id=user_ids,
        consent_type=consent_types,
        purpose_description=purpose_descriptions,
        data_usage_details=data_usage_details
    )
    @settings(max_examples=100, deadline=None)
    def test_user_can_retrieve_all_consents(
        self,
        user_id,
        consent_type,
        purpose_description,
        data_usage_details
    ):
        """
        Property: Users can always retrieve all their consent records.
        
        For any user with granted consents, the system must return
        all consent records associated with that user.
        """
        governance_service = DataGovernanceService()
        
        # Grant consent
        request = ConsentRequest(
            user_id=user_id,
            consent_type=consent_type,
            purpose_description=purpose_description,
            data_usage_details=data_usage_details
        )
        consent = governance_service.collect_consent(request)
        
        # Property: User can retrieve their consents
        user_consents = governance_service.get_user_consents(user_id)
        
        assert len(user_consents) >= 1
        assert any(c.consent_id == consent.consent_id for c in user_consents)
        assert all(c.user_id == user_id for c in user_consents)
    
    @given(
        user_id1=user_ids,
        user_id2=user_ids,
        consent_type=consent_types,
        purpose_description=purpose_descriptions,
        data_usage_details=data_usage_details
    )
    @settings(max_examples=100, deadline=None)
    def test_consent_isolation_between_users(
        self,
        user_id1,
        user_id2,
        consent_type,
        purpose_description,
        data_usage_details
    ):
        """
        Property: Consents are isolated between users.
        
        For any two different users, granting consent to one user
        should not affect the consent status of another user.
        """
        assume(user_id1 != user_id2)  # Ensure different users
        
        governance_service = DataGovernanceService()
        
        # Grant consent to user1
        request = ConsentRequest(
            user_id=user_id1,
            consent_type=consent_type,
            purpose_description=purpose_description,
            data_usage_details=data_usage_details
        )
        governance_service.collect_consent(request)
        
        # Property: User1 has consent
        assert governance_service.check_consent(user_id1, consent_type) is True
        
        # Property: User2 does not have consent (isolation)
        assert governance_service.check_consent(user_id2, consent_type) is False
    
    @given(
        user_id=user_ids,
        consent_type1=consent_types,
        consent_type2=consent_types,
        purpose_description=purpose_descriptions,
        data_usage_details=data_usage_details
    )
    @settings(max_examples=100, deadline=None)
    def test_consent_type_specificity(
        self,
        user_id,
        consent_type1,
        consent_type2,
        purpose_description,
        data_usage_details
    ):
        """
        Property: Consent is specific to consent type.
        
        For any user, granting consent for one type should not
        grant consent for a different type.
        """
        assume(consent_type1 != consent_type2)  # Ensure different types
        
        governance_service = DataGovernanceService()
        
        # Grant consent for type1
        request = ConsentRequest(
            user_id=user_id,
            consent_type=consent_type1,
            purpose_description=purpose_description,
            data_usage_details=data_usage_details
        )
        governance_service.collect_consent(request)
        
        # Property: User has consent for type1
        assert governance_service.check_consent(user_id, consent_type1) is True
        
        # Property: User does not have consent for type2 (specificity)
        assert governance_service.check_consent(user_id, consent_type2) is False
    
    @given(
        user_id=user_ids,
        consent_type=consent_types,
        purpose_description=purpose_descriptions,
        data_usage_details=data_usage_details
    )
    @settings(max_examples=100, deadline=None)
    def test_revocation_updates_status_and_timestamp(
        self,
        user_id,
        consent_type,
        purpose_description,
        data_usage_details
    ):
        """
        Property: Revoking consent updates status and sets revocation timestamp.
        
        For any revoked consent, the system must update the status to REVOKED
        and record when the revocation occurred.
        """
        governance_service = DataGovernanceService()
        
        # Grant consent
        request = ConsentRequest(
            user_id=user_id,
            consent_type=consent_type,
            purpose_description=purpose_description,
            data_usage_details=data_usage_details
        )
        consent = governance_service.collect_consent(request)
        
        # Revoke consent
        revocation = ConsentRevocation(
            consent_id=consent.consent_id,
            user_id=user_id
        )
        revoked_consent = governance_service.revoke_consent(revocation)
        
        # Property: Status is updated to REVOKED
        assert revoked_consent.status == ConsentStatus.REVOKED
        
        # Property: Revocation timestamp is set
        assert revoked_consent.revoked_at is not None
        assert isinstance(revoked_consent.revoked_at, datetime)
        
        # Property: Revocation timestamp is after grant timestamp
        assert revoked_consent.revoked_at >= revoked_consent.granted_at
    
    @given(
        user_id=user_ids,
        consent_type=consent_types,
        purpose_description=purpose_descriptions,
        data_usage_details=data_usage_details
    )
    @settings(max_examples=50, deadline=None)
    def test_expired_consent_is_not_valid(
        self,
        user_id,
        consent_type,
        purpose_description,
        data_usage_details
    ):
        """
        Property: Expired consent is not considered valid.
        
        For any consent with an expiration date in the past,
        check_consent should return False.
        """
        governance_service = DataGovernanceService()
        
        # Grant consent with expiration
        request = ConsentRequest(
            user_id=user_id,
            consent_type=consent_type,
            purpose_description=purpose_description,
            data_usage_details=data_usage_details,
            expires_in_days=1
        )
        consent = governance_service.collect_consent(request)
        
        # Manually expire the consent (simulate time passing)
        consent.expires_at = datetime.utcnow() - timedelta(days=1)
        
        # Property: Expired consent is not valid
        has_consent = governance_service.check_consent(user_id, consent_type)
        assert has_consent is False
        
        # Property: Status is updated to EXPIRED
        assert consent.status == ConsentStatus.EXPIRED
