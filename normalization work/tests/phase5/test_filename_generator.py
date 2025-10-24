"""
Tests for Filename Generator

Tests filename generation with various inputs including:
- Standard names
- Special characters
- Different document types
- Multiple sets
"""

import pytest
from src.phase5.filename_generator import generate_filename, sanitize_filename


class TestBasicFilenameGeneration:
    """Test basic filename generation."""

    def test_filename_format(self):
        """Test filename follows correct format."""
        filename = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=1,
            total_sets=2,
            filename_suffix="Discovery Propounded SROGs"
        )

        expected = "John Doe vs ABC Corp - Discovery Propounded SROGs Set 1 of 2"
        assert filename == expected

    def test_single_set_filename(self):
        """Test filename with single set (1 of 1)."""
        filename = generate_filename(
            plaintiff_name="Jane Smith",
            defendant_name="XYZ Properties",
            doc_type="PODs",
            set_number=1,
            total_sets=1,
            filename_suffix="Discovery Propounded PODs"
        )

        expected = "Jane Smith vs XYZ Properties - Discovery Propounded PODs Set 1 of 1"
        assert filename == expected

    def test_multiple_sets_numbering(self):
        """Test filename with multiple sets."""
        filename_1 = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=1,
            total_sets=3,
            filename_suffix="Discovery Propounded SROGs"
        )

        filename_2 = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=2,
            total_sets=3,
            filename_suffix="Discovery Propounded SROGs"
        )

        filename_3 = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=3,
            total_sets=3,
            filename_suffix="Discovery Propounded SROGs"
        )

        assert "Set 1 of 3" in filename_1
        assert "Set 2 of 3" in filename_2
        assert "Set 3 of 3" in filename_3

    def test_vs_separator_present(self):
        """Test 'vs' separator is present."""
        filename = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=1,
            total_sets=1,
            filename_suffix="Discovery Propounded SROGs"
        )

        assert " vs " in filename


class TestSpecialCharacters:
    """Test handling of special characters in names."""

    def test_filename_with_accented_characters(self):
        """Test filename handles accented characters."""
        filename = generate_filename(
            plaintiff_name="María José González",
            defendant_name="Señor Properties",
            doc_type="PODs",
            set_number=1,
            total_sets=1,
            filename_suffix="Discovery Propounded PODs"
        )

        assert "María José González" in filename
        assert "Señor Properties" in filename

    def test_filename_with_apostrophes(self):
        """Test filename handles apostrophes."""
        filename = generate_filename(
            plaintiff_name="O'Brien",
            defendant_name="Smith's Property Management",
            doc_type="SROGs",
            set_number=1,
            total_sets=1,
            filename_suffix="Discovery Propounded SROGs"
        )

        assert "O'Brien" in filename
        assert "Smith's Property Management" in filename

    def test_filename_with_hyphens(self):
        """Test filename handles hyphens in names."""
        filename = generate_filename(
            plaintiff_name="Mary-Jane Watson",
            defendant_name="Parker-Stacy LLC",
            doc_type="Admissions",
            set_number=1,
            total_sets=1,
            filename_suffix="Requests for Admissions"
        )

        assert "Mary-Jane Watson" in filename
        assert "Parker-Stacy LLC" in filename

    def test_filename_with_periods(self):
        """Test filename handles periods in names."""
        filename = generate_filename(
            plaintiff_name="Dr. John Smith",
            defendant_name="A.B.C. Corp.",
            doc_type="SROGs",
            set_number=1,
            total_sets=1,
            filename_suffix="Discovery Propounded SROGs"
        )

        assert "Dr. John Smith" in filename
        assert "A.B.C. Corp." in filename

    def test_filename_with_ampersands(self):
        """Test filename handles ampersands."""
        filename = generate_filename(
            plaintiff_name="Smith & Sons",
            defendant_name="Johnson & Associates",
            doc_type="PODs",
            set_number=1,
            total_sets=1,
            filename_suffix="Discovery Propounded PODs"
        )

        assert "Smith & Sons" in filename
        assert "Johnson & Associates" in filename


class TestDocumentTypes:
    """Test different document types."""

    def test_srogs_document_type(self):
        """Test SROGs document type."""
        filename = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=1,
            total_sets=1,
            filename_suffix="Discovery Propounded SROGs"
        )

        assert "Discovery Propounded SROGs" in filename

    def test_pods_document_type(self):
        """Test PODs document type."""
        filename = generate_filename(
            plaintiff_name="Jane Smith",
            defendant_name="XYZ Properties",
            doc_type="PODs",
            set_number=1,
            total_sets=1,
            filename_suffix="Discovery Propounded PODs"
        )

        assert "Discovery Propounded PODs" in filename

    def test_admissions_document_type(self):
        """Test Admissions document type."""
        filename = generate_filename(
            plaintiff_name="Bob Johnson",
            defendant_name="Test Company",
            doc_type="Admissions",
            set_number=1,
            total_sets=1,
            filename_suffix="Requests for Admissions"
        )

        assert "Requests for Admissions" in filename

    def test_custom_suffix(self):
        """Test custom filename suffix."""
        filename = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=1,
            total_sets=1,
            filename_suffix="Supplemental Discovery"
        )

        assert "Supplemental Discovery" in filename


