# Expense Splitter Toolkit

A modern, usable expense-splitting toolkit. Add people, log expenses with equal or exact splits, view balances, and get simplified settlement transactions — all through a clean web interface backed by a FastAPI API.

The app is **Vercel-ready** (zero-config FastAPI detection + static frontend served from `public/`) and supports **Supabase** for persistent storage.

---

## Project Structure

```
expense-toolkit/
├── app/                      # FastAPI backend
│   ├── __init__.py
│   ├── main.py               # FastAPI `app` instance (Vercel entrypoint)
│   ├── routes.py             # REST API routes
│   ├── store.py              # Persistence: Supabase (or in-memory fallback)
│   ├── models.py             # User, Expense (core logic unchanged)
│   ├── manager.py            # ExpenseManager (core logic unchanged)
│   ├── balances.py           # compute_balances (core logic unchanged)
│   └── simplify_debts.py     # simplify_debts (core logic unchanged)
├── public/                   # Static frontend (served by Vercel CDN)
│   ├── index.html
│   ├── style.css
│   └── script.js
├── supabase/
│   └── schema.sql            # Tables + indexes + RLS setup
├── legacy/                   # Original code (preserved unchanged)
│   ├── backend/
│   └── frontend/
├── requirements.txt          # Python dependencies
├── .env.example              # Local env template
├── vercel.json               # Vercel function configuration
├── .python-version           # Pins Python 3.12 for Vercel
├── run.py                    # Local dev server entry
├── README.md
└── .gitignore
```

## Core Logic (unchanged)

These modules preserve the original core logic exactly:

- `app/models.py` — `User` and `Expense` classes
- `app/manager.py` — `ExpenseManager` (add_user, add_expense, list_expenses with the same validation)
- `app/balances.py` — `compute_balances` (payer paid +amount; each split subtracted)
- `app/simplify_debts.py` — `simplify_debts` (greedy debtor→creditor settlement)

Only the **storage layer** (`app/store.py`) is new. It hydrates the same domain objects
from Supabase and validates writes through the unchanged `ExpenseManager`.

---

## Storage: Supabase (recommended) or in-memory

`app/store.py` chooses the backend at startup:

- If `SUPABASE_URL` and `SUPABASE_KEY` are set → **Supabase** persistence.
- Otherwise → the original **in-memory** behavior (great for local dev, data resets on restart).

### 1. Create the database tables

In your Supabase project, open **SQL Editor → New query**, paste the contents of
[`supabase/schema.sql`](supabase/schema.sql), and run it.

This creates three tables (`users`, `expenses`, `expense_splits`), indexes, and RLS.

### 2. Configure credentials

Backend environment variables:

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your project URL, e.g. `https://abcdefghijkl.supabase.co` |
| `SUPABASE_KEY` | **Service role key** (recommended, server-side only). The anon key also works if you enable the demo RLS policies in the schema. |

For local development, copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

> ⚠️ Keep the **service role** key server-side only. Never expose it in the browser.

### Local development

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py                     # API at http://127.0.0.1:8000
```

Then open `public/index.html`, or serve the frontend:

```bash
cd public
python -m http.server 5500
```

The frontend automatically calls `http://127.0.0.1:8000` when opened locally.

### Vercel CLI (closest to production)

```bash
npm i -g vercel
vercel dev
```

`vercel dev` runs both the static frontend and the FastAPI function together.

---

## Deploy to Vercel

1. Push this repository to GitHub.
2. Go to [vercel.com/new](https://vercel.com/new) and import the repository.
3. Vercel auto-detects FastAPI (`app/main.py`) and the `public/` static directory.
4. In **Project Settings → Environment Variables**, add:
   - `SUPABASE_URL`
   - `SUPABASE_KEY` (service role key)
5. Click **Deploy**.

No build settings are required — `vercel.json` configures the function.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users` | Add a person |
| GET | `/users` | List all people |
| DELETE | `/users/{id}` | Remove a person (if no expenses) |
| POST | `/expenses` | Add an expense |
| GET | `/expenses` | List all expenses |
| DELETE | `/expenses/{id}` | Remove an expense |
| GET | `/balances` | Compute net balances |
| GET | `/settlements` | Compute simplified settlements |

Interactive API docs are available at `/docs` when the server is running.

---

## Notes

- Without Supabase credentials the app falls back to in-memory storage (the original behavior). On Vercel that fallback is ephemeral, so set the Supabase variables for a real deployment.
- The original code is preserved unchanged in `legacy/` for reference.
- For any change to the core splitting/settlement logic, please consult first.
