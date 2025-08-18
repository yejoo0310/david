import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLineEdit, QVBoxLayout, QSizePolicy, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from calculator import Calculator
from calculator import CalculatorUI
import math
import re


class EngineeringCalculator(Calculator):
    def __init__(self):
        super().__init__()
        self.angle_mode = 'deg'

    def tokenizer(self, expression):
        expression = (expression or "")
        expression = expression.replace('(', ' ( ')
        expression = expression.replace(')', ' ) ')
        expression = expression.replace('x', '*')
        expression = expression.replace('÷', '/')
        expression = expression.replace('%', ' % ')
        expression = expression.replace('π', ' π ')
        expression = expression.replace('²', ' ² ')
        expression = expression.replace('³', ' ³ ')

        func_pattern = r'\b(sinh|cosh|tanh|sin|cos|tan)\b'
        expression = re.sub(func_pattern, r' \1 ', expression)

        tokens = expression.split()
        parsed_expressions = []

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == '-' and i + 1 < len(tokens) and tokens[i + 1] in ['sinh', 'cosh', 'tanh', 'sin', 'cos', 'tan']:
                parsed_expressions.append(-1.0)
                parsed_expressions.append('*')
                parsed_expressions.append(tokens[i + 1])
                i += 2
                continue
            if token == '%':
                parsed_expressions.append(token)
            elif token == 'π':
                parsed_expressions.append(math.pi)
            elif token in ['²', '³']:
                parsed_expressions.append(token)
            elif token in ['sinh', 'cosh', 'tanh', 'sin', 'cos', 'tan']:
                parsed_expressions.append(token)
            else:
                try:
                    parsed_expressions.append(float(token))
                except ValueError:
                    parsed_expressions.append(token)
            i += 1
        return parsed_expressions

    def evaluate(self, tokens):
        if not tokens:
            return None

        tokens = self._process_functions_and_powers(tokens)
        if tokens is None:
            return None

        return super().evaluate(tokens)

    def negative_positive(self, expression):
        tokens = self.tokenizer(expression)
        if not tokens:
            return expression

        i = len(tokens) - 1
        while i >= 0 and tokens[i] == '%':
            i -= 1
        if i >= 0 and tokens[i] in ('²', '³'):
            i -= 1
        if i >= 0 and self._is_number(tokens[i]):
            tokens[i] = -float(tokens[i])
            return self._tokens_to_string(tokens)
        if i >= 0 and tokens[i] == ')':
            paren = 1
            i -= 1
            while i >= 0 and paren > 0:
                if tokens[i] == ')':
                    paren += 1
                elif tokens[i] == '(':
                    paren -= 1
                i -= 1
            if paren != 0:
                return expression

            open_idx = i + 1
            func_idx = open_idx - 1
            func_set = {'sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh'}

            if func_idx >= 0 and tokens[func_idx] in func_set:
                if func_idx - 2 >= 0 \
                   and isinstance(tokens[func_idx - 2], (int, float)) \
                   and float(tokens[func_idx - 2]) == -1.0 \
                   and tokens[func_idx - 1] == '*':
                    del tokens[func_idx - 2:func_idx]
                else:
                    tokens[func_idx:func_idx] = [-1.0, '*']
                return self._tokens_to_string(tokens)

        return expression

    def _process_functions_and_powers(self, tokens):
        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token == '²':
                if i == 0 or not self._is_number(tokens[i-1]):
                    return None
                base = float(tokens[i-1])
                result = base ** 2
                tokens[i-1] = result
                tokens.pop(i)
                i -= 1
            elif token == '³':
                if i == 0 or not self._is_number(tokens[i-1]):
                    return None
                base = float(tokens[i-1])
                result = base ** 3
                tokens[i-1] = result
                tokens.pop(i)
                i -= 1

            elif token in ['sinh', 'cosh', 'tanh', 'sin', 'cos', 'tan']:
                if i + 1 < len(tokens) and tokens[i + 1] == '(':
                    paren_start = i + 1
                    paren_count = 1
                    paren_end = paren_start + 1

                    while paren_end < len(tokens) and paren_count > 0:
                        if tokens[paren_end] == '(':
                            paren_count += 1
                        elif tokens[paren_end] == ')':
                            paren_count -= 1
                        paren_end += 1

                    if paren_count == 0:
                        inner_tokens = tokens[paren_start + 1:paren_end - 1]
                        inner_result = self.evaluate(inner_tokens)

                        if inner_result is None:
                            return None

                        func_result = self._apply_function(token, inner_result)
                        if func_result is None:
                            return None

                        tokens = tokens[:i] + \
                            [func_result] + tokens[paren_end:]
                        continue
                    else:
                        return None
                else:
                    return None

            i += 1

        return tokens

    def _apply_function(self, func_name, value):
        try:
            if func_name == 'sin':
                r = math.sin(value)
            elif func_name == 'cos':
                r = math.cos(value)
            elif func_name == 'tan':
                r = math.tan(value)
            elif func_name == 'sinh':
                r = math.sinh(value)
            elif func_name == 'cosh':
                r = math.cosh(value)
            elif func_name == 'tanh':
                r = math.tanh(value)
            else:
                return None
            return r if math.isfinite(r) else None
        except (ValueError, OverflowError):
            return None

    def _tokens_to_string(self, tokens):
        out = []
        i = 0
        func_set = {'sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh'}
        while i < len(tokens):
            t = tokens[i]

            if isinstance(t, (int, float)) and float(t) == -1.0:
                if i + 2 < len(tokens) and tokens[i + 1] == '*' and str(tokens[i + 2]) in func_set:
                    out.append('-')
                    out.append(str(tokens[i + 2]))
                    i += 3
                    continue

            if isinstance(t, (int, float)):
                if t == math.pi:
                    out.append('π')
                else:
                    out.append(self._num_str(float(t)))
            else:
                out.append('x' if str(t) == '*' else str(t))
            i += 1

        return ' '.join(out)


