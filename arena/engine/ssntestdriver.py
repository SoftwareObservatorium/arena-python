import inspect
import logging
import random
import string
import time
from types import FunctionType, MethodType, MethodDescriptorType

from arena.engine.adaptation import AdaptedImplementation
from arena.execution import eval_code_expression, exec_code, create_callable
from arena.lql.lqlparser import Interface
from arena.ssn.ssnparser import ParsedSheet, ParsedCell, resolve_cell_reference
from arena.introspection import resolve_type_by_name, resolve_constructor, resolve_operation, is_function, is_method

logger = logging.getLogger(__name__)

# SSN keywords
SSN_CREATE = ["create".lower(), "$create".lower()]
SSN_EVAL = ["$eval".lower()]


class Test:
    """
    A resolved stimulus sheet subject for testing
    """

    def __init__(self, name: str, parsed_sheet: ParsedSheet, interface_specification: Interface, signature):
        self.name = name
        self.parsed_sheet = parsed_sheet
        self.interface_specification = interface_specification
        self.signature = signature


class TestInvocation:
    """
    A test invocation
    """

    def __init__(self, test: Test, invocation: str):
        self.test = test
        self.invocation = invocation


    def __str__(self):
        return f"{self.test.name}({self.invocation})"


class Parameter:
    """
    Parameter model
    """

    def __init__(self, target_class, expression: str | None, value: object):
        self.target_class = target_class
        self.expression = expression
        self.value = value
        self.coordinate = []


    def is_reference(self):
        return self.coordinate and len(self.coordinate) > 0


class Invocation:
    """
    Invocation model
    """

    def __init__(self, index: int):
        self.index = index
        self.parameters: [Parameter] = []
        self.target_class = None
        self.expected_output = None
        self.target: Parameter = None

    def execute(self, executed_invocations, executed_invocation, adapted_implementation: AdaptedImplementation):
        pass


class MemberInvocation(Invocation):
    """
    Invocation model for callables (operations and initializers)
    """

    def __init__(self, index: int):
        super().__init__(index)
        self.member = None


    def is_cut(self):
        pass


    def is_function(self):
        return is_function(self.member)


    def __str__(self):
        return f"{self.__class__.__name__} => {self.index}, {self.member}, {self.target_class}, {self.parameters}"


class MethodInvocation(MemberInvocation):
    """
    Invocation model for callables (operations and functions)
    """

    def execute(self, executed_invocations, executed_invocation, adapted_implementation: AdaptedImplementation):
        """
        Execute operation (method/function)

        :param executed_invocations:
        :param executed_invocation:
        :param adapted_implementation:
        :return:
        """

        # input values for operation
        inputs = [x.value for x in executed_invocation.inputs]

        # instance
        target_instance: Obj = executed_invocation.resolve_target_instance()

        obj = Obj()
        obj.producer_index = executed_invocation.invocation.index

        logger.debug(f"resolving cut method member for {self.member}")

        # builtin functions: e.g., special len() function
        if inspect.isbuiltin(self.member):
            try:
                logger.debug(f"Built in function {self.member}")
                # we need target instance
                result = self.member(target_instance.value)
                obj.value = result
            except Exception as e:
                obj.exception = e
        elif callable(self.member): # FIXME or isinstance(self.member, MethodType)??
            # resolve signature
            signature = executed_invocations.invocations.interface_mapping.lql_to_python_mapping[self.member]
            logger.debug(signature)
            index = executed_invocations.invocations.interface_mapping.interface_specification.get_methods().index(
                signature)
            cut_method = adapted_implementation.get_method(
                executed_invocations.invocations.interface_mapping.interface_specification, index)

            # call resolved member of CUT
            resolved_member = cut_method.member
            logger.debug(f"resolved method member is {resolved_member}")

            executed_invocation.adapted_member = cut_method

            # call method or function
            method_inputs = inputs  # just inputs
            logger.debug(f" type of member {type(resolved_member)}")
            if isinstance(resolved_member, MethodDescriptorType) or isinstance(resolved_member, MethodType) or is_method(resolved_member):
                logger.debug(f" resolved callable is method {resolved_member}")

                # we need target instance for method call
                method_inputs = [target_instance.value] + inputs  # instance + inputs

            try:
                logger.debug(f"calling {resolved_member} with args {method_inputs}")

                result = resolved_member(*method_inputs)
                obj.value = result
            except Exception as e:
                obj.exception = e
        else:
            logger.warning(f"unknown invocation {executed_invocation.invocation}")

        logger.debug(f"output {obj}")

        executed_invocation.output = obj


