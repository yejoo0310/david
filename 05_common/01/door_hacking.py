import os
import zipfile
import itertools
import string
import time
import math
from datetime import datetime
from typing import Optional

BASE_DIR = os.path.dirname(__file__)
SECRET_FILE = os.path.join(BASE_DIR, 'emergency_storage_key.zip')
PASSWORD_FILE = os.path.join(BASE_DIR, 'password.txt')

PASSWORD_SET = string.digits + string.ascii_lowercase
PASSWORD_LEN = 6
REPORT_EVERY = 50_000


def now_str() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def fmt_duration(sec: float) -> str:
    if sec < 60:
        return f"{sec:.1f}s"
    m, s = divmod(int(sec), 60)
    if m < 60:
        return f"{m}m{s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m{s:02d}s"


def try_password(zf: zipfile.ZipFile, member: zipfile.ZipInfo, pwd: str) -> bool:
    try:
        with zf.open(member, pwd=pwd.encode('utf-8')) as f:
            _ = f.read(1)
        return True
    except RuntimeError:
        return False
    except Exception:
        return False


def unlock_zip() -> Optional[str]:
    print(f'시작 시간: {now_str()}')

    if not os.path.exists(SECRET_FILE):
        print('zip 파일을 찾을 수 없습니다.')
        return None

    start = time.perf_counter()
    attempts = 0

    try:
        with zipfile.ZipFile(SECRET_FILE) as zf:
            infos = zf.infolist()
            if not infos:
                print('zip 내부가 비어있습니다.')
                return None
            member = infos[0]

            for tup in itertools.product(PASSWORD_SET, repeat=PASSWORD_LEN):
                pwd = ''.join(tup)
                attempts += 1

                if try_password(zf, member, pwd):
                    elapsed = time.perf_counter() - start
                    print('-----------------------------')
                    print('암호가 해독되었습니다!')
                    print(f'암호: {pwd}')
                    print(f'총 시도 횟수: {attempts:,}')
                    print(f'총 소요 시간: {elapsed:.2f}초')
                    print('-----------------------------')

                    with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
                        f.write(f'zip 파일 암호: {pwd}\n')
                    print('password.txt에 암호를 저장하였습니다.')
                    return pwd

                elapsed_time = time.perf_counter() - start
                print(
                    f'암호 = {pwd}, 시도 횟수 = {attempts}, 소요 시간 = {elapsed_time}')

        elapsed = time.perf_counter() - start
        print(f'\n모든 조합을 시도했지만 실패했습니다. (총 경과 {fmt_duration(elapsed)})')
        return None

    except zipfile.BadZipFile:
        print('손상된 ZIP 파일입니다.')
        return None
    except KeyboardInterrupt:
        elapsed = time.perf_counter() - start
        print(f'\n중단됨. 현재 시도={attempts}, 경과={fmt_duration(elapsed)}')
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
