import argparse
import logging
import os.path
import sys

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
    # parser.add_argument("--someparam", required=True,
    #                     help="XXX")
    # parser.add_argument("--someparam", default=".", help="YYY")
    # parser.add_argument("--someparam", type=int, default=50, help="ZZZ")

    # FIXME parse arguments
    #args = parser.parse_args()

    # get candidates via cache

    # prepare sheets

    # run sheets

    # store SRM
