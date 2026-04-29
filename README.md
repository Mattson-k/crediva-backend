# Crediva Backend

FastAPI backend for Crediva's license search, CSV export, renewal monitoring, and CRM webhook payloads.

## What is included

- Canonical `professional_licenses` table with renewal-window fields.
- Indexed search over state, profession, license type, status, location, and renewal window.
- CSV export matching the MVP spec.
- Saved renewal monitors.
- Webhook payload preview for CRM task creation.
- Sample ingestion source and normalizer.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

Then open:

- Frontend: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## Seed sample data

With the virtualenv active:

```bash
python -m app.ingest.run_sample
```

The seed command loads a small cross-state demo queue for physicians, nurses, contractors,
real estate salespeople, and electrical contractors so the frontend has usable rows immediately.

Example search:

```bash
curl "http://127.0.0.1:8000/licenses?source_state=TX&license_type_code=MD&renewal_window_min=0&renewal_window_max=60"
```

Example CSV:

```bash
curl "http://127.0.0.1:8000/licenses/export.csv?source_state=TX&license_type_code=MD&renewal_window_min=0&renewal_window_max=60"
```

## Production notes

Use Postgres in production:

```env
DATABASE_URL=postgresql+psycopg://user:password@host:5432/crediva
```

Local Postgres:

```bash
docker compose up -d postgres
DATABASE_URL=postgresql+psycopg://crediva:crediva@localhost:5432/crediva alembic upgrade head
DATABASE_URL=postgresql+psycopg://crediva:crediva@localhost:5432/crediva uvicorn app.main:app --reload
```

Next backend milestones:

1. Add auth and account-level usage metering.
2. Add source adapters for TX Medical Board, FL DBPR, CA DCA, and CA DRE.
3. Add CRM push workers for Salesforce and HubSpot.
4. Add monitor scheduler that emits renewal webhooks daily.
