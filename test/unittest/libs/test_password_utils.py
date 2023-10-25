import pytest
import re

from doko.libs.password_utils import (
    is_valid_password,
    pepper_password,
    hash_password,
    password_matches,
    password,
    password_regex,
    password_regex_description,
    pepper,
    hashing_rounds,
)


class TestPasswordValidation:
    """Test cases for password validation functionality."""

    def test_valid_passwords(self):
        """Test passwords that should be valid."""
        valid_passwords = [
            "password123",  # 11 chars, letters + digits
            "MyPass@2023",  # 12 chars, mixed case + special char + digits
            "Test#Pass$",   # 10 chars, special characters
            "Ab123456",     # 8 chars, minimum length
            "A" * 39,       # 39 chars, maximum length
            "Abc123@#$%^&+=",  # All allowed special characters
        ]
        
        for pwd in valid_passwords:
            assert is_valid_password(pwd), f"Password '{pwd}' should be valid"

    def test_invalid_passwords_too_short(self):
        """Test passwords that are too short."""
        short_passwords = [
            "",         # Empty
            "1",        # 1 char
            "Ab1@",     # 4 chars
            "Test123",  # 7 chars (just under minimum)
        ]
        
        for pwd in short_passwords:
            assert not is_valid_password(pwd), f"Password '{pwd}' should be invalid (too short)"

    def test_invalid_passwords_too_long(self):
        """Test passwords that are too long."""
        long_password = "A" * 40  # 40 chars (over maximum)
        assert not is_valid_password(long_password), "Password should be invalid (too long)"

    def test_invalid_passwords_forbidden_characters(self):
        """Test passwords with forbidden characters."""
        invalid_passwords = [
            "password!",    # Contains '!'
            "test space",   # Contains space
            "test.dot",     # Contains '.'
            "test,comma",   # Contains ','
            "test(paren)",  # Contains parentheses
            "test[bracket]", # Contains brackets
            "test{brace}",  # Contains braces
            "test<angle>",  # Contains angle brackets
            "test|pipe",    # Contains pipe
            "test\\slash",  # Contains backslash
            "test/slash",   # Contains forward slash
            "test?question", # Contains question mark
            "test:colon",   # Contains colon
            "test;semicolon", # Contains semicolon
            "test\"quote",  # Contains double quote
            "test'quote",   # Contains single quote
            "test~tilde",   # Contains tilde
            "test`backtick", # Contains backtick
        ]
        
        for pwd in invalid_passwords:
            assert not is_valid_password(pwd), f"Password '{pwd}' should be invalid (forbidden chars)"

    def test_regex_pattern_directly(self):
        """Test the regex pattern directly."""
        # Valid pattern
        assert re.fullmatch(password_regex, "Test123@")
        
        # Invalid patterns
        assert not re.fullmatch(password_regex, "Test!")
        assert not re.fullmatch(password_regex, "Test 123")


class TestPasswordPeppering:
    """Test cases for password peppering functionality."""

    def test_pepper_password_basic(self):
        """Test basic pepper functionality."""
        password_str = "testpassword"
        peppered = pepper_password(password_str)
        
        expected = f"{pepper}{password_str}".encode("utf-8")
        assert peppered == expected
        assert isinstance(peppered, bytes)

    def test_pepper_password_empty(self):
        """Test peppering empty password."""
        peppered = pepper_password("")
        expected = pepper.encode("utf-8")
        assert peppered == expected

    def test_pepper_password_special_chars(self):
        """Test peppering password with special characters."""
        password_str = "test@#$%^&+="
        peppered = pepper_password(password_str)
        
        expected = f"{pepper}{password_str}".encode("utf-8")
        assert peppered == expected

    def test_pepper_consistency(self):
        """Test that peppering the same password always returns the same result."""
        password_str = "consistent_test"
        peppered1 = pepper_password(password_str)
        peppered2 = pepper_password(password_str)
        
        assert peppered1 == peppered2


