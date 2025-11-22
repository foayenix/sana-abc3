"""
Interaction Checker
===================
Checks for interactions between supplements, herbs, and medications.
Uses a comprehensive interaction database and rule-based analysis.
"""

import logging
from typing import List, Dict, Optional, Set, Tuple
from uuid import UUID, uuid4
from datetime import datetime

from .models import (
    Ingredient,
    IngredientInteraction,
    InteractionSeverity,
    EvidenceQuality,
    InteractionWarning,
    Product,
)

logger = logging.getLogger(__name__)


class InteractionChecker:
    """
    Interaction Checking Engine

    Checks for:
    - Herb-drug interactions
    - Supplement-supplement interactions
    - Food-drug interactions
    - Dosage-related risks
    - Contraindicated combinations
    """

    def __init__(self):
        """Initialize the interaction checker with default database"""
        self.interactions_db = self._load_interaction_database()
        self.medication_classes = self._load_medication_classes()

    def _load_interaction_database(self) -> Dict[Tuple[str, str], IngredientInteraction]:
        """
        Load the interaction database

        Returns a dict where keys are (ingredient_a, ingredient_b) tuples
        (normalized to lowercase, alphabetically sorted)
        """
        # Core interaction database
        # In production, this would be loaded from a database or API
        interactions = [
            # St. John's Wort interactions (CYP3A4 inducer)
            IngredientInteraction(
                ingredient_a="st. john's wort",
                ingredient_b="warfarin",
                interaction_type="herb-drug",
                severity=InteractionSeverity.SEVERE,
                description="St. John's Wort significantly reduces warfarin levels, potentially leading to clot formation",
                mechanism="CYP3A4 and P-glycoprotein induction",
                clinical_significance="May require 50-100% increase in warfarin dose",
                evidence_quality=EvidenceQuality.HIGH,
                references=["PMID: 11085889", "PMID: 11095498"],
            ),
            IngredientInteraction(
                ingredient_a="st. john's wort",
                ingredient_b="ssri",
                interaction_type="herb-drug",
                severity=InteractionSeverity.SEVERE,
                description="Risk of serotonin syndrome when combined with SSRIs",
                mechanism="Additive serotonergic effects",
                clinical_significance="Potentially life-threatening",
                evidence_quality=EvidenceQuality.HIGH,
            ),
            IngredientInteraction(
                ingredient_a="st. john's wort",
                ingredient_b="oral contraceptives",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="May reduce effectiveness of birth control pills",
                mechanism="CYP3A4 induction increases estrogen metabolism",
                evidence_quality=EvidenceQuality.HIGH,
            ),

            # Ginkgo biloba interactions
            IngredientInteraction(
                ingredient_a="ginkgo biloba",
                ingredient_b="warfarin",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="Ginkgo may increase bleeding risk with warfarin",
                mechanism="Inhibition of platelet aggregation",
                evidence_quality=EvidenceQuality.MODERATE,
            ),
            IngredientInteraction(
                ingredient_a="ginkgo biloba",
                ingredient_b="aspirin",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="Increased bleeding risk when combined with aspirin",
                mechanism="Additive antiplatelet effects",
                evidence_quality=EvidenceQuality.MODERATE,
            ),
            IngredientInteraction(
                ingredient_a="ginkgo biloba",
                ingredient_b="ibuprofen",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="Increased bleeding risk with NSAIDs",
                mechanism="Additive effects on platelet function",
                evidence_quality=EvidenceQuality.MODERATE,
            ),

            # Valerian interactions
            IngredientInteraction(
                ingredient_a="valerian",
                ingredient_b="benzodiazepines",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="Enhanced sedation when combined with benzodiazepines",
                mechanism="Additive CNS depressant effects",
                evidence_quality=EvidenceQuality.MODERATE,
            ),
            IngredientInteraction(
                ingredient_a="valerian",
                ingredient_b="alcohol",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="Increased sedation and CNS depression",
                mechanism="Additive CNS depressant effects",
                evidence_quality=EvidenceQuality.LOW,
            ),

            # Kava interactions
            IngredientInteraction(
                ingredient_a="kava",
                ingredient_b="alcohol",
                interaction_type="herb-drug",
                severity=InteractionSeverity.SEVERE,
                description="Risk of liver damage and enhanced sedation",
                mechanism="Additive hepatotoxicity and CNS depression",
                evidence_quality=EvidenceQuality.MODERATE,
            ),
            IngredientInteraction(
                ingredient_a="kava",
                ingredient_b="benzodiazepines",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="Enhanced sedation effects",
                mechanism="Additive GABA receptor modulation",
                evidence_quality=EvidenceQuality.MODERATE,
            ),

            # Ginseng interactions
            IngredientInteraction(
                ingredient_a="ginseng",
                ingredient_b="warfarin",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="May alter warfarin effectiveness",
                mechanism="Affects CYP enzymes",
                evidence_quality=EvidenceQuality.LOW,
            ),
            IngredientInteraction(
                ingredient_a="ginseng",
                ingredient_b="insulin",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="May enhance hypoglycemic effects",
                mechanism="Ginseng has hypoglycemic properties",
                clinical_significance="Monitor blood glucose closely",
                evidence_quality=EvidenceQuality.MODERATE,
            ),

            # Garlic interactions
            IngredientInteraction(
                ingredient_a="garlic",
                ingredient_b="warfarin",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MINOR,
                description="High-dose garlic may slightly increase bleeding risk",
                mechanism="Antiplatelet effects",
                evidence_quality=EvidenceQuality.LOW,
            ),

            # Calcium interactions
            IngredientInteraction(
                ingredient_a="calcium",
                ingredient_b="iron",
                interaction_type="supplement-supplement",
                severity=InteractionSeverity.MINOR,
                description="Calcium inhibits iron absorption when taken together",
                mechanism="Competition for absorption in the gut",
                clinical_significance="Take at different times of day",
                evidence_quality=EvidenceQuality.HIGH,
            ),
            IngredientInteraction(
                ingredient_a="calcium",
                ingredient_b="thyroid medication",
                interaction_type="supplement-drug",
                severity=InteractionSeverity.MODERATE,
                description="Calcium reduces absorption of thyroid medications",
                mechanism="Forms insoluble complexes in the gut",
                clinical_significance="Take 4 hours apart",
                evidence_quality=EvidenceQuality.HIGH,
            ),

            # Iron interactions
            IngredientInteraction(
                ingredient_a="iron",
                ingredient_b="zinc",
                interaction_type="supplement-supplement",
                severity=InteractionSeverity.MINOR,
                description="High-dose zinc can inhibit iron absorption",
                mechanism="Competition for absorption",
                evidence_quality=EvidenceQuality.MODERATE,
            ),

            # Vitamin K interactions
            IngredientInteraction(
                ingredient_a="vitamin k",
                ingredient_b="warfarin",
                interaction_type="supplement-drug",
                severity=InteractionSeverity.SEVERE,
                description="Vitamin K directly antagonizes warfarin",
                mechanism="Vitamin K is required for clotting factor synthesis",
                clinical_significance="Avoid high-dose vitamin K; maintain consistent dietary intake",
                evidence_quality=EvidenceQuality.HIGH,
            ),

            # Magnesium interactions
            IngredientInteraction(
                ingredient_a="magnesium",
                ingredient_b="antibiotics",
                interaction_type="supplement-drug",
                severity=InteractionSeverity.MODERATE,
                description="Magnesium can reduce absorption of certain antibiotics",
                mechanism="Chelation in the gut",
                clinical_significance="Take 2 hours apart from quinolone and tetracycline antibiotics",
                evidence_quality=EvidenceQuality.HIGH,
            ),

            # Omega-3 interactions
            IngredientInteraction(
                ingredient_a="omega-3",
                ingredient_b="warfarin",
                interaction_type="supplement-drug",
                severity=InteractionSeverity.MINOR,
                description="High-dose omega-3 may slightly increase bleeding risk",
                mechanism="Antiplatelet effects",
                evidence_quality=EvidenceQuality.MODERATE,
            ),

            # Melatonin interactions
            IngredientInteraction(
                ingredient_a="melatonin",
                ingredient_b="blood pressure medications",
                interaction_type="supplement-drug",
                severity=InteractionSeverity.MINOR,
                description="Melatonin may affect blood pressure",
                mechanism="Melatonin influences circadian blood pressure patterns",
                evidence_quality=EvidenceQuality.LOW,
            ),

            # Echinacea interactions
            IngredientInteraction(
                ingredient_a="echinacea",
                ingredient_b="immunosuppressants",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="Echinacea may counteract immunosuppressant effects",
                mechanism="Immune-stimulating properties",
                clinical_significance="Avoid in transplant patients",
                evidence_quality=EvidenceQuality.MODERATE,
            ),

            # Turmeric/Curcumin interactions
            IngredientInteraction(
                ingredient_a="turmeric",
                ingredient_b="blood thinners",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="Curcumin may increase bleeding risk with blood thinners",
                mechanism="Antiplatelet and anticoagulant properties",
                evidence_quality=EvidenceQuality.MODERATE,
            ),

            # Licorice interactions
            IngredientInteraction(
                ingredient_a="licorice",
                ingredient_b="diuretics",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="Licorice can cause potassium loss and worsen hypokalemia",
                mechanism="Mineralocorticoid-like effects",
                evidence_quality=EvidenceQuality.HIGH,
            ),
            IngredientInteraction(
                ingredient_a="licorice",
                ingredient_b="blood pressure medications",
                interaction_type="herb-drug",
                severity=InteractionSeverity.MODERATE,
                description="Licorice can raise blood pressure and counteract medications",
                mechanism="Aldosterone-like effects",
                evidence_quality=EvidenceQuality.HIGH,
            ),
        ]

        # Convert to dict with sorted tuple keys
        db = {}
        for interaction in interactions:
            key = tuple(sorted([
                interaction.ingredient_a.lower(),
                interaction.ingredient_b.lower()
            ]))
            db[key] = interaction

        return db

    def _load_medication_classes(self) -> Dict[str, List[str]]:
        """
        Load medication class mappings

        Maps generic drug names to their classes for broader matching
        """
        return {
            "ssri": [
                "fluoxetine", "sertraline", "paroxetine", "citalopram",
                "escitalopram", "fluvoxamine", "prozac", "zoloft", "paxil",
                "lexapro", "celexa"
            ],
            "benzodiazepines": [
                "diazepam", "alprazolam", "lorazepam", "clonazepam",
                "temazepam", "valium", "xanax", "ativan", "klonopin"
            ],
            "blood thinners": [
                "warfarin", "heparin", "rivaroxaban", "apixaban",
                "dabigatran", "coumadin", "xarelto", "eliquis", "pradaxa"
            ],
            "antibiotics": [
                "ciprofloxacin", "levofloxacin", "doxycycline", "tetracycline",
                "amoxicillin", "azithromycin", "cipro", "levaquin"
            ],
            "blood pressure medications": [
                "lisinopril", "amlodipine", "losartan", "metoprolol",
                "atenolol", "hydrochlorothiazide", "norvasc", "lopressor"
            ],
            "thyroid medication": [
                "levothyroxine", "synthroid", "armour thyroid", "liothyronine",
                "cytomel", "levoxyl"
            ],
            "oral contraceptives": [
                "ethinyl estradiol", "norethindrone", "levonorgestrel",
                "birth control", "contraceptive pill"
            ],
            "immunosuppressants": [
                "cyclosporine", "tacrolimus", "mycophenolate", "azathioprine",
                "prednisone", "neoral", "prograf"
            ],
            "diuretics": [
                "furosemide", "hydrochlorothiazide", "spironolactone",
                "lasix", "hctz", "aldactone"
            ],
        }

    def _normalize_ingredient(self, ingredient: str) -> str:
        """Normalize ingredient name for matching"""
        normalized = ingredient.lower().strip()

        # Remove common suffixes
        suffixes = [" extract", " root", " leaf", " seed", " oil", " powder"]
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]

        return normalized

    def _get_medication_class(self, medication: str) -> Optional[str]:
        """Get the medication class for a drug"""
        med_lower = medication.lower()

        for med_class, members in self.medication_classes.items():
            if med_lower in members or any(med_lower in m for m in members):
                return med_class

        return None

    def check_interaction(
        self,
        ingredient_a: str,
        ingredient_b: str
    ) -> Optional[IngredientInteraction]:
        """
        Check for interaction between two ingredients

        Args:
            ingredient_a: First ingredient name
            ingredient_b: Second ingredient name

        Returns:
            IngredientInteraction if found, None otherwise
        """
        # Normalize names
        a = self._normalize_ingredient(ingredient_a)
        b = self._normalize_ingredient(ingredient_b)

        # Create sorted key
        key = tuple(sorted([a, b]))

        # Direct match
        if key in self.interactions_db:
            return self.interactions_db[key]

        # Check medication class matches
        class_a = self._get_medication_class(ingredient_a)
        class_b = self._get_medication_class(ingredient_b)

        if class_a:
            class_key = tuple(sorted([a, class_a]))
            if class_key in self.interactions_db:
                return self.interactions_db[class_key]

        if class_b:
            class_key = tuple(sorted([b, class_b]))
            if class_key in self.interactions_db:
                return self.interactions_db[class_key]

        if class_a and class_b:
            class_key = tuple(sorted([class_a, class_b]))
            if class_key in self.interactions_db:
                return self.interactions_db[class_key]

        return None

    def check_product_interactions(
        self,
        product: Product,
        medications: List[str] = None,
        other_supplements: List[str] = None
    ) -> List[InteractionWarning]:
        """
        Check all interactions for a product

        Args:
            product: Product to check
            medications: List of current medications
            other_supplements: List of other supplements being taken

        Returns:
            List of InteractionWarning objects
        """
        warnings = []
        medications = medications or []
        other_supplements = other_supplements or []

        # Get ingredient names from product
        product_ingredients = [
            ing.standardized_name or ing.name
            for ing in product.ingredients
        ]

        # Check interactions with medications
        for ingredient in product_ingredients:
            for medication in medications:
                interaction = self.check_interaction(ingredient, medication)
                if interaction:
                    warnings.append(self._create_warning(interaction, ingredient, medication))

        # Check interactions with other supplements
        for ingredient in product_ingredients:
            for supplement in other_supplements:
                interaction = self.check_interaction(ingredient, supplement)
                if interaction:
                    warnings.append(self._create_warning(interaction, ingredient, supplement))

        # Check interactions within the product's own ingredients
        for i, ing_a in enumerate(product_ingredients):
            for ing_b in product_ingredients[i + 1:]:
                interaction = self.check_interaction(ing_a, ing_b)
                if interaction:
                    warnings.append(self._create_warning(interaction, ing_a, ing_b))

        # Sort by severity (most severe first)
        severity_order = {
            InteractionSeverity.CONTRAINDICATED: 0,
            InteractionSeverity.SEVERE: 1,
            InteractionSeverity.MODERATE: 2,
            InteractionSeverity.MINOR: 3,
            InteractionSeverity.NONE: 4,
        }
        warnings.sort(key=lambda w: severity_order.get(w.severity, 5))

        return warnings

    def _create_warning(
        self,
        interaction: IngredientInteraction,
        item_a: str,
        item_b: str
    ) -> InteractionWarning:
        """Create an InteractionWarning from an IngredientInteraction"""
        recommendation = self._get_recommendation(interaction)

        return InteractionWarning(
            interacting_items=(item_a, item_b),
            severity=interaction.severity,
            description=interaction.description,
            recommendation=recommendation,
            evidence_quality=interaction.evidence_quality,
        )

    def _get_recommendation(self, interaction: IngredientInteraction) -> str:
        """Generate a recommendation based on interaction severity"""
        if interaction.severity == InteractionSeverity.CONTRAINDICATED:
            return "Do not use this combination. Consult your healthcare provider."
        elif interaction.severity == InteractionSeverity.SEVERE:
            return "Avoid this combination. If necessary, consult your healthcare provider for close monitoring."
        elif interaction.severity == InteractionSeverity.MODERATE:
            return "Use with caution. Consider spacing doses or consulting your healthcare provider."
        elif interaction.severity == InteractionSeverity.MINOR:
            return "Generally safe, but monitor for any unusual effects."
        else:
            return "No specific precautions needed."

    def get_all_interactions_for_ingredient(
        self,
        ingredient: str
    ) -> List[IngredientInteraction]:
        """
        Get all known interactions for a specific ingredient

        Args:
            ingredient: Ingredient name to look up

        Returns:
            List of all interactions involving this ingredient
        """
        normalized = self._normalize_ingredient(ingredient)
        interactions = []

        for key, interaction in self.interactions_db.items():
            if normalized in key:
                interactions.append(interaction)

        return interactions

    def get_severity_score(self, severity: InteractionSeverity) -> int:
        """Convert severity to numeric score for calculations"""
        return {
            InteractionSeverity.NONE: 0,
            InteractionSeverity.MINOR: 25,
            InteractionSeverity.MODERATE: 50,
            InteractionSeverity.SEVERE: 75,
            InteractionSeverity.CONTRAINDICATED: 100,
        }.get(severity, 0)
