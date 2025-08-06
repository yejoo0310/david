import os
import logging
import json
from datetime import datetime
import pprint

BASE_DIR = os.path.dirname(__file__)

LOG_FILE = os.path.join(BASE_DIR, 'mission_computer_main.log')
JSON_FILE = os.path.join(BASE_DIR, 'mission_computer_main.json')
MARKDOWN_FILE = os.path.join(BASE_DIR, 'log_analysis.md')
DANGER_FILE = os.path.join(BASE_DIR, 'danger_logs.txt')

DANGER_KEYWORDS = {'unstable', 'explosion', 'Max-Q', 'ignition', 'Oxygen'}


# mission_computer_main.log 파일 읽고 출력
def read_file(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            contents = f.read()
        print('---------------print log file---------------')
        print(contents)

        lines = [line.strip()
                 for line in contents.splitlines() if line.strip()]
        if lines and lines[0].lower().startswith('timestamp,'):
            lines = lines[1:]

        sorted_lines = sorted(
            lines,
            key=lambda line: datetime.fromisoformat(line.split(',', 1)[0]),
            reverse=True
        )

        print('---------------print sorted log file---------------')
        for ln in sorted_lines:
            print(ln)

        return contents
    except FileNotFoundError:
        print('[ERROR] 파일이 없습니다')
        return
    except UnicodeDecodeError:
        print('[ERROR] 디코딩 오류 발생')
        return
    except Exception as e:
        print(f'[ERROR] 데이터 읽는 중 알 수 없는 오류가 발생했습니다: {e}')
        return


# 날짜/시간, 메시지를 list로 전환
def file_to_list(file):
    if file is None:
        print('[ERROR] 파일이 존재하지 않음')
        return

    logs = [log for log in file.splitlines() if log.strip()]
    parsed = []

    start_idx = 1 if logs and logs[0].lower().startswith('timestamp,') else 0

    for log in logs[start_idx:]:
        parts = log.split(',', 2)
        if len(parts) != 3:
            logging.warning('[ERROR] 파일 형식 불일치 (3분할 실패)')
            continue

        timestamp, event, message = parts
        parsed.append([timestamp.strip(), message.strip()])

    return parsed


# 시간 역순으로 list 정렬
def sort_list(parsed_list):
    if parsed_list is None:
        print('[ERROR] 파일이 존재하지 않음')
        return

    valid_items = []

    for item in parsed_list:
        try:
            datetime.fromisoformat(item[0])
            valid_items.append(item)
        except (ValueError, TypeError):
            print(f'잘못된 데이터 형식: {item}')
            continue

    sorted_list = sorted(
        valid_items,
        key=lambda x: datetime.fromisoformat(x[0]),
        reverse=True
    )
    return sorted_list


# list 객체를 dictionary 객체로 변환
def list_to_dict(list_data):
    if list_data is None:
        print('[ERROR] 파일이 존재하지 않음')
        return

    dict_data = dict(list_data)
    return dict_data


def save_dict_to_json(dict_data, file):
    if dict_data is None:
        print('[ERROR] 파일이 존재하지 않음')
        return

    try:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(dict_data, f, ensure_ascii=False, indent=2)
        print(f"\n[INFO] JSON 파일로 저장됨: {file}")
    except Exception as e:
        print(f"[ERROR] JSON 저장 실패: {e}")


def save_markdown(report_content, file):
    try:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"[INFO] '{file}' 를 UTF-8로 저장했습니다.")
    except Exception as e:
        print(f"[ERROR] Markdown 파일 저장 실패: {e}")


def danger_keyword_filtering(sorted_list):
    filtered = []
    for item in sorted_list:
        message = item[1]
        for keyword in DANGER_KEYWORDS:
            if keyword in message:
                filtered.append(item)
                break
    return filtered


def save_danger_logs(danger_list, file):
    if not danger_list:
        print("[INFO] 위험 로그가 없습니다.")
        return
    try:
        with open(file, 'w', encoding='utf-8') as f:
            for ts, msg in danger_list:
                f.write(f"{ts}, {msg}\n")
        print(f"[INFO] 위험 로그 저장됨: {file}")
    except Exception as e:
        print(f"[ERROR] 위험 로그 저장 실패: {e}")


