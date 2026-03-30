# Module 1: DAG Architecture & Schema Design
**Owner:** Abinav Kiran

## Responsibilities
- Implementing SQLAlchemy models mapping identically to `Commit`, `Tree`, `TreeEntry`, `Blob`, `Branch`, and `Metadata` constraints.
- Processing mathematically sound recursive lineage sequences (CTEs).

## Universal Execution Environment (Docker)

To prevent localized errors (like missing Python binaries or OS-specific dependencies), **ALL developer execution must happen inside the synchronized Docker cluster automatically managing dependencies and PostgreSQL interactions.**

### 1. Build & Start the Environment
From the root of the repository, execute the following to instantiate the shared database (`db`) alongside the synchronized execution environment map (`dev-env`). 

First, create a root-level `credentials.json` file (local only) with this structure:
```json
{
	"database": {
		"user": "user",
		"password": "password",
		"name": "datahub",
		"host": "db",
		"port": 5432
	}
}
```

Then sync Docker environment values from the root `credentials.json` file:
```bash
./sync_credentials_env.ps1
# or in cmd
sync_credentials_env.cmd
```

Then start the environment:
```bash
docker-compose up -d --build
```
*(You must have Docker Desktop actively running).*

### 2. Perfectly Execute Module 1 Tests
All dependencies (SQLAlchemy, pytest) are automatically baked into the `dev-env` container. You can execute the Module 1 tests universally from your terminal using:
```bash
docker-compose run --rm dev-env pytest infrastructure/tests/test_db.py -v
```

This guarantees identical database environments perfectly routing the CTE mathematical checks, ensuring anyone on the team can replicate the unrolling logic flawlessly.
