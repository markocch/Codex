# Gestor de Tráfego IA — Meta Ads Manager

Cliente Python 3.10+ sem dependências de execução, exclusivamente de leitura.
Conta padrão: `act_184261823230641`. Meta Marketing API: `v26.0`.

## Executar

Configure `META_ACCESS_TOKEN` pelo gerenciador de segredos do ambiente, com acesso
à conta e permissão `ads_read`. Nunca coloque o token no código ou em argumentos.

```bash
cd meta-ads-manager
PYTHONPATH=src python -m meta_ads --period last_30d
PYTHONPATH=src python -m unittest discover -s tests -v
```

Também é possível instalar com `pip install .` e executar `meta-ads`.
Opções: `--account act_ID` e `--period last_30d|last_7d|today|yesterday|maximum`.

## Dados e interpretação

O relatório JSON consulta a conta, todas as páginas de campanhas e insights no
nível de campanha. Inclui nome, status configurado e efetivo, objetivo, orçamento
diário/vitalício quando disponível, gasto, impressões, alcance, cliques, cliques
no link, CTR, CPC, CPM, ações e custo por tipo de ação.

`spend` representa investimento realizado no período, na moeda da conta.
Orçamentos são limites configurados em unidades mínimas da moeda (centavos em
BRL), não gastos. `insights: null` significa ausência de linha retornada no
período, não prova de gasto histórico zero. CTR é percentual; CPC e CPM usam a
moeda da conta. Ações podem ter atribuições diferentes e não devem ser somadas
indiscriminadamente. Datas retornadas em `date_start` e `date_stop` delimitam o
relatório; a Meta usa o fuso da conta. Campanhas excluídas ou inacessíveis podem
não aparecer na listagem; linhas de insights sem campanha ficam em
`insights_without_campaign`. O resultado representa o acesso permitido ao token.

## Segurança e validação

Somente GET para um host fixo, TLS e proxy herdados, sem redirecionamentos.
Paginação por cursor reconstruída localmente, sem seguir URLs de resposta.
Erros não exibem corpo, token ou cabeçalhos. Não há rotas de escrita nem chamadas
de batch. Testes simulam API; não exigem segredos. GitHub Actions executa testes
em pushes e pull requests. Relatórios reais não são versionados por padrão.

Veja [configuração cloud](docs/CODEX_CLOUD.md).


## Fase 2 — Piloto da fechadura (rascunho, sem publicação)

Os três ângulos de campanha, testes A/B de título e perguntas para identificar
interesse qualificado em Florianópolis estão em
[campaigns/fechadura-florianopolis.json](campaigns/fechadura-florianopolis.json).

Para revisar a proposta sem conectar à Meta:
- [Prévia completa das campanhas](docs/CAMPANHA_FECHADURA.md)
- [Instruções de uso e limites](docs/FASE2.md)

```bash
cd meta-ads-manager
PYTHONPATH=src python -m meta_ads.drafts --format markdown
PYTHONPATH=src python -m meta_ads.drafts --format json
PYTHONPATH=src python -m unittest discover -s tests -v
```

**Segurança:** a geração de rascunhos não executa requisições HTTP nem utiliza
credenciais. A criação de anúncios e formulários reais continua bloqueada; requer
aprovação comercial, URL de política de privacidade e permissões adicionais.

## Revisão visual v2

A proposta agora é **vídeo-first**, com três demonstrações de 15–20s e imagem estática de controle. A IA só prepara rascunhos; o sistema continua GET e não cria anúncios.

- [Roteiros visuais](docs/CAMPANHA_FECHADURA.md)
- [Pesquisa e referências](docs/REFERENCIAS_CRIATIVAS.md)
