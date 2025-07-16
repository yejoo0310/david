# 입력 받은 문자들을 숫자로 변환
def to_float(s):
    numbers = []

    # 예외처리) 아무것도 입력하지 않았을때
    if not s:
        print("Invalid input.")
        return None

    # 예외처리) 숫자가 아닌 값을 입력했을때
    for num in s:
        try:
            number = float(num)
            numbers.append(number)
        except ValueError:
            print("Invalid input.")
            return None
    return numbers

# 숫자 오름차순으로 정렬
def sort_numbers(s):
    n = len(s)

    for i in range(n):
        for j in range(0, n - i -1):
            if s[j] > s[j + 1]:
                s[j], s[j + 1] = s[j + 1], s[j]
    
    return s

def main():
    a = input("Enter numbers: ")
    inputs = a.split()
    numbers = to_float(inputs)

    if numbers is None:
        return

    numbers = sort_numbers(numbers)
    print("Sorted:", *numbers)


if __name__ == "__main__":
    main()