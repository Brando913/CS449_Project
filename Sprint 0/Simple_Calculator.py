def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Can not divide by 0")
    return a / b


if __name__ == "__main__":
    choice = ''

    while True:
        print(
            'Choice of operation:\n'
            '1 - Add\n'
            '2 - Subtract\n'
            '3 - Multiply\n'
            '4 - Divide\n'
            'q - Quit'
        )

        choice = input('Enter Choice: ')

        if choice == 'q':
            break

        if choice not in ['1', '2', '3', '4']:
            print("Invalid choice")
            continue

        num1 = int(input('Enter first number: '))
        num2 = int(input('Enter second number: '))

        if choice == '1':
            print("Result:", add(num1, num2))

        elif choice == '2':
            print("Result:", subtract(num1, num2))

        elif choice == '3':
            print("Result:", multiply(num1, num2))

        elif choice == '4':
            try:
                print("Result:", divide(num1, num2))
            except ValueError as error:
                print(error)

        print()