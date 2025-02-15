import logging

import pandas as pd

from arena.engine.adaptation import PassThroughAdaptationStrategy, AdaptedImplementation
from arena.engine.ssntestdriver import InvocationListener, run_sheet, interpret_sheet, Test, ExecutedInvocation, \
    CodeInvocation, InstanceInvocation, MethodInvocation, Obj
from arena.lql.lqlparser import parse_lql, Interface
from arena.ssn.ssnparser import parse_sheet, ParsedSheet


logger = logging.getLogger(__name__)


class Sheet:
    """
    A stimulus sheet
    """

    def __init__(self, name: str, body: str, interface_lql: str):
        self.name = name
        self.body = body
        self.interface_lql = interface_lql


def parse_stimulus_matrix(sheets: [Sheet], cuts: list) -> pd.DataFrame:
    """
    Parse stimulus matrix

    :param sheets:
    :param cuts:
    :return:
    """

    tests = []
    for sheet in sheets:
        parsed_sheet = parse_sheet(sheet.body)
        parse_lql_result = parse_lql(sheet.interface_lql)
        tests.append(Test(sheet.name, parsed_sheet, parse_lql_result.interface))

    data = {}
    for cut in cuts:
        test_invocations = []
        for test in tests:
            test_invocations.append(test)

        data[cut] = test_invocations

    logger.debug(data)

    sm = pd.DataFrame.from_dict(data)

    return sm


def run_sheets(sm: pd.DataFrame, limit_adapters: int, invocation_listener: InvocationListener) -> pd.DataFrame:
    """
    Run stimulus matrix and return Stimulus Response Matrix (pandas DataFrame)

    :param sm:
    :param limit_adapters:
    :param invocation_listener:
    :return:
    """

    data = {}
    for cut in sm.columns:
        logger.debug(f"processing cut {cut}")
        # pick some random test
        random_test = sm[cut].iloc[0]

        adaptation_strategy = PassThroughAdaptationStrategy()
        adapted_implementations = adaptation_strategy.adapt(random_test.interface_specification, cut, limit_adapters)

        for adapted_implementation in adapted_implementations:
            logger.debug(f" Adapted implementation {adapted_implementation.adapter_id} of class under test {adapted_implementation.cut.class_under_test}")

            executed_tests = []
            for test in sm[cut]:
                # interpret (resolve bindings)
                invocations = interpret_sheet(test)

                # run
                executed_invocations = run_sheet(invocations, adapted_implementation, invocation_listener)

                executed_tests.append(executed_invocations)

            data[adapted_implementation] = executed_tests

        srm = pd.DataFrame.from_dict(data)

    return srm


def collect_actuation_sheets(srm: pd.DataFrame) -> pd.DataFrame:
    """
    Print contents of SRM (i.e., as actuation sheets)

    :param srm:
    :return:
    """

    data = {}
    for adapted_implementation in srm.columns:
        actuations = []
        for executed_invocations in srm[adapted_implementation]:
            actuation_data = {'output': [], 'operation': [], 'service': []}

            max_inputs = 0
            for executed_invocation in executed_invocations.executed_sequence:
                if len(executed_invocation.inputs) > max_inputs:
                    max_inputs = len(executed_invocation.inputs)

            for i in range(max_inputs):
                param = f"input_{i}"
                actuation_data[param] = [None] * len(executed_invocations.executed_sequence)

            for executed_invocation in executed_invocations.executed_sequence:
                actuation_data['output'].append(output_as_string(executed_invocation, adapted_implementation))
                actuation_data['operation'].append(op_as_string(executed_invocation, adapted_implementation))
                actuation_data['service'].append(target_as_string(executed_invocation, adapted_implementation))

                if len(executed_invocation.inputs) > 0:
                    for i in range(len(executed_invocation.inputs)):
                        param = f"input_{i}"
                        actuation_data[param][executed_invocation.invocation.index] = to_string(executed_invocation.inputs[i], adapted_implementation)

            actuations.append(pd.DataFrame.from_dict(actuation_data))
        data[adapted_implementation] = actuations

    return pd.DataFrame.from_dict(data)


def output_as_string(executed_invocation: ExecutedInvocation, adapted_implementation: AdaptedImplementation):
    return to_string(executed_invocation.output, adapted_implementation)


def op_as_string(executed_invocation: ExecutedInvocation, adapted_implementation: AdaptedImplementation):
    invocation = executed_invocation.invocation
    if type(invocation) is CodeInvocation:
        return invocation.expression
    elif type(invocation) is InstanceInvocation:
        if executed_invocation.adapted_member is not None:
            return str(executed_invocation.adapted_member.member.__name__)

        return str(invocation.member.__name__)
    elif type(invocation) is MethodInvocation:
        if executed_invocation.adapted_member is not None:
            return str(executed_invocation.adapted_member.member.__name__)

        return str(invocation.member.__name__)
    else:
        raise Exception(f"unknown invocation type {type(invocation)}")


def target_as_string(executed_invocation: ExecutedInvocation, adapted_implementation: AdaptedImplementation):
    invocation = executed_invocation.invocation
    if type(invocation) is CodeInvocation:
        return "$eval"
    elif type(invocation) is InstanceInvocation:
        return invocation.target_class.__name__
    elif type(invocation) is MethodInvocation:
        return to_string(executed_invocation.resolve_target_instance(), adapted_implementation)
    else:
        raise Exception(f"unknown invocation type {type(invocation)}")


def to_string(obj: Obj, adapted_implementation: AdaptedImplementation):
    serialized_str = ""
    if obj.has_exception():
        serialized_str =  f"$EXCEPTION@{type(obj.exception)}@{str(obj.exception)}"
    elif obj.value is None:
        serialized_str = None
    else:
        # FIXME is cut, otherwise value
        if obj.is_cut(adapted_implementation.cut.class_under_test):
            serialized_str = f"$CUT@{type(obj.value).__name__}@{obj.producer_index}"
        else:
            serialized_str = str(obj.value)

    return serialized_str

