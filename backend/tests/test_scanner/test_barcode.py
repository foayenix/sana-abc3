"""
Tests for Barcode Recognition
=============================
"""

import pytest
from uuid import uuid4

from algorithms.product_scanner import (
    BarcodeRecognizer,
    BarcodeScanInput,
    ScanType,
    normalize_barcode,
    convert_upc_to_ean,
    is_supplement_barcode,
)


class TestBarcodeRecognizer:
    """Tests for the BarcodeRecognizer class"""

    @pytest.fixture
    def recognizer(self):
        return BarcodeRecognizer()

    # Valid barcode tests
    def test_decode_valid_upc_a(self, recognizer):
        """Test decoding valid UPC-A barcode"""
        result = recognizer.decode_barcode_string("012345678905")
        assert result is not None
        assert result["format"] == "UPC-A"
        assert result["valid"] is True

    def test_decode_valid_ean_13(self, recognizer):
        """Test decoding valid EAN-13 barcode"""
        result = recognizer.decode_barcode_string("4006381333931")
        assert result is not None
        assert result["format"] == "EAN-13"
        assert result["valid"] is True

    def test_decode_valid_ean_8(self, recognizer):
        """Test decoding valid EAN-8 barcode"""
        result = recognizer.decode_barcode_string("96385074")
        assert result is not None
        assert result["format"] == "EAN-8"

    # Invalid barcode tests
    def test_decode_invalid_length(self, recognizer):
        """Test rejection of invalid length barcode"""
        result = recognizer.decode_barcode_string("12345")
        assert result is None

    def test_decode_invalid_checksum(self, recognizer):
        """Test rejection of invalid checksum"""
        # This has an intentionally wrong check digit
        result = recognizer.decode_barcode_string("012345678901")
        assert result is None

    def test_decode_non_numeric(self, recognizer):
        """Test rejection of non-numeric barcode"""
        result = recognizer.decode_barcode_string("0123456789AB")
        assert result is None

    # Scan barcode tests
    def test_scan_barcode_valid(self, recognizer):
        """Test scanning valid barcode returns ScanResult"""
        input_data = BarcodeScanInput(barcode="012345678905")
        result = recognizer.scan_barcode(input_data)

        assert result.scan_type == ScanType.BARCODE
        assert result.confidence_score == 1.0
        assert result.error_message is None

    def test_scan_barcode_invalid(self, recognizer):
        """Test scanning invalid barcode returns error"""
        input_data = BarcodeScanInput(barcode="invalid123")
        result = recognizer.scan_barcode(input_data)

        assert result.product_found is False
        assert result.confidence_score == 0.0
        assert result.error_message is not None

    # Barcode info tests
    def test_get_barcode_info_upc(self, recognizer):
        """Test getting barcode format info for UPC"""
        info = recognizer.get_barcode_info("012345678905")
        assert info is not None
        assert info["format"] == "UPC-A"
        assert "North America" in info["info"]["regions"]

    def test_get_barcode_info_ean(self, recognizer):
        """Test getting barcode format info for EAN"""
        info = recognizer.get_barcode_info("4006381333931")
        assert info is not None
        assert info["format"] == "EAN-13"
        assert "Worldwide" in info["info"]["regions"]


class TestBarcodeUtilities:
    """Tests for barcode utility functions"""

    def test_normalize_barcode_removes_spaces(self):
        """Test that normalize_barcode removes spaces"""
        assert normalize_barcode("012 345 678 905") == "012345678905"

    def test_normalize_barcode_removes_dashes(self):
        """Test that normalize_barcode removes dashes"""
        assert normalize_barcode("012-345-678-905") == "012345678905"

    def test_normalize_barcode_strips_whitespace(self):
        """Test that normalize_barcode strips whitespace"""
        assert normalize_barcode("  012345678905  ") == "012345678905"

    def test_convert_upc_to_ean(self):
        """Test UPC-A to EAN-13 conversion"""
        upc = "012345678905"
        ean = convert_upc_to_ean(upc)
        assert ean == "0012345678905"
        assert len(ean) == 13

    def test_convert_upc_to_ean_non_upc(self):
        """Test that non-UPC codes are returned unchanged"""
        ean = "4006381333931"
        assert convert_upc_to_ean(ean) == ean

    def test_is_supplement_barcode_known_prefix(self):
        """Test detection of known supplement manufacturer prefix"""
        # Nature's Way prefix
        assert is_supplement_barcode("0076123456789") is True

    def test_is_supplement_barcode_unknown_prefix(self):
        """Test non-supplement barcode returns False"""
        assert is_supplement_barcode("0123456789012") is False


class TestBarcodeValidation:
    """Tests for barcode validation logic"""

    @pytest.fixture
    def recognizer(self):
        return BarcodeRecognizer()

    def test_ean13_check_digit_calculation(self, recognizer):
        """Test EAN-13 check digit validation"""
        # Valid EAN-13
        valid = recognizer._validate_ean_check_digit("4006381333931")
        assert valid is True

        # Invalid EAN-13 (wrong check digit)
        invalid = recognizer._validate_ean_check_digit("4006381333932")
        assert invalid is False

    def test_upca_check_digit_calculation(self, recognizer):
        """Test UPC-A check digit validation"""
        # Valid UPC-A
        valid = recognizer._validate_ean_check_digit("012345678905")
        assert valid is True

        # Invalid UPC-A
        invalid = recognizer._validate_ean_check_digit("012345678901")
        assert invalid is False

    @pytest.mark.parametrize("barcode,expected", [
        ("012345678905", True),   # Valid UPC-A
        ("4006381333931", True),  # Valid EAN-13
        ("96385074", True),       # Valid EAN-8
        ("012345678900", False),  # Invalid check digit
        ("40063813339", False),   # Wrong length
        ("", False),              # Empty
    ])
    def test_barcode_validation_parametrized(self, recognizer, barcode, expected):
        """Parametrized test for various barcodes"""
        if barcode:
            result = recognizer.decode_barcode_string(barcode)
            if expected:
                assert result is not None
            else:
                assert result is None
        else:
            with pytest.raises(Exception):
                recognizer.decode_barcode_string(barcode)
