"""Tests for Two Sum (task-1)."""
import pytest
from solution import two_sum


def test_example_basic():
    assert sorted(two_sum([2, 7, 11, 15], 9)) == [0, 1]


def test_answer_at_end():
    assert sorted(two_sum([3, 2, 4], 6)) == [1, 2]


def test_duplicate_values():
    assert sorted(two_sum([3, 3], 6)) == [0, 1]


def test_negative_numbers():
    assert sorted(two_sum([-1, -2, -3, -4, -5], -8)) == [2, 4]


def test_larger_input():
    nums = list(range(100))
    result = sorted(two_sum(nums, 197))
    assert result == [98, 99]


def test_returns_indices_not_values():
    nums = [5, 75, 25]
    result = sorted(two_sum(nums, 100))
    assert result == [1, 2]
