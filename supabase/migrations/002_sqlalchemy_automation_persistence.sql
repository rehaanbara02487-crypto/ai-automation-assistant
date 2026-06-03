alter table public.automations
  add column if not exists description text,
  add column if not exists trigger_type text,
  add column if not exists workflow_json jsonb not null default '{}'::jsonb;

do $$
declare
  has_legacy_columns boolean;
begin
  select exists (
    select 1
    from information_schema.columns
    where table_schema = 'public'
      and table_name = 'automations'
      and column_name = 'trigger'
  )
  into has_legacy_columns;

  if has_legacy_columns then
    execute $migration$
      update public.automations
      set
        description = coalesce(description, summary, ''),
        trigger_type = coalesce(trigger_type, trigger, 'manual'),
        workflow_json = case
          when workflow_json = '{}'::jsonb then jsonb_build_object(
            'trigger', coalesce(trigger, trigger_type, 'manual'),
            'actions', coalesce(actions, '[]'::jsonb),
            'summary', coalesce(summary, description, ''),
            'steps', coalesce(steps, '[]'::jsonb),
            'workflow_id', coalesce(workflow_id, 'mock-' || id::text),
            'error_count', coalesce(error_count, 0),
            'run_count', coalesce(run_count, 0),
            'last_run_at', last_run_at
          )
          else workflow_json
        end
    $migration$;
  end if;
end $$;

update public.automations
set
  description = coalesce(description, ''),
  trigger_type = coalesce(trigger_type, 'manual');

alter table public.automations
  alter column description set not null,
  alter column trigger_type set not null,
  alter column workflow_json set not null;

alter table public.automations
  drop column if exists trigger,
  drop column if exists actions,
  drop column if exists summary,
  drop column if exists steps,
  drop column if exists workflow_id,
  drop column if exists error_count,
  drop column if exists run_count,
  drop column if exists last_run_at;
