import logging
import sys

import main
from arena.engine.artifacts import from_local_directory

# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def test_from_local_directory():
    folder = f"{main.PROJECT_ROOT}/code-samples/base64/"

    candidates = from_local_directory(folder)
    logger.debug(f"{candidates}")

    assert 3 == len(candidates)
