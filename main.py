from expression import Expression


class Script:
    COND_SIGNS = [">", "<", ">=", "<=", "==", "!="]
    script = ""
    variables = dict()

    def __init__(self, path) -> None:
        self.script = open(path).readlines()
        self.check_vars()
        self.check_conds()

    def check_expr(self, expr, idx) -> bool:
        if not expr.is_valid():
            if expr.has_division_by_zero and expr.is_expression_valid and expr.has_correct_operands_bounds and expr.are_operands_being_integers:
                print(f"The string {idx + 1}: Division by zero")
                return False
            elif not expr.is_expression_valid and expr.has_correct_operands_bounds and expr.are_operands_being_integers and not expr.has_division_by_zero:
                print(f"The string {idx + 1}: Division is not correct")
                return False
            elif not expr.has_correct_operands_bounds and expr.are_operands_being_integers and not expr.has_division_by_zero:
                print(f"The string {idx + 1}: One or more operands in the expression not in the range [-32768; 32768)")
                return False
            elif not expr.are_operands_being_integers and not expr.has_division_by_zero:
                print(f"The string {idx + 1}: One or more operands in the expression are not integers")
                return False

        return True

    def check_conds(self) -> None:
        has_if = False
        has_elseif = False
        has_else = False
        waiting_for_endif = False

        if_starts_at = -1
        elseif_starts_at = -1
        else_starts_at = -1

        for (idx, line) in enumerate(self.script):
            if line.startswith("if "):
                has_if = True
                if_starts_at = idx
                waiting_for_endif = True
            elif line.startswith("elif "):
                has_elseif = True
                elseif_starts_at = idx
            elif line.strip().startswith("else"):
                has_else = True
                else_starts_at = idx
            elif line.strip().startswith("endif"):
                if not has_if:
                    print(f"The string {idx + 1}: if is missing")
                    exit()
                elif not has_if and has_elseif:
                    print(f"The string {elseif_starts_at + 1}: if is missing")
                    exit()
                elif not has_if and not has_elseif and has_else:
                    print(f"The string {else_starts_at + 1}: if is missing")
                    exit()

                waiting_for_endif = False
                has_if = False
                has_elseif = False
                has_else = False
                if_starts_at = -1
                elseif_starts_at = -1
                else_starts_at = -1

        if has_if and waiting_for_endif:
            print(f"The string {if_starts_at + 1}: if isn't closed")
            exit()
        elif not has_if and has_elseif:
            print(f"The string {elseif_starts_at + 1}: if isn't closed")
            exit()
        elif not has_if and not has_elseif and has_else:
            print(f"The string {else_starts_at + 1}: if isn't closed")
            exit()

    def check_vars(self) -> None:
        for (idx, line) in enumerate(self.script):
            if line.count("==") == 0 and len(line.split("=")) > 2:
                print(f"The string {idx + 1}: assignment error")
                exit()

    def prepare_expr(self, expr, idx, to_be_cond):
        joinable = []

        for token in expr.split():
            if token not in self.variables.keys():
                joinable.append(token)
            else:
                joinable.append(self.variables[token])

        expr = Expression(" ".join(joinable))

        if not self.check_expr(expr, idx):
            exit()

        if to_be_cond:
            return expr

        return str(expr.evaluate())

    def execute(self):
        cond_proceed_exec = True
        cond_once_step = False

        for (idx, line) in enumerate(self.script):
            line = line.strip()

            # Variable assignment
            if " = " in line and cond_proceed_exec:
                expr = Expression(self.prepare_expr(line.split(" = ")[1].strip(), idx, False))

                if not self.check_expr(expr, idx):
                    exit()

                self.variables.update({line.split(" = ")[0].strip(): str(expr.evaluate())})

            # I/O routines
            elif (line.startswith("in ") or line.startswith("out ")) and cond_proceed_exec:
                if line.startswith("in "):
                    expr = Expression(self.prepare_expr(input(F"Input {line.split()[1]}: ").strip(), idx, False))

                    if not self.check_expr(expr, idx):
                        exit()

                    self.variables.update({line.split()[1]: str(expr.evaluate())})
                elif line.startswith("out "):
                    if line.partition(" ")[2].startswith('"') and line.partition(" ")[2].endswith('"'):
                        print(line.partition(" ")[2].lstrip('"').rstrip('"'))
                    else:
                        if line.partition(" ")[2] not in self.variables.keys():
                            try:
                                print(Expression(line.partition(" ")[2]).evaluate())
                            except Exception:
                                print(f"The string {idx + 1}: undeclared variable {line.partition(' ')[2]}")
                                exit()
                        else:
                            print(self.variables[line.partition(" ")[2]])

            # Conditionals
            elif line.startswith("if ") or line.startswith("elif ") or line.strip().startswith("else"):
                if line.startswith("if "):
                    expr = self.prepare_expr(line.lstrip("if "), idx, True)
                    is_cond_true = False
                elif line.startswith("elif "):
                    expr = self.prepare_expr(line.lstrip("elif "), idx, True)
                    is_cond_true = False
                else:
                    expr = self.prepare_expr("True", idx, True)
                    is_cond_true = not cond_once_step

                if not self.check_expr(expr, idx):
                    exit()

                if line.startswith("if ") or line.startswith("elif "):
                    for sign in self.COND_SIGNS:
                        if sign in line:
                            ops = expr.expression.lstrip("( ").rstrip(" )").split(sign)

                            match sign:
                                case '>':
                                    is_cond_true = int(ops[0]) > int(ops[1])
                                case '<':
                                    is_cond_true = int(ops[0]) < int(ops[1])
                                case '>=':
                                    is_cond_true = int(ops[0]) >= int(ops[1])
                                case '<=':
                                    is_cond_true = int(ops[0]) <= int(ops[1])
                                case '==':
                                    is_cond_true = int(ops[0]) == int(ops[1])
                                case '!=':
                                    is_cond_true = int(ops[0]) != int(ops[1])

                if is_cond_true:
                    cond_proceed_exec = True
                    cond_once_step = True
                else:
                    cond_proceed_exec = False

            elif line.strip().startswith("endif"):
                cond_once_step = False
                cond_proceed_exec = True

            elif not any([comm in line for comm in
                          ["in ", "out ", "if ", "elif ", "else", "endif", " = "]]) and line.strip() != "":
                print(f"The string {idx + 1}: unidentified construction {line.strip()}")
                exit()


if __name__ == "__main__":
    scr = Script("pl.txt")
    # scr = Script("test.txt")

    # scr = Script("pl_err_divzero.txt")
    # scr = Script("pl_err_wrongexp.txt")
    # scr = Script("pl_err_outbounds.txt")
    # scr = Script("pl_err_notinteger.txt")
    # scr = Script("pl_err_assign.txt")
    # scr = Script("pl_err_novar.txt")

    # scr = Script("pl_err_noif.txt")
    # scr = Script("pl_err_noendif.txt")
    # scr = Script("pl_err_noif_with_elif.txt")
    # scr = Script("pl_err_noif_only_else.txt")

    scr.execute()