def search_logs(dict_data):
    if dict_data is None:
        print('[ERROR] 검색할 데이터가 없습니다.')
        return
    query = input('검색할 문자열을 입력하세요: ').strip()
    if not query:
        print('검색 문자열이 입력되지 않았습니다.')
        return
    results = {ts: msg for ts, msg in dict_data.items() if query in msg}
    if results:
        print(f'\n---------------검색 결과 ({query})---------------')
        for ts, msg in results.items():
            print(f"{ts}, {msg}")
    else:
        print(f"'{query}'를 포함한 로그가 없습니다.")


def main():
    log_file = read_file(LOG_FILE)
    if log_file is None:
        return

    parsed_list = file_to_list(log_file)
    if parsed_list is None:
        return
    print('---------------print parsed list---------------')
    pprint.pprint(parsed_list, width=79)

    sorted_list = sort_list(parsed_list)
    if sorted_list is None:
        return
    print('---------------print sorted list---------------')
    pprint.pprint(sorted_list, width=79)

    danger_list = danger_keyword_filtering(sorted_list)
    save_danger_logs(danger_list, DANGER_FILE)

    dict_data = list_to_dict(sorted_list)
    if dict_data is None:
        return
    print('---------------print dict---------------')
    pprint.pprint(dict_data, width=79)

    save_dict_to_json(dict_data, JSON_FILE)

    search_logs(dict_data)

    report_content = """
# 사고 원인 분석 보고서


## 1. 개요

2025년 8월 27일 misson computer에서 발생한 사고의 원인을 분석하기 위해 작성된 보고서입니다.

---

## 2. 로그 요약

- 발사 준비 단계 (10:00:00 ~ 10:27:00)
- 이륙 및 상승 단계 (10:30:00 ~ 10:48:00)
- 궤도 진입 및 임무 수행 (10:50:00 ~ 11:05:00)
- 로켓 귀환 및 착륙 단계 (11:10:00 ~ 11:28:00)
- 임무 완료 및 사고 발생 (11:30:00 ~ 12:00:00)

---

## 3. 주요 이상 징후

1. **Oxygen tank unstable**  
   - **시간:** 2023-08-27 11:35:00  
   - **로그:** `“Oxygen tank unstable.”`  
   - **설명:** 착륙 후 로켓의 산소 탱크에서 문제 발생

2. **Oxygen tank explosion**  
   - **시간:** 2023-08-27 11:40:00  
   - **로그:** `“Oxygen tank explosion.”`  
   - **설명:** 불안정 상태 5분 후 탱크 내부 압력 급증 또는 재료 결함으로 폭발 발생.

3. **Mission control systems powered down**  
   - **시간:** 2023-08-27 12:00:00  
   - **로그:** `“Center and mission control systems powered down.”`  
   - **설명:** 사고 수습 및 안전 확보를 위해 미션 제어 시스템 셧다운.

---

## 4. 사고 경위 추론

1. **정상 미션 완료**  
   - 11:05:00에 위성 배치 성공 후 재진입 및 착륙까지 모든 시스템이 정상 작동.  

2. **착륙 직후 탱크 이상 징후 발생**  
   - 11:35:00 착륙 확인(11:28)을 기점으로, 착륙지 환경 변화(온도·압력 급변)나 탱크 구조적 결함으로 인해 산소 탱크 내부 압력 불안정이 감지됨.

3. **탱크 내부 압력 급증 및 폭발**  
   - 불안정 상태 감지 5분 후(11:40), 내부 압력 제어 실패로 탱크가 폭발. 이로 인해 주변 구조물 및 제어 시스템에 2차 피해가 발생했을 가능성 높음.

4. **시스템 셧다운**  
   - 사고 대응 프로토콜에 따라 12:00에 미션 제어 시스템을 안전하게 종료하여 추가 피해를 방지.


---

## 5. 결론

이 로그는 표면적으로는 완벽하게 성공한 임무였으나, 임무 종료 직후 발생한 하드웨어의 치명적인 고장으로 끝난 사례를 기록하고 있습니다. 이는 우주 임무의 복잡성과 위험성을 명확히 보여주며, 임무의 성공 여부는 발사부터 회수 후 안정화 단계까지 모든 과정이 안전하게 종료되어야만 판단할 수 있다는 교훈을 줍니다. 
    """
    save_markdown(report_content, MARKDOWN_FILE)


if __name__ == '__main__':
    main()
