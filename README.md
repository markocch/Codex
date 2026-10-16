# Codex

[meta-ads-manager](meta-ads-manager/README.md): gestor de campanhas Meta Ads em Python, exclusivamente de leitura, para o aplicativo **Gestor de Tráfego IA**.

- Conta padrão: `act_184261823230641`
- Meta Marketing API: `v26.0`
- [Configuração de rede e autenticação no Codex Cloud](meta-ads-manager/docs/CODEX_CLOUD.md)

```bash
cd meta-ads-manager
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m meta_ads --period last_30d
```
