create extension if not exists "uuid-ossp";

create table if not exists public.plans (
  id text primary key,
  name text not null,
  monthly_price_inr integer not null default 0,
  automation_limit integer not null,
  run_limit integer not null,
  created_at timestamptz not null default now()
);

insert into public.plans (id, name, monthly_price_inr, automation_limit, run_limit)
values
  ('free', 'Free', 0, 2, 50),
  ('pro', 'Pro', 99900, 20, 2000),
  ('team', 'Team', 0, 100, 10000)
on conflict (id) do nothing;

create table if not exists public.subscriptions (
  id uuid primary key default uuid_generate_v4(),
  user_id text not null,
  plan_id text not null references public.plans(id),
  stripe_customer_id text,
  stripe_subscription_id text,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.integrations (
  id uuid primary key default uuid_generate_v4(),
  user_id text not null,
  app text not null,
  status text not null default 'available',
  encrypted_secret_ref text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, app)
);

create table if not exists public.automations (
  id uuid primary key,
  user_id text not null,
  title text not null,
  status text not null check (status in ('active', 'draft', 'failed', 'paused')),
  trigger text not null,
  actions jsonb not null default '[]'::jsonb,
  summary text not null,
  steps jsonb not null default '[]'::jsonb,
  workflow_id text not null,
  error_count integer not null default 0,
  run_count integer not null default 0,
  last_run_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.workflow_logs (
  id uuid primary key default uuid_generate_v4(),
  automation_id uuid not null references public.automations(id) on delete cascade,
  status text not null,
  message text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table public.plans enable row level security;
alter table public.subscriptions enable row level security;
alter table public.integrations enable row level security;
alter table public.automations enable row level security;
alter table public.workflow_logs enable row level security;

create policy "Plans are readable" on public.plans
  for select using (true);

create policy "Users can read own subscriptions" on public.subscriptions
  for select using (auth.jwt() ->> 'sub' = user_id);

create policy "Users can manage own integrations" on public.integrations
  for all using (auth.jwt() ->> 'sub' = user_id);

create policy "Users can manage own automations" on public.automations
  for all using (auth.jwt() ->> 'sub' = user_id);

create policy "Users can read logs for own automations" on public.workflow_logs
  for select using (
    exists (
      select 1 from public.automations
      where automations.id = workflow_logs.automation_id
      and automations.user_id = auth.jwt() ->> 'sub'
    )
  );

create index if not exists automations_user_id_idx on public.automations(user_id);
create index if not exists workflow_logs_automation_id_idx on public.workflow_logs(automation_id);

