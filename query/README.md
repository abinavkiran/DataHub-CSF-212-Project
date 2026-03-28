# Module 6: Query Language 
**Owner:** Pashuvula Niranand Reddy

## Core Responsibility
To enable researchers to leverage Saurabh's Metadata (Module 5), you enforce custom domain-specific queries parsing string filters natively into Pythonic boundaries tracking the DAG natively.

## Contracted Interface (`query/parser.py`)

Your code sits atop the API responding to the `cli log --metric "row_count > 500"` commands. 

```python
from sqlalchemy.orm import Session
from sqlalchemy import select
from infrastructure.db import Metadata # Connecting explicitly into Abinav's DB!

def build_filter(query_string: str) -> dict:
    """
    Translates 'accuracy > 0.9' securely into an Abstract Syntax Dictionary representing the condition precisely.
    """
    pass

def execute_query(session: Session, ast: dict) -> list:
    """
    Takes an abstract AST and utilizes SQLAlchemy Core boundaries traversing Metadata tables
    and joining mapped Blob targets fitting the mathematical limits.
    """
    pass
```

## Strict Constraints
1. **No String Injecting:** Standard ML Engineers might pass nested malicious drop tables maliciously or accidentally mimicking strings: `accuracy > 0.9; DROP TABLE commit`. You must exclusively rely on SQLAlchemy core functions (`column("speed") > 0.9`) rejecting string interpolations strictly. 

## Execution
Utilize edge-case strings testing SQL defense mechanisms purely through Docker natively:
```bash
docker-compose run --rm dev-env pytest query/tests/test_parser.py -v
```
