import random
import time
from datetime import datetime
import os
import json
import threading
import platform
import psutil
import multiprocessing as mp

BASE_DIR = os.path.dirname(__file__)


class DummySensor:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': None,
            'mars_base_external_temperature': None,
            'mars_base_internal_humidity': None,
            'mars_base_external_illuminance': None,
            'mars_base_internal_co2': None,
            'mars_base_internal_oxygen': None
        }
        self.log_file = os.path.join(BASE_DIR, 'mars_sensor_log.txt')

    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = round(random.uniform(
            18, 30), 3)
        self.env_values['mars_base_external_temperature'] = round(random.uniform(
            0, 21), 3)
        self.env_values['mars_base_internal_humidity'] = round(
            random.uniform(50, 60), 3)
        self.env_values['mars_base_external_illuminance'] = round(random.uniform(
            500, 715), 3)
        self.env_values['mars_base_internal_co2'] = round(
            random.uniform(0.02, 0.1), 3)
        self.env_values['mars_base_internal_oxygen'] = round(
            random.uniform(4, 7), 3)

    def get_env(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = (
            f'{current_time}, '
            f"{self.env_values['mars_base_internal_temperature']}도, "
            f"{self.env_values['mars_base_external_temperature']}도, "
            f"{self.env_values['mars_base_internal_humidity']}%, "
            f"{self.env_values['mars_base_external_illuminance']}W/m2, "
            f"{self.env_values['mars_base_internal_co2']}%, "
            f"{self.env_values['mars_base_internal_oxygen']}%\n"
        )
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except:
            pass

        return dict(self.env_values)


class MissionComputer():
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': None,
            'mars_base_external_temperature': None,
            'mars_base_internal_humidity': None,
            'mars_base_external_illuminance': None,
            'mars_base_internal_co2': None,
            'mars_base_internal_oxygen': None
        }
        self.ds = DummySensor()
        self._stop_event = threading.Event()
        self.settings_file = os.path.join(BASE_DIR, 'setting.txt')
        self.settings = self.load_settings()

        self.sensor_history = []
        self.last_avg_time = time.time()
        self.avg_interval = 300
        self.data_lock = threading.Lock()

    def get_sensor_data(self, interval_seconds=5, stop_key='q', enable_input=True):
        if enable_input:
            thread = threading.Thread(target=self.wait_stop_key, kwargs={
                "stop_key": stop_key}, daemon=True)
            thread.start()

        try:
            while not self._stop_event.is_set():
                self.ds.set_env()
                sensor_data = self.ds.get_env()
                self.env_values.update(sensor_data)
                self.save_sensor_history(sensor_data)
                print(json.dumps(self.env_values, ensure_ascii=False), flush=True)

                if self.check_5min():
                    self.print_avg()
                    self.last_avg_time = time.time()

                for _ in range(interval_seconds):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)
        except KeyboardInterrupt:
            self._stop_event.set()
        finally:
            print('System stoped')

    def wait_stop_key(self, stop_key='q'):
        while not self._stop_event.is_set():
            try:
                cmd = input().strip().lower()
                if cmd == stop_key.lower():
                    print('시스템을 종료합니다.')
                    self._stop_event.set()
                    break
                elif cmd:
                    print(f"'{stop_key}'를 입력하면 종료됩니다.")
            except (EOFError, KeyboardInterrupt):
                self._stop_event.set()
                break

    def save_sensor_history(self, sensor_data):
        with self.data_lock:
            current_time = time.time()

            self.sensor_history.append({
                'timestamp': current_time,
                'data': sensor_data.copy()
            })

            new_sensor_history = []
            for entry in self.sensor_history:
                if current_time - entry['timestamp'] <= self.avg_interval:
                    new_sensor_history.append(entry)
            self.sensor_history = new_sensor_history

    def calculate_avg(self):
        with self.data_lock:
            if not self.sensor_history:
                return None

            avg = {}
            for key in self.env_values.keys():
                values = []
                for entry in self.sensor_history:
                    if key in entry['data'] and entry['data'][key] is not None:
                        values.append(entry['data'][key])

                if values:
                    avg[f"{key}_5min_avg"] = round(
                        sum(values) / len(values), 3)
                else:
                    avg[f"{key}_5min_avg"] = None

            return avg

    def print_avg(self):
        avg_data = self.calculate_avg()
        if avg_data:
            print('-----------------5분 평균값---------------')
            print(json.dumps(avg_data, ensure_ascii=False))
            print('---------------------------------------')

    def check_5min(self):
        current_time = time.time()
        return (current_time - self.last_avg_time) >= self.avg_interval

    def load_settings(self):
        try:
            if not os.path.exists(self.settings_file):
                raise FileNotFoundError('설정 파일이 없습니다')
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            return settings
        except Exception as e:
            raise RuntimeError('설정 파일 로드 오류')

    def get_mission_computer_info(self):
        try:
            system_info = {}
            settings = self.settings.get('system_info', {})

            if settings.get('os', True):
                system_info['os'] = platform.system()
            if settings.get('os_version', True):
                system_info['os_version'] = platform.version()
            if settings.get('cpu_type', True):
                system_info['cpu_type'] = platform.processor()
            if settings.get('cpu_cores', True):
                system_info['cpu_cores'] = psutil.cpu_count(
                    logical=False) + psutil.cpu_count(logical=True)
            if settings.get('memory_size', True):
                system_info['memory_size'] = round(
                    psutil.virtual_memory().total / (1024 ** 3), 2)

            print(json.dumps(system_info, ensure_ascii=False))
            return system_info
        except Exception as e:
            error_info = {'error': f'시스템 정보 수집 중 오류 발생: {str(e)}'}
            print('시스템 정보 수집 오류')
            print(json.dumps(error_info, ensure_ascii=False, indent=2))
            return error_info

    def get_mission_computer_load(self):
        try:
            load_info = {}
            settings = self.settings.get('load_info', {})

            if settings.get('cpu_usage', True):
                load_info['cpu_usage'] = psutil.cpu_percent(interval=1)

            if settings.get('memory_usage', True):
                load_info['memory_usage'] = psutil.virtual_memory().percent

            print(json.dumps(load_info, ensure_ascii=False))

            return load_info

        except Exception as e:
            error_info = {'error': f'시스템 부하 정보 수집 중 오류 발생: {str(e)}'}
            print('시스템 부하 정보 수집 오류')
            print(json.dumps(error_info, ensure_ascii=False, indent=2))
            return error_info