class TestSetNumbering:
    """Test set numbering in filenames."""

    def test_set_one_of_one(self):
        """Test set 1 of 1 format."""
        filename = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=1,
            total_sets=1,
            filename_suffix="Discovery Propounded SROGs"
        )

        assert "Set 1 of 1" in filename

    def test_set_one_of_five(self):
        """Test set 1 of 5 format."""
        filename = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=1,
            total_sets=5,
            filename_suffix="Discovery Propounded SROGs"
        )

        assert "Set 1 of 5" in filename

    def test_set_five_of_five(self):
        """Test last set format (5 of 5)."""
        filename = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=5,
            total_sets=5,
            filename_suffix="Discovery Propounded SROGs"
        )

        assert "Set 5 of 5" in filename

    def test_large_set_numbers(self):
        """Test large set numbers (e.g., 10+)."""
        filename = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=12,
            total_sets=15,
            filename_suffix="Discovery Propounded SROGs"
        )

        assert "Set 12 of 15" in filename


class TestFilenameConsistency:
    """Test filename consistency across related documents."""

    def test_same_parties_different_sets(self):
        """Test filenames for same parties but different sets."""
        base_params = {
            'plaintiff_name': "John Doe",
            'defendant_name': "ABC Corp",
            'doc_type': "SROGs",
            'total_sets': 2,
            'filename_suffix': "Discovery Propounded SROGs"
        }

        filename_1 = generate_filename(**base_params, set_number=1)
        filename_2 = generate_filename(**base_params, set_number=2)

        # Should differ only in set number
        assert filename_1.replace("Set 1 of 2", "Set 2 of 2") == filename_2

    def test_same_parties_different_doc_types(self):
        """Test filenames for same parties but different document types."""
        base_params = {
            'plaintiff_name': "John Doe",
            'defendant_name': "ABC Corp",
            'set_number': 1,
            'total_sets': 1
        }

        filename_srogs = generate_filename(
            **base_params,
            doc_type="SROGs",
            filename_suffix="Discovery Propounded SROGs"
        )

        filename_pods = generate_filename(
            **base_params,
            doc_type="PODs",
            filename_suffix="Discovery Propounded PODs"
        )

        # Both should have same parties
        assert "John Doe vs ABC Corp" in filename_srogs
        assert "John Doe vs ABC Corp" in filename_pods

        # But different suffixes
        assert "Discovery Propounded SROGs" in filename_srogs
        assert "Discovery Propounded PODs" in filename_pods


class TestSanitizeFilename:
    """Test filename sanitization helper."""

    def test_sanitize_removes_forward_slash(self):
        """Test sanitize removes forward slashes."""
        sanitized = sanitize_filename("Test/Name")
        assert "/" not in sanitized
        assert sanitized == "Test_Name"

    def test_sanitize_removes_backslash(self):
        """Test sanitize removes backslashes."""
        sanitized = sanitize_filename("Test\\Name")
        assert "\\" not in sanitized
        assert sanitized == "Test_Name"

    def test_sanitize_removes_colon(self):
        """Test sanitize removes colons."""
        sanitized = sanitize_filename("Test:Name")
        assert ":" not in sanitized
        assert sanitized == "Test_Name"

    def test_sanitize_removes_asterisk(self):
        """Test sanitize removes asterisks."""
        sanitized = sanitize_filename("Test*Name")
        assert "*" not in sanitized
        assert sanitized == "Test_Name"

    def test_sanitize_removes_question_mark(self):
        """Test sanitize removes question marks."""
        sanitized = sanitize_filename("Test?Name")
        assert "?" not in sanitized
        assert sanitized == "Test_Name"

    def test_sanitize_preserves_legal_characters(self):
        """Test sanitize preserves legal characters."""
        original = "John Doe vs ABC Corp - SROGs Set 1 of 2"
        sanitized = sanitize_filename(original)
        assert sanitized == original

    def test_sanitize_handles_multiple_unsafe_chars(self):
        """Test sanitize handles multiple unsafe characters."""
        sanitized = sanitize_filename("Test/Name\\With:Bad*Chars")
        assert "/" not in sanitized
        assert "\\" not in sanitized
        assert ":" not in sanitized
        assert "*" not in sanitized
        assert sanitized == "Test_Name_With_Bad_Chars"

    def test_sanitize_preserves_accents(self):
        """Test sanitize preserves accented characters."""
        original = "María José"
        sanitized = sanitize_filename(original)
        assert sanitized == original


class TestEdgeCases:
    """Test edge cases in filename generation."""

    def test_empty_plaintiff_name(self):
        """Test filename with empty plaintiff name."""
        filename = generate_filename(
            plaintiff_name="",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=1,
            total_sets=1,
            filename_suffix="Discovery Propounded SROGs"
        )

        # Should still generate valid filename
        assert " vs ABC Corp" in filename

    def test_empty_defendant_name(self):
        """Test filename with empty defendant name."""
        filename = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="",
            doc_type="SROGs",
            set_number=1,
            total_sets=1,
            filename_suffix="Discovery Propounded SROGs"
        )

        # Should still generate valid filename
        assert "John Doe vs " in filename

    def test_very_long_names(self):
        """Test filename with very long names."""
        long_plaintiff = "John Jacob Jingleheimer Schmidt III Esq."
        long_defendant = "The Super Long Property Management Company LLC"

        filename = generate_filename(
            plaintiff_name=long_plaintiff,
            defendant_name=long_defendant,
            doc_type="SROGs",
            set_number=1,
            total_sets=1,
            filename_suffix="Discovery Propounded SROGs"
        )

        assert long_plaintiff in filename
        assert long_defendant in filename

    def test_numeric_set_numbers_as_integers(self):
        """Test set numbers are properly formatted as integers."""
        filename = generate_filename(
            plaintiff_name="John Doe",
            defendant_name="ABC Corp",
            doc_type="SROGs",
            set_number=1,
            total_sets=10,
            filename_suffix="Discovery Propounded SROGs"
        )

        # Should format as "1" not "1.0"
        assert "Set 1 of 10" in filename
        assert "Set 1.0" not in filename