class InstanceInvocation(MemberInvocation):
    """
    Invocation model for callables (initializers like constructors)
    """

    def execute(self, executed_invocations, executed_invocation, adapted_implementation: AdaptedImplementation):
        """
        Create instance by using an initializer like a constructor

        :param executed_invocations:
        :param executed_invocation:
        :param adapted_implementation:
        :return:
        """

        inputs = [x.value for x in executed_invocation.inputs]

        obj = Obj()
        obj.producer_index = executed_invocation.invocation.index

        # call method/function
        try:
            target_class = executed_invocation.invocation.target_class

            logger.debug(f"calling {self.member} of target class {target_class} with args {inputs}")

            if len(executed_invocations.invocations.interface_mapping.interface_specification.get_constructors()) < 1:
                # get default instance of CUT
                if adapted_implementation.cut.is_module():
                    result = "$CUT@module" # FIXME find good identifier of module
                else:
                    result = adapted_implementation.cut.class_under_test() # e.g., list()
            else:
                # resolve signature
                signature = executed_invocations.invocations.interface_mapping.lql_to_python_mapping[self.member]
                index = executed_invocations.invocations.interface_mapping.interface_specification.get_constructors().index(signature)
                cut_initializer = adapted_implementation.get_initializer(executed_invocations.invocations.interface_mapping.interface_specification, index)

                # call resolved member of CUT
                resolved_member = cut_initializer.member
                logger.debug(f"resolved initializer member is {resolved_member}")

                executed_invocation.adapted_member = cut_initializer

                if callable(resolved_member):
                    logger.debug(f"init member is callable {resolved_member}")
                    # call it
                    if len(inputs) > 0:
                        result = resolved_member(*inputs)
                    else:
                        result = resolved_member()
                else:
                    logger.debug(f"init member is not callable {resolved_member}")
                    result = None

            obj.value = result
        except Exception as e:
            obj.exception = e

        logger.debug(f"init output {obj}")

        executed_invocation.output = obj


class CodeInvocation(Invocation):
    """
    Invocation model for code expressions that need to be evaluated
    """

    def __init__(self, index: int):
        super().__init__(index)
        self.expression = None


    def execute(self, executed_invocations, executed_invocation, adapted_implementation: AdaptedImplementation):
        """
        Execute code expression

        :param adapted_implementation:
        :param executed_invocations:
        :param executed_invocation:
        :return:
        """

        obj = Obj()
        try:
            result = eval_code_expression(self.expression)
            obj.value = result
        except Exception as e:
            obj.exception = e

        executed_invocation.output = obj


class Invocations:
    """
    Invocations model for a sequence of invocations
    """

    def __init__(self, test_invocation: TestInvocation, interface_mapping):
        self.test_invocation = test_invocation
        self.sequence = []
        self.interface_mapping = interface_mapping


    def create_method_invocation(self):
        invocation = MethodInvocation(len(self.sequence))
        self.sequence.append(invocation)
        return invocation


    def create_instance_invocation(self):
        invocation = InstanceInvocation(len(self.sequence))
        self.sequence.append(invocation)
        return invocation


    def create_code_invocation(self):
        invocation = CodeInvocation(len(self.sequence))
        self.sequence.append(invocation)
        return invocation


    def get_invocation(self, index: int):
        return self.sequence[index]


    def __str__(self):
        out = "Invocations\n"
        i = 0
        for invocation in self.sequence:
            out += f"{i} => {invocation}\n"
            i += 1
        return out


class Obj:
    """
    Container for result of the execution of an invocation (value or exception)
    """

    def __init__(self):
        self.producer_index = -1
        self.value = None
        self.exception = None


    def has_exception(self):
        return self.exception is not None


    def __str__(self):
        if self.has_exception():
            return f"{self.exception}"

        return f"{self.value}"


    def is_cut(self, class_under_test):
        return type(self.value) is class_under_test


