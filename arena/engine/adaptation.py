import inspect
import logging

from arena import introspection

logger = logging.getLogger(__name__)


class AdaptedMethod:
    """
    An adapted method (mapping between LQL signature and python callable)
    """

    def __init__(self, adapted_implementation, method_signature, member):
        self.adapted_implementation = adapted_implementation
        self.method_signature = method_signature
        self.member = member


class AdaptedInitializer:
    """
    An adapted initializer (mapping between LQL signature and python callable)
    """

    def __init__(self, adapted_implementation, method_signature, member):
        self.adapted_implementation = adapted_implementation
        self.method_signature = method_signature
        self.member = member


class AdaptedImplementation:
    """
    Model for adapted implementation
    """

    def __init__(self, cut, initializer_mapping: dict, method_mapping: dict):
        self.cut = cut
        self.initializer_mapping = initializer_mapping
        self.method_mapping = method_mapping
        self.adapter_id = "0"


    def get_method(self, interface_specification, index: int) -> AdaptedMethod:
        method_signature = interface_specification.methods[index]
        method = self.method_mapping[method_signature]

        return AdaptedMethod(self, method_signature, method)


    def get_initializer(self, interface_specification, index: int):
        init_signature = interface_specification.constructors[index]
        init = self.initializer_mapping[init_signature]

        return AdaptedMethod(self, init_signature, init)


    def __str__(self):
        return f"{str(self.cut.id)}_{self.cut.variant_id}_{self.adapter_id}"


class AdaptationStrategy:
    """
    Interface for adaptation strategies
    """

    def adapt(self, interface_specification, cut, no_adapters: int) -> [AdaptedImplementation]:
        pass


class PassThroughAdaptationStrategy(AdaptationStrategy):
    """
    Simple pass through strategy (1:1 mapping between interface spec and python callables)
    """

    def adapt(self, interface_specification, cut, no_adapters: int) -> [AdaptedImplementation]:
        """
        Only one adapter is created. The interface of the class under test is assumed to match the lql interface.

        :param interface_specification:
        :param class_under_test:
        :return:
        """

        initializer_mapping = self.resolve_initializers(interface_specification, cut.class_under_test)
        method_mapping = self.resolve_methods(interface_specification, cut.class_under_test)

        return [AdaptedImplementation(cut, initializer_mapping, method_mapping)]


    def resolve_methods(self, interface_specification, class_under_test):
        """
        Resolve method bindings

        :param interface_specification:
        :param class_under_test:
        :return:
        """

        mapping = dict()

        for method_spec in interface_specification.get_methods():
            callable_obj = None
            # python builtin functions in resolution process
            if method_spec.name in introspection.builtin_map:
                callable_obj = introspection.builtin_map[method_spec.name]
            else:
                callable_obj = getattr(class_under_test, method_spec.name)

            mapping[method_spec] = callable_obj

        return mapping


    def resolve_initializers(self, interface_specification, class_under_test):
        """
        Resolve initializer bindings

        :param interface_specification:
        :param class_under_test:
        :return:
        """

        mapping = dict()

        constructors = interface_specification.get_constructors()

        # should be only one constructor
        if len(constructors) > 0:
            assert 1 == len(constructors), "only one constructor supported in Python"

            constructor = constructors[0]
            callable_obj = getattr(class_under_test, "__init__")
            mapping[constructor] = callable_obj

        return mapping

class SingleFunctionAdaptationStrategy(AdaptationStrategy):
    """
    Simple adaptation based on the assumption that only one function exists in a module (*.py file) that will match our signature.
    Only works for single functions.
    """

    def adapt(self, interface_specification, cut, no_adapters: int) -> [AdaptedImplementation]:
        """
        Only one adapter is created. The interface of the class under test is assumed to match the lql interface.

        :param interface_specification:
        :param class_under_test:
        :return:
        """

        initializer_mapping = self.resolve_initializers(interface_specification, cut.class_under_test)
        method_mapping = self.resolve_methods(interface_specification, cut.class_under_test)

        return [AdaptedImplementation(cut, initializer_mapping, method_mapping)]


    def resolve_methods(self, interface_specification, class_under_test):
        """
        Resolve method bindings

        :param interface_specification:
        :param class_under_test:
        :return:
        """

        mapping = dict()

        for method_spec in interface_specification.get_methods():
            callable_obj = None
            # python builtin functions in resolution process
            if method_spec.name in introspection.builtin_map:
                callable_obj = introspection.builtin_map[method_spec.name]
            else:
                try:
                    callable_obj = getattr(class_under_test, method_spec.name)
                except AttributeError as ae:
                    # method/function does not exist at all, try to adapt
                    logger.info(f"Method/Function '{method_spec.name}' not found. Adaption needed.")

                    declared_functions = []

                    for name, obj in inspect.getmembers(class_under_test, inspect.isfunction):
                        #if obj.__module__ == my_module.__name__:
                        declared_functions.append((name, obj))

                    logger.info("Declared-in-this-module functions:")
                    for name, fn in declared_functions:
                        logger.debug(f" - {name}: {fn}")

                    if len(declared_functions) < 1:
                        raise AttributeError("no declared function found")

                    if len(declared_functions) > 1:
                        logger.warning(f"more than one function found for adaptation: {len(declared_functions)}")

                    # settle on the first one
                    callable_obj = declared_functions[0][1] # is tuple
                    logger.info(f"set adapted to {callable_obj}")

            mapping[method_spec] = callable_obj

        return mapping


    def resolve_initializers(self, interface_specification, class_under_test):
        """
        Resolve initializer bindings

        :param interface_specification:
        :param class_under_test:
        :return:
        """

        mapping = dict()

        constructors = interface_specification.get_constructors()

        # should be only one constructor
        if len(constructors) > 0:
            assert 1 == len(constructors), "only one constructor supported in Python"

            constructor = constructors[0]
            callable_obj = getattr(class_under_test, "__init__")
            mapping[constructor] = callable_obj

        return mapping

