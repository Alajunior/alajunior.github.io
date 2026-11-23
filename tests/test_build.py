"""build.py: o manifest vira HTML pronto (legível sem JS), com caminhos relativos que funcionam em qualquer página."""
import copy
import json
import re
from pathlib import Path

import pytest

import build

RAIZ = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((RAIZ / "manifest.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    saida = tmp_path_factory.mktemp("site")
    paginas = build.gerar(MANIFEST, saida)
    return saida, paginas


def ler(saida, nome):
    return (saida / nome).read_text(encoding="utf-8")


def test_paginas_geradas(site):
    saida, paginas = site
    assert sorted(p.relative_to(saida).as_posix() for p in paginas) == ["area/cobranca.html", "area/juridico.html", "index.html"]


def test_home(site):
    h = ler(site[0], "index.html")
    assert "Central de Projetos de Data Science" in h and "Neural Command Center" in h
    assert ">511<" in h
    for item in MANIFEST["como_trabalho"]:
        assert item["titulo"] in h
    assert 'href="area/cobranca.html"' in h and 'href="area/juridico.html"' in h
    for p in MANIFEST["projetos"]:
        assert p["nome"].replace("+", "+") in h.replace("&amp;", "&")
    assert re.search(r'<a [^>]*href="https://www\.linkedin\.com/in/andr%C3%A9-junior-338767262"[^>]*target="_blank"[^>]*rel="noopener"', h)
    assert "André Luis de Almeida Junior" in h and "Cientista de Dados" in h


def test_home_muda_com_a_visao(site):
    """O botão Negócio / Técnica tem de mudar algo visível também na home."""
    h = ler(site[0], "index.html").replace("&amp;", "&")
    assert 'class="stats so-negocio"' in h and 'class="stats so-tecnica"' in h
    for n in MANIFEST["numeros_tecnica"]:
        assert f'<b>{n["valor"]}</b>' in h
    for p in MANIFEST["projetos"]:
        assert f'{p["tecnica"]} · {p["metrica"]}' in h


def test_area(site):
    saida = site[0]
    for area, n in (("cobranca", 3), ("juridico", 1)):
        h = ler(saida, f"area/{area}.html")
        assert h.count('class="mod"') == n
        for p in (p for p in MANIFEST["projetos"] if p["area"] == area):
            ln = build.links(p)
            assert f'href="{ln["painel"]}"' in h and f'href="{ln["codigo"]}"' in h
            assert p["metrica"] in h
            for s in p["selos"]:
                assert s in h
            assert f'{p["tecnico"]["testes"]} testes' in h
        assert 'class="so-negocio' in h and 'class="so-tecnica' in h


def test_links():
    p = {"repo": "abc-def"}
    assert build.links(p) == {"painel": "https://alajunior.github.io/abc-def/", "codigo": "https://github.com/Alajunior/abc-def"}


def test_links_internos_existem(site):
    saida = site[0]
    for pag in ("index.html", "area/cobranca.html", "area/juridico.html"):
        h = ler(saida, pag)
        for alvo in re.findall(r'(?:href|src)="([^"#]+)"', h):
            if alvo.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            destino = (saida / pag).parent / alvo
            assert destino.resolve().is_file(), f"{pag} → {alvo}"


def test_texto_escapado(tmp_path):
    m = copy.deepcopy(MANIFEST)
    m["projetos"][0]["nome"] = 'A < B & "C"'
    build.gerar(m, tmp_path)
    h = (tmp_path / "area" / "cobranca.html").read_text(encoding="utf-8")
    assert "A &lt; B &amp; &quot;C&quot;" in h
    assert 'A < B & "C"' not in h


def test_docs_em_dia(tmp_path):
    """Falha se o manifest ou os modelos mudaram e alguém esqueceu de rodar `python build.py`."""
    build.gerar(MANIFEST, tmp_path)
    for pag in ("index.html", "area/cobranca.html", "area/juridico.html"):
        novo = (tmp_path / pag).read_bytes()
        versionado = (RAIZ / "docs" / pag).read_bytes().replace(b"\r\n", b"\n")
        assert novo == versionado, f"docs/{pag} desatualizado: rode python build.py"
