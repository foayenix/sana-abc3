"""
SOAP Note Generator
===================
AI-powered SOAP note generation from clinical observations and voice notes.
"""

import logging
import re
from typing import Optional, List, Dict, Any
from uuid import UUID

from .models import (
    SOAPNoteInput,
    SOAPNote,
    ClinicalTradition,
)

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. SOAP generation will use templates.")


class SOAPGenerator:
    """
    SOAP Note Generator

    Generates structured SOAP notes from:
    - Voice transcriptions
    - Free-text clinical notes
    - Structured symptom data

    Uses GPT-4 for intelligent extraction and formatting.
    """

    # System prompts for different traditions
    SYSTEM_PROMPTS = {
        ClinicalTradition.WESTERN_HERBALISM: """You are an experienced clinical herbalist writing SOAP notes.
Focus on constitutional assessment, herbal actions, and evidence-based herbal recommendations.
Use appropriate herbal terminology and reference materia medica when relevant.""",

        ClinicalTradition.TRADITIONAL_CHINESE_MEDICINE: """You are an experienced TCM practitioner writing SOAP notes.
Include pattern differentiation, tongue/pulse findings, and appropriate TCM terminology.
Reference classical formulas and modifications when relevant.""",

        ClinicalTradition.AYURVEDA: """You are an experienced Ayurvedic practitioner writing SOAP notes.
Include dosha assessment, agni evaluation, and appropriate Sanskrit terminology.
Reference classical texts and formulations when relevant.""",

        ClinicalTradition.NATUROPATHY: """You are an experienced naturopathic doctor writing SOAP notes.
Apply the therapeutic order and focus on removing obstacles to cure.
Include nutritional, botanical, and lifestyle recommendations.""",

        ClinicalTradition.FUNCTIONAL_MEDICINE: """You are an experienced functional medicine practitioner writing SOAP notes.
Focus on root cause analysis, systems biology, and biomarker interpretation.
Include evidence-based supplement and lifestyle interventions.""",

        ClinicalTradition.GENERAL: """You are an experienced integrative health practitioner writing SOAP notes.
Provide comprehensive, evidence-informed clinical documentation.
Balance traditional wisdom with modern clinical standards.""",
    }

    SOAP_TEMPLATE = """Based on the following clinical information, generate a comprehensive SOAP note.

## Patient Information:
{patient_info}

## Clinical Notes:
{clinical_notes}

## Current Medications/Supplements:
{medications}

## Generate a SOAP note with the following sections:

### SUBJECTIVE (S):
- Chief complaint
- History of present illness
- Review of relevant symptoms
- Patient's perspective and concerns

### OBJECTIVE (O):
- Vital signs (if available)
- Physical examination findings
- Laboratory results (if available)
- Relevant observations

### ASSESSMENT (A):
- Clinical impressions
- Differential considerations
- Contributing factors

### PLAN (P):
- Treatment recommendations (herbs, supplements, lifestyle)
- Specific dosages and protocols
- Follow-up timeline
- Patient education points

Also extract and list:
- Primary diagnoses/conditions
- Recommended herbs (with dosages)
- Recommended supplements (with dosages)
- Key lifestyle recommendations
- Follow-up interval

Format the output as a professional clinical note."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the SOAP generator

        Args:
            api_key: OpenAI API key (optional, uses env var if not provided)
        """
        self.api_key = api_key
        if OPENAI_AVAILABLE and api_key:
            openai.api_key = api_key

    def generate_soap_note(self, input_data: SOAPNoteInput) -> SOAPNote:
        """
        Generate a SOAP note from input data

        Args:
            input_data: SOAPNoteInput with clinical information

        Returns:
            Generated SOAPNote
        """
        # Combine all input text
        combined_notes = self._prepare_clinical_notes(input_data)

        if not combined_notes:
            raise ValueError("No clinical notes provided for SOAP generation")

        # Try AI generation, fall back to template
        if OPENAI_AVAILABLE and self.api_key:
            return self._generate_with_ai(input_data, combined_notes)
        else:
            return self._generate_with_template(input_data, combined_notes)

    def _prepare_clinical_notes(self, input_data: SOAPNoteInput) -> str:
        """Prepare clinical notes from various input sources"""
        notes_parts = []

        # Voice transcription
        if input_data.voice_transcription:
            notes_parts.append(f"Voice Note Transcription:\n{input_data.voice_transcription}")

        # Free text notes
        if input_data.free_text_notes:
            notes_parts.append(f"Clinical Notes:\n{input_data.free_text_notes}")

        # Chief complaint
        if input_data.chief_complaint:
            notes_parts.append(f"Chief Complaint: {input_data.chief_complaint}")

        # Symptoms
        if input_data.symptoms:
            symptoms_text = ", ".join(input_data.symptoms)
            duration = f" (Duration: {input_data.symptom_duration})" if input_data.symptom_duration else ""
            severity = f" (Severity: {input_data.symptom_severity}/10)" if input_data.symptom_severity else ""
            notes_parts.append(f"Symptoms: {symptoms_text}{duration}{severity}")

        # Patient history
        if input_data.patient_history:
            notes_parts.append(f"Medical History:\n{input_data.patient_history}")

        # Vitals
        if input_data.vitals:
            vitals_text = ", ".join(f"{k}: {v}" for k, v in input_data.vitals.items())
            notes_parts.append(f"Vitals: {vitals_text}")

        # Physical exam
        if input_data.physical_exam_notes:
            notes_parts.append(f"Physical Exam:\n{input_data.physical_exam_notes}")

        # Lab results
        if input_data.lab_results:
            labs_text = "\n".join(f"  {k}: {v}" for k, v in input_data.lab_results.items())
            notes_parts.append(f"Lab Results:\n{labs_text}")

        return "\n\n".join(notes_parts)

    def _generate_with_ai(self, input_data: SOAPNoteInput, clinical_notes: str) -> SOAPNote:
        """Generate SOAP note using OpenAI GPT-4"""
        try:
            # Prepare patient info
            patient_info = self._format_patient_info(input_data)

            # Format medications
            medications = self._format_medications(input_data)

            # Get tradition-specific system prompt
            system_prompt = self.SYSTEM_PROMPTS.get(
                input_data.tradition,
                self.SYSTEM_PROMPTS[ClinicalTradition.GENERAL]
            )

            # Format user prompt
            user_prompt = self.SOAP_TEMPLATE.format(
                patient_info=patient_info,
                clinical_notes=clinical_notes,
                medications=medications,
            )

            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=3000,
            )

            # Parse response
            generated_text = response.choices[0].message.content
            return self._parse_ai_response(generated_text, input_data)

        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return self._generate_with_template(input_data, clinical_notes)

    def _generate_with_template(self, input_data: SOAPNoteInput, clinical_notes: str) -> SOAPNote:
        """Generate SOAP note using template-based approach (fallback)"""
        # Extract key information
        chief_complaint = input_data.chief_complaint or "Not specified"
        symptoms = ", ".join(input_data.symptoms) if input_data.symptoms else "See notes"

        # Generate subjective
        subjective = f"""Chief Complaint: {chief_complaint}

History of Present Illness:
{clinical_notes}

Current Medications: {', '.join(input_data.current_medications) or 'None reported'}
Current Supplements: {', '.join(input_data.current_supplements) or 'None reported'}"""

        # Generate objective
        objective_parts = []
        if input_data.vitals:
            vitals_text = "\n".join(f"  {k}: {v}" for k, v in input_data.vitals.items())
            objective_parts.append(f"Vital Signs:\n{vitals_text}")
        if input_data.physical_exam_notes:
            objective_parts.append(f"Physical Exam:\n{input_data.physical_exam_notes}")
        if input_data.lab_results:
            labs_text = "\n".join(f"  {k}: {v}" for k, v in input_data.lab_results.items())
            objective_parts.append(f"Lab Results:\n{labs_text}")

        objective = "\n\n".join(objective_parts) if objective_parts else "See clinical notes for observations."

        # Generate assessment
        assessment = f"""Clinical Impression: {chief_complaint}
Associated Symptoms: {symptoms}

Note: AI-assisted assessment pending review. Please add clinical impressions."""

        # Generate plan
        plan = """Treatment Plan (to be completed):
1. Herbal/Supplement Recommendations: [Add recommendations]
2. Lifestyle Modifications: [Add recommendations]
3. Follow-up: [Specify timeline]
4. Patient Education: [Add key points]"""

        return SOAPNote(
            session_id=input_data.session_id,
            subjective=subjective,
            objective=objective,
            assessment=assessment,
            plan=plan,
            tradition=input_data.tradition,
            confidence_score=0.5,  # Lower confidence for template
            ai_model_used="template",
            source_free_text=clinical_notes,
        )

    def _parse_ai_response(self, response_text: str, input_data: SOAPNoteInput) -> SOAPNote:
        """Parse AI-generated response into structured SOAP note"""
        # Initialize sections
        subjective = ""
        objective = ""
        assessment = ""
        plan = ""

        # Extract sections using regex
        sections = {
            "subjective": r"(?:SUBJECTIVE|S:?|###\s*SUBJECTIVE)[:\s]*\n?(.*?)(?=(?:OBJECTIVE|O:|###\s*OBJECTIVE|\Z))",
            "objective": r"(?:OBJECTIVE|O:?|###\s*OBJECTIVE)[:\s]*\n?(.*?)(?=(?:ASSESSMENT|A:|###\s*ASSESSMENT|\Z))",
            "assessment": r"(?:ASSESSMENT|A:?|###\s*ASSESSMENT)[:\s]*\n?(.*?)(?=(?:PLAN|P:|###\s*PLAN|\Z))",
            "plan": r"(?:PLAN|P:?|###\s*PLAN)[:\s]*\n?(.*?)(?=(?:###|\Z|diagnos|recommend))",
        }

        for section_name, pattern in sections.items():
            match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                if section_name == "subjective":
                    subjective = content
                elif section_name == "objective":
                    objective = content
                elif section_name == "assessment":
                    assessment = content
                elif section_name == "plan":
                    plan = content

        # Extract diagnoses
        diagnoses = self._extract_list(response_text, r"diagnos(?:es|is)[:\s]*(.*?)(?:\n\n|\Z)")

        # Extract herbs
        herbs = self._extract_list(response_text, r"(?:recommended\s+)?herbs?[:\s]*(.*?)(?:\n\n|\Z)")

        # Extract supplements
        supplements = self._extract_list(response_text, r"(?:recommended\s+)?supplements?[:\s]*(.*?)(?:\n\n|\Z)")

        # Extract lifestyle recommendations
        lifestyle = self._extract_list(response_text, r"lifestyle[:\s]*(.*?)(?:\n\n|\Z)")

        return SOAPNote(
            session_id=input_data.session_id,
            subjective=subjective or "See clinical notes.",
            objective=objective or "No objective findings documented.",
            assessment=assessment or "Clinical assessment pending.",
            plan=plan or "Treatment plan to be determined.",
            diagnoses=diagnoses,
            recommended_herbs=herbs,
            recommended_supplements=supplements,
            lifestyle_recommendations=lifestyle,
            tradition=input_data.tradition,
            confidence_score=0.85,
            ai_model_used="gpt-4",
            source_voice_transcription=input_data.voice_transcription,
            source_free_text=input_data.free_text_notes,
        )

    def _extract_list(self, text: str, pattern: str) -> List[str]:
        """Extract a list of items from text using regex"""
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            items_text = match.group(1)
            # Split by newlines, bullets, or commas
            items = re.split(r'\n[-•*]|\n\d+\.|\n|,\s*', items_text)
            return [item.strip() for item in items if item.strip()]
        return []

    def _format_patient_info(self, input_data: SOAPNoteInput) -> str:
        """Format patient information for prompt"""
        parts = []
        if input_data.chief_complaint:
            parts.append(f"Chief Complaint: {input_data.chief_complaint}")
        if input_data.symptoms:
            parts.append(f"Symptoms: {', '.join(input_data.symptoms)}")
        if input_data.symptom_duration:
            parts.append(f"Duration: {input_data.symptom_duration}")
        if input_data.symptom_severity:
            parts.append(f"Severity: {input_data.symptom_severity}/10")
        return "\n".join(parts) if parts else "See clinical notes"

    def _format_medications(self, input_data: SOAPNoteInput) -> str:
        """Format current medications and supplements"""
        parts = []
        if input_data.current_medications:
            parts.append(f"Medications: {', '.join(input_data.current_medications)}")
        if input_data.current_supplements:
            parts.append(f"Supplements: {', '.join(input_data.current_supplements)}")
        return "\n".join(parts) if parts else "None reported"

    def regenerate_section(
        self,
        soap_note: SOAPNote,
        section: str,
        additional_context: Optional[str] = None
    ) -> str:
        """
        Regenerate a specific section of the SOAP note

        Args:
            soap_note: Existing SOAP note
            section: Section to regenerate (subjective, objective, assessment, plan)
            additional_context: Additional context for regeneration

        Returns:
            Regenerated section text
        """
        if not OPENAI_AVAILABLE or not self.api_key:
            return getattr(soap_note, section, "")

        prompt = f"""Based on this SOAP note, regenerate the {section.upper()} section.

Current SOAP Note:
Subjective: {soap_note.subjective}
Objective: {soap_note.objective}
Assessment: {soap_note.assessment}
Plan: {soap_note.plan}

{f'Additional context: {additional_context}' if additional_context else ''}

Regenerate only the {section.upper()} section, making it more detailed and clinically relevant."""

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a clinical documentation specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Section regeneration failed: {e}")
            return getattr(soap_note, section, "")
