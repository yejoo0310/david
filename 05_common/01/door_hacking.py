import os
import zipfile
import itertools
import string
import time
from datetime import datetime
from datetime import timedelta
import signal

from multiprocessing import Process, Event, Queue

BASE_DIR = os.path.dirname(__file__)
SECRET_FILE = os.path.join(BASE_DIR, 'emergency_storage_key.zip')
PASSWORD_FILE = os.path.join(BASE_DIR, 'password.txt')

PASSWORD_SET = string.digits + string.ascii_lowercase
PASSWORD_LEN = 6

BATCH_SIZE = 100


def try_password_batch(zf, member, pwd_batch):
    for pwd in pwd_batch:
        try:
            with zf.open(member, pwd=pwd.encode('utf-8')) as f:
                _ = f.read(1)
            return pwd
        except RuntimeError:
            continue
        except Exception:
            continue
    return None


def worker_process(process_id, prefixes, found_event, result_queue, progress_queue):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        with zipfile.ZipFile(SECRET_FILE) as zf:
            infos = zf.infolist()
            if not infos:
                return
            member = infos[0]

            attempts = 0
            tail_len = PASSWORD_LEN - len(prefixes[0])
            batch = [] 

            for pfx in prefixes:
                if found_event.is_set():
                    break

                for tail in itertools.product(PASSWORD_SET, repeat=tail_len):
                    if found_event.is_set():
                        break

                    pwd = pfx + ''.join(tail)
                    batch.append(pwd)
                    attempts += 1

                    if len(batch) >= BATCH_SIZE:
                        result = try_password_batch(zf, member, batch)
                        if result:
                            found_event.set()
                            result_queue.put((result, attempts))
                            return
                        batch = []

                    if attempts % (100000 // len(prefixes) + 1) == 0:
                        progress_queue.put((process_id, attempts))

                    if attempts % 5000 == 0:
                        time.sleep(0.001)

            if batch and not found_event.is_set():
                result = try_password_batch(zf, member, batch)
                if result:
                    found_event.set()
                    result_queue.put((result, attempts))
                    return

    except Exception as e:
        print(f'프로세스 {process_id}에서 오류 발생: {e}')


def unlock_zip():
    print(
        f"시작 시간: {datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f'배치 크기: {BATCH_SIZE} (처리 최적화 적용)')

    if not os.path.exists(SECRET_FILE):
        print('zip 파일을 찾을 수 없습니다.')
        return None

    total_space = len(PASSWORD_SET) ** PASSWORD_LEN
    start = time.perf_counter()

    num_processes = 4
    print(f'사용할 프로세스 수: {num_processes}개')

    found_event = Event()
    result_queue = Queue()
    progress_queue = Queue()

    prefixes = [a + b for a in PASSWORD_SET for b in PASSWORD_SET]
    buckets = [[] for _ in range(num_processes)]
    for i, pfx in enumerate(prefixes):
        buckets[i % num_processes].append(pfx)

    processes = []
    for i in range(num_processes):
        if not buckets[i]:
            continue
        p = Process(target=worker_process,
                    args=(i, buckets[i], found_event, result_queue, progress_queue))
        p.start()
        processes.append(p)

    total_attempts = 0
    process_attempts = [0] * num_processes
    last_update_time = time.perf_counter()

    try:
        while not found_event.is_set() and any(p.is_alive() for p in processes):
            try:
                while not progress_queue.empty():
                    process_id, attempts = progress_queue.get_nowait()
                    process_attempts[process_id] = attempts

                current_total = sum(process_attempts)
                current_time = time.perf_counter()

                if (current_total > total_attempts and
                        (current_time - last_update_time > 3 or current_total - total_attempts > 50000)):

                    total_attempts = current_total
                    elapsed = current_time - start
                    prog = total_attempts / total_space * 100
                    speed = total_attempts / elapsed if elapsed > 0 else 0

                    print(f"시도횟수={total_attempts:,}, 경과시간={str(timedelta(seconds=elapsed)).split('.')[0]}, "
                          f'진행률={prog:.6f}%, 속도={speed:,.0f}/초')
                    last_update_time = current_time

            except:
                pass

            time.sleep(0.2)

    except KeyboardInterrupt:
        print('\n중단 요청을 받았습니다.')

    for p in processes:
        p.join(timeout=1)
        if p.is_alive():
            p.terminate()

    if not result_queue.empty():
        result_data = result_queue.get()
        if isinstance(result_data, tuple):
            pwd, final_attempts = result_data
        else:
            pwd = result_data
            final_attempts = sum(process_attempts)

        elapsed = time.perf_counter() - start
        print('-----------------------------')
        print('암호가 해독되었습니다!')
        print(f'암호: {pwd}')
        print(f'총 시도 횟수: {final_attempts:,}')
        print(f'총 소요 시간: {elapsed:.2f}초')
        print(f'평균 속도: {final_attempts/elapsed:,.0f} passwords/sec')
        print(f'배치 처리 효과: 약 {BATCH_SIZE}개씩 묶어서 처리')
        print('-----------------------------')

        with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
            f.write(f'zip 파일 암호: {pwd}\n')
        return pwd

    elapsed = time.perf_counter() - start
    total_final = sum(process_attempts)
    if found_event.is_set():
        print(
            f"\n중단됨. 현재 시도={total_final:,}, 경과={str(timedelta(seconds=elapsed)).split('.')[0]}")
    else:
        print('암호 찾기를 실패하였습니다.')
    return None


def main():
    password = unlock_zip()

    if not password:
        print('암호 해독에 실패하였습니다.')


if __name__ == '__main__':
    main()
