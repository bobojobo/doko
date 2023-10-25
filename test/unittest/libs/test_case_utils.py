import pytest

from doko.libs.case_utils import camel_to_snake


class TestCamelToSnake:
    """Test cases for the camel_to_snake function."""

    def test_simple_camel_case(self):
        """Test basic CamelCase conversion."""
        assert camel_to_snake("CamelCase") == "camel_case"
        assert camel_to_snake("SimpleTest") == "simple_test"
        assert camel_to_snake("HttpResponse") == "http_response"

    def test_single_word(self):
        """Test single word inputs."""
        assert camel_to_snake("word") == "word"
        assert camel_to_snake("Word") == "word"
        assert camel_to_snake("WORD") == "w_o_r_d"

    def test_multiple_consecutive_capitals(self):
        """Test strings with consecutive capital letters."""
        assert camel_to_snake("XMLHttpRequest") == "x_m_l_http_request"
        assert camel_to_snake("HTTPSConnection") == "h_t_t_p_s_connection"
        assert camel_to_snake("URLParser") == "u_r_l_parser"

    def test_mixed_case_patterns(self):
        """Test various mixed case patterns."""
        assert camel_to_snake("someVariableName") == "some_variable_name"
        assert camel_to_snake("aVeryLongTestCase") == "a_very_long_test_case"
        assert camel_to_snake("getHTTPResponseCode") == "get_h_t_t_p_response_code"

    def test_edge_cases(self):
        """Test edge cases and special inputs."""
        assert camel_to_snake("") == ""
        assert camel_to_snake("a") == "a"
        assert camel_to_snake("A") == "a"
        assert camel_to_snake("AB") == "a_b"

    def test_already_snake_case(self):
        """Test inputs that are already in snake_case."""
        assert camel_to_snake("snake_case") == "snake_case"
        assert camel_to_snake("already_converted") == "already_converted"
        assert camel_to_snake("test_function_name") == "test_function_name"

    def test_numbers_in_string(self):
        """Test strings containing numbers."""
        assert camel_to_snake("version2Update") == "version2_update"
        assert camel_to_snake("test123Case") == "test123_case"
        assert camel_to_snake("api2Response") == "api2_response"

    def test_special_characters(self):
        """Test strings with special characters (should remain unchanged where present)."""
        assert camel_to_snake("test-Case") == "test-_case"
        assert camel_to_snake("api.Response") == "api._response"
        
    def test_real_world_examples(self):
        """Test real-world class and method names."""
        assert camel_to_snake("GamePlayer") == "game_player"
        assert camel_to_snake("CardDeck") == "card_deck"
        assert camel_to_snake("SessionToken") == "session_token"
        assert camel_to_snake("DatabaseConnection") == "database_connection"
        assert camel_to_snake("responseDto") == "response_dto"
        assert camel_to_snake("requestHandler") == "request_handler"