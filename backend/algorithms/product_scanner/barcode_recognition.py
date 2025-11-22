"""
Barcode Recognition
===================
Handles barcode and QR code scanning for product identification.
Uses pyzbar library for decoding barcodes from images.
"""

import logging
from typing import Optional, List, Tuple
from uuid import UUID
import base64
import io
import re

try:
    from pyzbar import pyzbar
    from pyzbar.pyzbar import ZBarSymbol
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from .models import (
    ScanType,
    BarcodeScanInput,
    ScanResult,
)

logger = logging.getLogger(__name__)


class BarcodeRecognizer:
    """
    Barcode Recognition Engine

    Supports:
    - UPC-A (12 digits) - Common in US/Canada
    - UPC-E (8 digits) - Compressed UPC
    - EAN-13 (13 digits) - International
    - EAN-8 (8 digits) - Smaller packages
    - QR Code - Can contain URL or product info
    """

    # Supported barcode formats
    SUPPORTED_FORMATS = [
        ZBarSymbol.EAN13,
        ZBarSymbol.EAN8,
        ZBarSymbol.UPCA,
        ZBarSymbol.UPCE,
        ZBarSymbol.QRCODE,
    ] if PYZBAR_AVAILABLE else []

    # Barcode format patterns
    BARCODE_PATTERNS = {
        "UPC-A": r"^\d{12}$",
        "UPC-E": r"^\d{8}$",
        "EAN-13": r"^\d{13}$",
        "EAN-8": r"^\d{8}$",
    }

    def __init__(self):
        """Initialize the barcode recognizer"""
        self.available = PYZBAR_AVAILABLE and PIL_AVAILABLE
        if not self.available:
            logger.warning(
                "Barcode recognition unavailable. "
                "Install pyzbar and Pillow: pip install pyzbar Pillow"
            )

    def decode_barcode_string(self, barcode: str) -> Optional[dict]:
        """
        Validate and decode a barcode string (manually entered or pre-scanned)

        Args:
            barcode: The barcode string to validate

        Returns:
            Dictionary with barcode info or None if invalid
        """
        barcode = barcode.strip()

        # Determine barcode format
        barcode_format = None
        for format_name, pattern in self.BARCODE_PATTERNS.items():
            if re.match(pattern, barcode):
                barcode_format = format_name
                break

        if not barcode_format:
            logger.warning(f"Unrecognized barcode format: {barcode}")
            return None

        # Validate check digit for EAN/UPC
        if not self._validate_check_digit(barcode, barcode_format):
            logger.warning(f"Invalid check digit for barcode: {barcode}")
            return None

        return {
            "barcode": barcode,
            "format": barcode_format,
            "valid": True,
        }

    def decode_from_image(self, image_data: bytes) -> List[dict]:
        """
        Decode barcodes from an image

        Args:
            image_data: Raw image bytes

        Returns:
            List of decoded barcode dictionaries
        """
        if not self.available:
            logger.error("Barcode recognition not available")
            return []

        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))

            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Decode barcodes
            decoded = pyzbar.decode(image, symbols=self.SUPPORTED_FORMATS)

            results = []
            for barcode in decoded:
                barcode_data = barcode.data.decode("utf-8")
                barcode_type = barcode.type

                results.append({
                    "barcode": barcode_data,
                    "format": barcode_type,
                    "valid": True,
                    "quality": barcode.quality if hasattr(barcode, 'quality') else 100,
                    "rect": {
                        "x": barcode.rect.left,
                        "y": barcode.rect.top,
                        "width": barcode.rect.width,
                        "height": barcode.rect.height,
                    } if barcode.rect else None,
                })

            return results

        except Exception as e:
            logger.error(f"Error decoding barcode from image: {e}")
            return []

    def decode_from_base64(self, base64_string: str) -> List[dict]:
        """
        Decode barcodes from a base64-encoded image

        Args:
            base64_string: Base64-encoded image data

        Returns:
            List of decoded barcode dictionaries
        """
        try:
            # Remove data URL prefix if present
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]

            # Decode base64
            image_data = base64.b64decode(base64_string)

            return self.decode_from_image(image_data)

        except Exception as e:
            logger.error(f"Error decoding base64 image: {e}")
            return []

    def _validate_check_digit(self, barcode: str, barcode_format: str) -> bool:
        """
        Validate the check digit of a barcode

        Uses the standard modulo 10 algorithm for UPC/EAN barcodes.
        """
        if barcode_format in ["UPC-A", "EAN-13", "EAN-8"]:
            return self._validate_ean_check_digit(barcode)
        elif barcode_format == "UPC-E":
            # UPC-E has different validation
            return self._validate_upce_check_digit(barcode)
        return True

    def _validate_ean_check_digit(self, barcode: str) -> bool:
        """
        Validate EAN/UPC-A check digit using modulo 10 algorithm
        """
        try:
            digits = [int(d) for d in barcode]

            # Odd positions sum (1-indexed, so even in 0-indexed)
            odd_sum = sum(digits[i] for i in range(0, len(digits) - 1, 2))

            # Even positions sum
            even_sum = sum(digits[i] for i in range(1, len(digits) - 1, 2))

            # Calculate check digit
            if len(barcode) == 13:  # EAN-13
                total = odd_sum + (even_sum * 3)
            else:  # UPC-A, EAN-8
                total = (odd_sum * 3) + even_sum

            calculated_check = (10 - (total % 10)) % 10

            return calculated_check == digits[-1]

        except (ValueError, IndexError):
            return False

    def _validate_upce_check_digit(self, barcode: str) -> bool:
        """
        Validate UPC-E check digit
        UPC-E is a compressed format, validation is more complex
        """
        # For simplicity, accept all 8-digit barcodes
        # In production, would expand to UPC-A and validate
        return len(barcode) == 8 and barcode.isdigit()

    def scan_barcode(self, input_data: BarcodeScanInput) -> ScanResult:
        """
        Main entry point for barcode scanning

        Args:
            input_data: BarcodeScanInput with barcode string

        Returns:
            ScanResult with decoded barcode info
        """
        # Validate and decode the barcode
        decoded = self.decode_barcode_string(input_data.barcode)

        if not decoded:
            return ScanResult(
                scan_type=ScanType.BARCODE,
                product_found=False,
                confidence_score=0.0,
                error_message=f"Invalid barcode format: {input_data.barcode}"
            )

        # At this point, we have a valid barcode
        # Product lookup will be done by the scanner service
        return ScanResult(
            scan_type=input_data.scan_type,
            product_found=False,  # Will be updated by service
            confidence_score=1.0,  # Barcode is valid
            extracted_text=decoded["barcode"],
        )

    def get_barcode_info(self, barcode: str) -> Optional[dict]:
        """
        Get information about a barcode format

        Args:
            barcode: The barcode string

        Returns:
            Dictionary with barcode format info
        """
        # Determine format
        decoded = self.decode_barcode_string(barcode)

        if not decoded:
            return None

        format_info = {
            "UPC-A": {
                "description": "Universal Product Code (US/Canada)",
                "digits": 12,
                "regions": ["North America"],
            },
            "UPC-E": {
                "description": "Compressed UPC for small packages",
                "digits": 8,
                "regions": ["North America"],
            },
            "EAN-13": {
                "description": "European Article Number (International)",
                "digits": 13,
                "regions": ["Worldwide"],
            },
            "EAN-8": {
                "description": "Compressed EAN for small packages",
                "digits": 8,
                "regions": ["Worldwide"],
            },
        }

        return {
            "barcode": barcode,
            "format": decoded["format"],
            "info": format_info.get(decoded["format"], {}),
            "valid": decoded["valid"],
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def normalize_barcode(barcode: str) -> str:
    """
    Normalize a barcode string
    - Remove spaces and dashes
    - Ensure consistent length
    """
    return barcode.replace(" ", "").replace("-", "").strip()


def convert_upc_to_ean(upc: str) -> str:
    """
    Convert UPC-A (12 digit) to EAN-13 (13 digit)
    by prepending a 0
    """
    if len(upc) == 12 and upc.isdigit():
        return "0" + upc
    return upc


def is_supplement_barcode(barcode: str) -> bool:
    """
    Check if a barcode is likely a supplement product
    based on known supplement manufacturer prefixes
    """
    # Known supplement manufacturer prefixes (first 3-4 digits)
    supplement_prefixes = [
        "0076",  # Nature's Way
        "0031",  # Nature Made
        "0027",  # NOW Foods
        "0088",  # Jarrow Formulas
        "0072",  # Solgar
        "0669",  # Life Extension
        "0017",  # Garden of Life
        "0020",  # Nordic Naturals
        # Add more as needed
    ]

    for prefix in supplement_prefixes:
        if barcode.startswith(prefix):
            return True

    return False
