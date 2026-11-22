"""Revisão final: contraste AA no tema Light, alvo de toque de 44 px, sem flash de tema e fundo estável ao rolar."""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CSS = (RAIZ / "estatico" / "estilo.css").read_text(encoding="utf-8")
JS = (RAIZ / "estatico" / "central.js").read_text(encoding="utf-8")
BASE = (RAIZ / "modelos" / "base.html").read_text(encoding="utf-8")


def _lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contraste(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _bloco_light():
    return re.search(r'body\[data-theme="light"\]\{(.*?)\}', CSS, re.S).group(1)


def test_contraste_aa_no_tema_light():
    bloco = _bloco_light()
    ac = re.search(r"--ac:(#[0-9a-fA-F]{6})", bloco).group(1)
    for fundo in ("#EDE6D8", "#F6F2E8", "#FFFFFF"):
        assert contraste(ac, fundo) >= 4.5, (ac, fundo)
    paradas = re.findall(r"#[0-9a-fA-F]{6}", re.search(r"--acg:linear-gradient\(([^)]*)\)", bloco).group(1))
    for cor in paradas:                                        # texto branco (--on-ac) sobre o botão principal
        assert contraste("#FFFFFF", cor) >= 4.5, cor


def test_botoes_de_alternancia_com_44px():
    regra = re.search(r"\.seg button\{([^}]*)\}", CSS).group(1)
    assert int(re.search(r"min-height:(\d+)px", regra).group(1)) >= 44


def test_tema_aplicado_antes_de_pintar():
    """Script inline logo após <body>: quem escolheu Light/Técnica não vê o flash de Midnight/Negócio ao navegar."""
    depois_body = BASE.split("<body", 1)[1].split("<canvas", 1)[0]
    assert "<script>" in depois_body and "central_tema" in depois_body and "central_visao" in depois_body
    assert "try" in depois_body


def test_resize_so_de_altura_nao_sorteia_a_rede():
    """No celular a barra de endereço some ao rolar e dispara resize só de altura: a rede não pode pular."""
    assert re.search(r"innerWidth\s*===\s*W", JS)
