import pytest
from two_sum import two_sum


def test_basic_example() -> None:
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]


def test_answer_not_at_start() -> None:
    assert two_sum([3, 2, 4], 6) == [1, 2]


def test_duplicate_values() -> None:
    assert two_sum([3, 3], 6) == [0, 1]


def test_negative_numbers() -> None:
    assert two_sum([-1, -2, -3, -4, -5], -8) == [2, 4]


def test_result_is_length_two() -> None:
    result = two_sum([1, 5, 3, 7], 8)
    assert len(result) == 2


def test_indices_sum_to_target() -> None:
    nums = [4, 6, 2, 8]
    target = 10
    i, j = two_sum(nums, target)
    assert nums[i] + nums[j] == target


def test_same_index_not_reused() -> None:
    # 5+5=10 but there is only one 5; 3+7=10 is the valid pair
    nums = [5, 3, 7]
    target = 10
    i, j = two_sum(nums, target)
    assert i != j
    assert nums[i] + nums[j] == target
