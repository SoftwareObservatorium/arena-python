import logging
from types import ModuleType

from arena.introspection import resolve_type_by_name


logger = logging.getLogger(__name__)


def load_by_name(clazz_name: str):
    """
    Simple strategy to load classes by fully qualified name

    FIXME isolation (class loader etc.)

    :param clazz_name:
    :return:
    """

    logger.debug(f"trying to load {clazz_name}")

    return resolve_type_by_name(clazz_name)


def load_from_candidate_module(candidate):
    """
    Simple strategy to load classes by fully qualified name

    FIXME isolation (class loader etc.)

    :param clazz_name:
    :return:
    """

    logger.debug(f"trying to load {candidate.clazz_name} from candidate module {candidate.code_module}")

    if len(candidate.clazz_name) == 0:
        return candidate.code_module

    return getattr(candidate.code_module, candidate.clazz_name)


class ClassUnderTest:
    """
    Models a class under test
    """

    def __init__(self, id: str, class_under_test, code_candidate = None):
        self.id = id
        self.variant_id = "original"
        self.code_candidate = code_candidate

        if isinstance(class_under_test, str):
            if code_candidate is not None:
                self.class_under_test = load_from_candidate_module(code_candidate)
            else:
                self.class_under_test = load_by_name(class_under_test)
        else:
            self.class_under_test = class_under_test


    def is_module(self):
        """
        Is the unit under test a module or class

        :return:
        """

        return type(self.class_under_test) is ModuleType


    def __str__(self):
        return f"{self.id}_{self.variant_id}"

