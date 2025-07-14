def main():
    while True:
        number = float(input("Enter number:"))
        if number <= 0:
            print("Invalid number input.")
            continue
        else:
            break

    while True:
        exponent = int(input("Enter exponent:"))
        if exponent < 0:
            print("Invalid Exponent input.")
            continue
        else:
            break

    result = 1
    while (exponent > 0):
        result *= number
        exponent -= 1
    
    print("Result:", int(result))

if __name__ == "__main__":
    main()
