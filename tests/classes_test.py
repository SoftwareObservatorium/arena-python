import collections
import logging
import sys
from collections import deque

from arena.engine.classes import ClassUnderTest

# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def test_load_by_name():
    # by type
    cut = ClassUnderTest("1", deque)
    assert cut.class_under_test is deque
    # by fully qualified type
    cut = ClassUnderTest("1", collections.deque)
    assert cut.class_under_test is deque
    # by class name DOES NOT WORK
    cut = ClassUnderTest("1", "deque")
    assert cut.class_under_test is None
    # by fully-qualified class name works
    cut = ClassUnderTest("1", "collections.deque")
    assert cut.class_under_test is deque
