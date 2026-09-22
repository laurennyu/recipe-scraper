-- Recipe Scraper database schema
-- Run this once in Supabase: SQL Editor -> New query -> Run.

create table if not exists public.accounts (
  id uuid primary key default gen_random_uuid(),
  username text not null,
  username_key text not null unique,
  created_at timestamptz not null default now(),
  constraint accounts_username_key_lowercase check (username_key = lower(username_key))
);

create table if not exists public.recipes (
  id uuid primary key default gen_random_uuid(),
  account_id uuid not null references public.accounts(id) on delete cascade,
  title text not null,
  recipe jsonb not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint recipes_account_title_unique unique (account_id, title)
);

create index if not exists recipes_account_id_title_idx
  on public.recipes (account_id, title);

-- The API will use Supabase's server-side service-role key. Keep row-level
-- security enabled and do not create public policies: browsers must never be
-- able to query this database directly.
alter table public.accounts enable row level security;
alter table public.recipes enable row level security;

-- Allow the backend service-role key to manage recipe data without custom RLS policies.
grant usage on schema public to service_role;
grant all on table public.accounts to service_role;
grant all on table public.recipes to service_role;
