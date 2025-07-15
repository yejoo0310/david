from typing import Optional, Tuple


def main():
    a = input("Enter expression: ")

    if a.isdigit():
        a = int(a)
        b = int(input("Enter second number: "))
        operator = input("Enter using operator: ")
    else:
        parsed = parse_expression(a)
        if parsed is None:
            return
        a, b, operator = parsed

    result = calculate(a, b, operator)
    print("result: ", result)


def calculate(a: int, b: int, operator: str):
    match operator:
        case '+':
            result = add(a, b)
        case '-':
            result = subtract(a, b)
        case '*':
            result = multiply(a, b)
        case '/':
            if b == 0:
                print("Error: Division by zero.")
                return
            result = divide(a, b)
        case _:
            print("Invalid operator.")
            return
    return result


def parse_expression(parse_expression: str) -> Optional[Tuple[int, int, str]]:
    elements: list[str] = parse_expression.split()
    if len(elements) != 3:
        print("Invalid expression format.")
        return None

    a_str, operator, b_str = elements

    try:
        a: int = int(a_str)
    except ValueError:
        print("Invalid input number for 'a'.")
        return None

    try:
        b: int = int(b_str)
    except ValueError:
        print("Invalid input number for 'b'.")
        return None

    return a, b, operator


def add(a: int, b: int) -> int:
    return a + b


def subtract(a: int, b: int) -> int:
    return a - b


def multiply(a: int, b: int) -> int:
    return a * b


def divide(a: int, b: int) -> float:
    return a / b


# === 테스트 코드 시작 ===
def run_tests():
    # add() 테스트
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

    # subtract() 테스트
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5
    assert subtract(-2, -3) == 1

    # multiply() 테스트
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6
    assert multiply(0, 100) == 0

    # divide() 테스트
    assert divide(10, 2) == 5.0
    assert divide(3, 2) == 1.5
    assert divide(-6, 3) == -2.0

    # calculate() 기본 연산 테스트
    assert calculate(2, 3, '+') == 5
    assert calculate(5, 2, '-') == 3
    assert calculate(4, 3, '*') == 12
    assert calculate(9, 3, '/') == 3.0

    # calculate() 에러 처리 테스트
    # - 0으로 나눌 때 None 반환
    assert calculate(5, 0, '/') is None
    # - 잘못된 연산자 시 None 반환
    assert calculate(5, 3, '%') is None

    # parse_expression() 정상 케이스
    assert parse_expression("10 + 20") == (10, 20, '+')
    assert parse_expression("30 - 5") == (30, 5, '-')
    assert parse_expression("6 * 7") == (6, 7, '*')

    # parse_expression() 포맷 오류 케이스
    assert parse_expression("1+2") is None
    assert parse_expression("1 2") is None
    assert parse_expression("1 + 2 + 3") is None

    # parse_expression() 숫자 변환 오류 케이스
    assert parse_expression("a + 2") is None
    assert parse_expression("2 + b") is None

    print("🎉 모든 테스트가 성공적으로 통과했습니다! 🎉")


if __name__ == "__main__":
    run_tests()
# === 테스트 코드 끝 ===
