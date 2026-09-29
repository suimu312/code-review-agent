"""示例代码：用于被 Code Review Agent 审查。
这个文件故意包含一些常见问题，方便演示审查效果。
"""

import os
import sys


def calculate_average(numbers):
    total = 0
    for n in numbers:
        total = total + n
    avg = total / len(numbers)
    return avg


def find_max(numbers):
    max_val = numbers[0]
    for n in numbers:
        if n > max_val:
            max_val = n
    return max_val


def process_data(data):
    result = []
    for item in data:
        if item > 0:
            transformed = item * 2
            result.append(transformed)
        else:
            transformed = item * -1
            result.append(transformed)
    # TODO: 这里需要处理 None 值
    return result


def main():
    nums = [1, 2, 3, 4, 5]
    avg = calculate_average(nums)
    print("Average:", avg)

    max_val = find_max(nums)
    print("Max:", max_val)

    processed = process_data(nums)
    print("Processed:", processed)


if __name__ == "__main__":
    main()
