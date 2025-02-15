from arena.lql.lqlparser import parse_lql


def test_parse():
    lql = """Base64 { encode(byte[])->byte[] }"""
    parse_result = parse_lql(lql)

    interface = parse_result.interface
    assert "Base64" == interface.name
    assert 1 == len(interface.methods)
    assert "encode" == interface.methods[0].name
    assert ["byte[]"] == interface.methods[0].inputs
    assert ["byte[]"] == interface.methods[0].outputs
