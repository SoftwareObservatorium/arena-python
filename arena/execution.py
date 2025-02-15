def eval_code_expression(code: str):
    return eval(code)


def exec_code(code: str):
    return exec(code)


def create_callable(name: str, code: str):
    exec(code)
    return eval(name)