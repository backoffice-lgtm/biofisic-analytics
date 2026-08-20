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

## 3. Environment variables
Cadastre no Netlify:

```
SUPABASE_URL=https://rxwkwmqnbvtzewplbujp.supabase.co
SUPABASE_SECRET_KEY=<secret key do Supabase>
DASHBOARD_USER=biofisic
DASHBOARD_PASSWORD=<senha desejada para o site>
DASHBOARD_SESSION_SECRET=<segredo aleatório longo para assinar a sessão>
```

Não existe nenhuma variável `RENDER_*` nesta versão.

Nunca coloque `SUPABASE_SECRET_KEY` no GitHub, HTML ou print público.

## 4. Deploy
Clique em Deploy. Ao abrir o endereço do Netlify, o visitante será direcionado para a página visual de login. A sessão segura permanece válida por 8 horas.

O `DASHBOARD_SESSION_SECRET` é recomendado e deve ter valor diferente da senha. Se ele não estiver configurado, a aplicação usa `DASHBOARD_PASSWORD` para assinar a sessão, preservando compatibilidade com o deploy anterior.

Envie a pasta/ZIP completa. Não publique somente o HTML: o dashboard também depende das pastas `netlify/functions` e `public/data`.

Nesta revisão, `public/index.html` e `public/dashboard_vendas_mar_abr_mai_2026.html` são cópias idênticas. O Netlify serve `public/index.html`; manter os dois arquivos sincronizados evita que a publicação exiba uma versão anterior do modelo final.

## 5. Testes na ordem
1. Visão Geral
2. Vendas
3. Cancelamentos
4. Financeiro
5. Frequência
6. Análise
7. Sincronizar agora
8. Exportar XLSX
9. Frequência → Heatmap de lotação → marcar/desmarcar unidades
10. Cancelamentos → Cohort de retenção → alternar Rede e unidades
11. Abrir uma janela anônima → confirmar redirecionamento para `/login.html`
12. Testar credencial inválida e credencial válida

## Novos estudos integrados — revisão 2026-08-20

- `public/data/heatmap-approved-2026-08.json`: heatmap aprovado, com consolidado da rede e 14 unidades.
- `public/data/cohort-retention-approved-2026.json`: cohort aprovado, com consolidado ponderado da rede e 14 unidades.
- Os dois gráficos têm dados locais de contingência, portanto permanecem visíveis mesmo quando uma chamada de dados de outra aba falha.
- O heatmap usa caixas de seleção e recalcula o consolidado para qualquer combinação de unidades.
- O cohort abre na visão Rede e permite escolher uma unidade por vez.
- Ambos mantêm os filtros dentro da visualização ampliada.

Os dois arquivos acima reproduzem os estudos aprovados de agosto/2026. Para atualizar esses estudos para outra competência, regenere os JSONs preservando o mesmo esquema ou substitua-os por uma função Supabase compatível antes do próximo deploy.

## Responsividade

- A grade abandona dimensões salvas do editor quando a tela tem até 1100 px e passa para uma coluna fluida.
- O cabeçalho passa para duas linhas em telas de tablet antes que marca e abas se sobreponham.
- Em celular, filtros e ações ocupam a largura disponível; tabelas extensas mantêm rolagem somente dentro do respectivo gráfico.
- O contêiner geral usa a largura real da tela, sem largura fixa de desktop.

## Atualização dos dados
As fontes das APIs continuam em `public`. As materialized views de `analytics` são atualizadas automaticamente a cada 5 minutos. O botão Sincronizar força uma atualização adicional.

## O que não foi alterado
- nenhuma tabela fonte das APIs recebeu UPDATE/DELETE/INSERT do dashboard;
- o frontend visual foi preservado do HTML que já estava validado;
- as regras foram migradas para funções SQL e materialized views separadas.

## Observação sobre validação
As abas foram validadas no Supabase quanto a retorno e estrutura JSON. Como a base está em atualização contínua, números atuais podem diferir de screenshots anteriores. Antes de usar para decisão final, compare os principais KPIs com a versão local de referência.

Nesta revisão, o frontend foi validado em 1440×900, 1024×768 e 390×844. A validação local não substitui a conferência final do domínio Netlify depois que o novo pacote for publicado.
