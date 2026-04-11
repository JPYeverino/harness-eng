from solution import contains_duplicate


def test_has_duplicate():
    assert contains_duplicate([1, 2, 3, 1]) is True


def test_no_duplicate():
    assert contains_duplicate([1, 2, 3, 4]) is False


def test_single_element():
    assert contains_duplicate([1]) is False


def test_empty():
    assert contains_duplicate([]) is False


def test_all_same():
    assert contains_duplicate([5, 5, 5, 5]) is True


def test_duplicate_not_adjacent():
    assert contains_duplicate([1, 3, 2, 4, 1]) is True