class TestPasswordHashing:
    """Test cases for password hashing functionality."""

    def test_hash_password_returns_bytes(self):
        """Test that hash_password returns bytes."""
        hashed = hash_password("testpassword")
        assert isinstance(hashed, bytes)

    def test_hash_password_different_results(self):
        """Test that hashing the same password produces different results due to salt."""
        password_str = "testpassword"
        hash1 = hash_password(password_str)
        hash2 = hash_password(password_str)
        
        # Should be different due to different salts
        assert hash1 != hash2

    def test_hash_password_bcrypt_format(self):
        """Test that the hash follows bcrypt format."""
        hashed = hash_password("testpassword")
        
        # bcrypt hashes start with $2b$ and have specific length
        assert hashed.startswith(b"$2b$")
        assert len(hashed) == 60  # Standard bcrypt hash length

    def test_hash_password_empty(self):
        """Test hashing empty password."""
        hashed = hash_password("")
        assert isinstance(hashed, bytes)
        assert hashed.startswith(b"$2b$")


class TestPasswordMatching:
    """Test cases for password matching functionality."""

    def test_password_matches_correct(self):
        """Test that correct password matches its hash."""
        password_str = "testpassword123"
        hashed = hash_password(password_str)
        
        assert password_matches(password_str, hashed)

    def test_password_matches_incorrect(self):
        """Test that incorrect password doesn't match hash."""
        password_str = "testpassword123"
        wrong_password = "wrongpassword123"
        hashed = hash_password(password_str)
        
        assert not password_matches(wrong_password, hashed)

    def test_password_matches_empty(self):
        """Test matching empty passwords."""
        hashed = hash_password("")
        
        assert password_matches("", hashed)
        assert not password_matches("notempty", hashed)

    def test_password_matches_case_sensitive(self):
        """Test that password matching is case sensitive."""
        password_str = "TestPassword"
        hashed = hash_password(password_str)
        
        assert password_matches("TestPassword", hashed)
        assert not password_matches("testpassword", hashed)
        assert not password_matches("TESTPASSWORD", hashed)

    def test_password_matches_special_chars(self):
        """Test matching passwords with special characters."""
        password_str = "Test@Pass#123"
        hashed = hash_password(password_str)
        
        assert password_matches(password_str, hashed)
        assert not password_matches("Test@Pass#124", hashed)


class TestPasswordClass:
    """Test cases for the password class functionality."""

    def test_password_class_initialization(self):
        """Test password class initialization."""
        pwd = password("testpassword")
        assert pwd.password == "testpassword"

    def test_password_class_peppered_password(self):
        """Test peppered_password property."""
        pwd = password("testpassword")
        expected = f"{password.pepper}testpassword".encode("utf-8")
        
        assert pwd.peppered_password == expected
        assert isinstance(pwd.peppered_password, bytes)

    def test_password_class_is_valid(self):
        """Test is_valid property."""
        # Valid password
        valid_pwd = password("ValidPass123")
        assert valid_pwd.is_valid
        
        # Invalid password (too short)
        invalid_pwd = password("short")
        assert not invalid_pwd.is_valid
        
        # Invalid password (forbidden chars)
        invalid_pwd2 = password("invalid!")
        assert not invalid_pwd2.is_valid

    def test_password_class_hash(self):
        """Test hash property."""
        pwd = password("testpassword")
        hashed = pwd.hash
        
        assert isinstance(hashed, bytes)
        assert hashed.startswith(b"$2b$")
        assert len(hashed) == 60

    def test_password_class_hash_different_instances(self):
        """Test that different instances produce different hashes."""
        pwd1 = password("testpassword")
        pwd2 = password("testpassword")
        
        hash1 = pwd1.hash
        hash2 = pwd2.hash
        
        # Should be different due to different salts
        assert hash1 != hash2

    def test_password_class_matches(self):
        """Test matches method."""
        pwd = password("testpassword123")
        hashed = pwd.hash
        
        # Same password should match
        assert pwd.matches(hashed)
        
        # Different password should not match
        different_pwd = password("differentpassword")
        assert not different_pwd.matches(hashed)

    def test_password_class_constants(self):
        """Test that class constants match module constants."""
        assert password.pepper == pepper
        assert password.hashing_rounds == hashing_rounds
        assert password.password_regex == password_regex
        # Note: password_regex_description has different whitespace indentation in class vs module
        # We'll test that both contain the same essential content
        class_desc_lines = [line.strip() for line in password.password_regex_description.split('\n') if line.strip()]
        module_desc_lines = [line.strip() for line in password_regex_description.split('\n') if line.strip()]
        assert class_desc_lines == module_desc_lines


