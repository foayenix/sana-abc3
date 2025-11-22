"""
Safety Analyzer
===============
Provides personalized safety analysis for supplements based on
user health profile, conditions, medications, and allergies.
"""

import logging
from typing import List, Dict, Optional, Set
from uuid import UUID
from datetime import datetime

from .models import (
    Product,
    Ingredient,
    UserHealthProfile,
    SafetyCheckInput,
    SafetyCheckResult,
    InteractionWarning,
    SafetyRating,
    InteractionSeverity,
    EvidenceQuality,
)
from .interaction_checker import InteractionChecker

logger = logging.getLogger(__name__)


class SafetyAnalyzer:
    """
    Personalized Safety Analysis Engine

    Analyzes supplements for safety based on:
    - User health conditions
    - Current medications
    - Known allergies
    - Age and life stage (pregnancy, breastfeeding)
    - Other supplements being taken
    """

    # Conditions that require special caution with supplements
    CONDITION_CONTRAINDICATIONS = {
        "pregnancy": {
            "contraindicated": [
                "st. john's wort", "kava", "dong quai", "black cohosh",
                "pennyroyal", "mugwort", "blue cohosh", "tansy",
                "high dose vitamin a", "retinol"
            ],
            "use_caution": [
                "ginger", "ginkgo biloba", "echinacea", "valerian",
                "licorice", "chamomile", "turmeric"
            ],
            "warning": "Many herbs have not been adequately studied during pregnancy."
        },
        "breastfeeding": {
            "contraindicated": [
                "kava", "comfrey", "st. john's wort"
            ],
            "use_caution": [
                "ginkgo biloba", "ginseng", "echinacea", "valerian"
            ],
            "warning": "Supplements may pass through breast milk to the infant."
        },
        "liver disease": {
            "contraindicated": [
                "kava", "comfrey", "chaparral", "germander",
                "greater celandine", "high dose niacin"
            ],
            "use_caution": [
                "black cohosh", "green tea extract", "turmeric",
                "valerian", "vitamin a"
            ],
            "warning": "Liver conditions increase risk of supplement-related hepatotoxicity."
        },
        "kidney disease": {
            "contraindicated": [
                "aristolochia", "high dose vitamin c", "high dose vitamin d"
            ],
            "use_caution": [
                "magnesium", "potassium", "phosphorus", "creatine"
            ],
            "warning": "Kidney function affects supplement metabolism and excretion."
        },
        "bleeding disorder": {
            "contraindicated": [],
            "use_caution": [
                "ginkgo biloba", "garlic", "ginger", "turmeric",
                "omega-3", "fish oil", "vitamin e", "feverfew",
                "dong quai", "white willow"
            ],
            "warning": "These supplements may increase bleeding risk."
        },
        "diabetes": {
            "use_caution": [
                "ginseng", "chromium", "alpha-lipoic acid", "bitter melon",
                "fenugreek", "gymnema"
            ],
            "warning": "These supplements may affect blood sugar levels."
        },
        "hypertension": {
            "contraindicated": [
                "licorice", "ephedra", "yohimbe"
            ],
            "use_caution": [
                "ginseng", "high dose caffeine", "guarana"
            ],
            "warning": "These supplements may affect blood pressure."
        },
        "anxiety": {
            "use_caution": [
                "caffeine", "guarana", "yerba mate", "ginseng"
            ],
            "warning": "Stimulant supplements may worsen anxiety."
        },
        "depression": {
            "use_caution": [
                "st. john's wort", "5-htp", "sam-e"
            ],
            "warning": "May interact with antidepressant medications."
        },
        "autoimmune disease": {
            "use_caution": [
                "echinacea", "astragalus", "reishi", "medicinal mushrooms"
            ],
            "warning": "Immune-stimulating supplements may worsen autoimmune conditions."
        },
        "hormone-sensitive conditions": {
            "contraindicated": [
                "red clover", "soy isoflavones", "black cohosh", "dong quai"
            ],
            "use_caution": [
                "maca", "licorice", "hops"
            ],
            "warning": "Phytoestrogens may affect hormone-sensitive conditions."
        },
    }

    # Common allergen ingredients in supplements
    COMMON_ALLERGENS = {
        "soy": ["soy", "soya", "soybean", "soy lecithin", "tocopherol"],
        "dairy": ["milk", "lactose", "casein", "whey", "lactalbumin"],
        "gluten": ["wheat", "gluten", "barley", "rye"],
        "shellfish": ["shellfish", "shrimp", "crab", "lobster", "glucosamine"],
        "fish": ["fish", "fish oil", "cod liver oil", "omega-3"],
        "tree nuts": ["almond", "walnut", "cashew", "brazil nut", "hazelnut"],
        "peanuts": ["peanut", "peanut oil"],
        "eggs": ["egg", "albumin", "lysozyme"],
        "corn": ["corn", "maize", "corn starch"],
        "sulfites": ["sulfite", "sulphite", "sodium metabisulfite"],
    }

    # Age-related considerations
    AGE_CONSIDERATIONS = {
        "pediatric": {  # Under 18
            "caution_message": "Not all supplements are safe for children. Consult a pediatrician.",
            "not_recommended": [
                "st. john's wort", "kava", "yohimbe", "ephedra",
                "high-dose vitamins", "weight loss supplements"
            ]
        },
        "elderly": {  # Over 65
            "caution_message": "Older adults may need adjusted doses and should be monitored for interactions.",
            "use_caution": [
                "ginkgo biloba", "vitamin e", "garlic", "ginger"
            ]
        },
    }

    def __init__(self):
        """Initialize the safety analyzer"""
        self.interaction_checker = InteractionChecker()

    def analyze_safety(
        self,
        product: Product,
        health_profile: UserHealthProfile
    ) -> SafetyCheckResult:
        """
        Perform comprehensive safety analysis

        Args:
            product: Product to analyze
            health_profile: User's health profile

        Returns:
            SafetyCheckResult with detailed findings
        """
        # Initialize result
        result = SafetyCheckResult(
            product_id=product.id,
            user_id=health_profile.user_id,
            is_safe=True,
            safety_score=100.0,
            safety_rating=SafetyRating.SAFE,
            interaction_warnings=[],
            condition_warnings=[],
            allergy_warnings=[],
            pregnancy_warnings=[],
            recommendations=[],
        )

        # Get ingredient names
        ingredients = [
            (ing.standardized_name or ing.name).lower()
            for ing in product.ingredients
        ]

        # 1. Check medication interactions
        interaction_warnings = self.interaction_checker.check_product_interactions(
            product=product,
            medications=health_profile.medications,
            other_supplements=health_profile.supplements_currently_taking,
        )
        result.interaction_warnings = interaction_warnings

        # 2. Check condition-specific warnings
        condition_warnings = self._check_condition_warnings(
            ingredients=ingredients,
            conditions=health_profile.conditions,
        )
        result.condition_warnings = condition_warnings

        # 3. Check allergy warnings
        allergy_warnings = self._check_allergy_warnings(
            product=product,
            allergies=health_profile.allergies,
        )
        result.allergy_warnings = allergy_warnings

        # 4. Check pregnancy/breastfeeding warnings
        pregnancy_warnings = self._check_pregnancy_warnings(
            ingredients=ingredients,
            is_pregnant=health_profile.is_pregnant,
            is_breastfeeding=health_profile.is_breastfeeding,
        )
        result.pregnancy_warnings = pregnancy_warnings

        # 5. Check age-related warnings
        age_warnings = self._check_age_warnings(
            ingredients=ingredients,
            age=health_profile.age,
        )
        result.condition_warnings.extend(age_warnings)

        # Calculate overall safety score
        result.safety_score = self._calculate_safety_score(result)

        # Determine safety rating
        result.safety_rating = self._determine_safety_rating(result)

        # Set is_safe flag
        result.is_safe = result.safety_rating in [
            SafetyRating.SAFE,
            SafetyRating.GENERALLY_SAFE
        ]

        # Generate recommendations
        result.recommendations = self._generate_recommendations(result)

        return result

    def _check_condition_warnings(
        self,
        ingredients: List[str],
        conditions: List[str]
    ) -> List[str]:
        """Check for condition-specific warnings"""
        warnings = []

        for condition in conditions:
            condition_lower = condition.lower()

            # Look for exact or partial matches in our database
            for known_condition, rules in self.CONDITION_CONTRAINDICATIONS.items():
                if known_condition in condition_lower or condition_lower in known_condition:
                    # Check contraindicated ingredients
                    contraindicated = rules.get("contraindicated", [])
                    for ingredient in ingredients:
                        for contra in contraindicated:
                            if contra in ingredient or ingredient in contra:
                                warnings.append(
                                    f"CONTRAINDICATED: {ingredient.title()} should not be used "
                                    f"with {condition}. {rules.get('warning', '')}"
                                )

                    # Check use-with-caution ingredients
                    use_caution = rules.get("use_caution", [])
                    for ingredient in ingredients:
                        for caution in use_caution:
                            if caution in ingredient or ingredient in caution:
                                warnings.append(
                                    f"USE CAUTION: {ingredient.title()} should be used carefully "
                                    f"with {condition}. {rules.get('warning', '')}"
                                )

        return warnings

    def _check_allergy_warnings(
        self,
        product: Product,
        allergies: List[str]
    ) -> List[str]:
        """Check for allergy-related warnings"""
        warnings = []

        # Get all text to search (ingredients + warnings)
        all_text = " ".join([
            (ing.standardized_name or ing.name).lower()
            for ing in product.ingredients
        ])
        all_text += " " + " ".join([w.lower() for w in product.warnings])

        for allergy in allergies:
            allergy_lower = allergy.lower()

            # Check against common allergen mappings
            for allergen_name, allergen_terms in self.COMMON_ALLERGENS.items():
                if allergen_name in allergy_lower or allergy_lower in allergen_name:
                    for term in allergen_terms:
                        if term in all_text:
                            warnings.append(
                                f"ALLERGY WARNING: This product may contain {term}, "
                                f"which is related to your {allergy} allergy."
                            )
                            break

            # Direct ingredient match
            for ingredient in product.ingredients:
                ing_name = (ingredient.standardized_name or ingredient.name).lower()
                if allergy_lower in ing_name or ing_name in allergy_lower:
                    warnings.append(
                        f"ALLERGY WARNING: This product contains {ingredient.name}, "
                        f"which matches your {allergy} allergy."
                    )

        return list(set(warnings))  # Remove duplicates

    def _check_pregnancy_warnings(
        self,
        ingredients: List[str],
        is_pregnant: bool,
        is_breastfeeding: bool
    ) -> List[str]:
        """Check for pregnancy and breastfeeding warnings"""
        warnings = []

        if is_pregnant:
            rules = self.CONDITION_CONTRAINDICATIONS.get("pregnancy", {})

            for ingredient in ingredients:
                # Check contraindicated
                for contra in rules.get("contraindicated", []):
                    if contra in ingredient or ingredient in contra:
                        warnings.append(
                            f"PREGNANCY WARNING: {ingredient.title()} is contraindicated "
                            f"during pregnancy."
                        )

                # Check use caution
                for caution in rules.get("use_caution", []):
                    if caution in ingredient or ingredient in caution:
                        warnings.append(
                            f"PREGNANCY CAUTION: {ingredient.title()} should be used with "
                            f"caution during pregnancy. Consult your healthcare provider."
                        )

            if warnings:
                warnings.append(rules.get("warning", ""))

        if is_breastfeeding:
            rules = self.CONDITION_CONTRAINDICATIONS.get("breastfeeding", {})

            for ingredient in ingredients:
                # Check contraindicated
                for contra in rules.get("contraindicated", []):
                    if contra in ingredient or ingredient in contra:
                        warnings.append(
                            f"BREASTFEEDING WARNING: {ingredient.title()} is contraindicated "
                            f"while breastfeeding."
                        )

                # Check use caution
                for caution in rules.get("use_caution", []):
                    if caution in ingredient or ingredient in caution:
                        warnings.append(
                            f"BREASTFEEDING CAUTION: {ingredient.title()} should be used with "
                            f"caution while breastfeeding."
                        )

            if warnings:
                warnings.append(rules.get("warning", ""))

        return list(set(warnings))  # Remove duplicates

    def _check_age_warnings(
        self,
        ingredients: List[str],
        age: Optional[int]
    ) -> List[str]:
        """Check for age-related warnings"""
        warnings = []

        if age is None:
            return warnings

        if age < 18:
            rules = self.AGE_CONSIDERATIONS.get("pediatric", {})
            warnings.append(rules.get("caution_message", ""))

            for ingredient in ingredients:
                for not_rec in rules.get("not_recommended", []):
                    if not_rec in ingredient or ingredient in not_rec:
                        warnings.append(
                            f"AGE WARNING: {ingredient.title()} is not recommended for "
                            f"individuals under 18."
                        )

        elif age >= 65:
            rules = self.AGE_CONSIDERATIONS.get("elderly", {})
            warnings.append(rules.get("caution_message", ""))

            for ingredient in ingredients:
                for caution in rules.get("use_caution", []):
                    if caution in ingredient or ingredient in caution:
                        warnings.append(
                            f"AGE CAUTION: {ingredient.title()} should be used with caution "
                            f"in older adults."
                        )

        return [w for w in warnings if w]  # Filter empty strings

    def _calculate_safety_score(self, result: SafetyCheckResult) -> float:
        """
        Calculate overall safety score (0-100)

        Scoring:
        - Start at 100
        - Deduct for interactions (severity-based)
        - Deduct for condition warnings
        - Deduct for allergy warnings
        - Deduct for pregnancy warnings
        """
        score = 100.0

        # Interaction deductions
        for warning in result.interaction_warnings:
            deduction = self.interaction_checker.get_severity_score(warning.severity)
            score -= deduction * 0.5  # Max 50 points per interaction

        # Condition warning deductions
        for warning in result.condition_warnings:
            if "CONTRAINDICATED" in warning:
                score -= 30
            elif "USE CAUTION" in warning or "CAUTION" in warning:
                score -= 10
            else:
                score -= 5

        # Allergy warning deductions
        for warning in result.allergy_warnings:
            score -= 40  # Allergies are serious

        # Pregnancy warning deductions
        for warning in result.pregnancy_warnings:
            if "CONTRAINDICATED" in warning or "contraindicated" in warning:
                score -= 40
            elif "CAUTION" in warning or "caution" in warning:
                score -= 15

        return max(0.0, min(100.0, score))

    def _determine_safety_rating(self, result: SafetyCheckResult) -> SafetyRating:
        """Determine overall safety rating based on score and warnings"""
        # Check for any contraindications
        has_contraindication = any(
            "CONTRAINDICATED" in w or "contraindicated" in w
            for w in result.condition_warnings + result.pregnancy_warnings
        )

        if has_contraindication:
            return SafetyRating.CONTRAINDICATED

        # Check for severe interactions
        has_severe_interaction = any(
            w.severity in [InteractionSeverity.SEVERE, InteractionSeverity.CONTRAINDICATED]
            for w in result.interaction_warnings
        )

        if has_severe_interaction:
            return SafetyRating.NOT_RECOMMENDED

        # Check for allergy warnings
        if result.allergy_warnings:
            return SafetyRating.CONTRAINDICATED

        # Score-based rating
        if result.safety_score >= 90:
            return SafetyRating.SAFE
        elif result.safety_score >= 70:
            return SafetyRating.GENERALLY_SAFE
        elif result.safety_score >= 50:
            return SafetyRating.USE_CAUTION
        else:
            return SafetyRating.NOT_RECOMMENDED

    def _generate_recommendations(self, result: SafetyCheckResult) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Interaction recommendations
        if result.interaction_warnings:
            severe_count = sum(
                1 for w in result.interaction_warnings
                if w.severity in [InteractionSeverity.SEVERE, InteractionSeverity.CONTRAINDICATED]
            )
            if severe_count > 0:
                recommendations.append(
                    "Consult your healthcare provider before using this product due to "
                    "potential serious interactions with your current medications."
                )
            else:
                recommendations.append(
                    "Monitor for any unusual effects and consider spacing doses from "
                    "your medications."
                )

        # Condition recommendations
        if any("CONTRAINDICATED" in w for w in result.condition_warnings):
            recommendations.append(
                "This product is not recommended for your health condition. "
                "Consider alternative products."
            )
        elif result.condition_warnings:
            recommendations.append(
                "Start with a lower dose and monitor how you feel. "
                "Consult your healthcare provider if you have concerns."
            )

        # Allergy recommendations
        if result.allergy_warnings:
            recommendations.append(
                "Do not use this product due to potential allergen content."
            )

        # Pregnancy recommendations
        if result.pregnancy_warnings:
            recommendations.append(
                "Consult your obstetrician or midwife before using any supplement "
                "during pregnancy or while breastfeeding."
            )

        # General safety recommendations
        if not recommendations:
            recommendations.append(
                "This product appears safe based on your health profile. "
                "Start with the recommended dose and monitor for any adverse effects."
            )

        return recommendations

    def quick_safety_check(
        self,
        ingredient_name: str,
        medications: List[str] = None,
        conditions: List[str] = None
    ) -> Dict:
        """
        Quick safety check for a single ingredient

        Args:
            ingredient_name: Name of the ingredient
            medications: Current medications
            conditions: Health conditions

        Returns:
            Dictionary with safety information
        """
        medications = medications or []
        conditions = conditions or []

        result = {
            "ingredient": ingredient_name,
            "is_safe": True,
            "warnings": [],
            "interactions": [],
        }

        # Check medication interactions
        for med in medications:
            interaction = self.interaction_checker.check_interaction(
                ingredient_name, med
            )
            if interaction:
                result["interactions"].append({
                    "with": med,
                    "severity": interaction.severity.value,
                    "description": interaction.description,
                })
                if interaction.severity in [
                    InteractionSeverity.SEVERE,
                    InteractionSeverity.CONTRAINDICATED
                ]:
                    result["is_safe"] = False

        # Check condition warnings
        for condition in conditions:
            condition_lower = condition.lower()
            for known_condition, rules in self.CONDITION_CONTRAINDICATIONS.items():
                if known_condition in condition_lower:
                    ing_lower = ingredient_name.lower()

                    for contra in rules.get("contraindicated", []):
                        if contra in ing_lower or ing_lower in contra:
                            result["warnings"].append(
                                f"Contraindicated with {condition}"
                            )
                            result["is_safe"] = False

                    for caution in rules.get("use_caution", []):
                        if caution in ing_lower or ing_lower in caution:
                            result["warnings"].append(
                                f"Use with caution with {condition}"
                            )

        return result
