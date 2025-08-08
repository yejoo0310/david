import os
import csv

BASE_DIR = os.path.dirname(__file__)
INPUT_CSV = os.path.join(BASE_DIR, 'Mars_Base_Inventory_List.csv')
DANGER_CSV = os.path.join(BASE_DIR, 'Mars_Base_Inventory_danger.csv')
FLAMMABILITY_KEY = 'flammability_index'
DANGER_THRESHOLD = 0.7


def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            raw = f.read()
        print('---------------print log file---------------')
        print(raw)
        return raw
    except FileNotFoundError:
        print('[ERROR] 파일이 없습니다')
        return
    except UnicodeDecodeError:
        print('[ERROR] 디코딩 오류 발생')
        return
    except Exception as e:
        print(f'[ERROR] 데이터 읽는 중 알 수 없는 오류가 발생했습니다: {e}')
        return


def raw_to_list(raw):
    parsed: list[list[str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        cols = [col.strip() for col in line.split(',')]
        if len(cols) != 5:
            print('[ERROR] 파일 형식 불일치 (5분할 실패)')
            return None
        parsed.append(cols)
    return parsed


def sort_list(inventory_list):
    header, *data = inventory_list

    try:
        idx = header.index("Flammability")
    except ValueError:
        raise ValueError("'Flammability' 컬럼을 찾을 수 없습니다.")

    data_sorted = sorted(
        data,
        key=lambda row: float(row[idx]),
        reverse=True
    )

    return [header] + data_sorted


def flammability_filtering_and_save(sorted_list):
    header, *data = sorted_list

    try:
        idx = header.index("Flammability")
    except ValueError:
        raise ValueError("'Flammability' 컬럼을 찾을 수 없습니다.")

    danger_rows = [row for row in data if float(row[idx]) >= DANGER_THRESHOLD]

    with open(DANGER_CSV, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(danger_rows)

    return [header] + danger_rows


def main():
    inventory = read_file(INPUT_CSV)
    if inventory is None:
        return

    inventory_list = raw_to_list(inventory)
    if inventory_list is None:
        return

    sorted_list = sort_list(inventory_list)
    if sorted_list is None:
        return

    danger_list = flammability_filtering_and_save(sorted_list)
    print('---------------print sorted danger list---------------')
    for row in danger_list:
        print(row)


if __name__ == '__main__':
    main()
