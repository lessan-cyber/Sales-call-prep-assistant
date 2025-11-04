"""Tests for prep router helper functions."""
import pytest
from backend.src.routers.prep import normalize_company_name


class TestNormalizeCompanyName:
    """Test company name normalization function."""

    def test_simple_name(self):
        """Test normalization of simple company name."""
        result = normalize_company_name("Acme Corp")
        assert result == "acme-corp"

    def test_name_with_special_characters(self):
        """Test normalization with special characters."""
        result = normalize_company_name("Acme Corp & Co., Ltd.")
        assert result == "acme-corp-co-ltd"

    def test_name_with_numbers(self):
        """Test normalization with numbers."""
        result = normalize_company_name("Company 123")
        assert result == "company-123"

    def test_name_with_multiple_spaces(self):
        """Test normalization with multiple spaces."""
        result = normalize_company_name("Acme   Corp")
        assert result == "acme-corp"

    def test_name_with_hyphens(self):
        """Test normalization with existing hyphens."""
        result = normalize_company_name("Acme-Corp")
        assert result == "acme-corp"

    def test_name_with_underscores(self):
        """Test normalization with underscores."""
        result = normalize_company_name("Acme_Corp")
        assert result == "acme-corp"

    def test_uppercase_name(self):
        """Test normalization converts to lowercase."""
        result = normalize_company_name("ACME CORPORATION")
        assert result == "acme-corporation"

    def test_mixed_case_name(self):
        """Test normalization with mixed case."""
        result = normalize_company_name("AcMe CoRp")
        assert result == "acme-corp"

    def test_name_with_leading_trailing_spaces(self):
        """Test normalization removes leading/trailing spaces."""
        result = normalize_company_name("  Acme Corp  ")
        assert result == "acme-corp"

    def test_name_with_parentheses(self):
        """Test normalization with parentheses."""
        result = normalize_company_name("Acme Corp (USA)")
        assert result == "acme-corp-usa"

    def test_empty_string(self):
        """Test normalization of empty string."""
        result = normalize_company_name("")
        assert result == ""

    def test_only_special_characters(self):
        """Test normalization of only special characters."""
        result = normalize_company_name("@#$%")
        assert result == ""

    def test_international_characters(self):
        """Test normalization with international characters."""
        # Non-alphanumeric international chars should be removed
        result = normalize_company_name("Café Corp")
        assert result == "caf-corp"