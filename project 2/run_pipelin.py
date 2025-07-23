import caffee_map
import map_draw
# import map_direct_save


def main():
    print('1단계: 데이터 수집 및 분석')
    caffee_map.main()

    print('')
    print('2단계: 지도 시각화')
    map_draw.main()

    # print('3단계: 최단 경로 탐색')
    # map_direct_save.main()


if __name__ == '__main__':
    main()
