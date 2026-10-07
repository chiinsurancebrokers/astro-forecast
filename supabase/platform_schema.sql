-- Reviewable schema draft for the Astrology Intelligence Platform.
-- Convert this file into a managed migration with the Supabase CLI after the
-- dedicated project and migration workflow are selected. Do not apply to prod
-- as part of this branch.
begin;

create table if not exists public.profiles (
    id uuid primary key references auth.users (id) on delete cascade,
    full_name text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.subscriptions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    stripe_customer_id text,
    stripe_subscription_id text unique,
    plan text not null default 'free'
        check (plan in ('free', 'premium_monthly', 'premium_annual')),
    status text not null default 'inactive'
        check (status in ('inactive', 'incomplete', 'trialing', 'active',
                          'past_due', 'canceled', 'unpaid', 'paused')),
    current_period_end timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id)
);

create index if not exists subscriptions_stripe_customer_id_idx
    on public.subscriptions (stripe_customer_id);

create table if not exists public.charts (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    label text not null,
    person_name text,
    birth_date date not null,
    birth_time time,
    place_name text not null,
    latitude double precision not null check (latitude between -90 and 90),
    longitude double precision not null check (longitude between -180 and 180),
    timezone text not null,
    chart_type text not null default 'natal'
        check (chart_type in ('natal', 'partner', 'saved_person')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (id, user_id)
);

create index if not exists charts_user_id_created_at_idx
    on public.charts (user_id, created_at desc);

create table if not exists public.reports (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    chart_id uuid not null,
    report_type text not null,
    title text not null,
    content_json jsonb not null default '{}'::jsonb,
    pdf_path text,
    created_at timestamptz not null default now(),
    foreign key (chart_id, user_id)
        references public.charts (id, user_id) on delete cascade
);

create index if not exists reports_user_id_created_at_idx
    on public.reports (user_id, created_at desc);

create table if not exists public.compatibility_reports (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    chart_a_id uuid not null,
    chart_b_id uuid not null,
    title text not null default 'Compatibility report',
    content_json jsonb not null default '{}'::jsonb,
    pdf_path text,
    created_at timestamptz not null default now(),
    check (chart_a_id <> chart_b_id),
    foreign key (chart_a_id, user_id)
        references public.charts (id, user_id) on delete cascade,
    foreign key (chart_b_id, user_id)
        references public.charts (id, user_id) on delete cascade
);

create index if not exists compatibility_reports_user_id_created_at_idx
    on public.compatibility_reports (user_id, created_at desc);

create table if not exists public.questions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    chart_id uuid not null,
    question text not null check (length(question) between 1 and 4000),
    answer text,
    status text not null default 'pending'
        check (status in ('pending', 'completed', 'failed')),
    credits_used integer not null default 0 check (credits_used >= 0),
    created_at timestamptz not null default now(),
    completed_at timestamptz,
    foreign key (chart_id, user_id)
        references public.charts (id, user_id) on delete cascade
);

create index if not exists questions_user_id_created_at_idx
    on public.questions (user_id, created_at desc);

create table if not exists public.usage_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    event_type text not null,
    metadata_json jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists usage_events_user_id_created_at_idx
    on public.usage_events (user_id, created_at desc);

create table if not exists public.credits (
    user_id uuid primary key references auth.users (id) on delete cascade,
    balance integer not null default 0 check (balance >= 0),
    updated_at timestamptz not null default now()
);

create table if not exists public.book_sources (
    source_id text primary key,
    title text not null,
    author text not null,
    system text not null
        check (system in ('VEDIC', 'WESTERN_TRADITIONAL',
                          'HELIOCENTRIC_HISTORICAL', 'MEDICAL_ASTROLOGY',
                          'HERMETIC_HISTORICAL')),
    coverage text[] not null default '{}',
    source_sha256 text,
    updated_at timestamptz not null default now()
);

