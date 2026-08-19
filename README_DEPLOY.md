# BIOFISIC ANALYTICS — NETLIFY + SUPABASE (SEM RENDER)

Esta é a nova versão para publicação limpa.

## Arquitetura

```
Navegador
   ↓
Netlify CDN — HTML/CSS/JS
   ↓
Netlify Functions — mantém a secret key fora do navegador
   ↓
Supabase RPC — cálculos no schema analytics
   ↓
Tabelas public — somente leitura
```

**Render não faz parte desta versão.**

## Antes de apagar os projetos antigos
Você pode apagar o site antigo do Netlify e o repositório antigo do GitHub, mas o caminho mais seguro é criar primeiro o novo repositório e confirmar as 6 abas.

**NÃO APAGUE o projeto Supabase `basededadosEVO` nem as tabelas que recebem as APIs.**

## 1. Criar um GitHub limpo
Crie um repositório vazio, por exemplo `biofisic-analytics`.

Extraia este ZIP e envie **o conteúdo da pasta**, preservando as pastas:

```
public/
netlify/
supabase/
referencia_legacy/
netlify.toml
package.json
.env.example
.gitignore
```

## 2. Criar projeto no Netlify
Use `Add new project → Import an existing project → GitHub`.

Selecione o repositório novo.

Configuração:
- Branch: `main`
- Base directory: vazio
- Build command: vazio
- Publish directory: `public`
- Functions directory: `netlify/functions`

O `netlify.toml` já contém essas rotas.

## 3. Environment variables — somente estas 4
Cadastre no Netlify:

```
SUPABASE_URL=https://rxwkwmqnbvtzewplbujp.supabase.co
SUPABASE_SECRET_KEY=<secret key do Supabase>
DASHBOARD_USER=biofisic
DASHBOARD_PASSWORD=<senha desejada para o site>
```

Não existe nenhuma variável `RENDER_*` nesta versão.

Nunca coloque `SUPABASE_SECRET_KEY` no GitHub, HTML ou print público.

## 4. Deploy
Clique em Deploy. Ao abrir o endereço do Netlify, o navegador pedirá usuário e senha.

## 5. Testes na ordem
1. Visão Geral
2. Vendas
3. Cancelamentos
4. Financeiro
5. Frequência
6. Análise
7. Sincronizar agora
8. Exportar XLSX

## Atualização dos dados
As fontes das APIs continuam em `public`. As materialized views de `analytics` são atualizadas automaticamente a cada 5 minutos. O botão Sincronizar força uma atualização adicional.

## O que não foi alterado
- nenhuma tabela fonte das APIs recebeu UPDATE/DELETE/INSERT do dashboard;
- o frontend visual foi preservado do HTML que já estava validado;
- as regras foram migradas para funções SQL e materialized views separadas.

## Observação sobre validação
As abas foram validadas no Supabase quanto a retorno e estrutura JSON. Como a base está em atualização contínua, números atuais podem diferir de screenshots anteriores. Antes de usar para decisão final, compare os principais KPIs com a versão local de referência.
