"""Gera o site estático da Central a partir do manifest.json.

    python build.py            # grava em docs/

O HTML sai pronto (legível sem JavaScript); o JS só cuida de tema, troca de visão e do fundo animado.
"""
import json
import shutil
from html import escape
from pathlib import Path
from string import Template

RAIZ = Path(__file__).resolve().parent
MODELOS = RAIZ / "modelos"
ESTATICO = RAIZ / "estatico"
DOCS = RAIZ / "docs"


def e(texto) -> str:
    return escape(str(texto), quote=True)


def links(projeto: dict) -> dict:
    return {"painel": f"https://alajunior.github.io/{projeto['repo']}/",
            "codigo": f"https://github.com/Alajunior/{projeto['repo']}"}


def _modelo(nome: str) -> Template:
    return Template((MODELOS / nome).read_text(encoding="utf-8"))


def _externo(href: str, texto: str, classe: str) -> str:
    return f'<a class="{classe}" href="{e(href)}" target="_blank" rel="noopener">{texto}</a>'


def _pagina(m: dict, raiz: str, titulo: str, descricao: str, conteudo: str) -> str:
    meta = m["meta"]
    return _modelo("base.html").substitute(
        titulo_pagina=e(titulo), descricao=e(descricao), raiz=raiz, autor=e(meta["autor"]), cargo=e(meta["cargo"]),
        linkedin=e(meta["linkedin"]), atualizado=e("/".join(reversed(meta["atualizado"].split("-")))), conteudo=conteudo)


def _home(m: dict) -> str:
    meta = m["meta"]
    ini, _, fim = meta["titulo"].rpartition(" de ")   # última parte em gradiente: "Data Science"
    def stats(lista):
        return "\n".join(f'    <div class="stat"><b>{e(n["valor"])}</b><span>{e(n["rotulo"])}</span></div>' for n in lista)
    cards = []
    for a in m["areas"]:
        projs = [p for p in m["projetos"] if p["area"] == a["id"]]
        itens = "".join(f'<li>{e(p["nome"])}<span class="mod-tec so-tecnica">{e(p["tecnica"])} · {e(p["metrica"])}</span></li>'
                        for p in projs)
        rotulo = f"{len(projs)} projeto" + ("s" if len(projs) > 1 else "")
        cards.append(f'    <a class="cart" href="area/{e(a["id"])}.html"><div class="eye">{rotulo}</div>'
                     f'<h3>{e(a["nome"])}</h3><p>{e(a["resumo"])}</p><ul class="mods">{itens}</ul>'
                     f'<div class="enter">Entrar →</div></a>')
    praticas = "\n".join(f'    <article class="pratica"><h3>{e(c["titulo"])}</h3><p>{e(c["texto"])}</p></article>'
                         for c in m["como_trabalho"])
    conteudo = _modelo("home.html").substitute(
        sobretitulo=e(meta["sobretitulo"]), titulo_ini=e(ini + " de"), titulo_fim=e(fim), frase=e(meta["frase"]),
        numeros=stats(m["numeros"]), numeros_tecnica=stats(m["numeros_tecnica"]), n_areas=f"{len(m['areas'])} áreas", areas="\n".join(cards),
        n_praticas=f"{len(m['como_trabalho'])} práticas", praticas=praticas)
    return _pagina(m, "", f"{meta['titulo']} · {meta['autor']}", meta["frase"], conteudo)


def _projeto(p: dict) -> str:
    ln, neg, tec = links(p), p["negocio"], p["tecnico"]
    chips = "".join(f'<span class="chip">{e(s)}</span>' for s in tec["stack"])
    selos = "".join(f'<span class="selo">{e(s)}</span>' for s in p["selos"])
    destaques = "".join(f"<li>{e(d)}</li>" for d in tec["destaques"])
    return f"""<article class="mod" id="{e(p['id'])}">
  <div class="mhead"><div><h2>{e(p['nome'])}</h2><div class="chips so-tecnica">{chips}</div></div><span class="badge">● {e(p['status'])}</span></div>
  <div class="mgrid">
    <div class="mtexto">
      <div class="metrica">{e(p['metrica'])}</div>
      <p class="metrica-sub">{e(p['metrica_sub'])}</p>
      <div class="selos">{selos}</div>
      <dl class="so-negocio">
        <dt>O problema</dt><dd>{e(neg['problema'])}</dd>
        <dt>O que o painel responde</dt><dd>{e(neg['responde'])}</dd>
        <dt>Resultado</dt><dd>{e(neg['resultado'])}</dd>
      </dl>
      <div class="so-tecnica">
        <p><b>Técnica:</b> {e(p['tecnica'])}</p>
        <p><b>Validação:</b> {e(tec['validacao'])}</p>
        <ul class="destaques">{destaques}</ul>
        <p class="ntestes">{tec['testes']} testes automatizados, rodando a cada push</p>
      </div>
      <div class="acoes">{_externo(ln['painel'], 'Painel ao vivo ↗', 'btn pri')}{_externo(ln['codigo'], 'Código ↗', 'btn')}</div>
    </div>
    <a class="shot" href="{e(ln['painel'])}" target="_blank" rel="noopener"><img src="../img/{e(p['imagem'])}" alt="Captura do painel: {e(p['nome'])}" width="1200" height="750" loading="lazy"></a>
  </div>
</article>"""


def _area(m: dict, a: dict) -> str:
    projs = "\n".join(_projeto(p) for p in m["projetos"] if p["area"] == a["id"])
    conteudo = _modelo("area.html").substitute(nome=e(a["nome"]), resumo=e(a["resumo"]), projetos=projs)
    return _pagina(m, "../", f"{a['nome']} · {m['meta']['titulo']}", a["resumo"], conteudo)


def gerar(m: dict, saida: Path) -> list[Path]:
    saida = Path(saida)
    (saida / "area").mkdir(parents=True, exist_ok=True)
    paginas = {saida / "index.html": _home(m)}
    for a in m["areas"]:
        paginas[saida / "area" / f"{a['id']}.html"] = _area(m, a)
    for caminho, html in paginas.items():
        caminho.write_text(html, encoding="utf-8", newline="\n")
    if ESTATICO.is_dir():
        for f in ESTATICO.iterdir():
            shutil.copyfile(f, saida / f.name)
    if saida.resolve() != DOCS.resolve():   # as imagens moram em docs/img; num destino de teste, vão junto
        shutil.copytree(DOCS / "img", saida / "img", dirs_exist_ok=True)
    return list(paginas)


if __name__ == "__main__":
    feitas = gerar(json.loads((RAIZ / "manifest.json").read_text(encoding="utf-8")), DOCS)
    print("\n".join(p.relative_to(RAIZ).as_posix() for p in feitas))
