import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.markers import MarkerStyle

INPUT_CSV = 'project/output/data.csv'
OUTPUT_PNG = 'project/output/map.png'


def load_file(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다 - '{file_path}'")
        return None
    except Exception as e:
        print(f"오류: CSV 파일을 읽는 중 문제가 발생했습니다 - {e}")
        return None


def draw_map(df, out_path):
    x_max = df['x'].max()
    y_max = df['y'].max()

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(1, x_max)
    ax.set_ylim(1, y_max)
    ax.invert_yaxis()
    ax.set_aspect('equal')

    ax.set_xticks(range(1, x_max + 1))
    ax.set_yticks(range(1, y_max + 1))
    ax.grid(True)

    def plot_pts(name, marker, color, z):
        pts = df[
            (df['structure_name'] == name)
        ]
        if pts.empty:
            return
        ax.scatter(
            pts['x'], pts['y'],
            marker=MarkerStyle(marker),
            edgecolors=color,
            facecolors=color,
            s=100,
            zorder=z,
            label=name
        )

    plot_pts('Apartment', 'o', 'brown', 2)
    plot_pts('Building', 'o', 'brown', 2)
    plot_pts('BandalgomCoffee', 's', 'green',  3)
    plot_pts('MyHome', '^', 'green',   3)

    pts_con = df[df['ConstructionSite'] == 1]
    if not pts_con.empty:
        ax.scatter(
            pts_con['x'], pts_con['y'],
            marker=MarkerStyle('s'),
            edgecolors='gray',
            facecolors='gray',
            s=100,
            zorder=4,
            label='Construction'
        )

    # 범례를 축의 오른쪽 바깥에 배치
    ax.legend(
        loc='upper left',
        bbox_to_anchor=(1.02, 1),
        borderaxespad=0,
        fontsize='small'
    )

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"지도 이미지가 저장되었습니다: {out_path}")


def main():
    df = load_file(INPUT_CSV)
    if df is None:
        return

    draw_map(df, OUTPUT_PNG)


if __name__ == '__main__':
    main()
