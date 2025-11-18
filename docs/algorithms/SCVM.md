# SCVM - SANA Credential Vetting Model

## Overview
Verifies practitioner credentials with 99%+ accuracy through multi-source validation.

## Verification Sources

- Licensing boards
- Certification bodies
- Educational institutions
- Professional associations

## Verification Process

1. **Document Analysis**
   - OCR extraction
   - Format validation
   - Authenticity checks

2. **Database Verification**
   - Cross-reference with issuing bodies
   - Check expiration dates
   - Validate license numbers

3. **Confidence Scoring**
   - Combine evidence from multiple sources
   - Weight by source reliability
   - Flag inconsistencies

## Input

```python
{
    "practitioner_id": UUID,
    "credentials": ["RYT-500", "L.Ac", "NCCAOM"],
    "documents": [
        {"type": "certificate", "file": "..."}
    ]
}
```

## Output

```python
{
    "practitioner_id": UUID,
    "verified": true,
    "verification_results": [
        {
            "credential": "RYT-500",
            "verified": true,
            "source": "Yoga Alliance",
            "expiration_date": "2025-12-31",
            "notes": ""
        },
        ...
    ],
    "confidence_score": 0.98,
    "flags": []
}
```

## Confidence Levels

| Score | Interpretation |
|-------|----------------|
| 0.95+ | Highly confident |
| 0.80-0.94 | Confident |
| 0.60-0.79 | Manual review recommended |
| <0.60 | Unable to verify |

## API Endpoint
```
POST /api/v1/verification/verify
```