create table if not exists public.book_knowledge_rules (
    rule_id text primary key,
    source_id text not null references public.book_sources (source_id) on delete restrict,
    system text not null,
    topics text[] not null check (cardinality(topics) > 0),
    locator text not null,
    summary text not null check (length(summary) between 20 and 600),
    keywords text[] not null default '{}',
    source_sha256 text,
    reviewed_at timestamptz not null default now(),
    check (system in ('VEDIC', 'WESTERN_TRADITIONAL',
                      'HELIOCENTRIC_HISTORICAL', 'MEDICAL_ASTROLOGY',
                      'HERMETIC_HISTORICAL'))
);

create index if not exists book_knowledge_rules_system_topics_idx
    on public.book_knowledge_rules using gin (system, topics);

-- Raw source chunks are private to the backend's service role.
-- Only short, reviewed paraphrases belong in book_knowledge_rules.
create table if not exists public.book_chunks (
    chunk_id text primary key,
    source_id text not null references public.book_sources (source_id) on delete cascade,
    system text not null
        check (system in ('VEDIC', 'WESTERN_TRADITIONAL',
                          'HELIOCENTRIC_HISTORICAL', 'MEDICAL_ASTROLOGY',
                          'HERMETIC_HISTORICAL')),
    page_start integer not null check (page_start > 0),
    page_end integer not null check (page_end >= page_start),
    topics text[] not null default '{}',
    content text not null,
    source_sha256 text not null check (source_sha256 ~ '^[0-9a-f]{64}$'),
    search_vector tsvector generated always as
        (to_tsvector('simple'::regconfig, coalesce(content, ''))) stored,
    ingested_at timestamptz not null default now()
);

create index if not exists book_chunks_source_pages_idx
    on public.book_chunks (source_id, page_start, page_end);

create index if not exists book_chunks_system_topics_idx
    on public.book_chunks using gin (topics);

create index if not exists book_chunks_search_vector_idx
    on public.book_chunks using gin (search_vector);

alter table public.profiles enable row level security;
alter table public.subscriptions enable row level security;
alter table public.charts enable row level security;
alter table public.reports enable row level security;
alter table public.compatibility_reports enable row level security;
alter table public.questions enable row level security;
alter table public.usage_events enable row level security;
alter table public.credits enable row level security;
alter table public.book_sources enable row level security;
alter table public.book_knowledge_rules enable row level security;
alter table public.book_chunks enable row level security;

-- Explicit grants are required for the Supabase Data API; RLS still controls rows.
grant usage on schema public to authenticated;
revoke all on public.profiles, public.subscriptions, public.charts,
    public.reports, public.compatibility_reports, public.questions,
    public.usage_events, public.credits, public.book_sources,
    public.book_knowledge_rules, public.book_chunks
    from anon, authenticated;

grant select, insert, update, delete on public.profiles to authenticated;
grant select on public.subscriptions to authenticated;
grant select, insert, update, delete on public.charts to authenticated;
grant select, delete on public.reports to authenticated;
grant select, delete on public.compatibility_reports to authenticated;
grant select, insert on public.questions to authenticated;
grant select on public.usage_events, public.credits,
    public.book_sources, public.book_knowledge_rules to authenticated;
grant all on public.profiles, public.subscriptions, public.charts,
    public.reports, public.compatibility_reports, public.questions,
    public.usage_events, public.credits, public.book_sources,
    public.book_knowledge_rules, public.book_chunks to service_role;

drop policy if exists profiles_select_own on public.profiles;
create policy profiles_select_own on public.profiles
    for select to authenticated
    using ((select auth.uid()) = id);
drop policy if exists profiles_insert_own on public.profiles;
create policy profiles_insert_own on public.profiles
    for insert to authenticated
    with check ((select auth.uid()) = id);
drop policy if exists profiles_update_own on public.profiles;
create policy profiles_update_own on public.profiles
    for update to authenticated
    using ((select auth.uid()) = id)
    with check ((select auth.uid()) = id);
drop policy if exists profiles_delete_own on public.profiles;
create policy profiles_delete_own on public.profiles
    for delete to authenticated
    using ((select auth.uid()) = id);

drop policy if exists subscriptions_select_own on public.subscriptions;
create policy subscriptions_select_own on public.subscriptions
    for select to authenticated
    using ((select auth.uid()) = user_id);

drop policy if exists charts_select_own on public.charts;
create policy charts_select_own on public.charts
    for select to authenticated
    using ((select auth.uid()) = user_id);
