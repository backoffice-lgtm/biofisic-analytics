# Tutorial — atualizar o BioFisic Analytics no Netlify

Este pacote foi preparado para substituir a versão atualmente publicada sem apagar o site, o domínio ou o projeto Supabase.

## Arquivo de publicação

Use a pasta extraída `BIOFISIC_NETLIFY_LOGIN_FINAL_2026-08-20`.

Na raiz dela devem aparecer diretamente:

- `netlify.toml`
- `package.json`
- pasta `public`
- pasta `netlify`
- pasta `supabase`

Não envie somente o HTML. O login, a sincronização e a exportação dependem das funções incluídas no pacote.

## Opção recomendada — atualizar o projeto Netlify atual

Esta opção mantém o mesmo endereço `netlify.app`, o domínio personalizado e o histórico de deploys.

1. Entre em [app.netlify.com](https://app.netlify.com/) com a conta que administra o dashboard.
2. Abra o projeto atual do BioFisic Analytics.
3. Antes da troca, abra **Site configuration → Environment variables** e confirme que existem estas cinco variáveis:

   ```text
   SUPABASE_URL
   SUPABASE_SECRET_KEY
   DASHBOARD_USER
   DASHBOARD_PASSWORD
   DASHBOARD_SESSION_SECRET
   ```

4. Para `SUPABASE_URL`, mantenha:

   ```text
   https://rxwkwmqnbvtzewplbujp.supabase.co
   ```

5. `SUPABASE_SECRET_KEY` deve continuar somente no Netlify. Não coloque a chave dentro do HTML, do ZIP ou do GitHub.
6. Defina `DASHBOARD_USER` e `DASHBOARD_PASSWORD` com as credenciais que serão usadas na nova página de login.
7. Defina `DASHBOARD_SESSION_SECRET` com um texto longo e aleatório, diferente da senha de acesso.
8. Salve as variáveis.
9. No computador, descompacte `BIOFISIC_NETLIFY_LOGIN_FINAL_2026-08-20.zip`.
10. No projeto do Netlify, abra a página **Deploys**.
11. Vá até a área de deploy manual e arraste a pasta extraída `BIOFISIC_NETLIFY_LOGIN_FINAL_2026-08-20` inteira para a área de upload.
12. Aguarde o status **Published**.
13. Abra o endereço do dashboard em uma janela anônima. A nova página de login deve ser apresentada.

## Conferência obrigatória após a publicação

Teste nesta ordem:

1. Credencial incorreta deve ser recusada.
2. Credencial correta deve abrir o dashboard.
3. Visão Geral deve carregar os cards e gráficos.
4. Vendas.
5. Cancelamentos, inclusive o cohort de retenção.
6. Financeiro.
7. Frequência, inclusive o heatmap e os seletores de unidades.
8. Análise.
9. Botão **Sincronizar agora**.
10. Botão **Exportar XLSX**.
11. Conferir o dashboard em computador e celular.

## Se a nova versão apresentar problema

1. Volte para **Deploys** no projeto do Netlify.
2. Abra o último deploy anterior que estava funcionando.
3. Use a opção do Netlify para publicar novamente esse deploy anterior.
4. O endereço e o domínio continuarão os mesmos.

Não exclua o projeto Supabase nem suas tabelas. A troca do frontend não exige recriação do banco.

## Se preferir criar um projeto Netlify novo

1. No Netlify, selecione **Add new project → Deploy manually**.
2. Arraste a pasta extraída completa.
3. Cadastre as cinco variáveis de ambiente listadas acima.
4. Faça um novo deploy depois de salvar as variáveis.
5. Valide todo o painel no endereço temporário `netlify.app`.
6. Somente depois da validação transfira o domínio do projeto antigo para o novo.

A atualização do projeto atual é a opção mais segura, pois preserva o domínio, o histórico e permite retorno imediato ao deploy anterior.
