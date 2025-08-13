import os

BASE_DIR = os.path.dirname(__file__)
PASSWORD_FILE = os.path.join(BASE_DIR, 'password.txt')
RESULT_FILE = os.path.join(BASE_DIR, 'result.txt')


def caesar_cipher_decode(target_text, shift):
    result = []

    for c in target_text:
        if 'a' <= c <= 'z':
            result.append(chr(ord('a') + ((ord(c) - ord('a') + shift) % 26)))
        else:
            result.append(c)

    return ''.join(result)


def read_password():
    try:
        with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
            line = f.read().strip()
            return line.split(':', 1)[1].strip()
    except FileNotFoundError:
        print('파일을 찾을 수 없습니다.')
        return None
    except Exception:
        print('파일을 읽는 도중 문제가 발생했습니다.')
        return None


def save_result(selected):
    with open(RESULT_FILE, 'w', encoding='utf-8') as f:
        f.write(selected)
    print(f"'{selected}'를 result.txt에 결과를 저장하였습니다.")


def main():
    target_text = read_password()
    if target_text is None:
        return

    decoded_list = []
    for shift in range(1, 27):
        decoded = caesar_cipher_decode(target_text, shift)
        print(f'{shift}: {decoded}')
        decoded_list.append(decoded)

    cmd = input('제대로 해독된 shift 값을 입력하세요. 식별이 불가능하다면 0 을 입력하세요: ').strip()

    if not cmd:
        print('잘못된 입력입니다.')
        return

    if not cmd.isdigit():
        print('잘못된 입력값입니다.')
        return

    shift = int(cmd)

    if not (0 <= shift <= 26):
        print('잘못된 입력값입니다.')
        return

    if shift == 0:
        print('암호 식별을 실패하였습니다.')
        return

    selected = decoded_list[shift - 1]
    print(f'식별 결과: {selected}')
    save_result(selected)


if __name__ == '__main__':
    main()
