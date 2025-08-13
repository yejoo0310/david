import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLineEdit, QVBoxLayout, QSizePolicy, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class CalculatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.current_expression = ''
        self.initUI()

    def initUI(self):
        self.setWindowTitle('아이폰 계산기')
        self.setFixedSize(320, 500)

        layout = QVBoxLayout(self)

        self.expression_lable = QLabel('')
        self.expression_lable.setAlignment(Qt.AlignRight)
        self.expression_lable.setFont(QFont('Arial', 14))
        self.expression_lable.setStyleSheet("color: #a5a5a5;")
        layout.addWidget(self.expression_lable)

        self.display = QLineEdit('0')
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFont(QFont('Arial', 36))
        self.display.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.display)

        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(10)
        grid_layout.setVerticalSpacing(10)
        layout.addLayout(grid_layout)

        layout.setStretch(0, 1)
        layout.setStretch(1, 2)
        layout.setStretch(2, 8)

        self.ac_or_del_label = 'AC'
        button_layout = [
            (self.ac_or_del_label, 0, 0, 1, 1), ('+/-', 0, 1, 1,
                                                 1), ('%', 0, 2, 1, 1), ('/', 0, 3, 1, 1),
            ('7', 1, 0, 1, 1), ('8', 1, 1, 1,
                                1), ('9', 1, 2, 1, 1), ('x', 1, 3, 1, 1),
            ('4', 2, 0, 1, 1), ('5', 2, 1, 1,
                                1), ('6', 2, 2, 1, 1), ('-', 2, 3, 1, 1),
            ('1', 3, 0, 1, 1), ('2', 3, 1, 1,
                                1), ('3', 3, 2, 1, 1), ('+', 3, 3, 1, 1),
            ('0', 4, 0, 1, 2), ('.', 4, 2, 1, 1), ('=', 4, 3, 1, 1)
        ]

        self.buttons = {}
        for text, r, c, rs, cs in button_layout:
            button = QPushButton(text)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setMinimumHeight(56)
            button.setFont(QFont('Arial', 20))
            self.buttons[text] = button
            grid_layout.addWidget(button, r, c, rs, cs)

        # 핵심 ②: 그리드의 각 열/행이 균등하게 늘어나도록
        for col in range(4):
            grid_layout.setColumnStretch(col, 1)
        for row in range(5):
            grid_layout.setRowStretch(row, 1)

        self.resize(320, 480)


def main():
    app = QApplication(sys.argv)

    window = CalculatorUI()
    window.show()

    app.exec_()


if __name__ == '__main__':
    main()
