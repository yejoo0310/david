import math

MATERIAL = {'glass', 'aluminum', 'carbon_steel'}
MARS_GRAVITY_FACTOR = 0.38
RESULT = {}


def sphere_area(diameter, material, thickness=1.0):
    try:
        diameter = float(diameter)
    except (TypeError, ValueError):
        raise ValueError('숫자 형식이 아닙니다.')
    if diameter <= 0:
        raise ValueError('0보다 큰 값을 입력해야합니다.')

    if not isinstance(material, str):
        raise ValueError('재질은 문자열이어야 합니다.')
    material = material.strip().lower()
    if material not in MATERIAL:
        raise ValueError('유효하지 않은 재질입니다.')

    if thickness is None or (isinstance(thickness, str) and thickness.strip() == ''):
        thickness = 1.0
    else:
        try:
            thickness = float(thickness)
        except (TypeError, ValueError):
            raise ValueError('두께는 숫자 형식이어야 합니다.')
        if thickness <= 0:
            raise ValueError('두께는 0보다 커야 합니다.')

    r = diameter / 2
    area = 2 * math.pi * r * r

    v = area * thickness * 10000
    if material == 'glass':
        p = 2.4
    elif material == 'aluminum':
        p = 2.7
    elif material == 'carbon_steel':
        p = 7.85
    else:
        raise ValueError('유효하지 않은 재질입니다.')

    m = (v * p) / 1000
    m_mars = m * MARS_GRAVITY_FACTOR

    return area, m_mars


def main():
    while True:
        try:
            cmd = input(
                "< Mars 돔 구조물 설계 프로그램 > 시작하려면 엔터를 누르세요. 종료하려면 'q'를 입력하세요.")
            if cmd == 'q':
                print('프로그램 종료')
                break

            diameter = input('지름(m)을 입력하세요: ')
            material = input('재질을 입력하세요 (glass, aluminum, carbon_steel만 가능): ')
            thickness = input('두께(cm)를 입력하세요 (기본값은 1cm): ').strip()

            area, mass = sphere_area(diameter, material, thickness)
            area_r = round(area, 3)
            mass_r = round(mass, 3)

            RESULT.clear()
            RESULT.update({
                'material': material.strip().lower(),
                'diameter': float(diameter),
                'thickness': 1.0 if thickness == '' else float(thickness),
                'area': area_r,
                'mass': mass_r
            })

            print(
                f'재질 -> {RESULT.get("material")}, '
                f'지름 -> {RESULT.get("diameter")}, '
                f'두께 -> {RESULT.get("thickness")}, '
                f'면적 -> {RESULT.get("area")}, '
                f'무게 -> {RESULT.get("mass")} kg'
            )
        except ValueError as e:
            print(f'입력 오류: {e}')


if __name__ == '__main__':
    main()