class ExecutedInvocation:
    """
    Models an executed invocation and its result
    """

    def __init__(self, invocation: Invocation, executed_invocations):
        self.executed_sequence = []
        self.invocation = invocation
        self.executed_invocations = executed_invocations
        self.output: Obj | None = None
        self.inputs: [Obj] = []
        self.adapted_member = None


    def resolve_target_instance(self):
        target = self.invocation.target
        executed_invocation = self.executed_invocations.get_executed_invocation(target.coordinate[0])

        return executed_invocation.output


    def __str__(self):
        return f"{self.__class__.__name__} => {self.invocation}, {self.inputs}, {self.output}"


class ExecutionInvocations:
    """
    Sequence of executed invocations and their result
    """

    def __init__(self, invocations: Invocations, adapted_implementation: AdaptedImplementation):
        self.executed_sequence = []
        self.invocations = invocations
        self.adapted_implementation = adapted_implementation


    def create(self, invocation: Invocation):
        executed_invocation = ExecutedInvocation(invocation, self)
        self.executed_sequence.append(executed_invocation)

        return executed_invocation


    def get_executed_invocation(self, index: int):
        return self.executed_sequence[index]


    def get_last_executed_invocation(self):
        return self.executed_sequence[-1]


    def __str__(self):
        out = "Executed Invocations\n"
        i = 0
        for executed_invocation in self.executed_sequence:
            out += f"{i} => {executed_invocation}\n"
            i += 1
        return out


def resolve_parameter_type(invocations: Invocations, arg: ParsedCell):
    """
    Resolve parameters and their types

    :param invocations:
    :param arg:
    :return:
    """

    if arg.is_cell_reference():
        coordinate = resolve_cell_reference(arg.value)
        invocation = invocations.get_invocation(coordinate[0])
        p = Parameter(invocation.target_class, None, None)
        p.coordinate = coordinate
        return p

    if arg.is_test_parameter():
        # parametermized tests: ?pX
        value = arg.value
        param = value.partition("?")[2]
        logger.debug(f"found test parameter {param}")

        # resolve test parameter value from signature
        p_index = -1
        for p in range(len(invocations.test_invocation.test.signature.method.inputNames)):
            input_name = invocations.test_invocation.test.signature.method.inputNames[p]
            if input_name is not None:
                p_index = p

        if p_index < 0:
            raise Exception(f"could not find test parameter {param}")

        invocation_expression = invocations.test_invocation.invocation
        param_values = eval_code_expression(f"[{invocation_expression}]") # evaluate as list ...
        logger.debug(f"sheet invocation expression {invocation_expression} evaluated to {param_values}")
        param_value = param_values[p_index]
        param_value_type = type(param_value)

        code_expr = invocation_expression.split(",")[p_index] # FIXME dangerous ..

        return Parameter(param_value_type, code_expr, param_value)

    # is code expression
    out_val = None
    out_expr = None
    if type(arg.value) == str:
        out_expr = arg.value

        # only if not empty
        if out_expr:
            out_val = eval_code_expression(arg.value)

    else:
        out_val = arg.value

    return Parameter(type(out_val), out_expr, out_val)


def resolve_parameter_types(invocations: Invocations, input_args):
    """
    Resolve parameters and their types

    :param invocations:
    :param input_args:
    :return:
    """

    parameters = []

    for input_arg in input_args:
        input_arg = resolve_parameter_type(invocations, input_arg)
        parameters.append(input_arg)

    return parameters


def instance_invocation(invocations: Invocations, class_name, input_args):
    """
    Create instance invocation

    :param invocations:
    :param class_name:
    :param input_args:
    :return:
    """

    invocation = invocations.create_instance_invocation()

    # resolve class (primitives, fully qualified class names etc.)
    # is cut adapter class?
    clazz = None
    if invocations.interface_mapping.is_cut(class_name):
        logger.debug(f"adapter class found {class_name}")
        clazz = invocations.interface_mapping.adapter_clazz
    else:
        clazz = resolve_type_by_name(class_name)

    logger.debug("found type " + str(clazz))
    invocation.target_class = clazz

    # resolve parameters
    input_parameters = resolve_parameter_types(invocations, input_args)
    invocation.parameters = input_parameters
    input_types = [x.target_class for x in input_parameters]

    # resolve constructor / initializer
    constructor = resolve_constructor(clazz, input_types)

    invocation.member = constructor

    return invocation


