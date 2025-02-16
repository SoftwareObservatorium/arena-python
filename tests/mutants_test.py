import logging
import sys

import main
from arena.engine.artifacts import CodeCandidate, import_candidate_module
from arena.measurement.mutation import create_mutants

# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def test_create_mutants():
    base_folder = f"{main.PROJECT_ROOT}/code-samples/base64"
    c1 = CodeCandidate("c108afda-e52c-454b-a7ed-c05f48257a9b", "Base64", f"{base_folder}/c108afda-e52c-454b-a7ed-c05f48257a9b/candidate.py")
    import_candidate_module(c1)

    #logger.debug(f"code module {c1.code_module}")

    create_mutants(c1)
