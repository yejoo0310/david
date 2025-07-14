def main():
    while True:
        number = input("Enter number: ")
        try:
            number = float(number)
            if number == 0:
                raise ValueError
            break
        except ValueError:
            print("Invalid number input.")
            continue
    
    flag = 0
    while True:
        exponent = input("Enter exponent: ")
        try:
            exponent = int(exponent)
            if exponent < 0:
                exponent *= -1
                flag = 1
            break
        except ValueError:
            print("Invalid exponent input.")
            continue
    
    result = 1
    while exponent > 0:
        result = result * number
        exponent -= 1
    
    if flag == 1:
        result = float(result)
        result = 1 / result

    print("Result:", result)

if __name__ == "__main__":
    main()
