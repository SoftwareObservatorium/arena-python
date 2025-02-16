import logging

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


class ClassUnderTest:
    """
    Models a class under test
    """

    def __init__(self, id: str, class_under_test):
        self.id = id

        if isinstance(class_under_test, str):
            self.class_under_test = load_by_name(class_under_test)
        else:
            self.class_under_test = class_under_test
