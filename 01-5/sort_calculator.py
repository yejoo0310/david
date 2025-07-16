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
    ans = s.copy()
    n = len(ans)

    for i in range(n):
        for j in range(0, n - i -1):
            if ans[j] > ans[j + 1]:
                ans[j], ans[j + 1] = ans[j + 1], ans[j]
    
    return ans

# 정렬된 숫자 출력
def print_numbers(s):
    print("Sorted: ", end="")
    for number in s:
        print(number, " ", end="")

def main():
    a = input("Enter numbers: ")
    inputs = a.split()
    numbers = to_float(inputs)

    if numbers is None:
        return

    numbers = sort_numbers(numbers)
    print_numbers(numbers)

if __name__ == "__main__":
    main()