# map_direct_save.py
import os
import csv
from collections import deque

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.markers import MarkerStyle

INPUT_CSV = 'project/output/data.csv'
OUTPUT_PATH_CSV = 'project/output/home_to_cafe.csv'
OUTPUT_PNG = 'project/output/map_final.png'


def load_file(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다 - '{file_path}'")
        return None
    except Exception as e:
        print(f'오류: CSV 파일을 읽는 중 문제가 발생했습니다 - {e}')
        return None


def find_shortest_path(df, start, goal):
    max_x = df['x'].max()
    max_y = df['y'].max()
    # 장애물 좌표 집합
    obstacles = {
        (row.x, row.y)
        for _, row in df.iterrows()
        if row.ConstructionSite == 1
    }

    visited = {start}
    queue = deque([[start]])

    # 인접 4방향
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        path = queue.popleft()
        x, y = path[-1]

        if (x, y) == goal:
            return path

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # 범위 검사 및 방문/장애물 중복 검사
            if not (1 <= nx <= max_x and 1 <= ny <= max_y):
                continue
            if (nx, ny) in visited or (nx, ny) in obstacles:
                continue

            visited.add((nx, ny))
            queue.append(path + [(nx, ny)])

    # 경로가 없으면 빈 리스트 반환
    return []


def save_path(path, out_csv):
    """
    최단 경로를 CSV로 저장.
    헤더: x, y
    """
    # output 디렉토리 보장
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)

    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x', 'y'])
        for x, y in path:
            writer.writerow([x, y])


def draw_map_with_path(df, path, out_png):
    """
    지도 + 최단 경로 시각화
    - df: area=1 데이터
    - path: [(x1,y1), ...]
    """
    os.makedirs(os.path.dirname(out_png), exist_ok=True)

    x_max = df['x'].max()
    y_max = df['y'].max()

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(1, x_max)
    ax.set_ylim(1, y_max)
    ax.invert_yaxis()
    ax.set_aspect('equal')

    # 그리드
    ax.set_xticks(range(1, x_max + 1))
    ax.set_yticks(range(1, y_max + 1))
    ax.grid(True)

    # 일반 구조물 (ConstructionSite==0) 그리기
    def plot_pts(name, marker, edge, face, z):
        pts = df[
            (df['structure_name'] == name) &
            (df['ConstructionSite'] == 0)
        ]
        if pts.empty:
            return
        ax.scatter(
            pts['x'], pts['y'],
            marker=MarkerStyle(marker),
            edgecolors=edge,
            facecolors=face,
            s=200,
            zorder=z,
            label=name
        )

    plot_pts('Apartment',       'o', 'brown', 'none', 2)
    plot_pts('Building',        'o', 'brown', 'none', 2)
    plot_pts('BandalgomCoffee', 's', 'green', 'green',  3)
    plot_pts('MyHome',          '^', 'green', 'none',   3)

    # 건설 현장 (ConstructionSite==1)
    pts_con = df[df['ConstructionSite'] == 1]
    if not pts_con.empty:
        ax.scatter(
            pts_con['x'], pts_con['y'],
            marker=MarkerStyle('s'),
            edgecolors='gray',
            facecolors='gray',
            s=200,
            zorder=4,
            label='Construction'
        )

    # 최단 경로 빨간 선으로 그리기
    if path:
        xs = [p[0] for p in path]
        ys = [p[1] for p in path]
        ax.plot(xs, ys,
                linewidth=2,
                color='red',
                zorder=5,
                label='Shortest Path')

    # 범례를 지도 밖에 배치
    ax.legend(
        loc='upper left',
        bbox_to_anchor=(1.02, 1),
        borderaxespad=0,
        fontsize='small'
    )

    plt.tight_layout()
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.close()


def main():
    df = load_file(INPUT_CSV)
    if df is None:
        return

    # 2) 시작점(내 집)과 도착점(반달곰 커피) 좌표 추출
    home_row = df[df['structure_name'] == 'MyHome']
    cafe_row = df[df['structure_name'] == 'BandalgomCoffee']
    if home_row.empty or cafe_row.empty:
        print("오류: 'MyHome' 또는 'BandalgomCoffee' 좌표를 찾을 수 없습니다.")
        return

    start = (home_row.iloc[0]['x'].tolist(), home_row.iloc[0]['y'].tolist())
    goal = (cafe_row.iloc[0]['x'].tolist(), cafe_row.iloc[0]['y'].tolist())

    # 3) 최단 경로 탐색
    path = find_shortest_path(df, start, goal)
    if not path:
        print("오류: 최단 경로를 찾지 못했습니다.")
        return

    # 4) 결과 저장
    save_path(path, OUTPUT_PATH_CSV)
    draw_map_with_path(df, path, OUTPUT_PNG)

    print("✅ home_to_cafe.csv 및 map_final.png 생성 완료")


if __name__ == '__main__':
    main()
