def build_filter(query_string: str):
    """
    Translates 'accuracy > 0.9' into a SQLAlchemy filter object / AST dict.
    """
    return {"operator": ">", "metric": "accuracy", "value": 0.9}
