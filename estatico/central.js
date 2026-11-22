// Central de Projetos: tema, visão (Negócio/Técnica) e o fundo de rede neural. O HTML funciona sem este arquivo.
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");
  var B = document.body;
  var store = {   // sem storage (aba anônima, bloqueado): cai nos padrões
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* sem storage */ } }
  };

  function marcar(grupo, attr, valor) {
    document.querySelectorAll("#" + grupo + " [data-" + attr + "]").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-" + attr) === valor ? "true" : "false");
    });
  }
  function aplicarTema(t) {
    if (["midnight", "dark", "light"].indexOf(t) < 0) t = "midnight";
    B.setAttribute("data-theme", t);
    marcar("segTema", "tema", t);
    store.set("central_tema", t);
    rede.cores();
  }
  function aplicarVisao(v) {
    if (["negocio", "tecnica"].indexOf(v) < 0) v = "negocio";
    B.setAttribute("data-visao", v);
    marcar("segVisao", "visao", v);
    store.set("central_visao", v);
  }

  // ---------- rede neural: nós que derivam, ligações por distância e pulsos que correm pelas ligações ----------
  var rede = (function () {
    var cv = document.getElementById("net");
    if (!cv || !cv.getContext) return { cores: function () {}, iniciar: function () {} };
    var ctx = cv.getContext("2d"), nos = [], pulsos = [], W = 0, H = 0, dpr = 1, dot = "255,122,89", line = "59,91,140";
    var parado = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var raf = 0, DIST = 150;

    function cores() {
      var cs = getComputedStyle(B);
      dot = (cs.getPropertyValue("--p-dot") || dot).trim();
      line = (cs.getPropertyValue("--p-line") || line).trim();
      if (parado) desenhar();
    }
    function medir() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = window.innerWidth; H = window.innerHeight;
      cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var n = Math.max(24, Math.min(70, Math.round(W * H / 22000)));
      nos = [];
      for (var i = 0; i < n; i++) {
        nos.push({ x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - .5) * .25, vy: (Math.random() - .5) * .25, r: 1.2 + Math.random() * 1.6 });
      }
      pulsos = [];
    }
    function desenhar() {
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < nos.length; i++) {
        for (var j = i + 1; j < nos.length; j++) {
          var dx = nos[i].x - nos[j].x, dy = nos[i].y - nos[j].y, d = Math.sqrt(dx * dx + dy * dy);
          if (d < DIST) {
            ctx.strokeStyle = "rgba(" + line + "," + (0.35 * (1 - d / DIST)).toFixed(3) + ")";
            ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(nos[i].x, nos[i].y); ctx.lineTo(nos[j].x, nos[j].y); ctx.stroke();
          }
        }
      }
      for (var k = 0; k < nos.length; k++) {
        ctx.fillStyle = "rgba(" + dot + ",.75)";
        ctx.beginPath(); ctx.arc(nos[k].x, nos[k].y, nos[k].r, 0, 6.2832); ctx.fill();
      }
      for (var p = 0; p < pulsos.length; p++) {
        var s = pulsos[p], a = nos[s.a], b = nos[s.b];
        var x = a.x + (b.x - a.x) * s.t, y = a.y + (b.y - a.y) * s.t;
        ctx.fillStyle = "rgba(" + dot + ",.95)";
        ctx.shadowColor = "rgba(" + dot + ",.9)"; ctx.shadowBlur = 8;
        ctx.beginPath(); ctx.arc(x, y, 2.2, 0, 6.2832); ctx.fill();
        ctx.shadowBlur = 0;
      }
    }
    function passo() {
      for (var i = 0; i < nos.length; i++) {
        var n = nos[i];
        n.x += n.vx; n.y += n.vy;
        if (n.x < 0 || n.x > W) n.vx *= -1;
        if (n.y < 0 || n.y > H) n.vy *= -1;
      }
      if (pulsos.length < 6 && Math.random() < 0.04) {   // disparo: escolhe uma ligação existente
        var a = Math.floor(Math.random() * nos.length);
        for (var j = 0; j < nos.length; j++) {
          var dx = nos[a].x - nos[j].x, dy = nos[a].y - nos[j].y;
          if (j !== a && dx * dx + dy * dy < DIST * DIST) { pulsos.push({ a: a, b: j, t: 0 }); break; }
        }
      }
      pulsos = pulsos.filter(function (s) {
        s.t += 0.025;
        var a = nos[s.a], b = nos[s.b], dx = a.x - b.x, dy = a.y - b.y;
        return s.t < 1 && dx * dx + dy * dy < DIST * DIST;
      });
      desenhar();
      raf = window.requestAnimationFrame(passo);
    }
    function iniciar() {
      medir(); cores();
      if (parado) { desenhar(); return; }   // movimento reduzido: um quadro estático
      raf = window.requestAnimationFrame(passo);
      document.addEventListener("visibilitychange", function () {   // aba em segundo plano: pausa
        window.cancelAnimationFrame(raf);
        if (!document.hidden) raf = window.requestAnimationFrame(passo);
      });
    }
    var t;
    window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(function () { medir(); if (parado) desenhar(); }, 150); });
    return { cores: cores, iniciar: iniciar };
  })();

  document.querySelectorAll("#segTema [data-tema]").forEach(function (b) {
    b.addEventListener("click", function () { aplicarTema(b.getAttribute("data-tema")); });
  });
  document.querySelectorAll("#segVisao [data-visao]").forEach(function (b) {
    b.addEventListener("click", function () { aplicarVisao(b.getAttribute("data-visao")); });
  });
  aplicarVisao(store.get("central_visao") || "negocio");
  aplicarTema(store.get("central_tema") || "midnight");
  rede.iniciar();
})();
