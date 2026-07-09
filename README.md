# Remote Jobs Fetching Automation

Automated daily collection of remote tech job postings from the **RemoteOK** and **Remotive** public APIs, orchestrated with **Apache Airflow**. This is the ingestion layer of a larger Business Intelligence project analyzing the remote tech job market (in-demand skills, salary trends, hiring companies, and remote-work scope over time).

## What this repo does

1. Calls the RemoteOK and Remotive APIs to pull all currently active remote job postings.
2. Saves each source's response as a raw, untouched CSV snapshot (`remoteok_jobs_raw.csv`, `remotive_jobs_raw.csv`).
3. Runs on a daily schedule via an Airflow DAG, so each run adds one more day of real historical data.

Because both APIs only expose **currently live** postings (there is no historical date-range endpoint), this pipeline is designed to be run once per day and accumulate its own history over time rather than backfill the past.

## Repository structure

├── remote jobs fetching.ipynb   # Core fetch logic: calls both APIs and writes the raw CSVs

├── remoteok_jobs_raw.csv        # Latest raw snapshot from RemoteOK

├── remotive_jobs_raw.csv        # Latest raw snapshot from Remotive

└── airflow/                     # Airflow DAG that schedules and triggers the notebook daily

## Data sources

| Source | Endpoint | Notes |
|---|---|---|
| RemoteOK | `https://remoteok.com/api` | No API key required. First element of the response array is a legal/metadata notice, not a job, and should be skipped. |
| Remotive | `https://remotive.com/api/remote-jobs` | No API key required for this basic usage. Remotive requests no more than ~4 requests/day, which is why this pipeline runs on a daily schedule rather than continuously. |

Both APIs require crediting the source and linking back to the original job URL if the data is ever displayed publicly.

## Orchestration (Airflow)

The `airflow/` folder contains the DAG that runs `remote jobs fetching.ipynb` on a schedule.

- **DAG id:** `remote_jobs_fetching_notebook`
- **Schedule:** `0 10 * * *` (daily at 10:00)
- **Trigger type:** Single Run (Backfill is not applicable here, since both APIs only return live data — there is nothing to "catch up" on for past dates, and future dates can't be triggered ahead of time)

> Note: the exact DAG implementation (e.g., whether it runs the notebook via `papermill`, `nbconvert`, or a `PythonOperator` wrapper) lives inside `airflow/` — see that folder directly for the operator/task definitions.

## Getting started

### Prerequisites
- Python 3.9+
- Jupyter (to run/inspect the notebook directly), or Docker + Apache Airflow (to run it on schedule)

### Run the fetch manually
```bash
pip install requests pandas jupyter
jupyter nbconvert --to notebook --execute "remote jobs fetching.ipynb"
```
This regenerates `remoteok_jobs_raw.csv` and `remotive_jobs_raw.csv` with the latest postings.

### Run it on a schedule with Airflow
1. Place the contents of `airflow/` in your Airflow `dags/` folder (or mount it if using Docker).
2. Start Airflow (`docker compose up` if using the standard Airflow Docker setup).
3. In the Airflow UI, locate the `remote_jobs_fetching_notebook` DAG and toggle it **on**.
4. It will run automatically every day at 10:00 based on the `0 10 * * *` schedule — no manual triggering needed going forward.

## Data collected per job

| Field | Description |
|---|---|
| Company | Hiring company name |
| Title / Position | Job title |
| Tags / Category | Skills or job category (RemoteOK provides a tag array; Remotive provides a single category) |
| Location | Free-text remote-scope/location field (e.g., "Worldwide", a region, or a country) |
| Salary | Numeric min/max on RemoteOK (often unpopulated); free-text range on Remotive |
| Posted date | Original posting date |
| URL | Link back to the original job listing |

**Known data quality notes**, carried forward into downstream cleaning:
- Salary fields have low coverage on both sources — treat any salary KPI as a subset, not the full market.
- RemoteOK's tags mix real skills with non-skill labels (e.g., "full time", "exec").
- Location strings are unstructured free text on both sources and need normalization before regional analysis.
- Neither source shares a common job ID, so cross-source deduplication should key on company + title + posted-date proximity.

## License

No license file is currently included in this repository.