def _thread_loop(callable_fn, period_sec, stop_event):
    try:
        while not stop_event.is_set():
            callable_fn()
            for _ in range(period_sec):
                if stop_event.is_set():
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()


def run_threads():
    mc = MissionComputer()
    stop_event = mc._stop_event

    t_info = threading.Thread(target=_thread_loop, args=(
        mc.get_mission_computer_info, 20, stop_event), daemon=True)
    t_load = threading.Thread(target=_thread_loop, args=(
        mc.get_mission_computer_load, 20, stop_event), daemon=True)
    t_sensor = threading.Thread(target=mc.get_sensor_data, kwargs={
                                "interval_seconds": 5}, daemon=True)
    t_info.start()
    t_load.start()
    t_sensor.start()

    try:
        print('멀티 쓰레드 실행 중. 종료하려면 "q"를 누르세요.', flush=True)
        while not stop_event.is_set():
            time.sleep(0.2)
    except KeyboardInterrupt:
        stop_event.set()

    print('모든 쓰레드가 종료되었습니다.', flush=True)


def _proc_info(ev: mp.Event):
    runComputer1 = MissionComputer()
    try:
        while not ev.is_set():
            runComputer1.get_mission_computer_info()
            for _ in range(20):
                if ev.is_set():
                    break
                time.sleep(1)
    except (KeyboardInterrupt, Exception):
        ev.set()


def _proc_load(ev: mp.Event):
    runComputer2 = MissionComputer()
    try:
        while not ev.is_set():
            runComputer2.get_mission_computer_load()

            for _ in range(20):
                if ev.is_set():
                    break
                time.sleep(1)
    except (KeyboardInterrupt, Exception):
        ev.set()


def _proc_sensor(ev: mp.Event):
    runComputer3 = MissionComputer()
    interval_seconds = 5

    try:
        runComputer3._stop_event = ev
        runComputer3.get_sensor_data(interval_seconds=5, enable_input=False)

    except (KeyboardInterrupt, Exception) as e:
        if not ev.is_set():
            ev.set()
    finally:
        pass


def run_processes():
    stop_ev = mp.Event()

    p1 = mp.Process(target=_proc_info, args=(
        stop_ev,), name="runComputer1_info")
    p2 = mp.Process(target=_proc_load, args=(
        stop_ev,), name="runComputer2_load")
    p3 = mp.Process(target=_proc_sensor, args=(
        stop_ev,), name="runComputer3_sensor")

    p1.start()
    p2.start()
    p3.start()

    try:
        print('멀티 프로세스 실행 중. 종료하려면 "q"를 누르세요.', flush=True)
        while not stop_ev.is_set():
            try:
                cmd = input().strip().lower()
                if cmd == 'q':
                    stop_ev.set()
                    break
            except (EOFError, KeyboardInterrupt):
                stop_ev.set()
                break
    finally:
        for p in (p1, p2):
            if p.is_alive():
                p.join(timeout=3)
        if p3.is_alive():
            p3.terminate()
        for p in (p1, p2, p3):
            if p.is_alive():
                p.terminate()


if __name__ == '__main__':
    cmd = input("실행 모드를 선택하세요: 1. 기본 ,  2. 멀티 쓰레드,  3. 멀티 프로세스\n").strip()

    if cmd == '1':
        print('기본 모드')
        ds = DummySensor()
        ds.set_env()
        env_data = ds.get_env()

        runCompurter = MissionComputer()
        runCompurter.get_mission_computer_info()
        runCompurter.get_mission_computer_load()

        RunComputer = MissionComputer()
        RunComputer.get_sensor_data(5)

    elif cmd == '2':
        print('멀티 쓰레드 모드')
        run_threads()

    elif cmd == '3':
        print('멀티 프로세스 모드')
        run_processes()

    else:
        print('잘못된 입력입니다.')
