# Rede e autenticação no Codex Cloud

Configure o segredo de rede `META_ACCESS_TOKEN`, vinculado à variável de mesmo
nome e restrito a `graph.facebook.com`. Autorize esse domínio na política HTTP.
Use as variáveis de proxy e os certificados injetados pelo ambiente; um valor
placeholder pode ser substituído pelo proxy durante a requisição.

Verifique a prontidão pelo status do ambiente, sem imprimir valores. Execute o
CLI normalmente. HTTP 200 confirma acesso à operação consultada, não a todos os
recursos. Erro Meta 190 indica problema de autenticação; HTTP 403 pode indicar
permissão de conta ou política de rede. Não desative TLS nem contorne o proxy.

A aplicação usa apenas GET na API Meta. O envio do código ao GitHub é uma operação
separada de versionamento e não altera anúncios, campanhas ou orçamentos.
