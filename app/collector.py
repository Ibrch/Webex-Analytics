import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

import duckdb
import requests
from dotenv import load_dotenv


# --------------------------------------------------
# Konfiguration
# --------------------------------------------------

BASE_DIR = Path("/opt/webex-analytics")
RAW_DIR = BASE_DIR / "data" / "raw"
PARQUET_DIR = BASE_DIR / "data" / "parquet"
DB_FILE = BASE_DIR / "state" / "webex.duckdb"

load_dotenv(BASE_DIR / ".env")

TOKEN = os.getenv("WEBEX_TOKEN")

if not TOKEN:
    raise RuntimeError("WEBEX_TOKEN wurde nicht gefunden.")

URL = "https://analytics-calling-eu.webexapis.com/v1/cdr_stream"


# --------------------------------------------------
# Zeitfenster
# --------------------------------------------------

now = datetime.now(timezone.utc)

END_DT = now - timedelta(minutes=2)
START_DT = END_DT - timedelta(minutes=30)

START_TIME = START_DT.strftime("%Y-%m-%dT%H:%M:%S.000Z")
END_TIME = END_DT.strftime("%Y-%m-%dT%H:%M:%S.000Z")


# --------------------------------------------------
# API Request
# --------------------------------------------------

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
}

params = {
    "startTime": START_TIME,
    "endTime": END_TIME,
}

print("Starte Webex API Abruf...")
print(f"Zeitraum: {START_TIME} bis {END_TIME}")

response = requests.get(
    URL,
    headers=headers,
    params=params,
    timeout=60,
)

print(f"HTTP Status: {response.status_code}")

response.raise_for_status()

data = response.json()

items = data.get("items", [])

print(f"CDRs von Webex: {len(items)}")


# --------------------------------------------------
# Raw JSON speichern
# --------------------------------------------------

RAW_DIR.mkdir(parents=True, exist_ok=True)

retrieved_at = datetime.now(timezone.utc).strftime(
    "%Y-%m-%dT%H-%M-%S.%fZ"
)

filename = (
    f"cdr_{START_TIME.replace(':', '').replace('.', '')}"
    f"_{END_TIME.replace(':', '').replace('.', '')}"
    f"_{retrieved_at}.json"
)

output_file = RAW_DIR / filename

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Raw JSON gespeichert: {output_file}")


# --------------------------------------------------
# DuckDB
# --------------------------------------------------

con = duckdb.connect(str(DB_FILE))

loaded_at = datetime.now(timezone.utc).replace(tzinfo=None)

inserted = 0
duplicates = 0


for cdr in items:

    report_id = cdr.get("Report ID")

    if not report_id:
        print("WARNUNG: CDR ohne Report ID übersprungen.")
        continue

    try:

        con.execute(
            """
            INSERT INTO cdr_raw (
                report_id,
                answer_time,
                answered,
                direction,
                call_id,
                start_time,
                call_type,
                client_type,
                correlation_id,
                duration,
                org_uuid,
                user_uuid,
                user_type,
                user_name,
                called_number,
                calling_number,
                location,
                dialed_digits,
                releasing_party,
                redirecting_number,
                site_uuid,
                user_number,
                call_outcome,
                call_outcome_reason,
                ring_duration,
                answer_indicator,
                release_time,
                pstn_vendor_name,
                external_customer_id,
                redirecting_party_uuid,
                original_called_party_uuid,
                queue_type,
                answered_elsewhere,
                hold_duration,
                interaction_id,
                transfer_type,
                transfer_type_context,
                source_file,
                loaded_at
            )
            VALUES (
                TRY_CAST(? AS UUID),
                TRY_CAST(? AS TIMESTAMP),
                ?,
                ?,
                ?,
                TRY_CAST(? AS TIMESTAMP),
                ?,
                ?,
                TRY_CAST(? AS UUID),
                ?,
                TRY_CAST(? AS UUID),
                TRY_CAST(? AS UUID),
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                TRY_CAST(? AS UUID),
                ?,
                ?,
                ?,
                ?,
                ?,
                TRY_CAST(? AS TIMESTAMP),
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                TRY_CAST(? AS UUID),
                ?,
                ?,
                ?
            )
            """,
            [
                report_id,
                cdr.get("Answer time") or None,
                cdr.get("Answered"),
                cdr.get("Direction"),
                cdr.get("Call ID"),
                cdr.get("Start time"),
                cdr.get("Call type"),
                cdr.get("Client type"),
                cdr.get("Correlation ID") or None,
                cdr.get("Duration"),
                cdr.get("Org UUID") or None,
                cdr.get("User UUID") or None,
                cdr.get("User type"),
                cdr.get("User"),
                cdr.get("Called number"),
                cdr.get("Calling number"),
                cdr.get("Location"),
                cdr.get("Dialed digits"),
                cdr.get("Releasing party"),
                cdr.get("Redirecting number"),
                cdr.get("Site UUID") or None,
                cdr.get("User number"),
                cdr.get("Call outcome"),
                cdr.get("Call outcome reason"),
                cdr.get("Ring duration"),
                cdr.get("Answer indicator"),
                cdr.get("Release time"),
                cdr.get("PSTN vendor name"),
                cdr.get("External customer ID"),
                cdr.get("Redirecting party UUID"),
                cdr.get("Original called party UUID"),
                cdr.get("Queue type"),
                cdr.get("Answered elsewhere"),
                cdr.get("Hold duration"),
                cdr.get("Interaction ID") or None,
                cdr.get("Transfer type"),
                cdr.get("Transfer type context"),
                str(output_file),
                loaded_at,
            ],
        )

        inserted += 1

    except duckdb.ConstraintException:

        duplicates += 1


# --------------------------------------------------
# Parquet aktualisieren
# --------------------------------------------------

PARQUET_DIR.mkdir(parents=True, exist_ok=True)

parquet_file = PARQUET_DIR / "cdr.parquet"

con.execute(
    f"""
    COPY (
        SELECT *
        FROM cdr_raw
        ORDER BY start_time
    )
    TO '{parquet_file}'
    (FORMAT PARQUET, COMPRESSION ZSTD)
    """
)

total = con.execute(
    "SELECT COUNT(*) FROM cdr_raw"
).fetchone()[0]

con.close()


# --------------------------------------------------
# Ergebnis
# --------------------------------------------------

print("DuckDB Import abgeschlossen.")
print(f"Neu eingefügt: {inserted}")
print(f"Duplikate übersprungen: {duplicates}")
print(f"Gesamt CDRs in DuckDB: {total}")
print(f"Parquet aktualisiert: {parquet_file}")

