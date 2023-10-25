import pytest

from doko.libs.functional_utils import exactly_one_not_none, apply_on_non_none


class TestExactlyOneNotNone:
    """Test cases for the exactly_one_not_none function."""

    def test_single_non_none_element(self):
        """Test with exactly one non-None element."""
        assert exactly_one_not_none([None, "test", None]) is True
        assert exactly_one_not_none([42, None, None]) is True
        assert exactly_one_not_none([None, None, True]) is True
        assert exactly_one_not_none([None, 0, None]) is True  # 0 is not None

    def test_no_non_none_elements(self):
        """Test with all None elements."""
        assert exactly_one_not_none([None, None, None]) is False
        assert exactly_one_not_none([None]) is False

    def test_multiple_non_none_elements(self):
        """Test with more than one non-None element."""
        assert exactly_one_not_none([1, 2, None]) is False
        assert exactly_one_not_none(["a", "b", "c"]) is False
        assert exactly_one_not_none([None, 1, 2]) is False
        assert exactly_one_not_none([True, False, None]) is False

    def test_empty_iterable(self):
        """Test with empty iterable."""
        assert exactly_one_not_none([]) is False
        assert exactly_one_not_none(()) is False

    def test_single_element_iterables(self):
        """Test with single element iterables."""
        assert exactly_one_not_none([None]) is False
        assert exactly_one_not_none(["test"]) is True
        assert exactly_one_not_none([0]) is True
        assert exactly_one_not_none([False]) is True  # False is not None

    def test_various_data_types(self):
        """Test with various data types as non-None elements."""
        assert exactly_one_not_none([None, [], None]) is True  # empty list is not None
        assert exactly_one_not_none([None, {}, None]) is True  # empty dict is not None
        assert exactly_one_not_none([None, "", None]) is True  # empty string is not None
        assert exactly_one_not_none([None, set(), None]) is True  # empty set is not None

    def test_with_generator(self):
        """Test with generator expressions."""
        gen = (x if x > 2 else None for x in [1, 2, 3, 4])
        assert exactly_one_not_none(gen) is False  # [None, None, 3, 4] - two non-None

    def test_with_tuple(self):
        """Test with tuple input."""
        assert exactly_one_not_none((None, "test", None)) is True
        assert exactly_one_not_none((1, 2, 3)) is False

    def test_edge_cases_with_falsy_values(self):
        """Test edge cases with falsy but non-None values."""
        assert exactly_one_not_none([None, 0, None]) is True  # 0 is not None
        assert exactly_one_not_none([None, False, None]) is True  # False is not None
        assert exactly_one_not_none([None, "", None]) is True  # empty string is not None
        assert exactly_one_not_none([None, [], None]) is True  # empty list is not None

    def test_real_world_examples(self):
        """Test real-world usage patterns."""
        # Simulating optional parameters where exactly one should be provided
        assert exactly_one_not_none([None, "file.txt", None]) is True  # filename provided
        assert exactly_one_not_none([42, None, None]) is True  # ID provided
        assert exactly_one_not_none([None, None, None]) is False  # nothing provided
        assert exactly_one_not_none(["file.txt", 42, None]) is False  # too many provided


class TestApplyOnNonNone:
    """Test cases for the apply_on_non_none function."""

    def test_single_non_none_element_with_function(self):
        """Test applying function on single non-None element."""
        result = apply_on_non_none([None, 5, None], lambda x: x * 2)
        assert result == 10

        result = apply_on_non_none([None, "hello", None], lambda x: x.upper())
        assert result == "HELLO"

        result = apply_on_non_none([None, [1, 2, 3], None], len)
        assert result == 3

    def test_single_non_none_element_with_builtin_function(self):
        """Test with built-in functions."""
        result = apply_on_non_none([None, "test", None], str.upper)
        assert result == "TEST"

        result = apply_on_non_none([None, 42, None], str)
        assert result == "42"

        result = apply_on_non_none([None, [3, 1, 4], None], sorted)
        assert result == [1, 3, 4]

    def test_no_non_none_elements_raises_exception(self):
        """Test that exception is raised when no non-None elements."""
        with pytest.raises(Exception, match="Invalid iterable: no non-none."):
            apply_on_non_none([None, None, None], lambda x: x)

        with pytest.raises(Exception, match="Invalid iterable: no non-none."):
            apply_on_non_none([], lambda x: x)

    def test_multiple_non_none_elements_raises_exception(self):
        """Test that exception is raised when multiple non-None elements."""
        with pytest.raises(Exception, match="Invalid iterable: more than one non-none."):
            apply_on_non_none([1, 2, None], lambda x: x)

        with pytest.raises(Exception, match="Invalid iterable: more than one non-none."):
            apply_on_non_none(["a", "b", "c"], lambda x: x)

    def test_with_complex_callable(self):
        """Test with more complex callable functions."""
        def complex_func(x):
            if isinstance(x, str):
                return len(x)
            elif isinstance(x, (int, float)):
                return x ** 2
            else:
                return str(type(x))

        result = apply_on_non_none([None, "hello", None], complex_func)
        assert result == 5

        result = apply_on_non_none([None, 3, None], complex_func)
        assert result == 9

        result = apply_on_non_none([None, [1, 2], None], complex_func)
        assert result == "<class 'list'>"

    def test_with_lambda_functions(self):
        """Test with various lambda functions."""
        # Mathematical operations
        result = apply_on_non_none([None, 10, None], lambda x: x + 5)
        assert result == 15

        # String operations
        result = apply_on_non_none([None, "world", None], lambda x: f"hello {x}")
        assert result == "hello world"

        # List operations
        result = apply_on_non_none([None, [1, 2, 3], None], lambda x: x[1])
        assert result == 2

    def test_with_method_calls(self):
        """Test with method calls on objects."""
        class TestObject:
            def __init__(self, value):
                self.value = value
            
            def get_doubled(self):
                return self.value * 2

        obj = TestObject(21)
        result = apply_on_non_none([None, obj, None], lambda x: x.get_doubled())
        assert result == 42

    def test_callable_returns_none(self):
        """Test when the callable itself returns None."""
        result = apply_on_non_none([None, "test", None], lambda x: None)
        assert result is None

    def test_callable_returns_false_or_zero(self):
        """Test when callable returns falsy values that are not None."""
        result = apply_on_non_none([None, "anything", None], lambda x: 0)
        assert result == 0

        result = apply_on_non_none([None, "anything", None], lambda x: False)
        assert result is False

        result = apply_on_non_none([None, "anything", None], lambda x: "")
        assert result == ""

    def test_with_tuple_input(self):
        """Test with tuple as input iterable."""
        result = apply_on_non_none((None, 42, None), lambda x: x / 2)
        assert result == 21.0

    def test_edge_case_with_zero_and_false(self):
        """Test edge cases where 0 and False are treated as non-None."""
        result = apply_on_non_none([None, 0, None], lambda x: x + 1)
        assert result == 1

        result = apply_on_non_none([None, False, None], lambda x: not x)
        assert result is True

    def test_callable_with_side_effects(self):
        """Test callable that has side effects."""
        call_count = []
        
        def counting_func(x):
            call_count.append(x)
            return x * 2
            
        result = apply_on_non_none([None, 5, None], counting_func)
        assert result == 10
        assert call_count == [5]

    def test_exception_in_callable(self):
        """Test behavior when callable raises an exception."""
        def failing_func(x):
            raise ValueError("Test error")
            
        with pytest.raises(ValueError, match="Test error"):
            apply_on_non_none([None, "test", None], failing_func)