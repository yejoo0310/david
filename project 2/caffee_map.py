import pandas as pd
from typing import Optional

CATEGORY_FILE = 'project/data/area_category.csv'
MAP_FILE = 'project/data/area_map.csv'
STRUCT_FILE = 'project/data/area_struct.csv'
AREA_TO_FILTER = 1


def load_file(file_path) -> Optional[pd.DataFrame]:
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다 - '{file_path}'")
        return None
    except Exception as e:
        print(f"오류: CSV 파일을 읽는 중 문제가 발생했습니다 - {e}")
        return None


def convert_category(df_category, df_map, df_struct) -> Optional[pd.DataFrame]:
    # key: category, value: struct 인 매핑 딕셔너리 생성
    mapping: dict[int, str] = (
        dict(zip(df_category['category'], df_category['struct'])) | {
            0: 'Empty'}
    )

    categories: set[int] = set(df_struct['category'].unique())
    invalid: set[int] = categories.difference(set(mapping.keys()))
    if invalid:
        print(f"오류: 다음 category 값은 허용되지 않습니다: {invalid}")
        return None

    df_struct['structure_name'] = df_struct['category'].map(mapping)
    merged = (
        df_map.merge(df_struct, on=['x', 'y'], how='left')
    )

    df = (
        merged
        .sort_values(['area', 'x', 'y'])
        .reset_index(drop=True)
    )
    return df


def filter_by_area(df, AREA_TO_FILTER):
    return df[df['area'] == AREA_TO_FILTER].reset_index(drop=True)


def print_summary(df):
    print('=== 구조물 종류별 개수 ===')
    counts = {}

    for name in df['structure_name']:
        if name == 'Empty':
            continue
        if name in counts:
            counts[name] += 1
        else:
            counts[name] = 1

    for name, count in counts.items():
        print(f"{name}: {count}개")


def main():
    df_category = load_file(CATEGORY_FILE)
    df_map = load_file(MAP_FILE)
    df_struct = load_file(STRUCT_FILE)

    if df_category is None or df_map is None or df_struct is None:
        return

    print('=== area_category.csv ===')
    print(df_category.to_string())
    print('')

    print('=== area_map.csv ===')
    print(df_map.to_string())
    print('')

    print('=== area_struct.csv ===')
    print(df_struct.to_string())
    print('')

    df = convert_category(
        df_category,
        df_map,
        df_struct
    )

    if df is None:
        return

    df.to_csv('project/output/data.csv', index=False)

    df = filter_by_area(df, AREA_TO_FILTER)
    print(df.to_string())
    print_summary(df)

    df.to_csv('project/output/area1_data.csv', index=False)


if __name__ == '__main__':
    main()
