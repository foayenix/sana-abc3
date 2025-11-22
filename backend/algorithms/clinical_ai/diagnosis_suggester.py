"""
Diagnosis Suggester
===================
AI-powered differential diagnosis suggestions based on symptoms and patient history.
"""

import logging
from typing import List, Dict, Optional
from uuid import uuid4

from .models import (
    DiagnosisSuggestionInput,
    DiagnosisSuggestionResult,
    DifferentialDiagnosis,
    DiagnosisConfidence,
    Symptom,
    ClinicalTradition,
)

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class DiagnosisSuggester:
    """
    Differential Diagnosis Suggester

    Analyzes symptoms and patient history to suggest possible diagnoses.
    Includes:
    - Differential diagnosis ranking
    - Red flag identification
    - Recommended tests
    - Referral suggestions
    """

    # Common condition patterns for fallback matching
    CONDITION_PATTERNS = {
        "anxiety": {
            "symptoms": ["worry", "nervousness", "restlessness", "racing heart",
                         "sleep problems", "difficulty concentrating", "irritability"],
            "icd_code": "F41.1",
            "red_flags": ["suicidal ideation", "panic attacks", "substance use"],
            "tests": ["Thyroid panel", "GAD-7 screening"],
        },
        "depression": {
            "symptoms": ["sadness", "hopelessness", "fatigue", "sleep changes",
                         "appetite changes", "difficulty concentrating", "low motivation"],
            "icd_code": "F32.9",
            "red_flags": ["suicidal ideation", "psychotic symptoms", "mania history"],
            "tests": ["PHQ-9 screening", "Thyroid panel", "Vitamin D"],
        },
        "ibs": {
            "symptoms": ["abdominal pain", "bloating", "constipation", "diarrhea",
                         "gas", "cramping", "changes in stool"],
            "icd_code": "K58.9",
            "red_flags": ["blood in stool", "unexplained weight loss", "family history of colon cancer"],
            "tests": ["CBC", "CRP", "Celiac panel", "Stool calprotectin"],
        },
        "chronic fatigue": {
            "symptoms": ["fatigue", "exhaustion", "brain fog", "post-exertional malaise",
                         "unrefreshing sleep", "muscle weakness"],
            "icd_code": "R53.83",
            "red_flags": ["progressive weakness", "significant weight loss", "fever"],
            "tests": ["CBC", "CMP", "Thyroid panel", "Iron studies", "Vitamin B12", "Vitamin D"],
        },
        "insomnia": {
            "symptoms": ["difficulty falling asleep", "difficulty staying asleep",
                         "early waking", "daytime fatigue", "irritability"],
            "icd_code": "G47.00",
            "red_flags": ["sleep apnea symptoms", "depression", "substance use"],
            "tests": ["Sleep study if indicated", "Thyroid panel"],
        },
        "tension headache": {
            "symptoms": ["headache", "head pressure", "neck tension", "stress",
                         "tight band around head"],
            "icd_code": "G44.209",
            "red_flags": ["sudden severe onset", "neurological symptoms", "fever", "vision changes"],
            "tests": ["Neurological exam", "Consider imaging if red flags"],
        },
        "migraine": {
            "symptoms": ["severe headache", "nausea", "light sensitivity", "sound sensitivity",
                         "aura", "throbbing pain", "one-sided headache"],
            "icd_code": "G43.909",
            "red_flags": ["sudden severe onset", "first migraine after 50", "neurological symptoms"],
            "tests": ["Neurological exam", "MRI if atypical features"],
        },
        "hypothyroidism": {
            "symptoms": ["fatigue", "weight gain", "cold intolerance", "constipation",
                         "dry skin", "hair loss", "depression", "brain fog"],
            "icd_code": "E03.9",
            "red_flags": ["rapid onset", "severe symptoms", "goiter"],
            "tests": ["TSH", "Free T4", "TPO antibodies"],
        },
        "adrenal fatigue": {
            "symptoms": ["fatigue", "stress intolerance", "salt craving", "low blood pressure",
                         "difficulty waking", "afternoon slump"],
            "icd_code": "E27.40",
            "red_flags": ["severe fatigue", "hyperpigmentation", "unexplained weight loss"],
            "tests": ["Morning cortisol", "DHEA-S", "4-point salivary cortisol"],
        },
        "menopause": {
            "symptoms": ["hot flashes", "night sweats", "mood changes", "sleep problems",
                         "vaginal dryness", "irregular periods"],
            "icd_code": "N95.1",
            "red_flags": ["vaginal bleeding after menopause", "severe depression"],
            "tests": ["FSH", "Estradiol", "Lipid panel"],
        },
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the diagnosis suggester"""
        self.api_key = api_key
        if OPENAI_AVAILABLE and api_key:
            openai.api_key = api_key

    def suggest_diagnoses(
        self,
        input_data: DiagnosisSuggestionInput
    ) -> DiagnosisSuggestionResult:
        """
        Generate differential diagnosis suggestions

        Args:
            input_data: Patient symptoms and history

        Returns:
            DiagnosisSuggestionResult with differential diagnoses
        """
        # Try AI-powered suggestion, fall back to pattern matching
        if OPENAI_AVAILABLE and self.api_key:
            return self._suggest_with_ai(input_data)
        else:
            return self._suggest_with_patterns(input_data)

    def _suggest_with_ai(self, input_data: DiagnosisSuggestionInput) -> DiagnosisSuggestionResult:
        """Generate diagnoses using OpenAI"""
        try:
            # Format symptoms
            symptoms_text = "\n".join([
                f"- {s.name}: severity {s.severity}/10, duration {s.duration or 'not specified'}"
                for s in input_data.symptoms
            ])

            prompt = f"""As a clinical decision support system, analyze these symptoms and suggest differential diagnoses.

Patient Information:
- Age: {input_data.patient_age or 'Not specified'}
- Sex: {input_data.patient_sex or 'Not specified'}

Symptoms:
{symptoms_text}

Medical History: {', '.join(input_data.medical_history) or 'None reported'}
Family History: {', '.join(input_data.family_history) or 'None reported'}
Current Medications: {', '.join(input_data.current_medications) or 'None'}

Provide:
1. Top 5 differential diagnoses ranked by likelihood
2. For each: ICD-10 code, confidence level, supporting symptoms, contradicting symptoms
3. Red flags to watch for
4. Recommended diagnostic tests
5. Any referrals that may be warranted

Format each diagnosis as:
DIAGNOSIS: [Name]
ICD-10: [Code]
CONFIDENCE: [High/Moderate/Low]
SUPPORTING: [symptoms that support this]
AGAINST: [symptoms that argue against]
RED FLAGS: [specific red flags]
TESTS: [recommended tests]"""

            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a clinical decision support AI. Always include appropriate disclaimers and encourage professional consultation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000,
            )

            return self._parse_ai_response(response.choices[0].message.content, input_data)

        except Exception as e:
            logger.error(f"AI diagnosis suggestion failed: {e}")
            return self._suggest_with_patterns(input_data)

    def _suggest_with_patterns(self, input_data: DiagnosisSuggestionInput) -> DiagnosisSuggestionResult:
        """Generate diagnoses using pattern matching (fallback)"""
        # Extract symptom names
        symptom_names = [s.name.lower() for s in input_data.symptoms]

        # Score each condition
        scored_conditions = []
        for condition_name, pattern in self.CONDITION_PATTERNS.items():
            # Count matching symptoms
            matching = sum(
                1 for symptom in symptom_names
                for pattern_symptom in pattern["symptoms"]
                if pattern_symptom in symptom or symptom in pattern_symptom
            )

            if matching > 0:
                score = matching / len(pattern["symptoms"])
                scored_conditions.append((condition_name, pattern, score, matching))

        # Sort by score
        scored_conditions.sort(key=lambda x: x[2], reverse=True)

        # Create differential diagnoses
        differentials = []
        for condition_name, pattern, score, matching in scored_conditions[:5]:
            # Determine confidence
            if score >= 0.5:
                confidence = DiagnosisConfidence.HIGH
            elif score >= 0.3:
                confidence = DiagnosisConfidence.MODERATE
            else:
                confidence = DiagnosisConfidence.LOW

            # Find supporting symptoms
            supporting = [
                s.name for s in input_data.symptoms
                if any(ps in s.name.lower() or s.name.lower() in ps
                       for ps in pattern["symptoms"])
            ]

            differentials.append(DifferentialDiagnosis(
                condition=condition_name.replace("_", " ").title(),
                icd_code=pattern.get("icd_code"),
                confidence=confidence,
                confidence_score=score,
                supporting_symptoms=supporting,
                red_flags=pattern.get("red_flags", []),
                recommended_tests=pattern.get("tests", []),
            ))

        # Collect all red flags
        all_red_flags = []
        for _, pattern, _, _ in scored_conditions[:5]:
            all_red_flags.extend(pattern.get("red_flags", []))

        return DiagnosisSuggestionResult(
            differential_diagnoses=differentials,
            primary_impression=differentials[0].condition if differentials else None,
            red_flags=list(set(all_red_flags)),
            disclaimer="AI-assisted suggestions require clinical validation. This is not a diagnosis.",
        )

    def _parse_ai_response(
        self,
        response_text: str,
        input_data: DiagnosisSuggestionInput
    ) -> DiagnosisSuggestionResult:
        """Parse AI response into structured result"""
        import re

        differentials = []
        red_flags = []

        # Parse each diagnosis block
        diagnosis_blocks = re.split(r'DIAGNOSIS:', response_text, flags=re.IGNORECASE)

        for block in diagnosis_blocks[1:]:  # Skip first empty block
            try:
                # Extract diagnosis name
                name_match = re.search(r'^([^\n]+)', block.strip())
                name = name_match.group(1).strip() if name_match else "Unknown"

                # Extract ICD code
                icd_match = re.search(r'ICD-?10:?\s*([A-Z]\d+\.?\d*)', block, re.IGNORECASE)
                icd_code = icd_match.group(1) if icd_match else None

                # Extract confidence
                conf_match = re.search(r'CONFIDENCE:?\s*(High|Moderate|Low)', block, re.IGNORECASE)
                if conf_match:
                    conf_str = conf_match.group(1).lower()
                    confidence = {
                        "high": DiagnosisConfidence.HIGH,
                        "moderate": DiagnosisConfidence.MODERATE,
                        "low": DiagnosisConfidence.LOW,
                    }.get(conf_str, DiagnosisConfidence.UNCERTAIN)
                    conf_score = {"high": 0.8, "moderate": 0.5, "low": 0.3}.get(conf_str, 0.2)
                else:
                    confidence = DiagnosisConfidence.UNCERTAIN
                    conf_score = 0.2

                # Extract supporting symptoms
                support_match = re.search(r'SUPPORTING:?\s*([^\n]+)', block, re.IGNORECASE)
                supporting = [s.strip() for s in support_match.group(1).split(',')] if support_match else []

                # Extract symptoms against
                against_match = re.search(r'AGAINST:?\s*([^\n]+)', block, re.IGNORECASE)
                against = [s.strip() for s in against_match.group(1).split(',')] if against_match else []

                # Extract red flags for this diagnosis
                flags_match = re.search(r'RED FLAGS:?\s*([^\n]+)', block, re.IGNORECASE)
                diag_flags = [f.strip() for f in flags_match.group(1).split(',')] if flags_match else []
                red_flags.extend(diag_flags)

                # Extract tests
                tests_match = re.search(r'TESTS:?\s*([^\n]+)', block, re.IGNORECASE)
                tests = [t.strip() for t in tests_match.group(1).split(',')] if tests_match else []

                differentials.append(DifferentialDiagnosis(
                    condition=name,
                    icd_code=icd_code,
                    confidence=confidence,
                    confidence_score=conf_score,
                    supporting_symptoms=supporting,
                    against_symptoms=against,
                    red_flags=diag_flags,
                    recommended_tests=tests,
                ))

            except Exception as e:
                logger.warning(f"Failed to parse diagnosis block: {e}")
                continue

        # Determine primary impression
        primary = differentials[0].condition if differentials else None

        return DiagnosisSuggestionResult(
            differential_diagnoses=differentials,
            primary_impression=primary,
            red_flags=list(set(red_flags)),
            disclaimer="AI-assisted suggestions require clinical validation. This is not a diagnosis.",
        )

    def check_red_flags(self, symptoms: List[Symptom]) -> List[str]:
        """
        Check for immediate red flags in symptoms

        Args:
            symptoms: List of symptoms

        Returns:
            List of identified red flags
        """
        red_flags = []
        symptom_text = " ".join([s.name.lower() for s in symptoms])

        # Critical red flags
        critical_patterns = [
            ("chest pain", "Possible cardiac emergency - urgent evaluation needed"),
            ("difficulty breathing", "Possible respiratory emergency"),
            ("severe headache", "Sudden severe headache requires immediate evaluation"),
            ("suicidal", "Mental health crisis - immediate intervention needed"),
            ("blood in stool", "GI bleeding - requires prompt evaluation"),
            ("unexplained weight loss", "May indicate serious underlying condition"),
            ("fever with stiff neck", "Possible meningitis - urgent evaluation"),
            ("vision loss", "Sudden vision changes require immediate evaluation"),
            ("weakness on one side", "Possible stroke - emergency evaluation"),
            ("confusion", "Altered mental status requires prompt assessment"),
        ]

        for pattern, warning in critical_patterns:
            if pattern in symptom_text:
                red_flags.append(warning)

        return red_flags
