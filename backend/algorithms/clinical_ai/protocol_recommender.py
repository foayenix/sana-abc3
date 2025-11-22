"""
Protocol Recommender
====================
AI-powered treatment protocol recommendations for various conditions.
"""

import logging
from typing import Optional, List, Dict
from uuid import uuid4

from .models import (
    ProtocolRecommendationInput,
    TreatmentProtocol,
    HerbRecommendation,
    SupplementRecommendation,
    LifestyleRecommendation,
    ClinicalTradition,
)

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ProtocolRecommender:
    """
    Treatment Protocol Recommender

    Generates evidence-informed treatment protocols based on:
    - Condition/diagnosis
    - Clinical tradition (Western herbalism, TCM, Ayurveda, etc.)
    - Patient-specific factors (age, contraindications)
    - Current medications (to avoid interactions)
    """

    # Condition-specific protocols (fallback database)
    PROTOCOL_DATABASE = {
        "anxiety": {
            ClinicalTradition.WESTERN_HERBALISM: {
                "herbs": [
                    {"name": "Ashwagandha", "botanical": "Withania somnifera",
                     "dosage": "300-600mg", "form": "standardized extract",
                     "frequency": "twice daily", "rationale": "Adaptogen, reduces cortisol"},
                    {"name": "Passionflower", "botanical": "Passiflora incarnata",
                     "dosage": "500mg or 45 drops tincture", "form": "capsule or tincture",
                     "frequency": "2-3x daily", "rationale": "GABAergic, calming"},
                    {"name": "Lemon Balm", "botanical": "Melissa officinalis",
                     "dosage": "300-600mg", "form": "capsule or tea",
                     "frequency": "as needed", "rationale": "Nervine, mild sedative"},
                ],
                "supplements": [
                    {"name": "Magnesium Glycinate", "dosage": "300-400mg",
                     "rationale": "Supports nervous system, often deficient"},
                    {"name": "L-Theanine", "dosage": "200mg",
                     "rationale": "Promotes calm focus without sedation"},
                ],
                "lifestyle": [
                    {"category": "breathing", "recommendation": "Practice 4-7-8 breathing 2x daily"},
                    {"category": "exercise", "recommendation": "30 min moderate exercise 5x/week"},
                    {"category": "sleep", "recommendation": "Consistent sleep schedule, no screens 1hr before bed"},
                ],
            },
            ClinicalTradition.TRADITIONAL_CHINESE_MEDICINE: {
                "pattern": "Liver Qi Stagnation with Heart Blood Deficiency",
                "formula": "Xiao Yao San (Free and Easy Wanderer) modified",
                "herbs": [
                    {"name": "Chai Hu (Bupleurum)", "dosage": "6-9g", "form": "decoction",
                     "rationale": "Spreads Liver Qi"},
                    {"name": "Bai Shao (White Peony)", "dosage": "9-15g", "form": "decoction",
                     "rationale": "Nourishes Blood, softens Liver"},
                    {"name": "Suan Zao Ren (Ziziphus)", "dosage": "9-15g", "form": "decoction",
                     "rationale": "Calms Shen, nourishes Heart"},
                ],
            },
        },
        "insomnia": {
            ClinicalTradition.WESTERN_HERBALISM: {
                "herbs": [
                    {"name": "Valerian", "botanical": "Valeriana officinalis",
                     "dosage": "300-600mg or 2-3ml tincture", "form": "capsule or tincture",
                     "frequency": "30-60 min before bed", "rationale": "GABAergic, sleep promoting"},
                    {"name": "Passionflower", "botanical": "Passiflora incarnata",
                     "dosage": "500mg", "form": "capsule",
                     "frequency": "before bed", "rationale": "Calming, reduces sleep latency"},
                    {"name": "California Poppy", "botanical": "Eschscholzia californica",
                     "dosage": "30-40 drops tincture", "form": "tincture",
                     "frequency": "before bed", "rationale": "Mild sedative, safe"},
                ],
                "supplements": [
                    {"name": "Magnesium Glycinate", "dosage": "300-400mg before bed",
                     "rationale": "Promotes relaxation, supports GABA"},
                    {"name": "Melatonin", "dosage": "0.5-3mg",
                     "rationale": "For circadian rhythm support (start low)"},
                ],
                "lifestyle": [
                    {"category": "sleep hygiene", "recommendation": "Cool, dark room; consistent schedule"},
                    {"category": "diet", "recommendation": "No caffeine after 2pm; light evening meal"},
                    {"category": "routine", "recommendation": "Relaxing pre-bed routine starting 1hr before"},
                ],
            },
        },
        "digestion": {
            ClinicalTradition.WESTERN_HERBALISM: {
                "herbs": [
                    {"name": "Ginger", "botanical": "Zingiber officinale",
                     "dosage": "500mg or fresh in tea", "form": "capsule or tea",
                     "frequency": "with meals", "rationale": "Carminative, promotes digestion"},
                    {"name": "Peppermint", "botanical": "Mentha piperita",
                     "dosage": "tea or 0.2ml enteric-coated oil", "form": "tea or capsule",
                     "frequency": "after meals", "rationale": "Antispasmodic, carminative"},
                    {"name": "Chamomile", "botanical": "Matricaria chamomilla",
                     "dosage": "1-2 cups tea", "form": "tea",
                     "frequency": "after meals", "rationale": "Anti-inflammatory, calming to GI"},
                ],
                "supplements": [
                    {"name": "Digestive Enzymes", "dosage": "1 capsule with meals",
                     "rationale": "Supports breakdown of food"},
                    {"name": "Probiotics", "dosage": "10-50 billion CFU daily",
                     "rationale": "Supports gut microbiome"},
                ],
                "lifestyle": [
                    {"category": "eating", "recommendation": "Eat slowly, chew thoroughly"},
                    {"category": "meal timing", "recommendation": "Regular meal times; avoid late eating"},
                    {"category": "stress", "recommendation": "Avoid eating when stressed"},
                ],
            },
        },
        "inflammation": {
            ClinicalTradition.WESTERN_HERBALISM: {
                "herbs": [
                    {"name": "Turmeric", "botanical": "Curcuma longa",
                     "dosage": "500-1000mg curcuminoids", "form": "standardized extract with piperine",
                     "frequency": "twice daily with food", "rationale": "Potent anti-inflammatory"},
                    {"name": "Boswellia", "botanical": "Boswellia serrata",
                     "dosage": "300-500mg", "form": "standardized extract",
                     "frequency": "twice daily", "rationale": "5-LOX inhibitor, joint support"},
                    {"name": "Ginger", "botanical": "Zingiber officinale",
                     "dosage": "500-1000mg", "form": "extract",
                     "frequency": "daily", "rationale": "COX inhibitor, antioxidant"},
                ],
                "supplements": [
                    {"name": "Omega-3 Fish Oil", "dosage": "2-3g EPA+DHA",
                     "rationale": "Anti-inflammatory, supports resolution"},
                    {"name": "Vitamin D3", "dosage": "2000-4000 IU",
                     "rationale": "Immune modulation, often deficient"},
                ],
                "lifestyle": [
                    {"category": "diet", "recommendation": "Anti-inflammatory diet; reduce sugar, processed foods"},
                    {"category": "exercise", "recommendation": "Regular low-impact exercise"},
                    {"category": "sleep", "recommendation": "Prioritize 7-9 hours quality sleep"},
                ],
            },
        },
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the protocol recommender"""
        self.api_key = api_key
        if OPENAI_AVAILABLE and api_key:
            openai.api_key = api_key

    def recommend_protocol(
        self,
        input_data: ProtocolRecommendationInput
    ) -> TreatmentProtocol:
        """
        Generate treatment protocol recommendation

        Args:
            input_data: Condition, tradition, and patient factors

        Returns:
            TreatmentProtocol with recommendations
        """
        # Try AI generation, fall back to database
        if OPENAI_AVAILABLE and self.api_key:
            return self._recommend_with_ai(input_data)
        else:
            return self._recommend_from_database(input_data)

    def _recommend_from_database(
        self,
        input_data: ProtocolRecommendationInput
    ) -> TreatmentProtocol:
        """Generate protocol from database (fallback)"""
        condition_lower = input_data.condition.lower()

        # Find matching condition
        matching_condition = None
        for cond_name in self.PROTOCOL_DATABASE:
            if cond_name in condition_lower or condition_lower in cond_name:
                matching_condition = cond_name
                break

        if not matching_condition:
            return self._create_generic_protocol(input_data)

        # Get protocol for tradition
        condition_protocols = self.PROTOCOL_DATABASE[matching_condition]
        tradition = input_data.tradition

        if tradition not in condition_protocols:
            tradition = ClinicalTradition.WESTERN_HERBALISM

        protocol_data = condition_protocols.get(
            tradition,
            condition_protocols.get(ClinicalTradition.WESTERN_HERBALISM, {})
        )

        # Build herb recommendations
        herbs = []
        for herb_data in protocol_data.get("herbs", []):
            # Check contraindications
            if not self._is_contraindicated(herb_data["name"], input_data):
                herbs.append(HerbRecommendation(
                    herb_name=herb_data["name"],
                    botanical_name=herb_data.get("botanical"),
                    dosage=herb_data["dosage"],
                    form=herb_data.get("form", "as directed"),
                    frequency=herb_data.get("frequency", "as directed"),
                    duration="4-8 weeks, then reassess",
                    rationale=herb_data.get("rationale", ""),
                ))

        # Build supplement recommendations
        supplements = []
        for supp_data in protocol_data.get("supplements", []):
            if not self._is_contraindicated(supp_data["name"], input_data):
                supplements.append(SupplementRecommendation(
                    name=supp_data["name"],
                    dosage=supp_data["dosage"],
                    form="as specified",
                    frequency="daily",
                    duration="ongoing",
                    rationale=supp_data.get("rationale", ""),
                ))

        # Build lifestyle recommendations
        lifestyle = []
        for life_data in protocol_data.get("lifestyle", []):
            lifestyle.append(LifestyleRecommendation(
                category=life_data["category"],
                recommendation=life_data["recommendation"],
                rationale="Supports treatment goals",
                priority="medium",
            ))

        return TreatmentProtocol(
            condition=input_data.condition,
            tradition=input_data.tradition,
            herbs=herbs,
            supplements=supplements,
            lifestyle=lifestyle,
            traditional_pattern=protocol_data.get("pattern"),
            classical_formula=protocol_data.get("formula"),
            expected_timeline="4-8 weeks for initial response",
            follow_up_recommendations=["Reassess in 4 weeks", "Monitor symptoms"],
            disclaimer="These recommendations require professional oversight.",
        )

    def _recommend_with_ai(
        self,
        input_data: ProtocolRecommendationInput
    ) -> TreatmentProtocol:
        """Generate protocol using AI"""
        try:
            tradition_name = input_data.tradition.value.replace("_", " ").title()

            prompt = f"""As a {tradition_name} practitioner, recommend a treatment protocol for:

Condition: {input_data.condition}
Patient Age: {input_data.patient_age or 'Adult'}
Patient Sex: {input_data.patient_sex or 'Not specified'}
Severity: {input_data.severity}

Contraindications/Allergies: {', '.join(input_data.contraindications) or 'None reported'}
Current Medications: {', '.join(input_data.current_medications) or 'None'}

Provide:
1. 3-5 HERBS with: name, botanical name, dosage, form, frequency, rationale
2. 2-3 SUPPLEMENTS with: name, dosage, rationale
3. 3-4 LIFESTYLE recommendations with: category, specific recommendation

Also include:
- Traditional pattern/diagnosis (if applicable to tradition)
- Expected timeline for improvement
- Follow-up recommendations

Format as structured sections for parsing."""

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are an expert {tradition_name} practitioner providing evidence-informed treatment recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            return self._parse_ai_protocol(response.choices[0].message.content, input_data)

        except Exception as e:
            logger.error(f"AI protocol generation failed: {e}")
            return self._recommend_from_database(input_data)

    def _parse_ai_protocol(
        self,
        response_text: str,
        input_data: ProtocolRecommendationInput
    ) -> TreatmentProtocol:
        """Parse AI response into structured protocol"""
        import re

        herbs = []
        supplements = []
        lifestyle = []

        # Parse herbs section
        herb_section = re.search(r'HERBS?:?(.*?)(?=SUPPLEMENTS?|LIFESTYLE|$)', response_text, re.IGNORECASE | re.DOTALL)
        if herb_section:
            herb_lines = herb_section.group(1).strip().split('\n')
            for line in herb_lines:
                if line.strip() and not line.strip().startswith('#'):
                    # Try to extract herb info
                    name_match = re.search(r'([A-Za-z\s]+)(?:\(([^)]+)\))?', line)
                    if name_match:
                        herbs.append(HerbRecommendation(
                            herb_name=name_match.group(1).strip(),
                            botanical_name=name_match.group(2) if name_match.group(2) else None,
                            dosage="As recommended",
                            form="As appropriate",
                            frequency="As directed",
                            duration="4-8 weeks",
                            rationale="See full recommendation",
                        ))

        # Parse supplements section
        supp_section = re.search(r'SUPPLEMENTS?:?(.*?)(?=LIFESTYLE|HERBS?|$)', response_text, re.IGNORECASE | re.DOTALL)
        if supp_section:
            supp_lines = supp_section.group(1).strip().split('\n')
            for line in supp_lines:
                if line.strip() and not line.strip().startswith('#'):
                    name_match = re.search(r'([A-Za-z0-9\s-]+)', line)
                    if name_match:
                        supplements.append(SupplementRecommendation(
                            name=name_match.group(1).strip(),
                            dosage="As recommended",
                            form="As appropriate",
                            frequency="Daily",
                            duration="Ongoing",
                            rationale="See full recommendation",
                        ))

        # Parse lifestyle section
        life_section = re.search(r'LIFESTYLE:?(.*?)(?=HERBS?|SUPPLEMENTS?|$)', response_text, re.IGNORECASE | re.DOTALL)
        if life_section:
            life_lines = life_section.group(1).strip().split('\n')
            for line in life_lines:
                if line.strip() and not line.strip().startswith('#'):
                    lifestyle.append(LifestyleRecommendation(
                        category="general",
                        recommendation=line.strip(),
                        rationale="Supports treatment goals",
                    ))

        return TreatmentProtocol(
            condition=input_data.condition,
            tradition=input_data.tradition,
            herbs=herbs if herbs else self._get_default_herbs(input_data),
            supplements=supplements,
            lifestyle=lifestyle,
            expected_timeline="4-8 weeks",
            disclaimer="AI-generated recommendations require professional review.",
        )

    def _is_contraindicated(
        self,
        herb_name: str,
        input_data: ProtocolRecommendationInput
    ) -> bool:
        """Check if an herb is contraindicated for this patient"""
        herb_lower = herb_name.lower()

        # Check explicit contraindications
        for contra in input_data.contraindications:
            if contra.lower() in herb_lower or herb_lower in contra.lower():
                return True

        # Check common medication interactions
        interaction_herbs = {
            "st. john's wort": ["ssri", "warfarin", "birth control"],
            "ginkgo": ["warfarin", "aspirin", "blood thinner"],
            "valerian": ["benzodiazepine", "ambien", "sedative"],
            "kava": ["liver", "alcohol"],
        }

        if herb_lower in interaction_herbs:
            for med in input_data.current_medications:
                med_lower = med.lower()
                for interact in interaction_herbs[herb_lower]:
                    if interact in med_lower:
                        return True

        return False

    def _create_generic_protocol(
        self,
        input_data: ProtocolRecommendationInput
    ) -> TreatmentProtocol:
        """Create a generic protocol when no specific match found"""
        return TreatmentProtocol(
            condition=input_data.condition,
            tradition=input_data.tradition,
            herbs=[],
            supplements=[],
            lifestyle=[
                LifestyleRecommendation(
                    category="general",
                    recommendation="Maintain a balanced diet rich in whole foods",
                    rationale="Foundation of health",
                ),
                LifestyleRecommendation(
                    category="exercise",
                    recommendation="Regular moderate physical activity",
                    rationale="Supports overall wellbeing",
                ),
                LifestyleRecommendation(
                    category="stress",
                    recommendation="Practice stress management techniques",
                    rationale="Stress impacts all conditions",
                ),
            ],
            expected_timeline="Varies by condition",
            follow_up_recommendations=["Consult with a qualified practitioner for specific recommendations"],
            disclaimer="No specific protocol available. Seek professional consultation.",
        )

    def _get_default_herbs(
        self,
        input_data: ProtocolRecommendationInput
    ) -> List[HerbRecommendation]:
        """Get default herbs when parsing fails"""
        return []
