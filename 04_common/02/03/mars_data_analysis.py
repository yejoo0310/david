import numpy as np
import os

BASE_DIR = os.path.dirname(__file__)
PARTS_ONE = os.path.join(BASE_DIR, 'mars_base_main_parts-001.csv')
PARTS_TWO = os.path.join(BASE_DIR, 'mars_base_main_parts-002.csv')
PARTS_THREE = os.path.join(BASE_DIR, 'mars_base_main_parts-003.csv')
OUTPUT_FILE = os.path.join(BASE_DIR, 'parts_to_work_on.csv')

DTYPE = [('parts', 'U100'), ('strength', 'f8')]
THRESHOLD = 50.0


def load_csv(path):
    try:
        arr = np.genfromtxt(
            path,
            delimiter=',',
            skip_header=1,
            dtype=DTYPE,
            encoding='utf-8',
            autostrip=True
        )
        return arr
    except Exception as e:
        raise RuntimeError(f'로드 실패: {path} - {e}')


def read_csv():
    arr1 = load_csv(PARTS_ONE)
    arr2 = load_csv(PARTS_TWO)
    arr3 = load_csv(PARTS_THREE)
    return arr1, arr2, arr3


def calculate_avg(parts):
    names = parts['parts']
    values = parts['strength']

    mask = ~np.isnan(values)

    uniq, inv = np.unique(names, return_inverse=True)

    sums = np.bincount(inv[mask], weights=values[mask], minlength=uniq.size)
    cnts = np.bincount(inv[mask], minlength=uniq.size)
    means = np.divide(
        sums,
        cnts,
        where=cnts != 0
    )

    return np.rec.fromarrays([uniq, means], names=('parts', 'mean_strength'))


def filter_and_save(parts_avg):
    mask = ~np.isnan(parts_avg['mean_strength']) & (
        parts_avg['mean_strength'] < THRESHOLD)
    filtered = parts_avg[mask]

    try:
        if filtered.size == 0:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                f.write('parts,mean_strength\n')
            return filtered

        strength_str = np.char.mod('%.6g', filtered['mean_strength'])
        rows = np.column_stack((filtered['parts'], strength_str))

        np.savetxt(
            OUTPUT_FILE,
            rows,
            delimiter=',',
            fmt='%s',
            header='parts,mean_strength',
            comments=''
        )
        return filtered
    except Exception as e:
        print(f"[ERROR] CSV 저장 중 오류: {e}")
        return None


def main():
    try:
        arr1, arr2, arr3 = read_csv()
    except RuntimeError as e:
        print(f'에러 발생 {e}')
        return

    parts = np.concatenate([arr1, arr2, arr3])

    parts_avg = calculate_avg(parts)

    filtered = filter_and_save(parts_avg)
    if filtered is None:
        return


if __name__ == '__main__':
    main()
