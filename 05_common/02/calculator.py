import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLineEdit, QVBoxLayout, QSizePolicy, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import math


class CalculatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.current_expression = ''
        self.ac_or_del_label = 'AC'
        self.calculator = Calculator()
        self.initUI()
        self._connect_signals()
        self._refresh_display()

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

        button_layout = [
            (self.ac_or_del_label, 0, 0, 1, 1),
            ('+/-', 0, 1, 1, 1),
            ('%', 0, 2, 1, 1),
            ('/', 0, 3, 1, 1),
            ('7', 1, 0, 1, 1),
            ('8', 1, 1, 1, 1),
            ('9', 1, 2, 1, 1),
            ('x', 1, 3, 1, 1),
            ('4', 2, 0, 1, 1),
            ('5', 2, 1, 1, 1),
            ('6', 2, 2, 1, 1),
            ('-', 2, 3, 1, 1),
            ('1', 3, 0, 1, 1),
            ('2', 3, 1, 1, 1),
            ('3', 3, 2, 1, 1),
            ('+', 3, 3, 1, 1),
            ('0', 4, 0, 1, 2),
            ('.', 4, 2, 1, 1),
            ('=', 4, 3, 1, 1)
        ]

        self.buttons = {}
        for text, r, c, rs, cs in button_layout:
            button = QPushButton(text)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setMinimumHeight(56)
            button.setFont(QFont('Arial', 20))
            self.buttons[text] = button
            grid_layout.addWidget(button, r, c, rs, cs)

        for col in range(4):
            grid_layout.setColumnStretch(col, 1)
        for row in range(5):
            grid_layout.setRowStretch(row, 1)

        self.resize(320, 480)

    def _connect_signals(self):
        for d in '0123456789':
            self.buttons[d].clicked.connect(lambda _, x=d: self._on_digit(x))
        self.buttons['.'].clicked.connect(self._on_decimal)
        for op in ['+', '-', 'x', '/']:
            self.buttons[op].clicked.connect(
                lambda _, o=op: self._on_operator(o))
        self.buttons['%'].clicked.connect(self._on_percent)
        self.buttons['+/-'].clicked.connect(self._on_sign_toggle)
        self.buttons['='].clicked.connect(self._on_equal)
        self.buttons[self.ac_or_del_label].clicked.connect(self._on_ac)

    def _on_digit(self, d):
        if self._ends_with_number_or_dot():
            self.current_expression += d
        else:
            if self.current_expression.strip() == '' or self.current_expression.strip() == '0':
                self.current_expression = d
            else:
                self.current_expression += f' {d}'
        self._refresh_display()

    def _on_decimal(self):
        if not self._ends_with_number_or_dot():
            if self.current_expression.strip() == '' or self.current_expression.strip().endswith((' +', ' -', ' x', ' /', '(')):
                self.current_expression += (
                    ' 0' if self.current_expression else '0')
        last_num = self._tail_numeric_part()
        if '.' in last_num:
            return
        self.current_expression += '.'
        self._refresh_display()

    def _on_operator(self, raw_op):
        op = {'x': 'x', '/': '/', '+': '+', '-': '-'}[raw_op]
        if self.current_expression.strip() == '' or self.current_expression.strip().endswith((' +', ' -', ' x', ' /', '(')):
            return
        self.current_expression += f' {op} '
        self._refresh_display()

    def _on_percent(self):
        expr = self._expr_for_engine()
        new_expr = self.calculator.percent(expr)
        self.current_expression = new_expr
        self._refresh_display()

    def _on_sign_toggle(self):
        expr = self._expr_for_engine()
        new_expr = self.calculator.negative_positive(expr)
        self.current_expression = new_expr
        self._refresh_display()

    def _on_ac(self):
        self.calculator.reset()
        self.current_expression = ''
        self.expression_lable.setText('')
        self._refresh_display()

    def _on_equal(self):
        expr = self._expr_for_engine()
        if not expr:
            return
        result = self.calculator.equal(expr)
        self.expression_lable.setText(expr)
        self.display.setText('Error' if result is None else self._fmt(result))
        self.current_expression = self.display.text() if result is not None else ''

    def _expr_for_engine(self):
        return self.current_expression.strip()

    def _ends_with_number_or_dot(self):
        s = self.current_expression
        if not s.strip():
            return False
        tail = s.rstrip().split(' ')[-1]

        if tail.lstrip('-').replace('.', '', 1).isdigit():
            return True
        if tail and tail[-1] == '.' and tail[:-1].isdigit():
            return True
        return False

    def _tail_numeric_part(self):
        s = self.current_expression.strip()
        if not s:
            return ''
        last = s.split(' ')[-1]
        if last.lstrip('-').replace('.', '', 1).isdigit():
            return last
        return ''

    def _fmt(self, val):
        s = f'{val:.12g}'
        if 'e' in s or 'E' in s:
            return s
        if '.' in s:
            s = s.rstrip('0').rstrip('.')
        return s

    def _refresh_display(self):
        text = self.current_expression.strip()
        self.display.setText(text if text else '0')


