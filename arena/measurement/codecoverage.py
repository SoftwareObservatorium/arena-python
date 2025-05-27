import json
import logging
import tempfile
import traceback

import coverage

from arena.engine.artifacts import CodeCandidate


logger = logging.getLogger(__name__)


def create_coverage_for(code_candidate: CodeCandidate) -> coverage.Coverage:
    """
    Measure code coverage for given candidate module

    :param code_candidate:
    :return:
    """

    cov = coverage.Coverage(source=[code_candidate.code_module.__name__], branch=True, data_file=f"{code_candidate.folder}.coverage")

    return cov


def get_metrics(cov: coverage.Coverage, code_candidate: CodeCandidate):
    """
    get metric measurements

    :param cov:
    :return:
    """

    measures = {}

    with tempfile.NamedTemporaryFile(delete_on_close=True) as fp:
        try:
            logger.info(f"creating temp file {fp.name}")

            cov.json_report(outfile=fp.name)
        except Exception as e:
            logger.warning(f"Error storing coverage report: {e}")
            traceback.print_exception(e)
            return measures


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

                measures['lines.total'] = candidate_measurement["summary"]["num_statements"]
                measures['lines.covered'] = candidate_measurement["summary"]["covered_lines"]
                measures['lines.missed'] = candidate_measurement["summary"]["missing_lines"]

                logger.debug(f"coverage report for branches {measures}")
            except Exception as e:
                logger.warning(e)

    return measures