class EngineerinCalculatorUI(CalculatorUI):
    def __init__(self):
        super().__init__()
        self.engineeringCalc = EngineeringCalculator()
        self.calculator = self.engineeringCalc
        self._connect_engineering_signals()

    def initUI(self):
        self.setWindowTitle('아이폰 공학용 계산기')
        self.setFixedSize(760, 360)

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
        grid_layout.setHorizontalSpacing(6)
        grid_layout.setVerticalSpacing(6)
        layout.addLayout(grid_layout)

        layout.setStretch(0, 1)
        layout.setStretch(1, 2)
        layout.setStretch(2, 8)

        button_layout = [
            ('(', 0, 0, 1, 1),
            (')', 0, 1, 1, 1),
            ('mc', 0, 2, 1, 1),
            ('m+', 0, 3, 1, 1),
            ('m-', 0, 4, 1, 1),
            ('mr', 0, 5, 1, 1),
            ('AC', 0, 6, 1, 1),
            ('+/-', 0, 7, 1, 1),
            ('%', 0, 8, 1, 1),
            ('/', 0, 9, 1, 1),
            ('2nd', 1, 0, 1, 1),
            ('x²', 1, 1, 1, 1),
            ('x³', 1, 2, 1, 1),
            ('xy', 1, 3, 1, 1),
            ('ex', 1, 4, 1, 1),
            ('10x', 1, 5, 1, 1),
            ('7', 1, 6, 1, 1),
            ('8', 1, 7, 1, 1),
            ('9', 1, 8, 1, 1),
            ('x', 1, 9, 1, 1),
            ('1/x', 2, 0, 1, 1),
            ('2√x', 2, 1, 1, 1),
            ('3√x', 2, 2, 1, 1),
            ('y√x', 2, 3, 1, 1),
            ('ln', 2, 4, 1, 1),
            ('log10', 2, 5, 1, 1),
            ('4', 2, 6, 1, 1),
            ('5', 2, 7, 1, 1),
            ('6', 2, 8, 1, 1),
            ('-', 2, 9, 1, 1),
            ('x!', 3, 0, 1, 1),
            ('sin', 3, 1, 1, 1),
            ('cos', 3, 2, 1, 1),
            ('tan', 3, 3, 1, 1),
            ('e', 3, 4, 1, 1),
            ('EE', 3, 5, 1, 1),
            ('1', 3, 6, 1, 1),
            ('2', 3, 7, 1, 1),
            ('3', 3, 8, 1, 1),
            ('+', 3, 9, 1, 1),
            ('Rad', 4, 0, 1, 1),
            ('sinh', 4, 1, 1, 1),
            ('cosh', 4, 2, 1, 1),
            ('tanh', 4, 3, 1, 1),
            ('π', 4, 4, 1, 1),
            ('Rand', 4, 5, 1, 1),
            ('0', 4, 6, 1, 2),
            ('.', 4, 8, 1, 1),
            ('=', 4, 9, 1, 1)
        ]

        self.buttons = {}
        for text, r, c, rs, cs in button_layout:
            button = QPushButton(text)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setFont(QFont('Arial', 15))
            self.buttons[text] = button
            grid_layout.addWidget(button, r, c, rs, cs)

        for col in range(10):
            grid_layout.setColumnStretch(col, 1)
        for row in range(5):
            grid_layout.setRowStretch(row, 1)

    def _connect_engineering_signals(self):
        self.buttons['('].clicked.connect(self._on_left_paren)
        self.buttons[')'].clicked.connect(self._on_right_paren)
        self.buttons['π'].clicked.connect(self._on_pi)
        self.buttons['x²'].clicked.connect(self._on_squared)
        self.buttons['x³'].clicked.connect(self._on_cubed)
        self.buttons['sin'].clicked.connect(self._on_sin)
        self.buttons['cos'].clicked.connect(self._on_cos)
        self.buttons['tan'].clicked.connect(self._on_tan)
        self.buttons['sinh'].clicked.connect(self._on_sinh)
        self.buttons['cosh'].clicked.connect(self._on_cosh)
        self.buttons['tanh'].clicked.connect(self._on_tanh)

    def _on_left_paren(self):
        if self._ends_with_number_or_dot():
            self.current_expression += 'x '
        self.current_expression += '('
        self._refresh_display()

    # 왼쪽 괄호 개수만큼만 추가됨
    # 숫자 다음에만 추가되는듯?
    # 삼각함수 뒤에서만 추가하면 안되는듯
    def _on_right_paren(self):
        left_cnt = self._exist_left_paren()
        right_cnt = self._exist_right_paren()
        print(left_cnt, right_cnt)
        if left_cnt > right_cnt:
            if not self._ends_with_functions():
                self.current_expression += ')'
        self._refresh_display()

    def _ends_with_functions(self):
        tokens = self.engineeringCalc.tokenizer(self.current_expression)
        tail = tokens[-1]
        if tail in ['sinh', 'cosh', 'tanh', 'sin', 'cos', 'tan']:
            return True
        return False

    # 숫자, 연산자, 괄호
    def _on_pi(self):
        self.current_expression += 'π'
        self._refresh_display()

    # 연산자 %로 끝나면 그냥 sin(
    # 숫자로 끝나면 해당 숫자가 sin()안에 들어감
    def _on_sin(self):
        if self._ends_with_number_or_dot():
            tail = self._tail_numeric_part()
            if tail:
                tokens = self.engineeringCalc.tokenizer(
                    self.current_expression)
                tokens[-1] = f'sin({tail}'
                self.current_expression = self.engineeringCalc._tokens_to_string(
                    tokens)
            else:
                self.current_expression += 'sin('
        else:
            self.current_expression += 'sin('
        self._refresh_display()

    def _on_cos(self):
        if self._ends_with_number_or_dot():
            tail = self._tail_numeric_part()
            if tail:
                tokens = self.engineeringCalc.tokenizer(
                    self.current_expression)
                tokens[-1] = f'cos({tail}'
                self.current_expression = self.engineeringCalc._tokens_to_string(
                    tokens)
            else:
                self.current_expression += 'cos('
        else:
            self.current_expression += 'cos('
        self._refresh_display()

    def _on_tan(self):
        if self._ends_with_number_or_dot():
            tail = self._tail_numeric_part()
            if tail:
                tokens = self.engineeringCalc.tokenizer(
                    self.current_expression)
                tokens[-1] = f'tan({tail}'
                self.current_expression = self.engineeringCalc._tokens_to_string(
                    tokens)
            else:
                self.current_expression += 'tan('
        else:
            self.current_expression += 'tan('
        self._refresh_display()

    def _on_sinh(self):
        if self._ends_with_number_or_dot():
            tail = self._tail_numeric_part()
            if tail:
                tokens = self.engineeringCalc.tokenizer(
                    self.current_expression)
                tokens[-1] = f'sinh({tail}'
                self.current_expression = self.engineeringCalc._tokens_to_string(
                    tokens)
            else:
                self.current_expression += 'sinh('
        else:
            self.current_expression += 'sinh('
        self._refresh_display()

    def _on_cosh(self):
        if self._ends_with_number_or_dot():
            tail = self._tail_numeric_part()
            if tail:
                tokens = self.engineeringCalc.tokenizer(
                    self.current_expression)
                tokens[-1] = f'cosh({tail}'
                self.current_expression = self.engineeringCalc._tokens_to_string(
                    tokens)
            else:
                self.current_expression += 'cosh('
        else:
            self.current_expression += 'cosh('
        self._refresh_display()

    def _on_tanh(self):
        if self._ends_with_number_or_dot():
            tail = self._tail_numeric_part()
            if tail:
                tokens = self.engineeringCalc.tokenizer(
                    self.current_expression)
                tokens[-1] = f'tanh({tail}'
                self.current_expression = self.engineeringCalc._tokens_to_string(
                    tokens)
            else:
                self.current_expression += 'tanh('
        else:
            self.current_expression += 'tanh('
        self._refresh_display()

    # 연산자 뒤에선 안됨
    # 숫자 뒤에서만 가능 %도 가능
    def _on_squared(self):
        tokens = self.engineeringCalc.tokenizer(self.current_expression)
        if not tokens:
            return
        tail = tokens[-1]
        if tail == '%':
            self.current_expression = '수식오류'
        elif self.engineeringCalc._is_number(tail):
            num = float(tail)
            if num.is_integer():
                display_num = str(int(num))
            else:
                display_num = tail
            tokens[-1] = f'{display_num}²'
            self.current_expression = self.engineeringCalc._tokens_to_string(
                tokens)
        self._refresh_display()

    def _on_cubed(self):
        tokens = self.engineeringCalc.tokenizer(self.current_expression)
        if not tokens:
            return
        tail = tokens[-1]
        if tail == '%':
            self.current_expression = '수식오류'
        elif self.engineeringCalc._is_number(tail):
            num = float(tail)
            if num.is_integer():
                display_num = str(int(num))
            else:
                display_num = tail
            tokens[-1] = f'{display_num}³'
            self.current_expression = self.engineeringCalc._tokens_to_string(
                tokens)
        self._refresh_display()

    def _exist_left_paren(self):
        tokens = self.engineeringCalc.tokenizer(self.current_expression)
        if not tokens:
            return 0
        left_cnt = 0
        for i in range(len(tokens)):
            if tokens[i] == '(':
                left_cnt += 1
        return left_cnt

    def _exist_right_paren(self):
        tokens = self.engineeringCalc.tokenizer(self.current_expression)
        if not tokens:
            return 0
        right_cnt = 0
        for i in range(len(tokens)):
            if tokens[i] == ')':
                right_cnt += 1
        return right_cnt


def main():
    app = QApplication(sys.argv)
    window = EngineerinCalculatorUI()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
