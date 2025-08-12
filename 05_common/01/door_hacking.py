import os
import zipfile
import itertools
import string
import time
import math
from datetime import datetime
from typing import Optional, Iterator, List, Set, Tuple

from multiprocessing import Process, Event, Value, Lock, cpu_count

BASE_DIR = os.path.dirname(__file__)
SECRET_FILE = os.path.join(BASE_DIR, 'emergency_storage_key.zip')
PASSWORD_FILE = os.path.join(BASE_DIR, 'password.txt')

PASSWORD_SET = string.digits + string.ascii_lowercase
PASSWORD_LEN = 6

REPORT_SEC = 3.0              # 진행 로그(시간 기준)
COUNTER_BATCH = 10_000        # 카운터를 이만큼 누적 후에만 공유메모리에 반영(락 경합 ↓)
MAX_PROCS = 32                # 과도 생성 방지 상한선


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


def try_password(zf, member, pwd):
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

    total_space = len(PASSWORD_SET) ** PASSWORD_LEN
    start = time.perf_counter()
    attempts = 0

    try:
        with zipfile.ZipFile(SECRET_FILE) as zf:
            infos = zf.infolist()
            if not infos:
                print('zip 내부가 비어있습니다.')
                return None
            member = min(infos, key=lambda i: (i.file_size or 0))

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
                    return pwd

                if attempts % 50_000 == 0:
                    elapsed = time.perf_counter() - start
                    rate = attempts / elapsed if elapsed > 0 else 0.0
                    prog = attempts / total_space * 100
                    remain = max(total_space - attempts, 0)
                    eta = remain / rate if rate > 0 else math.inf
                    eta_str = "∞" if not math.isfinite(
                        eta) else fmt_duration(eta)
                    print(f'[single] 시도횟수={attempts:,}, 경과시간={fmt_duration(elapsed)}, '
                          f'진행률={prog:.6f}%')
        print('실패: 전체 공간 소진')
        return None
    except KeyboardInterrupt:
        elapsed = time.perf_counter() - start
        print(f'\n중단됨. 현재 시도={attempts:,}, 경과={fmt_duration(elapsed)}')
        return None


def try_password_bytes(zf, member, pwd_bytes):
    try:
        with zf.open(member, pwd=pwd_bytes) as f:
            _ = f.read(1)
        return True
    except RuntimeError:
        return False
    except Exception:
        return False


PASSWORD_SET_BYTES: Tuple[bytes, ...] = tuple(
    bytes([c]) for c in (PASSWORD_SET.encode()))


def _worker_full(zip_path: str,
                 member_name: str,
                 two_char_prefixes: List[bytes],
                 found: Event,
                 attempts_shared: Value,
                 lock: Lock):
    try:
        with zipfile.ZipFile(zip_path) as zf:
            member_info = zf.getinfo(member_name)  # 워커 시작 시 1회만
            tail_repeat = PASSWORD_LEN - 2
            local = 0
            for pfx in two_char_prefixes:
                for tail in itertools.product(PASSWORD_SET_BYTES, repeat=tail_repeat):
                    if found.is_set():
                        # 남들이 찾았으면 즉시 종료
                        if local:
                            with lock:
                                attempts_shared.value += local
                        return
                    pwd_bytes = pfx + b''.join(tail)
                    if try_password_bytes(zf, member_info, pwd_bytes):
                        with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
                            f.write(f'zip 파일 암호: {pwd_bytes.decode()}\n')
                        print(f'[MP] 성공! 암호={pwd_bytes.decode()}')
                        found.set()
                        if local:
                            with lock:
                                attempts_shared.value += local
                        return
                    local += 1
                    # 카운터는 배치로만 반영(락 경합 최소화)
                    if local >= COUNTER_BATCH:
                        with lock:
                            attempts_shared.value += local
                        local = 0
            # 잔여 반영
            if local:
                with lock:
                    attempts_shared.value += local
    except KeyboardInterrupt:
        return


def unlock_zip_fast_mp(procs: int = 0) -> Optional[str]:
    """
    더 빠른 알고리즘:
      - ZIP 내부 '가장 작은 파일'로 검증(I/O 최소화)
      - 두 글자(prefix 2자리) 분할 → 36*36=1296 버킷을 프로세스에 균등 분배
      - 비밀번호 bytes 조합으로 인코딩 비용 제거
    """
    print(f'시작 시간: {now_str()}')

    if not os.path.exists(SECRET_FILE):
        print('zip 파일을 찾을 수 없습니다.')
        return None

    total_space = len(PASSWORD_SET) ** PASSWORD_LEN  # 36^6
    start = time.perf_counter()

    # 멤버 이름(가장 작은 파일)만 사전 확보
    try:
        with zipfile.ZipFile(SECRET_FILE) as zf:
            infos = zf.infolist()
            if not infos:
                print('zip 내부가 비어있습니다.')
                return None
            member_name = min(infos, key=lambda i: (i.file_size or 0)).filename
    except zipfile.BadZipFile:
        print('손상된 ZIP 파일입니다.')
        return None

    if procs <= 0:
        procs = max(1, min(cpu_count(), MAX_PROCS))
    print(f'프로세스={procs} (2글자 prefix 분할)')

    # 2글자 prefix 1296개 생성 → 균등 분배
    first = PASSWORD_SET.encode()
    two_prefixes: List[bytes] = []
    for a in first:
        for b in first:
            two_prefixes.append(bytes([a, b]))

    buckets: List[List[bytes]] = [[] for _ in range(procs)]
    for i, pfx in enumerate(two_prefixes):
        buckets[i % procs].append(pfx)

    found = Event()
    attempts_shared = Value('Q', 0)
    lock = Lock()

    ps: List[Process] = []
    for b in buckets:
        if not b:
            continue
        p = Process(target=_worker_full, args=(
            SECRET_FILE, member_name, b, found, attempts_shared, lock))
        p.start()
        ps.append(p)

    last = 0.0
    try:
        while any(p.is_alive() for p in ps) and not found.is_set():
            now = time.perf_counter()
            if now - last >= REPORT_SEC:
                last = now
                tried = attempts_shared.value
                elapsed = now - start
                rate = tried / elapsed if elapsed > 0 else 0.0
                prog = tried / total_space * 100
                remain = max(total_space - tried, 0)
                eta = remain / rate if rate > 0 else math.inf
                eta_str = "∞" if not math.isfinite(eta) else fmt_duration(eta)
                print(f'[MP] 시도={tried:,}, 경과={fmt_duration(elapsed)}, 처리율={rate:,.0f}/s, '
                      f'진행률={prog:.6f}%, ETA={eta_str}')
            time.sleep(0.2)
    except KeyboardInterrupt:
        print('\n중단 요청')
    finally:
        for p in ps:
            p.join(timeout=0.2)

    if found.is_set():
        elapsed = time.perf_counter() - start
        print(f'[MP] 완료. 총 소요 {fmt_duration(elapsed)}')
        try:
            with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
                return f.read().strip().split(':', 1)[-1].strip()
        except Exception:
            return None

    print('[MP] 실패: 전체 공간 소진')
    return None


def main():
    password = unlock_zip_fast_mp(procs=4)  # 0=자동 코어 수
    # 필요 시 단일 프로세스 테스트:
    # password = unlock_zip()

    if not password:
        print('암호 해독에 실패하였습니다.')


if __name__ == '__main__':
    main()
