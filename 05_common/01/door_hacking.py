import os
import zipfile
import itertools
import string
import time
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
SECRET_FILE = os.path.join(BASE_DIR, 'emergency_storage_key.zip')
PASSWORD_FILE = os.path.join(BASE_DIR, 'password.txt')

PASSWORD_SET = string.digits + string.ascii_lowercase
PASSWORD_LEN = 6


def unlock_zip():
    start_time = time.time()
    start_datetime = datetime.now()
    print(f"시작 시간: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        with zipfile.ZipFile(SECRET_FILE, 'r') as zf:
            attempt_count = 0

            for password_tuple in itertools.product(PASSWORD_SET, repeat=PASSWORD_LEN):
                password = ''.join(password_tuple)
                attempt_count += 1

                if attempt_count % 1000 == 0:
                    elapsed_time = time.time() - start_time
                    print(f'시도 횟수: {attempt_count:,} | '
                          f'현재 암호: {password} | '
                          f'진행 시간: {elapsed_time:.2f}초')

                try:
                    zf.extractall(pwd=password.encode('utf-8'))

                    end_time = time.time()
                    elapsed_time = end_time - start_time

                    print('------------------------------')
                    print('암호가 해독되었습니다.')
                    print(f'발견된 암호: {password}')
                    print(f'총 시도 횟수: {attempt_count:,}')
                    print(f"총 소요 시간: {elapsed_time:.2f}초")
                    print('------------------------------')

                    with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
                        f.write(f'ZIP 파일 암호: {password}\n')

                    print(f"암호가 '{PASSWORD_FILE}' 파일에 저장되었습니다.")
                    return password

                except (RuntimeError, zipfile.BadZipFile):
                    continue
                except Exception as e:
                    continue

            print('\n모든 조합을 시도했지만, 암호 찾기를 실패하였습니다.')
            return None

    except FileNotFoundError:
        print(f"오류: '{SECRET_FILE}' 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f'ZIP 파일을 여는 중 오류 발생: {e}')
        return None


def main():
    password = unlock_zip()

    if not password:
        print('암호 해독에 실패하였습니다.')


if __name__ == '__main__':
    main()
