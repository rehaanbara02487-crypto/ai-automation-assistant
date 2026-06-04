alter table public.users
  add column if not exists last_login_at timestamptz;

create index if not exists users_email_idx on public.users(email);
