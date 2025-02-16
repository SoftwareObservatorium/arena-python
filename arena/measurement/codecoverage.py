import json
import logging
import tempfile

import coverage

from arena.engine.artifacts import CodeCandidate


logger = logging.getLogger(__name__)


def create_coverage_for(code_candidate: CodeCandidate) -> coverage.Coverage:
    """
    Measure code coverage for given candidate module

    :param code_candidate:
    :return:
    """

    cov = coverage.Coverage(source=[code_candidate.code_module.__name__], branch=True)

    return cov


def get_metrics(cov: coverage.Coverage, code_candidate: CodeCandidate):
    """
    get metric measurements

    :param cov:
    :return:
    """

    measures = {}

    with tempfile.NamedTemporaryFile(delete_on_close=False) as fp:
        try:
            cov.json_report(outfile=fp.name)
        except Exception as e:
            logger.warning(f"Error storing coverage report: {e}")
            raise e


        # open file
        with open(fp.name, mode='rb') as f:
            try:
                parsed_json = json.load(f)
                logger.debug(f"coverage report {parsed_json}")

                # assume first key is candidate
                first_file = next(iter(parsed_json["files"]))

                # FIXME create observations for SRM
                candidate_measurement = parsed_json["files"][first_file]

                measures['branches.total'] = candidate_measurement["summary"]["num_branches"]
                measures['branches.covered'] = candidate_measurement["summary"]["covered_branches"]
                measures['branches.missed'] = candidate_measurement["summary"]["missing_branches"]

                logger.debug(f"coverage report for branches {measures}")
            except Exception as e:
                raise e

    return measures