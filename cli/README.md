# Module 3: Client-Side CLI
**Owner:** Kedar Medishetty

## Core Responsibility
The CLI simulates Git's interactions for Data Scientists processing gigabyte datasets. You are tasked with generating cross-platform terminal bindings via Click parsing.

## Contracted Interface (`cli/main.py`)

The Command Line is inherently isolated. It executes client-side where artists and engineers have their datasets locally. You run this entrypoint natively:

```python
import click

@click.group()
def cli(): pass

@cli.command()
def init(): pass # Initialize `.datahub/` locally

@cli.command()
def push(remote_url: str): pass # Traverse local workspace, dispatch bytes matching new hashes 
```

## Strict Constraints
1. **Network Segregation:** As a CLI running on an end-user's laptop, **you are strictly forbidden from connecting directly to the PostgreSQL instance or `infrastructure/db.py`**.
2. **Communication:** You must communicate explicitly across HTTP REST executing `POST` calls aimed purely into Module 4 (`api/server.py`).
3. **Optimized Scanning:** When pushing, the CLI must locally compute SHA-256 for files and query the API `GET /check_hash/{hash}` *before* uploading payload boundaries, dropping unneeded traffic geometrically.

## Execution
Run your CLI integration mock tests via Docker explicitly injecting spoofed API requests:
```bash
docker-compose run --rm dev-env pytest cli/tests/test_main.py -v
```
