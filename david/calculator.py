def main():
    a = input("Enter expression: ")
    
    if a.isdigit():
        a = int(a)
        calculate(a)
    else:
        bonus_calculate(a)

def calculate(a):
    b = input("Second Number: ")
    b = int(b)

    oper = input()
    if oper == '+':
        print("Result:", add(a, b))
    elif oper == '-':
        print("Result:", subtract(a, b))
    elif oper == '*':
        print("Result:", multiply(a, b))
    elif oper == '/':
        if b == 0:
            print("Error: Division by zero.")
            return
        print("Result:", divide(a, b))
    else:
        print("Invalid operator.")
        return

def bonus_calculate(ex):
    elements = ex.split()
    if len(elements) != 3:
        print("Invalid expression format.")
        return
    
    try:
        a = int(elements[0])
    except ValueError:
        print("Invalid Input Number")
        return

    try:
        b = int(elements[2])
    except ValueError:
        print("Invalid Input Number")
        return

    if elements[1] == '+':
        print("Result:", add(a, b))
    elif elements[1] == '-':
        print("Result:", subtract(a, b))
    elif elements[1] == '*':
        print("Result:", multiply(a, b))
    elif elements[1] == '/':
        if b == 0:
            print("Error: Division by zero.")
            return
        print("Result:", divide(a, b))
    else:
        print("Invalid operator.")
        return
    

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b

if __name__ == "__main__":
    main()