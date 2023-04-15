class Expression:
    OP_TOKENS = ["+", "-", "*", "/", "(", ")"]
    COND_SIGNS = [">", "<", ">=", "<=", "==", "!=", "True", "False"]

    expression = ""
    rev_polska = ""
    is_expression_valid = True
    has_correct_operands_bounds = True
    are_operands_being_integers = True
    has_division_by_zero = False
    states = []

    def __init__(self, expression) -> None:
        self.expression = expression

    def is_valid(self) -> bool:
        try:
            self.states.append("is_valid:S0")
            eval(self.expression)

            for number in self.expression.split():
                if number not in self.OP_TOKENS and number not in self.COND_SIGNS:
                    if not (-32768 <= int(float(number)) < 32768):
                        self.has_correct_operands_bounds = False
                    elif not (float(number) == int(float(number))):
                        self.are_operands_being_integers = False
        except SyntaxError:
            self.is_expression_valid = False
        except ZeroDivisionError:
            self.has_division_by_zero = True

        self.states.append("is_valid:S1")
        self.states.append("is_valid:S0")
        return self.is_expression_valid and self.has_correct_operands_bounds and self.are_operands_being_integers and not self.has_division_by_zero

    def to_rpn(self) -> str:
        self.states.append("to_rpn:S0")
        stack = []
        tokenized = []

        for token in self.expression.split():
            self.states.append("to_rpn:S1")
            match token:
                case "+" | "-":
                    if len(stack) == 0 or stack[-1] == "(":
                        stack.append(token)
                    else:
                        while len(stack) != 0 and stack[-1] in ["*", "/", "+", "-"]:
                            tokenized.append(stack.pop())
                        stack.append(token)
                case "*" | "/":
                    if len(stack) == 0 or stack[-1] in ["+", "-", "("]:
                        stack.append(token)
                    else:
                        while len(stack) != 0 and stack[-1] in ["*", "/"]:
                            tokenized.append(stack.pop())
                        stack.append(token)
                case "(":
                    stack.append(token)
                case ")":
                    while len(stack) != 0 and stack[-1] != "(":
                        tokenized.append(stack.pop())
                    if len(stack) != 0:
                        stack.pop()
                case _:
                    tokenized.append(token)

        while len(stack) > 0:
            tokenized.append(stack.pop())

        self.rev_polska = " ".join(tokenized)

        self.states.append("to_rpn:S2")
        self.states.append("to_rpn:S0")
        return self.rev_polska

    def evaluate(self) -> float:
        self.states.append("evaluate:S0")
        self.to_rpn()
        tokenized = self.rev_polska.split()
        stack = []

        for val in tokenized:
            self.states.append("evaluate:S1")
            if val not in self.OP_TOKENS:
                stack.append(int(val))
            else:
                right = int(stack.pop())
                left = int(stack.pop())
                self.states.append("evaluate:S2")

                match val:
                    case "+":
                        stack.append(left + right)
                    case "-":
                        stack.append(left - right)
                    case "*":
                        stack.append(left * right)
                    case "/":
                        stack.append(int(left / right))

        self.states.append("evaluate:S0")

        val = stack.pop()
        if not (-32768 <= int(float(val)) < 32768):
            print("The result of the expression is not in the range [-32768; 32768)")
            exit()

        return val


if __name__ == "__main__":
    # exp = Expression(input("Введите выражение, где элементы отделены пробелом: "))
    exp = Expression("2 + 44 * ( 56 - 12 ) / 8 - 66")
    # exp = Expression("5 + ( 14 - 4 ) * 4")
    # exp = Expression("( 3.1 + 5.6 ) * 10.4")
    # exp = Expression("( 141 + 24 ) * 50000")
    # exp = Expression("(4*) (5+3)")
    # exp = Expression("( -17 + 3 ) * 2 / 10")
    exp = Expression("16384 + 16380 + 2 * 2 + 1")

    if exp.is_valid():
        print(exp.evaluate())
        print(exp.rev_polska)
        print(*exp.states)
    else:
        if exp.has_division_by_zero and exp.is_expression_valid and exp.has_correct_operands_bounds and exp.are_operands_being_integers:
            print("Division by zero")
        elif not exp.is_expression_valid and exp.has_correct_operands_bounds and exp.are_operands_being_integers and not exp.has_division_by_zero:
            print("Expression is not correct")
        elif not exp.has_correct_operands_bounds and exp.are_operands_being_integers and not exp.has_division_by_zero:
            print("One or more operands in the expression are not in the range [-32768; 32768)")
        elif not exp.are_operands_being_integers and not exp.has_division_by_zero:
            print("One or more operands in the expression are not integers")