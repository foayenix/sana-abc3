"""
OCR Label Parser
================
Parses supplement labels using OCR to extract product information,
ingredients, and dosage information.
"""

import logging
import re
import base64
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass

from .models import (
    OCRResult,
    Ingredient,
    LabelRegion,
    ImageScanInput,
    ScanResult,
    ScanType,
)

logger = logging.getLogger(__name__)


# Try to import Google Cloud Vision
try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    logger.info("Google Cloud Vision not available. Using fallback OCR.")


class LabelParser:
    """
    Supplement Label Parser

    Extracts structured information from supplement labels including:
    - Product name and brand
    - Ingredients list with amounts
    - Serving size
    - Warnings and contraindications
    """

    # Common supplement label section headers
    SECTION_PATTERNS = {
        "supplement_facts": r"supplement\s*facts?|nutrition\s*facts?",
        "ingredients": r"other\s*ingredients?|ingredients?:",
        "warnings": r"warning[s]?:|caution[s]?:|do\s*not\s*use",
        "directions": r"direction[s]?:|suggested\s*use|how\s*to\s*use",
        "storage": r"storage:|store\s*in|keep\s*in",
    }

    # Common units in supplements
    DOSAGE_UNITS = [
        "mg", "g", "mcg", "iu", "ml", "oz", "mg/ml",
        "billion cfu", "million cfu", "cfu",
        "softgel", "softgels", "capsule", "capsules",
        "tablet", "tablets", "drop", "drops",
    ]

    # Standardized ingredient names mapping
    INGREDIENT_ALIASES = {
        "vit c": "vitamin c",
        "vit d": "vitamin d",
        "vit d3": "vitamin d3",
        "vit b12": "vitamin b12",
        "vit b6": "vitamin b6",
        "ascorbic acid": "vitamin c",
        "cholecalciferol": "vitamin d3",
        "cobalamin": "vitamin b12",
        "pyridoxine": "vitamin b6",
        "retinol": "vitamin a",
        "tocopherol": "vitamin e",
        "alpha-tocopherol": "vitamin e",
        "fish oil": "omega-3 fatty acids",
        "epa": "omega-3 epa",
        "dha": "omega-3 dha",
    }

    def __init__(self, use_google_vision: bool = True):
        """
        Initialize the label parser

        Args:
            use_google_vision: Whether to use Google Cloud Vision API
        """
        self.use_google_vision = use_google_vision and GOOGLE_VISION_AVAILABLE
        self._vision_client = None

    @property
    def vision_client(self):
        """Lazy initialization of Google Vision client"""
        if self._vision_client is None and GOOGLE_VISION_AVAILABLE:
            self._vision_client = vision.ImageAnnotatorClient()
        return self._vision_client

    def parse_label(self, input_data: ImageScanInput) -> OCRResult:
        """
        Parse a supplement label image

        Args:
            input_data: ImageScanInput with base64 image

        Returns:
            OCRResult with extracted information
        """
        import time
        start_time = time.time()

        # Decode base64 image
        try:
            if "," in input_data.image_base64:
                image_data = base64.b64decode(input_data.image_base64.split(",")[1])
            else:
                image_data = base64.b64decode(input_data.image_base64)
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {e}")
            return OCRResult(
                raw_text="",
                confidence=0.0,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        # Perform OCR
        if self.use_google_vision:
            raw_text, confidence = self._ocr_google_vision(image_data)
        else:
            raw_text, confidence = self._ocr_fallback(image_data)

        # Parse the raw text
        result = self._parse_raw_text(raw_text)
        result.raw_text = raw_text
        result.confidence = confidence
        result.processing_time_ms = int((time.time() - start_time) * 1000)
        result.ocr_engine = "google_vision" if self.use_google_vision else "tesseract"

        return result

    def _ocr_google_vision(self, image_data: bytes) -> Tuple[str, float]:
        """
        Perform OCR using Google Cloud Vision API

        Args:
            image_data: Raw image bytes

        Returns:
            Tuple of (extracted text, confidence score)
        """
        if not GOOGLE_VISION_AVAILABLE or self.vision_client is None:
            return self._ocr_fallback(image_data)

        try:
            image = vision.Image(content=image_data)

            # Use document text detection for better results on labels
            response = self.vision_client.document_text_detection(image=image)

            if response.error.message:
                logger.error(f"Google Vision error: {response.error.message}")
                return "", 0.0

            text_annotation = response.full_text_annotation

            if not text_annotation:
                return "", 0.0

            # Calculate average confidence
            confidences = []
            for page in text_annotation.pages:
                for block in page.blocks:
                    confidences.append(block.confidence)

            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return text_annotation.text, avg_confidence

        except Exception as e:
            logger.error(f"Google Vision OCR failed: {e}")
            return self._ocr_fallback(image_data)

    def _ocr_fallback(self, image_data: bytes) -> Tuple[str, float]:
        """
        Fallback OCR using Tesseract (if available) or return empty

        Args:
            image_data: Raw image bytes

        Returns:
            Tuple of (extracted text, confidence score)
        """
        try:
            import pytesseract
            from PIL import Image
            import io

            image = Image.open(io.BytesIO(image_data))

            # Preprocess image for better OCR
            image = image.convert("L")  # Grayscale

            # Get OCR data with confidence
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            # Extract text and calculate confidence
            text_parts = []
            confidences = []

            for i, word in enumerate(data["text"]):
                if word.strip():
                    text_parts.append(word)
                    conf = data["conf"][i]
                    if conf > 0:
                        confidences.append(conf / 100.0)

            text = " ".join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return text, avg_confidence

        except ImportError:
            logger.warning("Tesseract not available for fallback OCR")
            return "", 0.0
        except Exception as e:
            logger.error(f"Fallback OCR failed: {e}")
            return "", 0.0

    def _parse_raw_text(self, raw_text: str) -> OCRResult:
        """
        Parse raw OCR text into structured data

        Args:
            raw_text: Raw text from OCR

        Returns:
            OCRResult with parsed fields
        """
        result = OCRResult(
            raw_text=raw_text,
            confidence=0.0,
        )

        if not raw_text:
            return result

        # Normalize text
        text = raw_text.lower()

        # Extract product name (usually first line or largest text)
        result.product_name = self._extract_product_name(raw_text)

        # Extract brand name
        result.brand_name = self._extract_brand_name(raw_text)

        # Extract ingredients section
        result.ingredients_text = self._extract_section(text, "ingredients")

        # Parse ingredients into structured format
        if result.ingredients_text:
            result.parsed_ingredients = self._parse_ingredients(result.ingredients_text)

        # Extract serving size
        result.serving_size = self._extract_serving_size(text)

        # Extract warnings
        result.warnings_text = self._extract_section(text, "warnings")

        return result

    def _extract_product_name(self, text: str) -> Optional[str]:
        """Extract product name from text"""
        lines = text.strip().split("\n")

        # Product name is usually in the first few lines
        for line in lines[:5]:
            line = line.strip()
            # Skip very short lines or common headers
            if len(line) > 3 and not self._is_common_header(line.lower()):
                # Clean up the line
                name = re.sub(r"[®™©]", "", line)
                return name.title()

        return None

    def _extract_brand_name(self, text: str) -> Optional[str]:
        """Extract brand name from text"""
        # Common brand patterns
        brand_patterns = [
            r"(?:by|from)\s+([A-Z][A-Za-z\s]+)",
            r"([A-Z][A-Za-z]+)\s+(?:brand|supplements?)",
        ]

        for pattern in brand_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return None

    def _extract_section(self, text: str, section_type: str) -> Optional[str]:
        """Extract a specific section from the label text"""
        pattern = self.SECTION_PATTERNS.get(section_type)
        if not pattern:
            return None

        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return None

        # Extract text after the section header
        start_pos = match.end()

        # Find the next section or end of text
        next_section_pos = len(text)
        for other_type, other_pattern in self.SECTION_PATTERNS.items():
            if other_type != section_type:
                other_match = re.search(other_pattern, text[start_pos:], re.IGNORECASE)
                if other_match:
                    pos = start_pos + other_match.start()
                    next_section_pos = min(next_section_pos, pos)

        section_text = text[start_pos:next_section_pos].strip()
        return section_text if section_text else None

    def _extract_serving_size(self, text: str) -> Optional[str]:
        """Extract serving size information"""
        patterns = [
            r"serving\s*size[:\s]+(.+?)(?:\n|$)",
            r"(\d+\s*(?:capsule|tablet|softgel)s?\s*(?:per|/)\s*serving)",
            r"(\d+\s*(?:ml|oz|g|mg)\s*(?:per|/)\s*serving)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _parse_ingredients(self, ingredients_text: str) -> List[Ingredient]:
        """
        Parse ingredients text into structured Ingredient objects

        Args:
            ingredients_text: Raw ingredients text

        Returns:
            List of Ingredient objects
        """
        ingredients = []

        # Split by common delimiters
        parts = re.split(r"[,;]|\n", ingredients_text)

        for part in parts:
            part = part.strip()
            if not part or len(part) < 2:
                continue

            ingredient = self._parse_single_ingredient(part)
            if ingredient:
                ingredients.append(ingredient)

        return ingredients

    def _parse_single_ingredient(self, text: str) -> Optional[Ingredient]:
        """
        Parse a single ingredient string

        Args:
            text: Single ingredient text

        Returns:
            Ingredient object or None
        """
        text = text.strip().lower()

        if not text or len(text) < 2:
            return None

        # Try to extract amount and unit
        amount = None
        unit = None
        name = text

        # Pattern: "vitamin c 500mg" or "500mg vitamin c"
        for u in self.DOSAGE_UNITS:
            # Check for "500mg" pattern
            amount_pattern = rf"(\d+(?:\.\d+)?)\s*{re.escape(u)}"
            match = re.search(amount_pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                unit = u
                name = re.sub(amount_pattern, "", text, flags=re.IGNORECASE).strip()
                break

        # Clean up the name
        name = re.sub(r"[()]", "", name).strip()

        # Standardize ingredient name
        standardized_name = self.INGREDIENT_ALIASES.get(name, name)

        if not name:
            return None

        return Ingredient(
            name=name.title(),
            amount=amount,
            unit=unit,
            standardized_name=standardized_name.title(),
        )

    def _is_common_header(self, text: str) -> bool:
        """Check if text is a common header to skip"""
        headers = [
            "supplement facts",
            "nutrition facts",
            "ingredients",
            "other ingredients",
            "directions",
            "warning",
            "storage",
        ]
        return text.strip().lower() in headers

    def detect_label_regions(self, image_data: bytes) -> List[LabelRegion]:
        """
        Detect different regions on a supplement label

        Args:
            image_data: Raw image bytes

        Returns:
            List of detected LabelRegion objects
        """
        regions = []

        # This would use more advanced CV to detect regions
        # For now, we'll parse based on text patterns
        if self.use_google_vision and GOOGLE_VISION_AVAILABLE:
            try:
                image = vision.Image(content=image_data)
                response = self.vision_client.document_text_detection(image=image)

                if response.full_text_annotation:
                    text = response.full_text_annotation.text

                    for section_type, pattern in self.SECTION_PATTERNS.items():
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            regions.append(LabelRegion(
                                region_type=section_type,
                                text=match.group(0),
                                confidence=0.8,
                            ))

            except Exception as e:
                logger.error(f"Error detecting label regions: {e}")

        return regions


def scan_label_image(input_data: ImageScanInput) -> ScanResult:
    """
    Convenience function to scan a label image

    Args:
        input_data: ImageScanInput with base64 image

    Returns:
        ScanResult with extracted information
    """
    parser = LabelParser()
    ocr_result = parser.parse_label(input_data)

    return ScanResult(
        scan_type=ScanType.IMAGE_OCR,
        product_found=bool(ocr_result.product_name),
        extracted_text=ocr_result.raw_text,
        extracted_ingredients=ocr_result.parsed_ingredients,
        confidence_score=ocr_result.confidence,
    )