def method_invocation(invocations: Invocations, clazz_cell, operation_name: str, input_args):
    """
    Create operation (method, function) invocation

    :param invocations:
    :param clazz_cell:
    :param operation_name:
    :param input_args:
    :return:
    """

    invocation = invocations.create_method_invocation()

    # resolve instance by cell identifier
    clazz_name_cell_ref = clazz_cell.value
    coordinate = resolve_cell_reference(clazz_name_cell_ref)

    instance_invocation = invocations.get_invocation(coordinate[0])
    target_class = instance_invocation.target_class
    invocation.target_class = target_class

    logger.debug(f"resolved coordinate {coordinate} from {clazz_name_cell_ref} for operation {operation_name} / target class {target_class}")

    # set target
    target = Parameter(target_class, clazz_cell, None)
    target.coordinate = coordinate
    invocation.target = target

    # resolve parameters
    input_parameters = resolve_parameter_types(invocations, input_args)
    invocation.parameters = input_parameters
    input_types = [x.target_class for x in input_parameters]

    # resolve operation (method/function)
    operation = resolve_operation(target_class, operation_name, input_types)
    invocation.member = operation

    logger.debug(f"Resolved operation {operation} for class {target_class}")

    return invocation


def code_invocation(invocations: Invocations, code_cell):
    """
    Execute a code expression

    :param invocations:
    :param code_cell:
    :return:
    """

    invocation = invocations.create_code_invocation()
    invocation.expression = code_cell.value
    # execute expression
    result = eval_code_expression(code_cell.value)
    if result:
        invocation.target_class = type(result)

    invocation.parameters = []

    return invocation


class InterfaceMapping:

    def __init__(self, interface_specification: Interface, adapter_clazz, lql_to_python_mapping: dict):
        self.interface_specification = interface_specification
        self.adapter_clazz = adapter_clazz
        self.lql_to_python_mapping = lql_to_python_mapping


    def is_cut(self, clazz_name: str):
        logger.debug(f"{self.interface_specification.name} vs {clazz_name}")
        return self.interface_specification.name == clazz_name


def lql_to_python_class(interface_specification: Interface):
    """
    Create python class on the fly (adapter class) - later delegate calls to adapted implementation

    :param interface_specification:
    :return:
    """

    # can only be exactly one in Python
    constructors = interface_specification.get_constructors()
    methods = interface_specification.get_methods()

    # unique names for adapter class and methods ...
    adapter_prefix = ''.join(random.choices(string.ascii_uppercase, k=10))
    adapter_clazz_name = f"{adapter_prefix}.{interface_specification.name}"
    # create new class on the fly
    adapter_clazz = type(adapter_clazz_name, (object,), {})

    assert len(constructors) < 2, "only zero or one constructors allowed"

    mapping = dict()
    if len(constructors) == 1:
        constructor = constructors[0]

        params = ""
        for i in range(len(constructor.inputs)):
            params += f"param{i}"

        init_name = '__init__'
        init_source = f"def {adapter_prefix}_cls_init(self, {params}):\n\tpass" #self.type = 3"
        init_obj = create_callable(f"{adapter_prefix}_cls_init", init_source)
        #adapter_clazz.__init__ = cls_init
        setattr(adapter_clazz, init_name, init_obj)

        mapping[getattr(adapter_clazz, init_name)] = constructor
    if len(methods) > 0:
        for method in methods:
            params = ""
            for i in range(len(method.inputs)):
                params += f"param{i}"

            method_name = f"{adapter_prefix}_{method.name}"
            method_source = f"def {method_name}(self, {params}):\n\tpass"
            method_obj = create_callable(method_name, method_source)

            logger.debug(f"{method_obj}")

            setattr(adapter_clazz, method.name, method_obj)
            mapping[getattr(adapter_clazz, method.name)] = method

    #
    logger.debug(adapter_clazz.__name__)
    logger.debug(inspect.getmembers(adapter_clazz))

    return InterfaceMapping(interface_specification, adapter_clazz, mapping)


