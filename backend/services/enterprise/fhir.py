"""
FHIR R4 integration service for clinical interoperability.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime, date
from pydantic import BaseModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FHIRResourceType(str, Enum):
    """Supported FHIR R4 resource types."""
    PATIENT = "Patient"
    PRACTITIONER = "Practitioner"
    OBSERVATION = "Observation"
    CONDITION = "Condition"
    PROCEDURE = "Procedure"
    ENCOUNTER = "Encounter"
    CARE_PLAN = "CarePlan"
    DIAGNOSTIC_REPORT = "DiagnosticReport"
    MEDICATION_REQUEST = "MedicationRequest"
    ALLERGY_INTOLERANCE = "AllergyIntolerance"
    APPOINTMENT = "Appointment"
    QUESTIONNAIRE_RESPONSE = "QuestionnaireResponse"


class FHIRResource(BaseModel):
    """A FHIR R4 resource."""
    resourceType: str
    id: str
    meta: Dict[str, Any] = {}
    text: Optional[Dict[str, Any]] = None
    identifier: List[Dict[str, Any]] = []
    # Resource-specific fields stored here
    data: Dict[str, Any] = {}


class FHIRIntegrationService:
    """
    FHIR R4 integration for clinical data interoperability.

    Features:
    - Resource mapping from SANA to FHIR
    - FHIR bundle creation
    - Validation against profiles
    - NHS Digital profile support
    """

    # SANA to FHIR code mappings
    CONDITION_CODES = {
        "chronic_pain": {"system": "http://snomed.info/sct", "code": "82423001", "display": "Chronic pain"},
        "anxiety": {"system": "http://snomed.info/sct", "code": "48694002", "display": "Anxiety"},
        "insomnia": {"system": "http://snomed.info/sct", "code": "193462001", "display": "Insomnia"},
        "fatigue": {"system": "http://snomed.info/sct", "code": "84229001", "display": "Fatigue"},
        "stress": {"system": "http://snomed.info/sct", "code": "73595000", "display": "Stress"},
        "depression": {"system": "http://snomed.info/sct", "code": "35489007", "display": "Depression"},
        "headache": {"system": "http://snomed.info/sct", "code": "25064002", "display": "Headache"},
        "back_pain": {"system": "http://snomed.info/sct", "code": "161891005", "display": "Back pain"}
    }

    PROCEDURE_CODES = {
        "acupuncture": {"system": "http://snomed.info/sct", "code": "44868003", "display": "Acupuncture"},
        "massage": {"system": "http://snomed.info/sct", "code": "387854002", "display": "Therapeutic massage"},
        "herbal_medicine": {"system": "http://snomed.info/sct", "code": "410942007", "display": "Herbal medicine therapy"},
        "naturopathy": {"system": "http://snomed.info/sct", "code": "276239002", "display": "Naturopathy"}
    }

    def __init__(self):
        self.resources: Dict[str, FHIRResource] = {}
        logger.info("FHIRIntegrationService initialized")

    def map_client_to_patient(self, client_data: Dict[str, Any]) -> FHIRResource:
        """
        Map SANA client to FHIR Patient resource.

        Args:
            client_data: SANA client data

        Returns:
            FHIR Patient resource
        """
        resource_id = str(uuid4())

        patient = FHIRResource(
            resourceType="Patient",
            id=resource_id,
            meta={
                "profile": ["https://fhir.nhs.uk/R4/StructureDefinition/UKCore-Patient"],
                "lastUpdated": datetime.utcnow().isoformat()
            },
            identifier=[
                {
                    "system": "https://sana.health/patient",
                    "value": str(client_data.get("id", ""))
                }
            ],
            data={
                "active": True,
                "name": [{
                    "use": "official",
                    "family": client_data.get("last_name", ""),
                    "given": [client_data.get("first_name", "")]
                }],
                "telecom": [
                    {
                        "system": "email",
                        "value": client_data.get("email", ""),
                        "use": "home"
                    }
                ],
                "gender": client_data.get("gender", "unknown"),
                "birthDate": client_data.get("date_of_birth", ""),
                "address": [{
                    "use": "home",
                    "city": client_data.get("city", ""),
                    "postalCode": client_data.get("postal_code", ""),
                    "country": "GB"
                }]
            }
        )

        self.resources[resource_id] = patient
        return patient

    def map_practitioner_to_fhir(self, practitioner_data: Dict[str, Any]) -> FHIRResource:
        """Map SANA practitioner to FHIR Practitioner resource."""
        resource_id = str(uuid4())

        practitioner = FHIRResource(
            resourceType="Practitioner",
            id=resource_id,
            meta={
                "profile": ["https://fhir.nhs.uk/R4/StructureDefinition/UKCore-Practitioner"],
                "lastUpdated": datetime.utcnow().isoformat()
            },
            identifier=[
                {
                    "system": "https://sana.health/practitioner",
                    "value": str(practitioner_data.get("id", ""))
                }
            ],
            data={
                "active": True,
                "name": [{
                    "use": "official",
                    "text": practitioner_data.get("name", ""),
                    "prefix": [practitioner_data.get("title", "")]
                }],
                "telecom": [
                    {
                        "system": "email",
                        "value": practitioner_data.get("email", ""),
                        "use": "work"
                    }
                ],
                "qualification": [
                    {
                        "code": {
                            "coding": [{
                                "system": "https://sana.health/qualification",
                                "code": q.get("type", ""),
                                "display": q.get("name", "")
                            }]
                        },
                        "issuer": {"display": q.get("issuer", "")}
                    }
                    for q in practitioner_data.get("credentials", [])
                ]
            }
        )

        self.resources[resource_id] = practitioner
        return practitioner

    def map_session_to_encounter(
        self,
        session_data: Dict[str, Any],
        patient_id: str,
        practitioner_id: str
    ) -> FHIRResource:
        """Map SANA session to FHIR Encounter resource."""
        resource_id = str(uuid4())

        encounter = FHIRResource(
            resourceType="Encounter",
            id=resource_id,
            meta={
                "profile": ["https://fhir.nhs.uk/R4/StructureDefinition/UKCore-Encounter"],
                "lastUpdated": datetime.utcnow().isoformat()
            },
            identifier=[
                {
                    "system": "https://sana.health/session",
                    "value": str(session_data.get("id", ""))
                }
            ],
            data={
                "status": self._map_session_status(session_data.get("status", "")),
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "AMB",
                    "display": "ambulatory"
                },
                "type": [{
                    "coding": [{
                        "system": "https://sana.health/session-type",
                        "code": session_data.get("type", "consultation"),
                        "display": session_data.get("type", "Consultation")
                    }]
                }],
                "subject": {"reference": f"Patient/{patient_id}"},
                "participant": [{
                    "individual": {"reference": f"Practitioner/{practitioner_id}"}
                }],
                "period": {
                    "start": session_data.get("start_time", ""),
                    "end": session_data.get("end_time", "")
                },
                "reasonCode": [
                    {
                        "coding": [self._get_condition_code(condition)]
                    }
                    for condition in session_data.get("conditions", [])
                ]
            }
        )

        self.resources[resource_id] = encounter
        return encounter

    def map_prom_to_observation(
        self,
        prom_data: Dict[str, Any],
        patient_id: str
    ) -> FHIRResource:
        """Map SANA PROM response to FHIR Observation."""
        resource_id = str(uuid4())

        # Map PROM type to LOINC code
        prom_codes = {
            "WHO5": {"code": "71111-6", "display": "WHO-5 Well-Being Index"},
            "DASS21": {"code": "71116-5", "display": "DASS-21"},
            "VAS_PAIN": {"code": "72514-3", "display": "Pain severity - visual analog score"}
        }

        prom_type = prom_data.get("type", "")
        code_info = prom_codes.get(prom_type, {"code": "unknown", "display": prom_type})

        observation = FHIRResource(
            resourceType="Observation",
            id=resource_id,
            meta={
                "profile": ["https://fhir.nhs.uk/R4/StructureDefinition/UKCore-Observation"],
                "lastUpdated": datetime.utcnow().isoformat()
            },
            identifier=[
                {
                    "system": "https://sana.health/prom",
                    "value": str(prom_data.get("id", ""))
                }
            ],
            data={
                "status": "final",
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "survey",
                        "display": "Survey"
                    }]
                }],
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": code_info["code"],
                        "display": code_info["display"]
                    }]
                },
                "subject": {"reference": f"Patient/{patient_id}"},
                "effectiveDateTime": prom_data.get("completed_at", ""),
                "valueQuantity": {
                    "value": prom_data.get("score", 0),
                    "unit": "score",
                    "system": "http://unitsofmeasure.org",
                    "code": "{score}"
                },
                "interpretation": [{
                    "coding": [{
                        "system": "https://sana.health/severity",
                        "code": prom_data.get("severity", "normal"),
                        "display": prom_data.get("severity", "Normal")
                    }]
                }]
            }
        )

        self.resources[resource_id] = observation
        return observation

    def create_bundle(
        self,
        resources: List[FHIRResource],
        bundle_type: str = "collection"
    ) -> Dict[str, Any]:
        """
        Create a FHIR Bundle from resources.

        Args:
            resources: List of FHIR resources
            bundle_type: Type of bundle (collection, document, transaction)

        Returns:
            FHIR Bundle
        """
        return {
            "resourceType": "Bundle",
            "id": str(uuid4()),
            "meta": {
                "lastUpdated": datetime.utcnow().isoformat()
            },
            "type": bundle_type,
            "total": len(resources),
            "entry": [
                {
                    "fullUrl": f"urn:uuid:{r.id}",
                    "resource": {
                        "resourceType": r.resourceType,
                        "id": r.id,
                        "meta": r.meta,
                        "identifier": r.identifier,
                        **r.data
                    }
                }
                for r in resources
            ]
        }

    def _map_session_status(self, status: str) -> str:
        """Map SANA session status to FHIR encounter status."""
        mapping = {
            "scheduled": "planned",
            "confirmed": "planned",
            "in_progress": "in-progress",
            "completed": "finished",
            "cancelled": "cancelled",
            "no_show": "cancelled"
        }
        return mapping.get(status, "unknown")

    def _get_condition_code(self, condition: str) -> Dict[str, str]:
        """Get SNOMED CT code for a condition."""
        condition_key = condition.lower().replace(" ", "_")
        return self.CONDITION_CODES.get(
            condition_key,
            {"system": "https://sana.health/condition", "code": condition, "display": condition}
        )

    def validate_resource(self, resource: FHIRResource) -> Dict[str, Any]:
        """Validate a FHIR resource against profile."""
        # Basic validation - in production would use FHIR validator
        errors = []
        warnings = []

        if not resource.resourceType:
            errors.append("Missing resourceType")

        if not resource.id:
            errors.append("Missing resource id")

        # Check required fields based on resource type
        if resource.resourceType == "Patient":
            if "name" not in resource.data:
                warnings.append("Patient should have a name")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def get_resource(self, resource_id: str) -> Optional[FHIRResource]:
        """Get a stored FHIR resource."""
        return self.resources.get(resource_id)

    def export_patient_record(
        self,
        patient_id: str,
        include_observations: bool = True,
        include_encounters: bool = True
    ) -> Dict[str, Any]:
        """Export complete patient record as FHIR Bundle."""
        resources = []

        # Get patient
        patient = self.get_resource(patient_id)
        if patient:
            resources.append(patient)

        # Get related resources
        for resource in self.resources.values():
            if resource.resourceType == "Observation" and include_observations:
                if resource.data.get("subject", {}).get("reference") == f"Patient/{patient_id}":
                    resources.append(resource)
            elif resource.resourceType == "Encounter" and include_encounters:
                if resource.data.get("subject", {}).get("reference") == f"Patient/{patient_id}":
                    resources.append(resource)

        return self.create_bundle(resources, "document")
