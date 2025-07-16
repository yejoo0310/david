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

def parse_expression(s):
    parsed = s.split()

    # 예외) 항목 개수가 홀수가 아니면 잘못된 형식으로 입력됨
    if len(parsed) % 2 == 0:
        print("Invalid input.")
        return None
    
    # 예외) 숫자 또는 기호가 제대로 들어오지 않은 경우
    for i, token in enumerate(parsed):
        if i % 2 == 0:
            try:
                parsed[i] = float(token)
            except ValueError:
                print("Invalid input.")
                return None
        else:
            if token not in ['+', '-', '/', '*']:
                print("Invalid input.")
                return None
    
    return parsed

def calculate(parsed):
    while index < len(parsed):
        if parsed[index] == '/' or parsed[index] == '*':
              

def main():
    a = input("Enter numbers: ")
    parsed = parse_expression(a)

    if parsed is None:
        return    

if __name__ == "__main__":
    main()