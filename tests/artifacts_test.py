import collections
import logging
import os
import sys
from collections import deque

from arena.engine.artifacts import from_local_directory
from arena.engine.classes import ClassUnderTest

# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def test_from_local_directory():
    #
    logger.debug(f"{os.getcwd()}")

    folder = f"{os.getcwd()}/../code-samples/base64/"

    candidates = from_local_directory(folder)
    logger.debug(f"{candidates}")

    assert 3 == len(candidates)