class Calculator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.expression = ''
        self.last_result = 0.0

    def add(self, a, b):
        r = a + b
        return r if self._finite(r) else None

    def subtract(self, a, b):
        r = a - b
        return r if self._finite(r) else None

    def multiply(self, a, b):
        r = a * b
        return r if self._finite(r) else None

    def divide(self, a, b):
        if b == 0.0:
            print('Error: divide by zero')
            return None
        r = a / b
        return r if self._finite(r) else None

    def modulo(self, a, b):
        if b == 0.0:
            print('Error: 0으로 나눌 수 없습니다')
            return None
        r = a % b
        return r if self._finite(r) else None

    def tokenizer(self, expression):
        expression = (expression or "")
        expression = expression.replace('(', ' ( ')
        expression = expression.replace(')', ' ) ')
        expression = expression.replace('x', '*')
        expression = expression.replace('÷', '/')
        expression = expression.replace('%', ' % ')
        tokens = expression.split()
        parsed_expressions = []
        for token in tokens:
            if token == '%':
                parsed_expressions.append(token)
                continue
            try:
                parsed_expressions.append(self._safe_float(token))
            except ValueError:
                parsed_expressions.append(token)
        return parsed_expressions

    def negative_positive(self, expression):
        tokens = self.tokenizer(expression)
        if not tokens:
            return expression
        i = len(tokens) - 1
        while i >= 0 and tokens[i] == '%':
            i -= 1
        if i >= 0 and self._is_number(tokens[i]):
            value = float(tokens[i])
            value = -value
            tokens[i] = value
            return self._tokens_to_string(tokens)
        return expression

    def percent(self, expression):
        tokens = self.tokenizer(expression)
        if not tokens:
            return expression
        if tokens[-1] == '%':
            return self._tokens_to_string(tokens)
        if (self._is_number(tokens[-1]) or tokens[-1] == ')'):
            tokens.append('%')
            return self._tokens_to_string(tokens)
        return expression

    def equal(self, expression):
        tokens = self.tokenizer(expression)
        result = self.evaluate(tokens)
        if result is not None:
            self.last_result = result
        return result

    def precedence(self, op):
        if op in ['+', '-']:
            return 1
        if op in ['*', '/', '%']:
            return 2
        return 0

    def apply_operator(self, operators, values):
        if not operators:
            return False
        if len(values) < 2:
            return False
        op = operators.pop()
        b = values.pop()
        a = values.pop()
        if op == '+':
            result = self.add(a, b)
        elif op == '-':
            result = self.subtract(a, b)
        elif op == '*':
            result = self.multiply(a, b)
        elif op == '/':
            result = self.divide(a, b)
            if result is None:
                return False
        elif op == '%':
            result = self.modulo(a, b)
            if result is None:
                return False
        else:
            print('잘못된 입력값으로 인한 계산 오류')
            return False

        if result is None or not self._finite(result):
            print('연산 결과가 표현 가능 범위를 벗어났습니다')
            return False

        values.append(result)
        return True

    def evaluate(self, tokens):
        values = []
        operators = []
        i = 0
        while i < len(tokens):
            token = tokens[i]

            if isinstance(token, (int, float)):
                if not self._finite(token):
                    print('입력 값이 표현 가능 범위를 벗어났습니다')
                    return None
                values.append(float(token))

            elif token == '%':
                is_modulo = False
                if i + 1 < len(tokens):
                    next_token = tokens[i+1]
                    if self._is_number(next_token) or next_token == '(':
                        is_modulo = True

                if is_modulo:
                    while (operators and operators[-1] != '(' and
                           self.precedence(operators[-1]) >= self.precedence(token)):
                        if not self.apply_operator(operators, values):
                            return None
                    operators.append(token)
                else:
                    if not values:
                        return None
                    values[-1] = values[-1] / 100.0

            elif token == '(':
                operators.append(token)

            elif token == ')':
                while operators and operators[-1] != '(':
                    if not self.apply_operator(operators, values):
                        return None
                if not operators:
                    print('괄호 오류')
                    return None
                operators.pop()

            elif token in ['+', '*', '-', '/']:
                while (operators and operators[-1] != '(' and
                       self.precedence(operators[-1]) >= self.precedence(token)):
                    if not self.apply_operator(operators, values):
                        return None
                operators.append(token)

            else:
                print('잘못된 입력값으로 인한 계산 오류')
                return None
            i += 1

        while operators:
            if operators[-1] == '(':
                print('괄호 오류')
                return None
            if not self.apply_operator(operators, values):
                return None

        return values[0] if values else None

    def _is_number(self, token):
        try:
            float(token)
            return True
        except (ValueError, TypeError):
            return False

    def _num_str(self, value):
        s = f'{value:.12g}'
        if 'e' in s or 'E' in s:
            return s
        if '.' in s:
            s = s.rstrip('0').rstrip('.')
        return s

    def _tokens_to_string(self, tokens):
        out = []
        for t in tokens:
            if isinstance(t, (int, float)):
                out.append(self._num_str(float(t)))
            else:
                out.append(str(t))
        expression = ' '.join(out)
        return expression.replace('*', 'x')

    def _finite(self, x):
        return isinstance(x, (int, float)) and math.isfinite(x)

    def _safe_float(self, token):
        try:
            v = float(token)
        except (ValueError, TypeError):
            raise
        if not self._finite(v):
            raise ValueError("out-of-range")
        return v


def main():
    app = QApplication(sys.argv)
    window = CalculatorUI()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
