import inspect
import logging
from pydoc import locate


logger = logging.getLogger(__name__)


def is_function(operation):
    return inspect.isfunction(operation)


def resolve_type_by_name(type_str: str):
    """
    Lookup type object for given type

    :param type_str:
    :return:
    """
    return locate(type_str)


def resolve_constructor(clazz, input_types):
    """
    Resolve constructor given clazz

    :param clazz:
    :param input_types:
    :return:
    """

    # FIXME resolve constructor (there's only ONE constructor in Python!)
    sig = inspect.signature(clazz.__init__)
    logger.debug(f"found constructor {sig} for type {clazz}")

    # FIXME check input_types

    return clazz.__init__


def resolve_operation(clazz, operation_name, input_types):
    """
    Resolve method/function for given clazz

    :param clazz:
    :param operation_name:
    :param input_types:
    :return:
    """

    if operation_name == "len":
        return len

    op = getattr(clazz, operation_name)

    # FIXME check input_types

    return op


def get_source_code(code_unit):
    """
    Obtain source code

    :param code_unit:
    :return:
    """

    return inspect.getsource(code_unit)


def is_method(unit):
    # return inspect.ismethod(unit) for whatever reason, this doesn't work reliably
    if inspect.ismethod(unit):
        return True

    if not inspect.isfunction(unit):
        return False

    signature = inspect.signature(unit)
    has_self = 'self' in signature.parameters.keys() # FIXME find better ways ..

    return has_self

