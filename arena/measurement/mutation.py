import logging

from mutmut.__main__ import yield_mutants_for_module
from parso import parse

from arena.engine.artifacts import CodeCandidate

logger = logging.getLogger(__name__)


def create_mutants(code_candidate: CodeCandidate):
    with open(code_candidate.folder) as f:
        source = f.read()

        #logger.debug(f"source {source}")

        parsed_source = parse(source)

        # for type_, x, name_and_hash, mutant_name in yield_mutants_for_module(parsed_source, no_mutate_lines=[]):
        #     logger.debug(f"mutant {type_} {x} {name_and_hash} {mutant_name}")

        mutants = [
            mutant
            for type_, mutant, _, _ in yield_mutants_for_module(parsed_source, {})
            if type_ == 'mutant'
        ]
        logger.debug(f"mutant {mutants}")

        logger.debug(f"created {len(mutants)} mutants")