drop policy if exists charts_insert_own on public.charts;
create policy charts_insert_own on public.charts
    for insert to authenticated
    with check ((select auth.uid()) = user_id);
drop policy if exists charts_update_own on public.charts;
create policy charts_update_own on public.charts
    for update to authenticated
    using ((select auth.uid()) = user_id)
    with check ((select auth.uid()) = user_id);
drop policy if exists charts_delete_own on public.charts;
create policy charts_delete_own on public.charts
    for delete to authenticated
    using ((select auth.uid()) = user_id);

drop policy if exists reports_select_own on public.reports;
create policy reports_select_own on public.reports
    for select to authenticated
    using ((select auth.uid()) = user_id);
drop policy if exists reports_delete_own on public.reports;
create policy reports_delete_own on public.reports
    for delete to authenticated
    using ((select auth.uid()) = user_id);

drop policy if exists compatibility_reports_select_own on public.compatibility_reports;
create policy compatibility_reports_select_own on public.compatibility_reports
    for select to authenticated
    using ((select auth.uid()) = user_id);
drop policy if exists compatibility_reports_delete_own on public.compatibility_reports;
create policy compatibility_reports_delete_own on public.compatibility_reports
    for delete to authenticated
    using ((select auth.uid()) = user_id);

drop policy if exists questions_select_own on public.questions;
create policy questions_select_own on public.questions
    for select to authenticated
    using ((select auth.uid()) = user_id);
drop policy if exists questions_insert_pending_own on public.questions;
create policy questions_insert_pending_own on public.questions
    for insert to authenticated
    with check (
        (select auth.uid()) = user_id
        and answer is null
        and status = 'pending'
        and credits_used = 0
    );

drop policy if exists usage_events_select_own on public.usage_events;
create policy usage_events_select_own on public.usage_events
    for select to authenticated
    using ((select auth.uid()) = user_id);

drop policy if exists credits_select_own on public.credits;
create policy credits_select_own on public.credits
    for select to authenticated
    using ((select auth.uid()) = user_id);

drop policy if exists book_sources_select_authenticated on public.book_sources;
create policy book_sources_select_authenticated on public.book_sources
    for select to authenticated
    using (true);

drop policy if exists book_knowledge_rules_select_authenticated on public.book_knowledge_rules;
create policy book_knowledge_rules_select_authenticated on public.book_knowledge_rules
    for select to authenticated
    using (true);

-- No anon/authenticated grants or policies exist for raw book chunks.

create or replace function public.search_book_chunks(
    search_query text,
    requested_systems text[] default null,
    requested_topics text[] default null,
    result_limit integer default 8
)
returns table (
    chunk_id text,
    source_id text,
    source_title text,
    author text,
    system text,
    topics text[],
    page_start integer,
    page_end integer,
    content text,
    rank real
)
language sql
stable
security invoker
set search_path = ''
as $$
    select
        chunks.chunk_id,
        chunks.source_id,
        sources.title,
        sources.author,
        chunks.system,
        chunks.topics,
        chunks.page_start,
        chunks.page_end,
        chunks.content,
        pg_catalog.ts_rank_cd(
            chunks.search_vector,
            pg_catalog.websearch_to_tsquery('simple'::regconfig, search_query)
        ) as rank
    from public.book_chunks as chunks
    join public.book_sources as sources using (source_id)
    where pg_catalog.btrim(coalesce(search_query, '')) <> ''
      and chunks.search_vector @@
          pg_catalog.websearch_to_tsquery('simple'::regconfig, search_query)
      and (
          coalesce(pg_catalog.cardinality(requested_systems), 0) = 0
          or chunks.system = any(requested_systems)
      )
      and (
          coalesce(pg_catalog.cardinality(requested_topics), 0) = 0
          or chunks.topics && requested_topics
      )
    order by rank desc, chunks.source_id, chunks.page_start
    limit greatest(1, least(coalesce(result_limit, 8), 50));
$$;

revoke all on function public.search_book_chunks(text, text[], text[], integer)
    from public, anon, authenticated;
grant execute on function public.search_book_chunks(text, text[], text[], integer)
    to service_role;

commit;
