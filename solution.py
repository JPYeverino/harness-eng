"""Two Sum — hash-map implementation (O(n) time, O(n) space)."""


def two_sum(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}  # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    raise ValueError("No solution found")
