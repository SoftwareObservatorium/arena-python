def eval_code_expression(code: str):
    return eval(code)


def exec_code(code: str):
    return exec(code)


def create_callable(name: str, code: str):
    """
    Create a callable from code and make available in namespace

    :param name:
    :param code:
    :return:
    """

    namespace = {}
    exec(code, namespace)
    # make available
    globals().update(namespace)

    return eval(name)
