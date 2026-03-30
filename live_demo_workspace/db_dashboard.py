import os
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote_plus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError


def _build_database_url_from_credentials() -> str:
  credentials_path = os.getenv("DATAHUB_CREDENTIALS_FILE")
  if credentials_path:
    path = Path(credentials_path)
  else:
    path = Path(__file__).resolve().parents[1] / "credentials.json"

  if not path.exists():
    raise RuntimeError(f"credentials.json not found at {path}")

  payload = json.loads(path.read_text(encoding="utf-8"))
  database = payload.get("database", {})

  user = database.get("user")
  password = database.get("password")
  name = database.get("name")
  port = database.get("port", 5432)

  if not user or not password or not name:
    raise RuntimeError("credentials.json must include database.user, database.password, and database.name")

  host = os.getenv("DATAHUB_DB_HOST", database.get("host", "localhost"))

  safe_user = quote_plus(str(user))
  safe_password = quote_plus(str(password))

  return f"postgresql://{safe_user}:{safe_password}@{host}:{port}/{name}"


DATABASE_URL = os.getenv("DATABASE_URL") or _build_database_url_from_credentials()
engine = create_engine(DATABASE_URL, future=True)

app = FastAPI(title="DataHub DB Dashboard")


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def load_tables_snapshot() -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    inspector = inspect(engine)
    table_names = inspector.get_table_names(schema="public")
    snapshot: Dict[str, Dict[str, List[Dict[str, str]]]] = {}

    with engine.connect() as conn:
        for table_name in table_names:
            columns = [column["name"] for column in inspector.get_columns(table_name, schema="public")]
            safe_table_name = table_name.replace('"', '""')
            rows = conn.execute(text(f'SELECT * FROM "{safe_table_name}"')).mappings().all()

            normalized_rows: List[Dict[str, str]] = []
            for row in rows:
                normalized_rows.append({column: _stringify(row.get(column)) for column in columns})

            snapshot[table_name] = {
                "columns": columns,
                "rows": normalized_rows,
            }

    return snapshot


@app.get("/api/snapshot")
def snapshot() -> JSONResponse:
    try:
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tables": load_tables_snapshot(),
        }
        return JSONResponse(payload)
    except SQLAlchemyError as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    try:
        tables = load_tables_snapshot()
    except SQLAlchemyError as exc:
        return HTMLResponse(
            f"<h1>Database Error</h1><pre>{escape(str(exc))}</pre>",
            status_code=500,
        )

    cards: List[str] = []

    for table_name, payload in tables.items():
        columns = payload["columns"]
        rows = payload["rows"]

        header_html = "".join(f"<th>{escape(column)}</th>" for column in columns)

        body_rows: List[str] = []
        for row in rows:
            cells = "".join(f"<td>{escape(row.get(column, ''))}</td>" for column in columns)
            body_rows.append(f"<tr>{cells}</tr>")

        body_html = "".join(body_rows) if body_rows else f"<tr><td colspan=\"{max(1, len(columns))}\">No rows</td></tr>"

        cards.append(
            """
            <section class=\"table-card\">
              <h2>{table}</h2>
              <p class=\"meta\">Rows: {row_count}</p>
              <div class=\"table-wrap\">
                <table>
                  <thead><tr>{header}</tr></thead>
                  <tbody>{body}</tbody>
                </table>
              </div>
            </section>
            """.format(
                table=escape(table_name),
                row_count=len(rows),
                header=header_html,
                body=body_html,
            )
        )

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <meta http-equiv=\"refresh\" content=\"5\" />
        <title>DataHub DB Dashboard</title>
        <style>
          :root {{
            --bg: #f6f8fb;
            --panel: #ffffff;
            --border: #d9e0ea;
            --ink: #1d2733;
            --muted: #5f6f82;
            --accent: #0b6eb8;
          }}
          body {{
            margin: 0;
            padding: 20px;
            font-family: Segoe UI, Tahoma, Arial, sans-serif;
            color: var(--ink);
            background: radial-gradient(circle at top right, #dfefff, var(--bg));
          }}
          h1 {{ margin: 0 0 6px 0; }}
          .sub {{ margin: 0 0 18px 0; color: var(--muted); }}
          .grid {{
            display: grid;
            gap: 16px;
          }}
          .table-card {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 14px rgba(16, 42, 67, 0.08);
          }}
          .table-card h2 {{ margin: 0 0 4px 0; font-size: 18px; }}
          .meta {{ margin: 0 0 8px 0; color: var(--muted); font-size: 13px; }}
          .table-wrap {{ overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; }}
          table {{ width: 100%; border-collapse: collapse; min-width: 600px; }}
          thead {{ background: #eff5fb; }}
          th, td {{
            text-align: left;
            padding: 8px 10px;
            border-bottom: 1px solid var(--border);
            vertical-align: top;
            font-size: 13px;
          }}
          th {{ color: var(--accent); font-weight: 700; }}
          code {{ background: #edf3fa; padding: 2px 5px; border-radius: 4px; }}
        </style>
      </head>
      <body>
        <h1>DataHub Database Dashboard</h1>
        <p class=\"sub\">Auto-refreshes every 5 seconds. Generated at {generated_at}.</p>
        <div class=\"grid\">{cards}</div>
      </body>
    </html>
    """.format(generated_at=generated_at, cards="".join(cards))

    return HTMLResponse(html)
