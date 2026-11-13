# Expense Splitter Toolkit

A modern, usable expense-splitting toolkit. Add people, log expenses with equal or exact splits, view balances, and get simplified settlement transactions — all through a clean web interface backed by a FastAPI API.

The app is **Vercel-ready** (zero-config FastAPI detection + static frontend served from `public/`).

---

## Project Structure

```
expense-toolkit/
├── app/                      # FastAPI backend (core logic)
│   ├── __init__.py
│   ├── main.py               # FastAPI `app` instance (Vercel entrypoint)
│   ├── routes.py             # REST API routes
│   ├── models.py             # User, Expense (core logic unchanged)
│   ├── manager.py            # ExpenseManager (core logic unchanged)
│   ├── balances.py           # compute_balances (core logic unchanged)
│   └── simplify_debts.py     # simplify_debts (core logic unchanged)
├── public/                   # Static frontend (served by Vercel CDN)
│   ├── index.html
│   ├── style.css
│   └── script.js
├── legacy/                   # Original code (preserved unchanged)
│   ├── backend/
│   └── frontend/
├── requirements.txt          # Python dependencies
├── vercel.json               # Vercel function configuration
├── .python-version           # Pins Python 3.12 for Vercel
├── run.py                    # Local dev server entry
├── README.md
└── .gitignore
```

## Core Logic (unchanged)

The following modules preserve the original core logic exactly:

- `app/models.py` — `User` and `Expense` classes
- `app/manager.py` — `ExpenseManager` (add_user, add_expense, list_expenses with the same validation)
- `app/balances.py` — `compute_balances` (payer paid +amount; each split subtracted)
- `app/simplify_debts.py` — `simplify_debts` (greedy debtor→creditor settlement)

---

## Local Development

### Option A — run the backend and open the frontend manually

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py                     # API at http://127.0.0.1:8000
```

Then open `public/index.html` in your browser. The frontend automatically points to
`http://127.0.0.1:8000` when opened locally.

### Option B — serve the frontend with a static server

```bash
cd public
python -m http.server 5500
```

Visit `http://localhost:5500`. The frontend will call the local API at
`http://127.0.0.1:8000` automatically.

### Option C — Vercel CLI (closest to production)

```bash
npm i -g vercel
vercel dev
```

`vercel dev` runs both the static frontend and the FastAPI function together.

---

## Deploy to Vercel

### Option 1 — Git integration (recommended)

1. Push this repository to GitHub.
2. Go to [vercel.com/new](https://vercel.com/new) and import the repository.
3. Vercel auto-detects FastAPI (`app/main.py`) and the `public/` static directory.
4. Click **Deploy**.

No build settings are required — `vercel.json` configures the function.

### Option 2 — Vercel CLI

```bash
npm i -g vercel
vercel
vercel --prod
```

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

## ⚠️ Important: In-Memory State on Vercel

The backend stores users and expenses **in memory** (the same design as the original
`legacy/backend/api.py`). This works perfectly on a single long-running server, but
**Vercel Functions are stateless and ephemeral**:

- Different requests may hit different function instances.
- Cold starts reset all data.
- There is no shared storage between invocations.

> **On Vercel, data will not reliably persist between requests.** The UI and API will
> work, but added people/expenses may disappear on the next request or cold start.

To make a production deployment with persistent data, the storage layer must be
swapped for a database (e.g. Vercel Postgres, Vercel KV/Redis, Neon, Supabase) or
another shared store. **This is a core architecture change**, so confirm before
implementing. The splitting/balance/settlement logic itself would stay identical —
only the storage layer changes.

---

## Notes

- The original code is preserved unchanged in `legacy/` for reference.
- For any change to the core splitting/settlement logic, please consult first.
