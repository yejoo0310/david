import pandas as pd
import matplotlib.pyplot as plt


def generate_map():
    try:
        # 데이터 불러오기
        df = pd.read_csv('map_data.csv')
        df.columns = df.columns.str.strip()
        df = df.apply(lambda col: col.map(
            lambda x: x.strip() if isinstance(x, str) else x))

        # area가 1이거나 MyHome인 경우만 필터링
        df = df[(df['area'] == 1) | (df['struct'] == 'MyHome')]

        # 시각화 크기 및 축 생성
        plt.figure(figsize=(10, 10))
        ax = plt.gca()

        # x, y 최대값 계산
        x_max = df['x'].max()
        y_max = df['y'].max()

        # 가장 큰 값을 기준으로 정사각형 사이즈 결정
        size = max(x_max, y_max)

        # y좌표를 위에서 아래로 보기 위해 변환
        df['y_draw'] = y_max - df['y'] + 1

        # 각 건물 시각화
        for _, row in df.iterrows():
            x = row['x']
            y = row['y_draw']  # 반전된 y좌표
            category = row['category']
            site = row['ConstructionSite']

            if site == 1:
                ax.scatter(x, y, c='gray', marker='s', s=100)  # 공사 현장
            elif category == 1 or category == 2:
                ax.scatter(x, y, c='saddlebrown', marker='o', s=100)  # 아파트, 빌딩
            elif category == 3:
                ax.scatter(x, y, c='green', marker='^', s=100)  # 내 집
            elif category == 4:
                ax.scatter(x, y, c='green', marker='s', s=100)  # 반달곰 커피

        # 축 설정
        plt.title('Bandalgom Coffee Map')
        ax.xaxis.set_label_position('top')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.grid(True)

        # x축 눈금: 위쪽에 1부터 size까지 표시
        ax.xaxis.tick_top()
        plt.xticks(range(1, size + 1))

        # y축 눈금: 위에서 아래로 1부터 size까지 표시
        plt.yticks(
            ticks=range(1, size + 1),
            labels=list(reversed(range(1, size + 1)))
        )

        # 축 범위도 정사각형으로 고정
        plt.xlim(0.5, size + 0.5)
        plt.ylim(0.5, size + 0.5)

        # 이미지 저장
        plt.savefig('map.png')
        print(f'   지도 저장 완료: map.png')
        return True
    except FileNotFoundError:
        print(f"   [ERROR] 'map_data.csv' 파일을 찾을 수 없습니다.")
        return False
    except (KeyError, ValueError) as e:
        print(f"   [ERROR] 'map_data.csv' 파일의 데이터 형식에 문제가 있습니다: {e}")
        return False
    except Exception as e:
        print(f'   [ERROR] 지도 생성 중 알 수 없는 오류가 발생했습니다: {e}')
        return False


def main():
    return generate_map()


if __name__ == "__main__":
    main()
