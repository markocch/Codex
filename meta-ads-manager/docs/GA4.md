# Integração direta com Google Analytics 4

Sem assinatura de intermediários. Usa a Google Analytics Data API e está sujeita
às cotas do Google. Não cria ou altera eventos, campanhas ou propriedades.
A Meta continua exclusivamente GET. O endpoint Google `runReport` exige POST,
embora apenas leia relatórios. Autorize essa exceção antes de executar consultas.

## Configurar acesso

1. No GA4, Administrador → Detalhes da propriedade: obtenha o **ID numérico**.
   O identificador de medição `G-…` não serve como ID da propriedade.
2. Em um projeto Google Cloud, habilite **Google Analytics Data API**.
3. Para uso inicial, obtenha um token OAuth de um usuário com acesso Leitor à
   propriedade, usando o escopo `https://www.googleapis.com/auth/analytics.readonly`.
   Outra opção é uma conta de serviço adicionada como Leitor à propriedade e um
   token emitido para ela. Não basta uma chave de API.
4. Salve o token como segredo de rede `GA4_ACCESS_TOKEN`, variável homônima,
   restrito a `analyticsdata.googleapis.com`. Autorize esse domínio na rede.
   Nunca cole credenciais no código, nos comandos de exemplo ou no GitHub.
5. Aplique a configuração ao ambiente. Tokens OAuth normalmente expiram em cerca
   de uma hora; este cliente inicial não renova tokens automaticamente. A emissão
   e renovação OAuth também exigem operações POST, fora deste cliente.

```bash
cd meta-ads-manager
PYTHONPATH=src python -m meta_ads.ga4 --property 123456789 --start 2026-10-01 --end 2026-10-31
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Avaliar Groomer

O relatório retorna campanha da sessão, origem/mídia, página de entrada, sessões,
sessões engajadas, taxa de engajamento, eventos principais e receita. Preserva os
metadados de resposta (por exemplo, limiares de privacidade). Faz paginação; não
segue redirecionamentos nem usa endpoints de escrita de configuração.

Cruze com os mesmos períodos da Meta e confira o fuso da propriedade. O nome da
campanha no GA4 depende de UTMs; não presuma correspondência pelo nome do anúncio.
Sem UTMs, tráfego pode aparecer como referral, direto ou sem campanha. Cliques da
Meta não equivalem a sessões do GA4. Consentimento, bloqueadores e atribuição
causam diferenças. A dimensão de URL pode conter parâmetros sensíveis: mantenha
relatórios fora do GitHub (a pasta `reports/` é ignorada).

`keyEvents` agrega eventos marcados como principais, não apenas leads ou vendas.
A auditoria dos nomes dos eventos e a consulta por evento são etapas adicionais.
Receita zero não prova ausência de vendas: o evento de compra e seu valor precisam
estar configurados. Este cliente não instala tags nem recupera eventos passados
que não foram coletados. Testes são simulados; uma consulta real exige acesso
configurado e ID informado pelo responsável.
