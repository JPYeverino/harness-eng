from solution import two_sum


def test_example():
    assert two_sum([2, 7, 11, 15], 9) == [0, 1] or two_sum([2, 7, 11, 15], 9) == [1, 0]


def test_middle_elements():
    result = two_sum([3, 2, 4], 6)
    assert sorted(result) == [1, 2]


def test_same_value_different_indices():
    result = two_sum([3, 3], 6)
    assert sorted(result) == [0, 1]


def test_negative_numbers():
    result = two_sum([-1, -2, -3, -4, -5], -8)
    assert sorted(result) == [2, 4]


def test_larger_array():
    result = two_sum([1, 5, 3, 8, 2], 10)
    assert sorted(result) == [3, 4]
