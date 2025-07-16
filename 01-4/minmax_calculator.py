def main():
    a = input("Enter numbers: ")
    inputs = a.split()
    numbers = to_float(inputs)
    if numbers is None:
        return
    max_num = find_max(numbers)
    min_num = find_min(numbers)

    print("Min:", min_num, ", Max:", max_num)

# 입력 받은 문자들을 숫자로 변환
def to_float(s):
    numbers = []
    for num in s:
        try:
            number = float(num)
            numbers.append(number)
        except ValueError:
            print("Invalid input.")
            return None
    return numbers

# 최대값 찾기
def find_max(s):
    max = s[0]
    for num in s:
        if num > max:
            max = num
    return max

# 최소값 찾기
def find_min(s):
    min = s[0]
    for num in s:
        if num < min:
            min = num
            continue
    return min

if __name__ == "__main__":
    main()