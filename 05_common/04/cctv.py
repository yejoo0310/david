import os
import zipfile
from pathlib import Path
import cv2
import glob

BASE_DIR = os.path.dirname(__file__)
CCTV_ZIP = os.path.join(BASE_DIR, 'cctv.zip')
OUTPUT_DIR = Path(os.path.join(BASE_DIR, 'cctv'))
YOLO_CFG = Path(os.path.join(BASE_DIR, 'yolov3.cfg'))
YOLO_WEIGHTS = Path(os.path.join(BASE_DIR, 'yolov3.weights'))
YOLO_NAMES = Path(os.path.join(BASE_DIR, 'coco.names'))


class MasImageHelper:
    def __init__(self):
        self.images = []
        self.current_index = 0
        self.net = None
        self.classes = []

    def unzip_file(self):
        OUTPUT_DIR.mkdir(exist_ok=True)

        if not zipfile.is_zipfile(CCTV_ZIP):
            print('cctv.zip 폴더를 찾을 수 없음')
            return False

        try:
            with zipfile.ZipFile(CCTV_ZIP, 'r') as zf:
                zf.extractall(OUTPUT_DIR)
            return True
        except zipfile.BadZipFile:
            print('Error: 잘못된 zip 파일입니다.')
            return False

    def load_image(self):
        image_extensions = ['*.jpg', '*.jpeg',
                            '*.png', '*.bmp', '*.tiff', '*.tif']
        for ext in image_extensions:
            self.images.extend(glob.glob(os.path.join(OUTPUT_DIR, ext)))
            self.images.extend(
                glob.glob(os.path.join(OUTPUT_DIR, ext.upper())))
        self.images.sort()

        if not self.images:
            print('cctv 폴더에 이미지가 없습니다.')
            return False

        return True

    def show_image(self):
        if not self.images:
            print('이미지 리스트가 비어있습니다.')
            return False
        current_file = self.images[self.current_index]
        current_image = cv2.imread(current_file)
        image_title = os.path.basename(current_file)
        window_title = f'{image_title} ({self.current_index + 1}/{len(self.images)})'
        cv2.imshow(window_title, current_image)
        return True

    def select_image(self):
        if not self.show_image():
            return

        while True:
            cmd = cv2.waitKey(0)

            if cmd == ord('q') or cmd == 27:
                break
            elif cmd == 2:
                if self.current_index > 0:
                    self.current_index -= 1
                    cv2.destroyAllWindows()
                    self.show_image()
                else:
                    print('첫번째 이미지입니다. 이전 이미지로 이동할 수 없습니다.')
            elif cmd == 3:
                if self.current_index < len(self.images) - 1:
                    self.current_index += 1
                    cv2.destroyAllWindows()
                    self.show_image()
                else:
                    print('마지막 이미지입니다. 다음 이미지로 이동할 수 없습니다.')
        cv2.destroyAllWindows()

    def load_yolo(self):
        if not os.path.exists(YOLO_CFG) or not os.path.exists(YOLO_WEIGHTS) or not os.path.exists(YOLO_NAMES):
            print('yolo 모델 파일을 찾을 수 없습니다.')
            return False

        self.net = cv2.dnn.readNet(YOLO_WEIGHTS, YOLO_CFG)
        with open(YOLO_NAMES, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        return True

    def get_output_layers(self):
        layer_names = self.net.getLayerNames()
        return [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]

    def find_and_show_people(self):
        if not self.images:
            print('이미지 리스트가 비어있습니다.')
            return

        while self.current_index < len(self.images):
            image_path = self.images[self.current_index]
            current_image = cv2.imread(image_path)

            if current_image is None:
                print(f'{image_path} 이미지를 읽을 수 없습니다. 다음 이미지로 이동합니다.')
                self.current_index += 1
                continue

            blob = cv2.dnn.blobFromImage(
                current_image, 1/255.0, (416, 416), swapRB=True)
            self.net.setInput(blob)

            outs = self.net.forward(self.get_output_layers())

            person_found = 0
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    max_confidence = -1.0
                    class_id = -1
                    for i, confidence_score in enumerate(scores):
                        if confidence_score > max_confidence:
                            max_confidence = confidence_score
                            class_id = i
                    confidence = scores[class_id]
                    if confidence > 0.5 and self.classes[class_id] == 'person':
                        person_found = 1
                        break

            if person_found:
                print(f'사람 발견 {os.path.basename(image_path)}')
                current_file = self.images[self.current_index]
                current_image = cv2.imread(current_file)
                image_title = os.path.basename(current_file)
                window_title = f'{image_title} ({self.current_index + 1}/{len(self.images)})'
                cv2.imshow(window_title, current_image)

                cmd = cv2.waitKey(0)
                cv2.destroyAllWindows()

                if cmd == 13:
                    self.current_index += 1
                elif cmd == ord('q') or cmd == 27:
                    print('검색 종료')
                    return
            else:
                self.current_index += 1

        print('모든 이미지 검색이 완료되었습니다.')


def main():
    marsImageHelper = MasImageHelper()

    try:
        cmd = int(input('번호를 선택하세요(1: 문제 1, 2: 문제 2) : '))
    except ValueError:
        print('잘못된 입력값입니다.')
        return

    if not marsImageHelper.unzip_file():
        return
    if not marsImageHelper.load_image():
        return

    if cmd == 1:
        marsImageHelper.select_image()
    elif cmd == 2:
        if not marsImageHelper.load_yolo():
            return
        marsImageHelper.find_and_show_people()
    else:
        print('잘못된 입력값입니다.')

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
