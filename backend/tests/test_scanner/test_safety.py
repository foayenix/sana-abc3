"""
Tests for Safety Analyzer
=========================
"""

import pytest
from uuid import uuid4

from algorithms.product_scanner import (
    SafetyAnalyzer,
    InteractionChecker,
    Product,
    Ingredient,
    UserHealthProfile,
    ProductCategory,
    SafetyRating,
    InteractionSeverity,
)


class TestSafetyAnalyzer:
    """Tests for the SafetyAnalyzer class"""

    @pytest.fixture
    def analyzer(self):
        return SafetyAnalyzer()

    @pytest.fixture
    def sample_product(self):
        return Product(
            id=uuid4(),
            name="Test Supplement",
            category=ProductCategory.HERBS,
            ingredients=[
                Ingredient(name="Vitamin D", amount=5000, unit="IU",
                           standardized_name="Vitamin D"),
                Ingredient(name="Magnesium", amount=400, unit="mg",
                           standardized_name="Magnesium"),
            ],
            safety_score=85.0,
        )

    @pytest.fixture
    def st_johns_wort_product(self):
        return Product(
            id=uuid4(),
            name="St. John's Wort",
            category=ProductCategory.HERBS,
            ingredients=[
                Ingredient(name="St. John's Wort Extract", amount=300, unit="mg",
                           standardized_name="St. John's Wort"),
            ],
            safety_score=65.0,
        )

    @pytest.fixture
    def healthy_profile(self):
        return UserHealthProfile(
            user_id=uuid4(),
            conditions=[],
            medications=[],
            allergies=[],
            age=35,
            is_pregnant=False,
            is_breastfeeding=False,
        )

    @pytest.fixture
    def complex_profile(self):
        return UserHealthProfile(
            user_id=uuid4(),
            conditions=["anxiety", "hypertension"],
            medications=["sertraline", "lisinopril"],
            allergies=["soy"],
            age=45,
            is_pregnant=False,
            is_breastfeeding=False,
        )

    # Basic safety analysis tests
    def test_safe_product_healthy_user(self, analyzer, sample_product, healthy_profile):
        """Test that safe product + healthy user = safe rating"""
        result = analyzer.analyze_safety(sample_product, healthy_profile)

        assert result.is_safe is True
        assert result.safety_score >= 80
        assert result.safety_rating in [SafetyRating.SAFE, SafetyRating.GENERALLY_SAFE]

    def test_safety_result_structure(self, analyzer, sample_product, healthy_profile):
        """Test that safety result has all required fields"""
        result = analyzer.analyze_safety(sample_product, healthy_profile)

        assert result.product_id == sample_product.id
        assert result.user_id == healthy_profile.user_id
        assert isinstance(result.safety_score, float)
        assert 0 <= result.safety_score <= 100
        assert isinstance(result.recommendations, list)

    # Medication interaction tests
    def test_ssri_interaction_detected(self, analyzer, st_johns_wort_product, complex_profile):
        """Test that St. John's Wort + SSRI interaction is detected"""
        result = analyzer.analyze_safety(st_johns_wort_product, complex_profile)

        assert result.is_safe is False
        assert len(result.interaction_warnings) > 0

        # Check for SSRI interaction
        has_ssri_warning = any(
            "sertraline" in str(w.interacting_items).lower() or
            "ssri" in str(w.interacting_items).lower()
            for w in result.interaction_warnings
        )
        assert has_ssri_warning

    def test_warfarin_interaction(self, analyzer, st_johns_wort_product):
        """Test warfarin interaction detection"""
        profile = UserHealthProfile(
            user_id=uuid4(),
            medications=["warfarin"],
        )

        result = analyzer.analyze_safety(st_johns_wort_product, profile)

        assert len(result.interaction_warnings) > 0
        assert any(
            w.severity in [InteractionSeverity.SEVERE, InteractionSeverity.MODERATE]
            for w in result.interaction_warnings
        )

    # Condition-based warnings tests
    def test_pregnancy_warning(self, analyzer, st_johns_wort_product):
        """Test pregnancy warnings are generated"""
        pregnant_profile = UserHealthProfile(
            user_id=uuid4(),
            is_pregnant=True,
        )

        result = analyzer.analyze_safety(st_johns_wort_product, pregnant_profile)

        assert len(result.pregnancy_warnings) > 0
        assert any("pregnancy" in w.lower() for w in result.pregnancy_warnings)

    def test_breastfeeding_warning(self, analyzer, st_johns_wort_product):
        """Test breastfeeding warnings are generated"""
        breastfeeding_profile = UserHealthProfile(
            user_id=uuid4(),
            is_breastfeeding=True,
        )

        result = analyzer.analyze_safety(st_johns_wort_product, breastfeeding_profile)

        assert len(result.pregnancy_warnings) > 0

    def test_liver_disease_warning(self, analyzer):
        """Test liver disease warnings for kava"""
        kava_product = Product(
            id=uuid4(),
            name="Kava Extract",
            category=ProductCategory.HERBS,
            ingredients=[
                Ingredient(name="Kava Root Extract", standardized_name="Kava"),
            ],
        )

        profile = UserHealthProfile(
            user_id=uuid4(),
            conditions=["liver disease"],
        )

        result = analyzer.analyze_safety(kava_product, profile)

        assert len(result.condition_warnings) > 0

    # Allergy tests
    def test_allergy_warning(self, analyzer):
        """Test allergy warnings are generated"""
        soy_product = Product(
            id=uuid4(),
            name="Vitamin E",
            category=ProductCategory.VITAMINS,
            ingredients=[
                Ingredient(name="Soybean Oil", standardized_name="Soybean Oil"),
                Ingredient(name="Vitamin E", standardized_name="Vitamin E"),
            ],
        )

        profile = UserHealthProfile(
            user_id=uuid4(),
            allergies=["soy"],
        )

        result = analyzer.analyze_safety(soy_product, profile)

        assert len(result.allergy_warnings) > 0
        assert result.safety_rating == SafetyRating.CONTRAINDICATED

    # Age-based tests
    def test_pediatric_warning(self, analyzer, st_johns_wort_product):
        """Test warnings for children"""
        child_profile = UserHealthProfile(
            user_id=uuid4(),
            age=12,
        )

        result = analyzer.analyze_safety(st_johns_wort_product, child_profile)

        # Should have age-related warnings
        has_age_warning = any(
            "age" in w.lower() or "18" in w
            for w in result.condition_warnings
        )
        assert has_age_warning

    def test_elderly_warning(self, analyzer):
        """Test warnings for elderly users"""
        ginkgo_product = Product(
            id=uuid4(),
            name="Ginkgo Biloba",
            category=ProductCategory.HERBS,
            ingredients=[
                Ingredient(name="Ginkgo Biloba Extract", standardized_name="Ginkgo Biloba"),
            ],
        )

        elderly_profile = UserHealthProfile(
            user_id=uuid4(),
            age=75,
        )

        result = analyzer.analyze_safety(ginkgo_product, elderly_profile)

        # Should have caution message for elderly
        has_elderly_caution = any(
            "older" in w.lower() or "elderly" in w.lower() or "age" in w.lower()
            for w in result.condition_warnings
        )
        assert has_elderly_caution

    # Safety score calculation tests
    def test_safety_score_decreases_with_warnings(self, analyzer, st_johns_wort_product):
        """Test that safety score decreases with more warnings"""
        healthy_profile = UserHealthProfile(user_id=uuid4())
        complex_profile = UserHealthProfile(
            user_id=uuid4(),
            medications=["warfarin", "sertraline"],
            conditions=["liver disease"],
        )

        healthy_result = analyzer.analyze_safety(st_johns_wort_product, healthy_profile)
        complex_result = analyzer.analyze_safety(st_johns_wort_product, complex_profile)

        assert complex_result.safety_score < healthy_result.safety_score

    def test_safety_score_bounds(self, analyzer, sample_product, healthy_profile):
        """Test safety score is within 0-100"""
        result = analyzer.analyze_safety(sample_product, healthy_profile)
        assert 0 <= result.safety_score <= 100

    # Recommendations tests
    def test_recommendations_generated(self, analyzer, st_johns_wort_product, complex_profile):
        """Test that recommendations are generated"""
        result = analyzer.analyze_safety(st_johns_wort_product, complex_profile)
        assert len(result.recommendations) > 0


