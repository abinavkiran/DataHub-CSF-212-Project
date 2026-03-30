# Live Manual Demo Guide

This workspace is designed for a live terminal demo where you run each step manually and prove results through CLI output and direct database queries.

## 0. Start From a Clean Slate (Optional but Recommended)

If you want demo-only rows in `log` and `query`, reset Docker volumes first:

```powershell
docker compose down -v
```

## 1. Prepare Infrastructure (Terminal A)

Run these commands from repository root:

```powershell
docker compose up -d --build
docker compose exec dev-env uvicorn api.server:app --host 0.0.0.0 --port 8000
```

Keep Terminal A running because it hosts the API.

If port 8000 is already in use, run API on another port such as 8010 and pass that URL explicitly in `push/log/query`.

If you want Terminal B to always use a non-default API URL, set this before running commands:

```bat
set DATAHUB_REMOTE_URL=http://localhost:8010
```

## 2. Open Demo Terminal (Terminal B)

Use one of these options:

### Option A: PowerShell

```powershell
cd live_demo_workspace
. .\load-demo-alias.ps1
```

### Option B: Command Prompt (cmd)

```bat
cd live_demo_workspace
```

In cmd, use `datahub` directly. This folder includes `datahub.cmd`.
Use double quotes in cmd for values with spaces, for example: `datahub push -m "initial demo"`.

## 3. Manual Demo Flow (Terminal B)

### Step 1: Initialize local DataHub metadata

```powershell
datahub init
```

### Step 2: Push first snapshot

```powershell
datahub push -m "Initial demo snapshot"
```

### Step 3: Show commit history

```powershell
datahub log
```

### Step 4: Show metadata query result

```powershell
datahub query "row_count == 8"
```

### Step 5: Make a visible change to the CSV

PowerShell:

```powershell
Add-Content .\experiments.csv "exp009,v2.1,CatBoost,0.92,0.08"
```

cmd:

```bat
echo exp009,v2.1,CatBoost,0.92,0.08>>experiments.csv
```

### Step 6: Push second snapshot

```powershell
datahub push -m "Added exp009 after tuning"
```

### Step 7: Show updated history and query again

```powershell
datahub log
datahub query "row_count == 9"
```

## 4. Prove Data Is In PostgreSQL (Terminal C Optional)

From repository root:

PowerShell:

```powershell
docker compose exec db psql -P pager=off -U user -d datahub -c 'SELECT commit_hash, author, message, created_at FROM commit ORDER BY created_at DESC LIMIT 10;'
docker compose exec db psql -P pager=off -U user -d datahub -c 'SELECT id, target_hash, stats->>''row_count'' AS row_count, stats->>''format'' AS format FROM metadata ORDER BY id DESC LIMIT 10;'
docker compose exec db psql -P pager=off -U user -d datahub -c 'SELECT id, tree_hash, name, object_hash, object_type FROM tree_entry ORDER BY id DESC LIMIT 20;'
```

cmd:

```bat
docker compose exec db psql -P pager=off -U user -d datahub -c "SELECT commit_hash, author, message, created_at FROM commit ORDER BY created_at DESC LIMIT 10;"
docker compose exec db psql -P pager=off -U user -d datahub -c "SELECT id, target_hash, stats->>'row_count' AS row_count, stats->>'format' AS format FROM metadata ORDER BY id DESC LIMIT 10;"
docker compose exec db psql -P pager=off -U user -d datahub -c "SELECT id, tree_hash, name, object_hash, object_type FROM tree_entry ORDER BY id DESC LIMIT 20;"
```

## 5. Reset Demo Data (Optional)

If you want a fresh rerun in this folder:

PowerShell:

```powershell
Remove-Item -Recurse -Force .\.datahub
docker compose down -v
```

cmd:

```bat
if exist .datahub rmdir /s /q .datahub
docker compose down -v
```
