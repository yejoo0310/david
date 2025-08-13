import sys
from PyQt5.QtWidgets import *


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('아이폰 계산기')
        self.setFixedSize(320, 500)
        self.setStyleSheet('background-color: black;')


def main():
    app = QApplication(sys.argv)
    
    window = MyWidget()
    window.show()
    
    app.exec_()


if __name__ == '__main__':
    main()
