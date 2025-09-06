-- profiles with starting credits
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  display_name text,
  credits integer not null default 20,
  created_at timestamptz default now()
);
alter table public.profiles enable row level security;
create policy "own profile rw" on public.profiles
  for select using (auth.uid() = id)
  with check (auth.uid() = id);

-- credit ledger (append-only)
create table if not exists public.credit_ledger (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  delta integer not null,
  reason text not null,
  meta jsonb,
  created_at timestamptz default now()
);
alter table public.credit_ledger enable row level security;
create policy "read own ledger" on public.credit_ledger for select using (auth.uid() = user_id);
-- inserts via RPC or service key only (no public insert policy)

-- create profile on signup
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.profiles(id, email, display_name) values (new.id, new.email, coalesce(new.raw_user_meta_data->>'full_name',''));
  return new;
end; $$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
for each row execute procedure public.handle_new_user();

-- spend credits atomically
create or replace function public.spend_credits(amount int, reason text, meta jsonb default '{}'::jsonb)
returns integer language plpgsql security definer as $$
declare new_balance int;
begin
  if amount <= 0 then raise exception 'amount must be > 0'; end if;
  update public.profiles set credits = credits - amount
   where id = auth.uid() and credits >= amount
   returning credits into new_balance;
  if not found then raise exception 'insufficient_credits'; end if;
  insert into public.credit_ledger(user_id, delta, reason, meta) values (auth.uid(), -amount, reason, meta);
  return new_balance;
end; $$;

-- admin grant (service role only)
create or replace function public.admin_grant_credits(target uuid, amount int, reason text, meta jsonb default '{}'::jsonb)
returns integer language plpgsql security definer as $$
declare new_balance int;
begin
  if current_setting('request.jwt.claims', true)::jsonb->>'role' <> 'service_role' then
    raise exception 'forbidden';
  end if;
  update public.profiles set credits = credits + amount where id = target returning credits into new_balance;
  insert into public.credit_ledger(user_id, delta, reason, meta) values (target, amount, reason, meta);
  return new_balance;
end; $$;