def interpret_sheet(test_invocation: TestInvocation):
    """
    Interpretation (dry) run of parsed sheet (resolves all bindings)

    :param test:
    :return:
    """

    test = test_invocation.test

    interface_mapping = lql_to_python_class(test.interface_specification)

    invocations = Invocations(test_invocation, interface_mapping)

    for parsed_row in test.parsed_sheet.rows:
        output = parsed_row.get_output()
        operation = parsed_row.get_operation()
        inputs = parsed_row.get_inputs()

        #either points to class name to instantiate (with "create" operation) or reference to object
        clazz_cell = inputs[0]
        input_args = []
        #remaining input parameters
        if len(inputs) > 1:
            input_args = inputs[1:]

        invocation = None
        if operation.value.lower() in SSN_CREATE:
            # constructor invocation
            clazz_name = clazz_cell.value
            invocation = instance_invocation(invocations, clazz_name, input_args)
        elif operation.value.lower() in SSN_EVAL:
            # code invocation
            invocation = code_invocation(invocations, clazz_cell)
        else:
            # method invocation
            invocation = method_invocation(invocations, clazz_cell, operation.value, input_args)

        # resolve expected output
        expected_output = resolve_parameter_type(invocations, output)
        invocation.expected_output = expected_output

    return invocations


def resolve_inputs(executed_invocations: ExecutionInvocations, executed_invocation: ExecutedInvocation):
    invocation = executed_invocation.invocation
    inputs = []
    for parameter in invocation.parameters:
        if parameter.is_reference():
            ref = executed_invocations.get_executed_invocation(parameter.coordinate[0])
            inputs.append(ref.output)
        else:
            # assumes code expression
            obj = Obj()
            try:
                result = eval_code_expression(parameter.expression)
                obj.value = result
            except Exception as e:
                obj.exception = e

            inputs.append(obj)

    return inputs


class InvocationListener:
    """
    Listener for sheet invocations on adapted implementation candidates.
    """

    # def visit_before_execution(self, adapted_implementation: AdaptedImplementation):
    #     logger.debug(f"before execution {adapted_implementation}")
    #
    #
    # def visit_after_execution(self, adapted_implementation: AdaptedImplementation):
    #     logger.debug(f"after execution {adapted_implementation}")


    def visit_before_invocation(self, executed_invocations: ExecutionInvocations, index: int, adapted_implementation: AdaptedImplementation):
        logger.debug(f"before invocation {index}, {adapted_implementation}")


    def visit_after_invocation(self, executed_invocations: ExecutionInvocations, index: int, adapted_implementation: AdaptedImplementation):
        logger.debug(f"after invocation {index}, {adapted_implementation}")


    def visit_before_invocations(self, executed_invocations: ExecutionInvocations,
                                adapted_implementation: AdaptedImplementation):
        logger.debug(f"before all invocations, {adapted_implementation}")


    def visit_after_invocations(self, executed_invocations: ExecutionInvocations,
                               adapted_implementation: AdaptedImplementation):
        logger.debug(f"after all invocations, {adapted_implementation}")


def run_sheet(invocations: Invocations, adapted_implementation: AdaptedImplementation, invocation_listener: InvocationListener = InvocationListener()):
    """
    Run stimulus sheet on adapted implementation candidate.

    :param invocations:
    :param adapted_implementation:
    :param invocation_listener
    :return:
    """
    executed_invocations = ExecutionInvocations(invocations, adapted_implementation)

    # before execution
    try:
        invocation_listener.visit_before_invocations(executed_invocations, adapted_implementation)
    except Exception as e:
        logger.warning(e)

    for invocation in invocations.sequence:
        executed_invocation = executed_invocations.create(invocation)

        # resolve inputs
        inputs = resolve_inputs(executed_invocations, executed_invocation)
        executed_invocation.inputs = inputs

        # before execution invocation
        try:
            invocation_listener.visit_before_invocation(executed_invocations, executed_invocation.invocation.index, adapted_implementation)
        except Exception as e:
            logger.warning(e)

        # execute the invocation
        start_time = time.time()
        try:
            invocation.execute(executed_invocations, executed_invocation, adapted_implementation)
        except Exception as e:
            logger.warning(e)

        end_time = time.time()
        execution_time = int((end_time - start_time) * 1_000_000)  # Convert to microseconds
        logger.debug(f"sheet execution took {execution_time} microseconds")

        # after execution invocation
        try:
            invocation_listener.visit_after_invocation(executed_invocations, executed_invocation.invocation.index, adapted_implementation)
        except Exception as e:
            logger.warning(e)


    # after execution
    try:
        invocation_listener.visit_after_invocations(executed_invocations, adapted_implementation)
    except Exception as e:
        logger.warning(e)

    return executed_invocations
