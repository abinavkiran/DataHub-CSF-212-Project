def build_filter(query_string: str) -> dict:
    """
    Converts 'accuracy > 0.9' into a dictionary AST.
    """

    parts = query_string.strip().split()

    if len(parts) != 3:
        raise ValueError("Invalid query format. Use: metric operator value")

    metric = parts[0]
    operator = parts[1]
    value = float(parts[2])

    ast = {
        "metric": metric,
        "operator": operator,
        "value": value
    }

    return ast

from sqlalchemy.orm import Session
from sqlalchemy import select
from infrastructure.db import Metadata


def execute_query(session: Session, ast: dict) -> list:
    metric = ast["metric"]
    operator = ast["operator"]
    value = ast["value"]

    # Access JSON field
    column = Metadata.stats[metric].as_float()

    query = select(Metadata)

    if operator == ">":
        query = query.where(column > value)
    elif operator == "<":
        query = query.where(column < value)
    elif operator == ">=":
        query = query.where(column >= value)
    elif operator == "<=":
        query = query.where(column <= value)
    elif operator == "==":
        query = query.where(column == value)
    else:
        raise ValueError("Invalid operator")

    result = session.execute(query)
    return result.fetchall()