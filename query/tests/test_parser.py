from query.parser import build_filter

def test_build_filter_basic():
    ast = build_filter("accuracy > 0.9")
    assert ast["operator"] == ">"
    assert ast["value"] == 0.9
