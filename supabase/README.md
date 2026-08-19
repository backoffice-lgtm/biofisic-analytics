# Supabase Analytics — já configurado no projeto vivo

Projeto: `basededadosEVO` (`rxwkwmqnbvtzewplbujp`).

## Regra de segurança
As tabelas de origem em `public` continuam sendo as fontes das APIs e **não foram editadas pelo dashboard**. O projeto novo apenas lê essas tabelas.

Foi criado um schema isolado `analytics`, contendo:
- views normalizadas;
- materialized views para desempenho;
- funções SQL de regra de negócio;
- RPCs de cada aba do dashboard.

As materialized views são atualizadas automaticamente a cada 5 minutos pelo `pg_cron`.

## RPC público usado somente pela Function do Netlify
`public.biofisic_dashboard_tab(p_tab, p_filters, p_force)`

Execução foi revogada para `anon` e `authenticated`; somente `service_role` pode executar. A secret key fica nas Environment Variables do Netlify e nunca no HTML.

## RPCs analíticos
- `analytics.dashboard_ativos_fast(jsonb)`
- `analytics.dashboard_vendas_fast(jsonb)`
- `analytics.dashboard_cancelamentos_fast(jsonb)`
- `analytics.dashboard_financeiro_fast(jsonb)`
- `analytics.dashboard_frequencia_fast(jsonb)`
- `analytics.dashboard_isaias_fast(jsonb)`

## Atualização
`analytics.refresh_sources()` atualiza apenas as materialized views do schema analytics.
`public.biofisic_dashboard_sync()` é o wrapper utilizado pelo Netlify.

**Não apague o projeto Supabase nem as tabelas/API existentes.**
