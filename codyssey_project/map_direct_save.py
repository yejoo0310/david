import pandas as pd
from collections import deque
import matplotlib.pyplot as plt

# CSV 파일을 읽고 문자열 공백 제거


def load_data(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    df.columns = df.columns.str.strip()
    df = df.apply(lambda col: col.map(
        lambda x: x.strip() if isinstance(x, str) else x))
    return df

# MyHome 위치와 BandalgomCoffee 좌표 리스트 추출


def find_home_and_cafes(df: pd.DataFrame):
    home = df[df['struct'] == 'MyHome'].iloc[0]
    home_pos = (int(home['x']), int(home['y']))
    cafes = df[df['struct'] == 'BandalgomCoffee']
    cafe_positions = list(zip(cafes['x'], cafes['y']))
    return home_pos, cafe_positions

# 해당 위치가 이동 가능한지 확인


def is_accessible(x, y, visited, df):
    if not (1 <= x <= 15 and 1 <= y <= 15):
        return False
    if visited[y][x]:
        return False
    tile = df[(df['x'] == x) & (df['y'] == y)]
    if tile.empty:
        return True
    if int(tile['ConstructionSite'].values[0]) == 1:
        return False
    return True

# BFS로 최단 경로 탐색


def bfs_shortest_path(start, goals, df):
    queue = deque()
    visited = [[False] * 16 for _ in range(16)]
    prev = dict()

    sx, sy = start
    queue.append((sx, sy))
    visited[sy][sx] = True

    while queue:
        x, y = queue.popleft()
        if (x, y) in goals:
            # 경로 추적
            path = [(x, y)]
            while (x, y) != start:
                x, y = prev[(x, y)]
                path.append((x, y))
            return path[::-1]  # 역순으로 반환

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if is_accessible(nx, ny, visited, df):
                queue.append((nx, ny))
                visited[ny][nx] = True
                prev[(nx, ny)] = (x, y)

    return []  # 경로 없음

# 최단 경로를 CSV로 저장


def save_path_to_csv(path, filename='home_to_cafe.csv'):
    path_df = pd.DataFrame(path, columns=['x', 'y'])
    path_df.to_csv(filename, index=False)

# 경로 시각화 및 이미지 저장 함수


def draw_map_with_path(df: pd.DataFrame, path: list[tuple], filename='map_final.png'):
    # 1. 시각화 크기 및 축 생성
    plt.figure(figsize=(10, 10))
    ax = plt.gca()

    # 2. x, y 최대값 계산
    x_max = df['x'].max()
    y_max = df['y'].max()
    size = max(x_max, y_max)

    # y 좌표 변환 (위 → 아래)
    df['y_draw'] = y_max - df['y'] + 1

    # area == 1 또는 MyHome만 필터링 (시각화 용도만)
    df_filtered = df[(df['area'] == 1) | (df['struct'] == 'MyHome')]

    # 3. 각 건물 시각화
    for _, row in df_filtered.iterrows():
        x = row['x']
        y = row['y_draw']
        category = row['category']
        site = row['ConstructionSite']

        if site == 1:
            ax.scatter(x, y, c='gray', marker='s', s=100)            # 공사현장
        elif category == 1 or category == 2:
            ax.scatter(x, y, c='saddlebrown', marker='o', s=100)     # 건물
        elif category == 3:
            ax.scatter(x, y, c='green', marker='^', s=100)           # MyHome
        elif category == 4:
            ax.scatter(x, y, c='green', marker='s', s=100)           # 반달곰 커피

    # 최단 경로를 빨간 선으로 시각화
    if path:
        px = [x for x, y in path]
        py = [y_max - y + 1 for x, y in path]  # y 좌표 반전
        plt.plot(px, py, color='red', linewidth=2,
                 marker='o', markersize=5, label='Path')

    # 4. 축 설정
    plt.title('Bandalgom Coffee Map')
    ax.xaxis.set_label_position('top')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True)
    ax.xaxis.tick_top()
    plt.xticks(range(1, size + 1))
    plt.yticks(
        ticks=range(1, size + 1),
        labels=list(reversed(range(1, size + 1)))
    )
    plt.xlim(0.5, size + 0.5)
    plt.ylim(0.5, size + 0.5)
    plt.legend()

    # 5. 저장
    plt.savefig(filename)
    print(f'   최단 경로 포함 지도 저장 완료: {filename}')
    plt.close()


def main():
    try:
        df = load_data('map_data.csv')
        home_pos, cafe_positions = find_home_and_cafes(df)

        path = bfs_shortest_path(home_pos, set(cafe_positions), df)

        if path:
            save_path_to_csv(path)  # 경로 저장
            # 최단 경로까지 구해진 후에 시각화 함수 호출
            draw_map_with_path(df, path, filename='map_final.png')
        else:
            print('이동 가능한 경로가 없습니다.')
        return True
    except FileNotFoundError:
        print(f"   [ERROR] 'map_data.csv' 파일을 찾을 수 없습니다.")
        return False
    except (KeyError, ValueError) as e:
        print(f"   [ERROR] 'map_data.csv' 파일의 데이터 형식에 문제가 있습니다: {e}")
        return False
    except IndexError:
        print(f"   [ERROR] 'MyHome' 또는 'BandalgomCoffee' 위치를 찾을 수 없습니다.")
        return False
    except Exception as e:
        print(f'   [ERROR] 최단 경로 계산 중 알 수 없는 오류가 발생했습니다: {e}')
        return False


if __name__ == '__main__':
    main()
