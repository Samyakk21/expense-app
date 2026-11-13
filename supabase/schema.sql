-- Expense Splitter Toolkit — Supabase schema
-- Run this in the Supabase SQL editor (Dashboard → SQL → New query).

-- ---------------------------------------------------------------------------
-- Tables
-- ---------------------------------------------------------------------------
create table if not exists public.users (
  id          bigint primary key,
  name        text not null,
  created_at  timestamptz not null default now()
);

create table if not exists public.expenses (
  id          bigint generated always as identity primary key,
  payer_id    bigint not null references public.users(id) on delete restrict,
  amount      double precision not null check (amount >= 0),
  created_at  timestamptz not null default now()
);

create table if not exists public.expense_splits (
  expense_id  bigint not null references public.expenses(id) on delete cascade,
  user_id     bigint not null references public.users(id) on delete restrict,
  amount      double precision not null,
  primary key (expense_id, user_id)
);

create index if not exists idx_expenses_payer on public.expenses(payer_id);
create index if not exists idx_splits_user      on public.expense_splits(user_id);

-- ---------------------------------------------------------------------------
-- Row Level Security
-- ---------------------------------------------------------------------------
-- Enable RLS on all tables.
alter table public.users          enable row level security;
alter table public.expenses       enable row level security;
alter table public.expense_splits enable row level security;

-- RECOMMENDED (secure): keep RLS enabled and use the SERVICE ROLE key on the
-- backend. The service role bypasses RLS, so no policies are needed below.
--
-- OPTION B (demo only): if you must use the public anon key, uncomment the
-- permissive policies below. WARNING: this allows anyone with the anon key to
-- read and write all rows. Do not use in production.
--
-- create policy "demo_all_users"   on public.users          for all using (true) with check (true);
-- create policy "demo_all_expenses" on public.expenses       for all using (true) with check (true);
-- create policy "demo_all_splits"  on public.expense_splits for all using (true) with check (true);
