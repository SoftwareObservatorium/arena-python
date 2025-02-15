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


# def instantiate_with_reflection(cls, *args):
#     """
#     Dynamically instantiates a class based on its constructor parameters.
#
#     Args:
#         cls (type): The class to instantiate.
#         *args: A tuple of values to pass as arguments.
#
#     Returns:
#         Instance of the specified class.
#     """
#     # Check if __init__ is present
#     if not hasattr(cls, '__init__'):
#         raise TypeError(f"Class {cls.__name__} does not have an __init__ method.")
#
#     sig = inspect.signature(cls.__init__)
#     bound_arguments = sig.bind(*args)
#     bound_arguments.apply_defaults()
#
#     # Prepare the arguments for instantiation
#     prepare_args = []
#     for name, param in sig.parameters.items():
#         if param.default == inspect.Parameter.empty:
#             raise TypeError(f"Missing required argument: {name}")
#
#         value = args[index]
#         typehint = param.annotation
#         if isinstance(value, type) and typehint is not type:
#             raise TypeError(f"Type mismatch for parameter '{name}': expected {typehint}, got {type(value)}")
#
#         prepare_args.append((name, value))
#
#     # Create the instance
#     instance = cls.__prepare__(*args)
#     for name, value in prepare_args:
#         setattr(instance, name, value)
#     return instance
#
#
# try:
#     obj = instantiate_with_reflection(MyClass, arg1=value1, arg2=value2)
# except Exception as e:
#     print(f"Failed to instantiate class: {e}")

# def method_matches(instance_class):
#     def predicate(self, *args):
#         for name in dir(instance_class):
#             attr = getattr(instance_class, name)
#             if callable(attr) and isinstance(attr, MethodType):
#                 sig = inspect.signature(attr)
#                 try:
#                     bound_arguments = sig.bind(self.__dict__.copy(), *args)
#                 except TypeError as e:
#                     continue
#                 else:
#                     for param in sig.parameters.values():
#                         annotation = param.annotation
#                         if not isinstance(bound_arguments.get(param.name, None), annotation):
#                             return False
#                     return True
#         return False
#
#     return predicate
#
#
# # Usage example:
# class MyClass:
#     def my_method(self, a: int, b: str) -> bool:
#         return a > 5 and b.startswith('test')
#
#
# MyClass.my_method = method_matches(MyClass)
# instance = MyClass()
# print(MyClass.my_method(instance, 10, 'testing'))  # Should print True