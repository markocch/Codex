"""Prévia offline de campanhas; não faz chamadas à API da Meta."""
import argparse
import json
from pathlib import Path

DEFAULT_PLAN = Path(__file__).resolve().parents[2] / "campaigns" / "fechadura-florianopolis.json"


def validate_plan(plan):
    if plan.get("state") != "draft" or plan.get("read_only") is not True:
        raise ValueError("Somente planos de rascunho e leitura são aceitos.")
    if not plan.get("ad_account", "").startswith("act_"):
        raise ValueError("Conta de anúncios não configurada.")
    price = plan["price_brl"]
    if not (0 < price["min"] <= price["max"]):
        raise ValueError("Faixa de preço inválida.")
    campaigns = plan.get("campaigns", [])
    if len(campaigns) != 3 or len({c["id"] for c in campaigns}) != 3:
        raise ValueError("São esperadas três abordagens distintas.")
    for campaign in campaigns:
        for key in ("name", "hypothesis", "primary_text", "headline_a", "headline_b", "visual_brief", "cta"):
            if not isinstance(campaign.get(key), str) or not campaign[key].strip():
                raise ValueError("Campo obrigatório ausente: " + key)
        if campaign["headline_a"] == campaign["headline_b"]:
            raise ValueError("O teste deve variar o título.")
    questions = plan["lead_form"]["questions"]
    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("Perguntas duplicadas.")
    for q in questions:
        if q["type"] == "choice" and not q.get("options"):
            raise ValueError("Pergunta sem opções: " + q["id"])
    return plan


def load_plan(path=DEFAULT_PLAN):
    with Path(path).open(encoding="utf-8") as fp:
        return validate_plan(json.load(fp))


def is_qualified(answers):
    """Critério exploratório; não é avaliação de crédito ou renda."""
    return (
        answers.get("cidade") == "florianopolis"
        and answers.get("faixa_preco") in {"sim", "sim_parcelado"}
        and answers.get("prazo") in {"ate_30", "ate_90"}
        and answers.get("quer_avaliacao") == "sim"
    )


def render_markdown(plan):
    validate_plan(plan)
    price = plan["price_brl"]
    lines = [
        "# " + plan["project"],
        "",
        "**Status:** RASCUNHO — não publicado; sem operações de escrita na Meta.",
        "",
        "**Conta:** " + plan["ad_account"],
        "",
        "**Região:** " + plan["region"],
        "",
        "**Objetivo:** " + plan["objective"],
        "",
        "**Oferta indicativa:** R$ {:,.0f}–R$ {:,.0f}, equipamento, instalação, configuração e suporte inicial.".format(price["min"], price["max"]),
        "",
        "**Condição:** " + price["disclaimer"],
        "",
        "## Criativos e testes A/B",
        "",
        "Cada par A/B modifica apenas a chamada (headline); o texto principal e o conceito visual permanecem iguais.",
        ""
    ]
    for c in plan["campaigns"]:
        lines.extend([
            "### " + c["name"], "",
            "**Hipótese:** " + c["hypothesis"], "",
            "**Texto principal:** " + c["primary_text"], "",
            "**Título A:** " + c["headline_a"], "",
            "**Título B:** " + c["headline_b"], "",
            "**Brief visual:** " + c["visual_brief"], "",
            "**CTA:** " + c["cta"], ""
        ])
        if c.get("scenes"):
            lines.extend(["**Vídeo: sequência visual**", ""])
            for timing, shot, overlay in c["scenes"]:
                lines.append("- {}: {} — **{}**".format(timing, shot, overlay))
            lines.append("")
    form = plan["lead_form"]
    lines.extend(["## Formulário de interesse", "", "**Título:** " + form["title"], "",
                  form["intro"], ""])
    for q in form["questions"]:
        option_text = ""
        if q["type"] == "choice":
            option_text = " — " + " / ".join(o["label"] for o in q["options"])
        lines.append("- " + q["label"] + option_text)
    lines.extend(["", "**Contato:** " + ", ".join(form["contact_fields"]),
                  "", "**Consentimento:** " + form["consent"], "",
                  "**Política de privacidade:** PENDENTE (URL obrigatória antes de publicar).",
                  "", "## Regras do piloto", "",
                  "**Teste:** " + plan["experiment"]["method"], "",
                  "**Métrica principal:** " + plan["experiment"]["hypothesis_metric"], "",
                  "**Qualificação:** " + plan["experiment"]["qualifying_conditions"], ""])
    lines.extend("- " + item for item in plan["experiment"]["guardrails"])
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Visualização local; não publica anúncios.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--plan", default=str(DEFAULT_PLAN))
    args = parser.parse_args(argv)
    plan = load_plan(args.plan)
    print(json.dumps(plan, indent=2, ensure_ascii=False) if args.format == "json"
          else render_markdown(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
