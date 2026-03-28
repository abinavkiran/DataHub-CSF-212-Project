# DataHub Standardized Development

## Core Philosophy:
**Do NOT install Python natively** or set up local SQLite database stubs.
This repository runs **100% via Docker** using `docker-compose`. This ensures every team member perfectly aligns with the `python:3.11-slim` architecture paired alongside production-parity `postgres:15-alpine`.

## Quick Start
1. Ensure **Docker Desktop** is open and running on your machine.
2. Build and boot the cluster: 
   ```bash
   docker-compose up -d --build
   ```
3. Your local codebase directory is now `Volume Mounted` perfectly inside the isolated `dev-env` network container.

### Running Individual Module Tests
Because dependencies are synchronized globally inside Docker, executing individual tests requires routing the command strictly through `dev-env`:

- **Module 1 (Architecture):**
  ```bash
  docker-compose run --rm dev-env pytest infrastructure/tests/test_db.py
  ```
- **Run the entire suite:**
  ```bash
  docker-compose run --rm dev-env pytest
  ```

### Adding Requirements
If you need a new pip package, append it centrally to `requirements.txt` and cleanly trigger a rapid cluster rebuild via:
```bash
docker-compose up -d --build
```
