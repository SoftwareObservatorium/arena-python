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

    def __init__(self, class_under_test, initializer_mapping: dict, method_mapping: dict):
        self.class_under_test = class_under_test
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


class AdaptationStrategy:
    """
    Interface for adaptation strategies
    """

    def adapt(self, interface_specification, class_under_test, no_adapters: int) -> [AdaptedImplementation]:
        pass


class PassThroughAdaptationStrategy(AdaptationStrategy):
    """
    Simple pass through strategy (1:1 mapping between interface spec and python callables)
    """

    def adapt(self, interface_specification, class_under_test, no_adapters: int) -> [AdaptedImplementation]:
        """
        Only one adapter is created. The interface of the class under test is assumed to match the lql interface.

        :param interface_specification:
        :param class_under_test:
        :return:
        """

        initializer_mapping = self.resolve_initializers(interface_specification, class_under_test)
        method_mapping = self.resolve_methods(interface_specification, class_under_test)

        return [AdaptedImplementation(class_under_test, initializer_mapping, method_mapping)]


    def resolve_methods(self, interface_specification, class_under_test):
        """
        Resolve method bindings

        :param interface_specification:
        :param class_under_test:
        :return:
        """

        mapping = dict()

        for method in interface_specification.get_methods():
            callable_obj = None
            # FIXME python builtin functions in resolution process
            # FIXME centralize resolution
            if method.name == "len":
                callable_obj = len
            else:
                callable_obj = getattr(class_under_test, method.name)

            mapping[method] = callable_obj

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

