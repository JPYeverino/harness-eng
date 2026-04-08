def two_sum(nums: list[int], target: int) -> list[int]:
    """Return indices of the two numbers that add up to target.

    Optimal: O(n) time, O(n) space.
    Single pass: for each element look up its complement in a hash map,
    then store the current value -> index. Looking up before inserting
    ensures the same index is never reused.
    """
    seen: dict[int, int] = {}  # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i

    raise ValueError("No solution found — violates problem guarantee")
