def binary_search(array, target, low, high):
    if low > high:
        return False

    mid = (low + high) // 2
    if target == array[mid]:
        return True
    elif target < array[mid]:
        return binary_search(array, target, low, mid - 1)
    else:
        return binary_search(array, target, mid + 1, high)


def main():
    array = [1, 3, 7, 10]
    target = 3
    low = 0
    high = len(array) - 1

    is_found = binary_search(array, target, low, high)
    print(is_found)


if __name__ == '__main__':
    main()