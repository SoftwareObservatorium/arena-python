import logging
import sys

from arena.lql.lqlparser import parse_lql

# logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def test_parse():
    lql = """Base64 { encode(byte[])->byte[] }"""
    parse_result = parse_lql(lql)

    interface = parse_result.interface
    assert "Base64" == interface.name
    assert 1 == len(interface.methods)
    assert "encode" == interface.methods[0].name
    assert ["byte[]"] == interface.methods[0].inputs
    assert ["byte[]"] == interface.methods[0].outputs