class TestInteractionChecker:
    """Tests for the InteractionChecker class"""

    @pytest.fixture
    def checker(self):
        return InteractionChecker()

    def test_st_johns_wort_warfarin_interaction(self, checker):
        """Test known St. John's Wort + Warfarin interaction"""
        interaction = checker.check_interaction("st. john's wort", "warfarin")

        assert interaction is not None
        assert interaction.severity == InteractionSeverity.SEVERE
        assert "CYP3A4" in interaction.mechanism or "warfarin" in interaction.description.lower()

    def test_ginkgo_aspirin_interaction(self, checker):
        """Test known Ginkgo + Aspirin interaction"""
        interaction = checker.check_interaction("ginkgo biloba", "aspirin")

        assert interaction is not None
        assert interaction.severity == InteractionSeverity.MODERATE

    def test_calcium_iron_interaction(self, checker):
        """Test calcium + iron supplement interaction"""
        interaction = checker.check_interaction("calcium", "iron")

        assert interaction is not None
        assert interaction.severity == InteractionSeverity.MINOR
        assert "absorption" in interaction.description.lower()

    def test_no_interaction(self, checker):
        """Test that no interaction is found for safe combination"""
        interaction = checker.check_interaction("vitamin c", "zinc")
        # May or may not have interaction, but shouldn't be severe
        if interaction:
            assert interaction.severity != InteractionSeverity.CONTRAINDICATED

    def test_medication_class_matching(self, checker):
        """Test that medication classes are properly matched"""
        # Sertraline is an SSRI
        interaction = checker.check_interaction("st. john's wort", "sertraline")
        assert interaction is not None

    def test_get_all_interactions_for_ingredient(self, checker):
        """Test getting all interactions for an ingredient"""
        interactions = checker.get_all_interactions_for_ingredient("st. john's wort")

        assert len(interactions) > 0
        # Should have at least warfarin and SSRI interactions
        has_warfarin = any("warfarin" in i.ingredient_b for i in interactions)
        assert has_warfarin

    def test_severity_score_conversion(self, checker):
        """Test severity to score conversion"""
        assert checker.get_severity_score(InteractionSeverity.NONE) == 0
        assert checker.get_severity_score(InteractionSeverity.MINOR) == 25
        assert checker.get_severity_score(InteractionSeverity.MODERATE) == 50
        assert checker.get_severity_score(InteractionSeverity.SEVERE) == 75
        assert checker.get_severity_score(InteractionSeverity.CONTRAINDICATED) == 100


class TestQuickSafetyCheck:
    """Tests for quick safety check functionality"""

    @pytest.fixture
    def analyzer(self):
        return SafetyAnalyzer()

    def test_quick_check_safe_ingredient(self, analyzer):
        """Test quick check for generally safe ingredient"""
        result = analyzer.quick_safety_check(
            ingredient_name="vitamin c",
            medications=[],
            conditions=[],
        )

        assert result["is_safe"] is True
        assert len(result["warnings"]) == 0
        assert len(result["interactions"]) == 0

    def test_quick_check_with_interaction(self, analyzer):
        """Test quick check detects interaction"""
        result = analyzer.quick_safety_check(
            ingredient_name="ginkgo biloba",
            medications=["warfarin"],
            conditions=[],
        )

        assert len(result["interactions"]) > 0

    def test_quick_check_with_condition(self, analyzer):
        """Test quick check with health condition"""
        result = analyzer.quick_safety_check(
            ingredient_name="kava",
            medications=[],
            conditions=["liver disease"],
        )

        assert result["is_safe"] is False or len(result["warnings"]) > 0
