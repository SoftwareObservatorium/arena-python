import importlib
import logging
import os
import sys

from arena.engine.classes import ClassUnderTest

logger = logging.getLogger(__name__)


class CodeCandidate:
    """
    A code candidate (e.g., local directory of code modules of a code candidate)
    """

    def __init__(self, id: str, clazz_name: str, folder: str):
        self.id = id
        self.clazz_name = clazz_name
        self.folder = folder
        self.code_module = None

    def __str__(self):
        return f"{self.id} => {self.folder}"


def from_local_directory(folder: str):
    """
    Load code artifacts (i.e., candidates) from local directory

    :param folder:
    :return:
    """

    candidate_folders = [f.path for f in os.scandir(folder) if f.is_dir()]
    candidate_ids = [os.path.basename(f) for f in candidate_folders]

    candidates = []
    for c in range(len(candidate_folders)):
        code_candidate = CodeCandidate(candidate_ids[c], "", candidate_folders[c])
        candidates.append(code_candidate)

    return candidates


def import_candidate_module(candidate: CodeCandidate):
    """
    Import code candidate into python execution environment

    :param candidate:
    :return:
    """

    candidate_id = candidate.id

    spec = importlib.util.spec_from_file_location(candidate_id, candidate.folder)
    candidate_module = importlib.util.module_from_spec(spec)
    sys.modules[candidate_id] = candidate_module
    spec.loader.exec_module(candidate_module)

    candidate.code_module = candidate_module


def import_classes_under_test(candidates: [CodeCandidate]) -> [ClassUnderTest]:
    """
    Import all candidates

    :param candidates:
    :return:
    """

    cuts = []
    for candidate in candidates:
        import_candidate_module(candidate)

        cut = ClassUnderTest(candidate.id, candidate.clazz_name, code_candidate=candidate)
        cuts.append(cut)

    return cuts