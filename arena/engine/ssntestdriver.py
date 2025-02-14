from arena.lql.lqlparser import Interface
from arena.ssn.ssnparser import ParsedSheet, ParsedCell, resolve_cell_reference


def eval_code_expression(code: str):
    return eval(code)


def resolve_parameter_type(arg: ParsedCell):
    if arg.is_cell_reference():
        coordinate = resolve_cell_reference(arg.value)
        # FIXME get invocation

    if arg.is_test_parameter():
        # ?pX
        pass

    # is code expression
    out_val = None
    if type(arg.value) == str:
        out_val = eval_code_expression(arg.value)
    else:
        out_val = arg.value

    print(out_val)


def interpret(parsed_sheet: ParsedSheet, interface_specification: Interface):
    for parsed_row in parsed_sheet.rows:
        output = parsed_row.get_output()
        operation = parsed_row.get_operation()
        inputs = parsed_row.get_inputs()

        #either points to class name to instantiate (with "create" operation) or reference to object
        clazz = inputs[0]
        input_args = []
        #remaining input parameters
        if len(inputs) > 1:
            input_args = inputs[1:]
        if operation == "create":
            # constructor invocation
            pass
        else:
            # method invocation
            pass

        # resolve expected output
        resolve_parameter_type(output)