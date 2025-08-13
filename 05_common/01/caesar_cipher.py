import os

BASE_DIR = os.path.dirname(__file__)
PASSWORD_FILE = os.path.join(BASE_DIR, 'zippassword.txt')
RESULT_FILE = os.path.join(BASE_DIR, 'result.txt')


def caesar_cipher_decode(target_text, shift):
    result = []

    for c in target_text:
        original_c = c
        c = c.lower()
        if 'a' <= c <= 'z':
            result.append(chr(ord('a') + ((ord(c) - ord('a') + shift) % 26)))
        else:
            result.append(original_c)

    return ''.join(result)


def read_password():
    print(f"파일 경로 확인: {PASSWORD_FILE}")
    print(f"파일 존재 여부: {os.path.exists(PASSWORD_FILE)}")

    try:
        with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            print(f"파일 내용: '{content}'")

            if ':' in content:
                return content.split(':', 1)[1].strip()
            else:
                return content

    except FileNotFoundError:
        print(f'파일을 찾을 수 없습니다: {PASSWORD_FILE}')
        return None
    except Exception as e:
        print(f'파일을 읽는 도중 문제가 발생했습니다: {e}')
        return None


def save_result(selected):
    try:
        with open(RESULT_FILE, 'w', encoding='utf-8') as f:
            f.write(selected)
        print(f"'{selected}'를 result.txt에 저장하였습니다.")
    except Exception as e:
        print(f"결과 저장 중 오류 발생: {e}")


def main():
    target_text = read_password()
    if target_text is None:
        return

    decoded_list = []
    for shift in range(1, 27):
        decoded = caesar_cipher_decode(target_text, shift)
        print(f'{shift:2d}: {decoded}')
        decoded_list.append(decoded)

    print("-" * 40)
    cmd = input('제대로 해독된 shift 값을 입력하세요 (1-26, 불가능하면 0): ').strip()

    if not cmd:
        print('잘못된 입력입니다.')
        return

    if not cmd.isdigit():
        print('숫자를 입력해주세요.')
        return

    shift = int(cmd)

    if not (0 <= shift <= 26):
        print('0부터 26 사이의 값을 입력해주세요.')
        return

    if shift == 0:
        print('암호 해독을 취소하였습니다.')
        return

    selected = decoded_list[shift - 1]
    print(f'해독 결과: {selected}')
    save_result(selected)


if __name__ == '__main__':
    main()
