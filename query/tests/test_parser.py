from query.parser import build_filter
import pytest

def test_build_filter_greater():
    ast = build_filter("accuracy > 0.9")
    assert ast["metric"] == "accuracy"
    assert ast["operator"] == ">"
    assert ast["value"] == 0.9

def test_build_filter_less():
    ast = build_filter("loss < 0.2")
    assert ast["metric"] == "loss"
    assert ast["operator"] == "<"
    assert ast["value"] == 0.2

def test_build_filter_equal():
    ast = build_filter("accuracy == 0.95")
    assert ast["metric"] == "accuracy"
    assert ast["operator"] == "=="
    assert ast["value"] == 0.95

def test_invalid_query():
    with pytest.raises(ValueError):
        build_filter("accuracy 0.9")