class TestPasswordRegexDescription:
    """Test cases for password regex description."""

    def test_regex_description_exists(self):
        """Test that password regex description exists and is a string."""
        assert isinstance(password_regex_description, str)
        assert len(password_regex_description.strip()) > 0

    def test_regex_description_mentions_requirements(self):
        """Test that description mentions key requirements."""
        description = password_regex_description.lower()
        
        assert "8" in description  # Minimum length
        assert "39" in description  # Maximum length
        assert "character" in description


class TestPasswordConstants:
    """Test cases for password-related constants."""

    def test_pepper_constant(self):
        """Test pepper constant."""
        assert isinstance(pepper, str)
        assert len(pepper) > 0
        # Pepper should be 32 chars as mentioned in comment
        assert len(pepper) == 32

    def test_hashing_rounds_constant(self):
        """Test hashing rounds constant."""
        assert isinstance(hashing_rounds, int)
        assert hashing_rounds == 11  # As specified in code

    def test_password_regex_constant(self):
        """Test password regex constant."""
        assert isinstance(password_regex, str)
        assert len(password_regex) > 0
        
        # Test that it's a valid regex
        try:
            re.compile(password_regex)
        except re.error:
            pytest.fail("password_regex is not a valid regex pattern")


class TestIntegrationScenarios:
    """Integration test cases combining multiple functions."""

    def test_full_password_workflow(self):
        """Test complete password workflow: validate -> hash -> check."""
        password_str = "SecurePass123@"
        
        # 1. Validate password
        assert is_valid_password(password_str)
        
        # 2. Hash password
        hashed = hash_password(password_str)
        
        # 3. Verify password matches
        assert password_matches(password_str, hashed)
        
        # 4. Verify wrong password doesn't match
        assert not password_matches("WrongPass123@", hashed)

    def test_class_vs_functional_consistency(self):
        """Test that class-based and functional approaches are consistent."""
        password_str = "TestConsistency123"
        
        # Functional approach
        func_peppered = pepper_password(password_str)
        func_hashed = hash_password(password_str)
        func_valid = is_valid_password(password_str)
        
        # Class approach
        pwd_obj = password(password_str)
        class_peppered = pwd_obj.peppered_password
        class_hashed = pwd_obj.hash
        class_valid = pwd_obj.is_valid
        
        # Peppered passwords should be the same
        assert func_peppered == class_peppered
        
        # Validation should be the same
        assert func_valid == class_valid
        
        # Both hashes should work with both matching functions
        assert password_matches(password_str, func_hashed)
        assert password_matches(password_str, class_hashed)
        assert pwd_obj.matches(func_hashed)

    def test_edge_case_passwords(self):
        """Test edge case passwords."""
        edge_cases = [
            "12345678",     # Minimum length, digits only
            "ABCDEFGH",     # Minimum length, uppercase only
            "abcdefgh",     # Minimum length, lowercase only
            "@#$%^&+=",     # Minimum length, special chars only (invalid - too short)
            "A" + "@#$%^&+=" + "1234567890" + "a" * 18,  # Maximum length with all char types
        ]
        
        for pwd in edge_cases:
            if is_valid_password(pwd):
                hashed = hash_password(pwd)
                assert password_matches(pwd, hashed)
                
                # Test with class too
                pwd_obj = password(pwd)
                assert pwd_obj.is_valid
                assert pwd_obj.matches(pwd_obj.hash)