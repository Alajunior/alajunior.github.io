"""Conteúdo da Central: o manifest é a fonte única, e os números têm de bater com os READMEs dos projetos."""
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
LINKEDIN = "https://www.linkedin.com/in/andr%C3%A9-junior-338767262"


@pytest.fixture(scope="module")
def m():
    return json.loads((RAIZ / "manifest.json").read_text(encoding="utf-8"))


def _textos(x):
    if isinstance(x, dict):
        for v in x.values():
            yield from _textos(v)
    elif isinstance(x, list):
        for v in x:
            yield from _textos(v)
    elif isinstance(x, str):
        yield x


def test_estrutura(m):
    for k in ("meta", "numeros", "como_trabalho", "areas", "projetos"):
        assert k in m
    for k in ("titulo", "sobretitulo", "frase", "autor", "cargo", "linkedin", "atualizado"):
        assert m["meta"][k]
    assert len(m["numeros"]) == 4 and len(m["como_trabalho"]) == 5
    assert [a["id"] for a in m["areas"]] == ["cobranca", "juridico"]
    assert len(m["projetos"]) == 4
    ids = {a["id"] for a in m["areas"]}
    for p in m["projetos"]:
        assert p["area"] in ids
        for k in ("id", "repo", "nome", "tecnica", "metrica", "metrica_sub", "selos", "status", "negocio", "tecnico", "imagem"):
            assert p[k], (p.get("id"), k)
        assert set(p["negocio"]) == {"problema", "responde", "resultado"}
        assert isinstance(p["tecnico"]["testes"], int) and p["tecnico"]["validacao"] and p["tecnico"]["destaques"] and p["tecnico"]["stack"]
    assert m["meta"]["titulo"] == "Central de Projetos de Data Science"
    assert m["meta"]["sobretitulo"] == "Neural Command Center"


def test_identificacao(m):
    assert m["meta"]["autor"] == "André Luis de Almeida Junior"
    assert m["meta"]["cargo"] == "Cientista de Dados"
    assert m["meta"]["linkedin"] == LINKEDIN
    for t in _textos(m):
        assert not re.search(r"[\w.+-]+@[\w-]+\.\w+", t), t
        assert "utm_" not in t, t


def test_testes_batem_com_readmes(m):
    soma = 0
    for p in m["projetos"]:
        soma += p["tecnico"]["testes"]
        readme = RAIZ.parent / p["repo"] / "README.md"
        if readme.is_file():
            n = re.search(r"#\s*(\d+) testes", readme.read_text(encoding="utf-8"))
            assert n and int(n.group(1)) == p["tecnico"]["testes"], p["repo"]
    item = next(n for n in m["numeros"] if "testes" in n["rotulo"])
    assert item["valor"] == str(soma) == "418"


def test_imagens(m):
    for p in m["projetos"]:
        f = RAIZ / "docs" / "img" / p["imagem"]
        assert f.is_file(), f
        assert f.stat().st_size <= 200_000, (f, f.stat().st_size)
