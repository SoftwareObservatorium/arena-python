import argparse
import logging
import os.path
import sys
import time

from arena.arena import Sheet, parse_stimulus_matrix, SheetInvocation, run_sheets
from arena.engine.adaptation import PassThroughAdaptationStrategy, SingleFunctionAdaptationStrategy
from arena.engine.artifacts import write_modules_and_import_lasso_cuts
from arena.engine.ssntestdriver import InvocationListener
from lasso.job.ignite import LassoClusterClient, ClientArenaJobRepository, ClientSrmRepository
from lasso.srh.serialize import SRHWriter

# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


PROJECT_ROOT = os.path.dirname(__file__)


def parse_features(feature_string):
  """
  Parses a comma-delimited string of features into a list of strings.

  Args:
    feature_string: A string containing comma-separated features.  Can handle
      leading/trailing whitespace and multiple spaces between commas.

  Returns:
    A list of strings, where each string represents a feature.  Returns an
    empty list if the input string is empty or None.
  """
  if not feature_string:  # Handle empty or None input
    return []

  # Split the string by commas and strip whitespace from each resulting part
  features = [feature.strip() for feature in feature_string.split(',')]

  # Remove any empty strings that might have resulted from multiple commas
  features = [feature for feature in features if feature]

  return features


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Arena Test Driver")
    parser.add_argument("--mode", default="distributed", help="Mode of Operation")
    parser.add_argument("--lassoaddresses", default="127.0.0.1:10800", help="LASSO Ignite Thin Client Addresses")
    parser.add_argument("--lassojob", help="LASSO Job ID")
    parser.add_argument("--workdir", default=".", help="Work directory")

    parser.add_argument("--features", default="", help="Features to enable")
    parser.add_argument("--task", default="SSNExecute", help="Arena Task to call")

    # parse arguments
    args = parser.parse_args()

    # get candidates via cache
    logger.info(f"Connecting to LASSO cluster via {args.lassoaddresses}")
    ssl_params = {
        'ssl_keyfile': '/ssl/lasso_selfsigned_key.pem',  # private key (if required)
        'ssl_certfile': '/ssl/lasso_selfsigned_cert.pem',  # client certificate (if required)
        'ssl_ca_certfile': '/ssl/lasso_selfsigned_cert.pem',  # CA certificate or self-signed cert
        'ssl_cert_reqs': 'CERT_NONE',  # 'CERT_NONE' for testing/self-signed
    }

    cluster_client = LassoClusterClient(ssl_params=ssl_params, address=args.lassoaddresses)
    job_repository = ClientArenaJobRepository(cluster_client)

    job_id = args.lassojob
    logger.info(f"LASSO Job ID is '{job_id}'")

    # json
    job = job_repository.get_as_json(job_id)

    logger.info(f"JOB JSON {job}")

    # FIXME job configuration
    adapter_strategy = PassThroughAdaptationStrategy()
    if job['adapterStrategy']:
        if job['adapterStrategy'] == 'PassThroughAdaptationStrategy':
            adapter_strategy = PassThroughAdaptationStrategy()
        elif job['adapterStrategy'] == 'SingleFunctionAdaptationStrategy':
            adapter_strategy = SingleFunctionAdaptationStrategy()

    limit_adapters = job['maxPermutations']
    #job['scope'] scope for measurements

    # enable features
    features = parse_features(args.features)
    measure_code_coverage = "cc" in features
    mutation_coverage = "mutation" in features

    # prepare sheets
    stimulus_sheets = job['stimulusSheets']

    logger.info(f"Total number of stimulus sheets {len(stimulus_sheets)}")

    sheets = []
    sheet_invocations = []
    for sheet in stimulus_sheets:
        signature = sheet['signature']
        # FIXME invocations (list): sheet['invocations']
        name = signature.split('(', 1)[0]
        sheet_invocations.append(SheetInvocation(name, ""))

        # FIXME sheet['ssn'] (if ssn: XXX else : python test ..

        sheets.append(Sheet(signature, sheet['body'], sheet['interfaceSpecification']))

    logger.info(f"sheets {len(sheets)}")

    # prepare implementations
    implementations = job['implementations']

    # FIXME in docker container: permission denied
    #target_folder = f"{args.workdir}/python-{round(time.time() * 1000)}"
    target_folder = f"/tmp/arena-python-{round(time.time() * 1000)}"
    # units under test
    cuts = write_modules_and_import_lasso_cuts(target_folder, implementations)

    logger.info(f"cuts {cuts}")

    # create stimulus matrix
    sm = parse_stimulus_matrix(sheets, cuts, sheet_invocations)
    logger.info(sm.to_string())

    # run stimulus matrix
    try:
        invocation_listener = InvocationListener()

        arena_id = "myarenaid"  # FIXME arena id

        srm = run_sheets(sm, limit_adapters, invocation_listener, measure_code_coverage=measure_code_coverage, adaptation_strategy=adapter_strategy)
        # results based on internal ExecutedInvocation
        logger.info(srm.to_string())

        # store SRM (CellValue schema)
        srh_writer = SRHWriter(ClientSrmRepository(cluster_client))
        srh_writer.store_srm(job, arena_id, srm)

        # update job status
        #     CREATED,
        #     FINISHED,
        #     FAILED
        job_repository.put(job_id, "FINISHED")
    except Exception as e:
        logger.warning(f"Run sheets failed with {e}")
        job_repository.put(job_id, "FAILED")
    finally:
        # close
        cluster_client.close()
