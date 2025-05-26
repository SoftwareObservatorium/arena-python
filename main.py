import argparse
import logging
import os.path
import sys
import time

import pandas as pd

from arena.arena import Sheet, parse_stimulus_matrix, SheetInvocation, run_sheets
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
    #job['adapterStrategy']
    #job['maxPermutations']
    #job['specification']
    #job['scope']

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

    # FIXME permission denied
    #target_folder = f"{args.workdir}/python-{round(time.time() * 1000)}"
    target_folder = f"/tmp/arena-python-{round(time.time() * 1000)}"
    # units under test
    cuts = write_modules_and_import_lasso_cuts(target_folder, implementations)

    logger.info(f"cuts {cuts}")

    # create stimulus matrix
    sm = parse_stimulus_matrix(sheets, cuts, sheet_invocations)
    logger.info(sm.to_string())

    # run stimulus matrix
    invocation_listener = InvocationListener()
    srm = run_sheets(sm, 1, invocation_listener)
    # results based on internal ExecutedInvocation
    logger.info(srm.to_string())

    # FIXME store SRM (CellValue schema)
    srh_writer = SRHWriter(ClientSrmRepository(cluster_client))
    srh_writer.store_srm(job, "myarenaid", srm)

    # update job status
    #     CREATED,
    #     FINISHED,
    #     FAILED
    job_repository.put(job_id, "FINISHED")

    # close
    cluster_client.close()
