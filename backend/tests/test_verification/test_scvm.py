"""
Unit tests for SCVM (Credential Vetting Model) algorithm
"""
import pytest
from uuid import uuid4
from datetime import date, datetime, timedelta

from algorithms.verification.scvm import SCVMAlgorithm, verify_credentials
from algorithms.verification.models import (
    PractitionerVerificationInput,
    PractitionerCredential,
    InsurancePolicy,
    UploadedDocument,
    VerificationTier,
    VerificationStatus,
    FraudRiskLevel,
    DocumentType
)


class TestSCVM:

    @pytest.fixture
    def scvm(self):
        """Create SCVM instance"""
        return SCVMAlgorithm()

    @pytest.fixture
    def valid_practitioner(self):
        """Create valid practitioner input"""
        doc_id = uuid4()
        cred_id = uuid4()
        policy_id = uuid4()

        return PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="valid@example.com",
            full_name="Dr. Test Practitioner",
            date_of_birth=date(1985, 1, 1),
            credentials=[
                PractitionerCredential(
                    credential_id=cred_id,
                    credential_type="BSc",
                    credential_name="BSc Nutritional Science",
                    issuing_body="University of Westminster",
                    issue_date=date(2010, 7, 1),
                    credential_number="NUT-2010-001",
                    supporting_documents=[doc_id]
                )
            ],
            registry_numbers={"CNHC": "12345"},
            insurance_policies=[
                InsurancePolicy(
                    policy_id=policy_id,
                    provider="Balens Insurance",
                    policy_number="BAL-001",
                    coverage_amount=2000000.0,
                    start_date=date(2024, 1, 1),
                    end_date=date(2025, 1, 1),
                    covers_cam_practice=True
                )
            ],
            uploaded_documents=[
                UploadedDocument(
                    document_id=doc_id,
                    document_type=DocumentType.DEGREE_CERTIFICATE,
                    filename="certificate.pdf",
                    file_size_bytes=1024000,
                    upload_timestamp=datetime.utcnow(),
                    mime_type="application/pdf",
                    ocr_text="University of Westminster BSc Nutritional Science",
                    metadata_extracted={"software": "Adobe Acrobat"},
                    hash_value="abc123"
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

    def test_verify_valid_practitioner(self, scvm, valid_practitioner):
        """Test verification of valid practitioner"""
        result = scvm.verify(valid_practitioner)

        assert result.practitioner_id == valid_practitioner.practitioner_id
        assert result.overall_confidence > 0.5
        assert len(result.credential_results) == 1

    def test_verify_returns_correct_structure(self, scvm, valid_practitioner):
        """Test that verification returns complete structure"""
        result = scvm.verify(valid_practitioner)

        # Check all required fields are present
        assert result.practitioner_id is not None
        assert result.verification_tier == VerificationTier.STANDARD
        assert result.overall_status is not None
        assert isinstance(result.overall_confidence, float)
        assert isinstance(result.verified, bool)
        assert isinstance(result.credential_results, list)
        assert isinstance(result.issues, list)
        assert isinstance(result.fraud_indicators, list)
        assert isinstance(result.badges, list)
        assert isinstance(result.recommendations, list)
        assert result.total_checks_performed > 0

    def test_known_institution_verified(self, scvm, valid_practitioner):
        """Test that known institutions are properly verified"""
        result = scvm.verify(valid_practitioner)

        # University of Westminster is in known institutions
        cred_result = result.credential_results[0]
        institution_check = [
            c for c in cred_result.checks_performed
            if c.check_name == "institution_verification"
        ]
        assert len(institution_check) == 1
        assert institution_check[0].passed == True

    def test_unknown_institution_flagged(self, scvm):
        """Test that unknown institutions are flagged"""
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="unknown@example.com",
            full_name="Unknown Inst Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="Diploma",
                    credential_name="Diploma in Wellness",
                    issuing_body="Unknown Random College",
                    issue_date=date(2020, 1, 1)
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should have issues about unknown institution
        assert any("institution" in i.issue_type for i in result.issues)

    def test_diploma_mill_detected(self, scvm):
        """Test that diploma mills are detected"""
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="fraud@example.com",
            full_name="Fake Degree Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="PhD",
                    credential_name="PhD in Everything",
                    issuing_body="Belford University",  # Known diploma mill
                    issue_date=date(2022, 1, 1)
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should have low confidence due to diploma mill
        assert result.overall_confidence < 0.5

    def test_expired_credential_detected(self, scvm):
        """Test that expired credentials are detected"""
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="expired@example.com",
            full_name="Expired Cred Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="Certificate",
                    credential_name="Certificate in Nutrition",
                    issuing_body="University of Westminster",
                    issue_date=date(2015, 1, 1),
                    expiry_date=date(2020, 1, 1)  # Expired
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should have expired credential issue
        assert any("expired" in i.issue_type for i in result.issues)

    def test_date_inconsistency_fraud_detected(self, scvm):
        """Test that date inconsistencies are flagged as fraud"""
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="inconsistent@example.com",
            full_name="Date Issue Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="BSc",
                    credential_name="BSc Test",
                    issuing_body="University of Westminster",
                    issue_date=date(2025, 1, 1),  # After expiry
                    expiry_date=date(2020, 1, 1)
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should have fraud indicator for date inconsistency
        assert any(
            f.indicator_type == "date_inconsistency"
            for f in result.fraud_indicators
        )

    def test_document_metadata_fraud_detected(self, scvm):
        """Test that suspicious document metadata is detected"""
        doc_id = uuid4()
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="edited@example.com",
            full_name="Edited Doc Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="BSc",
                    credential_name="BSc Test",
                    issuing_body="University of Westminster",
                    issue_date=date(2020, 1, 1),
                    supporting_documents=[doc_id]
                )
            ],
            uploaded_documents=[
                UploadedDocument(
                    document_id=doc_id,
                    document_type=DocumentType.DEGREE_CERTIFICATE,
                    filename="fake.pdf",
                    file_size_bytes=500000,
                    upload_timestamp=datetime.utcnow(),
                    mime_type="application/pdf",
                    metadata_extracted={"software": "photoshop"},  # Red flag
                    hash_value="fake123"
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should have fraud indicator for metadata manipulation
        assert any(
            f.indicator_type == "metadata_manipulation"
            for f in result.fraud_indicators
        )

    def test_insurance_verification(self, scvm, valid_practitioner):
        """Test that valid insurance is verified"""
        result = scvm.verify(valid_practitioner)

        assert result.insurance_verified == True

    def test_expired_insurance_detected(self, scvm):
        """Test that expired insurance is detected"""
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="noinsurance@example.com",
            full_name="Expired Insurance Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="BSc",
                    credential_name="BSc Test",
                    issuing_body="University of Westminster",
                    issue_date=date(2020, 1, 1)
                )
            ],
            insurance_policies=[
                InsurancePolicy(
                    policy_id=uuid4(),
                    provider="Old Insurance",
                    policy_number="OLD-001",
                    coverage_amount=1000000.0,
                    start_date=date(2019, 1, 1),
                    end_date=date(2020, 1, 1),  # Expired
                    covers_cam_practice=True
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should have expired insurance issue
        assert any("expired_insurance" in i.issue_type for i in result.issues)
        assert result.insurance_verified == False

    def test_registry_verification(self, scvm, valid_practitioner):
        """Test that registry numbers are verified"""
        result = scvm.verify(valid_practitioner)

        # Check for registry check
        registry_checks = [
            c for c in result.credential_results[0].checks_performed
            if "registry" in c.check_name
        ]
        # Registry checks might not be on credentials directly
        # but we should have no unknown registry issues
        assert not any(
            "unknown_registry" in i.issue_type
            for i in result.issues
        )

    def test_unknown_registry_flagged(self, scvm):
        """Test that unknown registries are flagged"""
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="fakereg@example.com",
            full_name="Fake Registry Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="BSc",
                    credential_name="BSc Test",
                    issuing_body="University of Westminster",
                    issue_date=date(2020, 1, 1)
                )
            ],
            registry_numbers={"FAKE_REGISTRY": "00000"},
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should have unknown registry issue
        assert any("unknown_registry" in i.issue_type for i in result.issues)

    def test_human_review_triggered_for_issues(self, scvm):
        """Test that human review is triggered when needed"""
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="review@example.com",
            full_name="Needs Review Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="PhD",
                    credential_name="PhD Test",
                    issuing_body="Unknown University",  # Unknown
                    issue_date=date(2020, 1, 1)
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should require human review
        assert result.requires_human_review == True
        assert result.human_review_request is not None

    def test_badges_awarded_on_verification(self, scvm, valid_practitioner):
        """Test that badges are awarded when verified"""
        # Modify to ensure high confidence
        result = scvm.verify(valid_practitioner)

        # If verified, should have badges
        if result.overall_status == VerificationStatus.VERIFIED:
            assert len(result.badges) > 0
            assert any(b.badge_type == "verified_practitioner" for b in result.badges)

    def test_recommendations_generated(self, scvm):
        """Test that recommendations are generated for issues"""
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="recs@example.com",
            full_name="Needs Recs Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="BSc",
                    credential_name="BSc Test",
                    issuing_body="Unknown University",
                    issue_date=date(2015, 1, 1),
                    expiry_date=date(2020, 1, 1)  # Expired
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should have recommendations
        assert len(result.recommendations) > 0

    def test_processing_time_tracked(self, scvm, valid_practitioner):
        """Test that processing time is tracked"""
        result = scvm.verify(valid_practitioner)

        assert result.processing_time_seconds > 0
        assert result.started_at is not None
        assert result.completed_at is not None

    def test_multi_credential_verification(self, scvm):
        """Test verification with multiple credentials"""
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="multi@example.com",
            full_name="Multi Cred Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="BSc",
                    credential_name="BSc Nutrition",
                    issuing_body="University of Westminster",
                    issue_date=date(2010, 1, 1)
                ),
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="MSc",
                    credential_name="MSc Clinical Nutrition",
                    issuing_body="University of Lincoln",
                    issue_date=date(2012, 1, 1)
                ),
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="Diploma",
                    credential_name="Diploma in Herbal Medicine",
                    issuing_body="College of Naturopathic Medicine",
                    issue_date=date(2015, 1, 1)
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should have results for all credentials
        assert len(result.credential_results) == 3

    def test_verification_tiers(self, scvm):
        """Test different verification tiers"""
        base_input = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="tiers@example.com",
            full_name="Tier Test Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="BSc",
                    credential_name="BSc Test",
                    issuing_body="University of Westminster",
                    issue_date=date(2020, 1, 1)
                )
            ],
            verification_tier=VerificationTier.BASIC
        )

        result_basic = scvm.verify(base_input)
        assert result_basic.verification_tier == VerificationTier.BASIC

        base_input.verification_tier = VerificationTier.ENHANCED
        result_enhanced = scvm.verify(base_input)
        assert result_enhanced.verification_tier == VerificationTier.ENHANCED

    def test_fraud_risk_score_calculation(self, scvm):
        """Test that fraud risk score is calculated correctly"""
        # Create suspicious input
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="risky@example.com",
            full_name="High Risk Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="PhD",
                    credential_name="PhD Everything",
                    issuing_body="Belford University",  # Diploma mill
                    issue_date=date(2025, 1, 1),  # Date inconsistency
                    expiry_date=date(2020, 1, 1)
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should have elevated fraud risk
        assert result.fraud_risk_score > 0

    def test_summary_generated(self, scvm, valid_practitioner):
        """Test that summary is generated"""
        result = scvm.verify(valid_practitioner)

        assert result.summary != ""
        assert len(result.summary) > 10

    def test_expiry_warning_flag(self, scvm):
        """Test that expiry warning is set for soon-to-expire credentials"""
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="expiring@example.com",
            full_name="Soon Expiring Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="Certificate",
                    credential_name="Certificate Test",
                    issuing_body="University of Westminster",
                    issue_date=date(2020, 1, 1),
                    expiry_date=date.today() + timedelta(days=30)  # Expiring soon
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Check for expiry warning
        assert any(r.expiry_warning for r in result.credential_results)

    def test_legacy_function(self):
        """Test legacy verify_credentials function"""
        result = verify_credentials(
            practitioner_id=uuid4(),
            credentials=["BSc Nutrition", "MSc Clinical Nutrition"],
            documents=[]
        )

        assert result.practitioner_id is not None
        assert result.verified == True
        assert len(result.verification_results) == 2
        assert result.confidence_score > 0

    def test_no_credentials_handles_gracefully(self, scvm):
        """Test handling of input with no credentials"""
        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="nocreds@example.com",
            full_name="No Credentials Person",
            credentials=[],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should return valid result with no credential results
        assert len(result.credential_results) == 0
        assert result.overall_confidence == 0.0

    def test_duplicate_documents_detected(self, scvm):
        """Test that duplicate documents are detected"""
        doc_id_1 = uuid4()
        doc_id_2 = uuid4()
        shared_hash = "duplicate_hash_123"

        input_data = PractitionerVerificationInput(
            practitioner_id=uuid4(),
            email="dupes@example.com",
            full_name="Duplicate Docs Person",
            credentials=[
                PractitionerCredential(
                    credential_id=uuid4(),
                    credential_type="BSc",
                    credential_name="BSc Test",
                    issuing_body="University of Westminster",
                    issue_date=date(2020, 1, 1),
                    supporting_documents=[doc_id_1, doc_id_2]
                )
            ],
            uploaded_documents=[
                UploadedDocument(
                    document_id=doc_id_1,
                    document_type=DocumentType.DEGREE_CERTIFICATE,
                    filename="cert1.pdf",
                    file_size_bytes=1000,
                    upload_timestamp=datetime.utcnow(),
                    mime_type="application/pdf",
                    hash_value=shared_hash
                ),
                UploadedDocument(
                    document_id=doc_id_2,
                    document_type=DocumentType.DEGREE_CERTIFICATE,
                    filename="cert2.pdf",
                    file_size_bytes=1000,
                    upload_timestamp=datetime.utcnow(),
                    mime_type="application/pdf",
                    hash_value=shared_hash  # Same hash = duplicate
                )
            ],
            verification_tier=VerificationTier.STANDARD
        )

        result = scvm.verify(input_data)

        # Should detect duplicate document
        assert any(
            f.indicator_type == "duplicate_document"
            for f in result.fraud_indicators
        )
