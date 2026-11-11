/* Apps da família: Prontidão, Boatos, Regeneração e Reserva da Casa se mostram uns nos outros.
   Fonte única: ~/Documents/familia/familia.js. Para atualizar os sites, rode ~/Documents/familia/sync.sh.
   Uso na página: <div id="familia" data-atual="boatos"></div> e <script src="familia.js" defer></script>
   Só lê dados públicos de cada app; não envia nada e não guarda nada. */
(function () {
  const APPS = [
    { id: "prontidao", nome: "Prontidão Civil", papel: "O que é real agora", url: "https://prontidao.coderstudio.club/",
      icone: "https://prontidao.coderstudio.club/icons/icon-192.png",
      status: () => pegar("https://prontidao.coderstudio.club/status.json").then(s => ({
        cor: { verde: "#2e8a57", amarelo: "#dda115", vermelho: "#c6372c" }[s.nivel],
        texto: `Nível de hoje: ${s.nivel.charAt(0).toUpperCase() + s.nivel.slice(1)}. ${s.resumo}` })) },
    { id: "boatos", nome: "Monitor de Boatos", papel: "O que não é verdade", url: "https://boatos.coderstudio.club/",
      icone: "https://boatos.coderstudio.club/icons/icon-192.png",
      status: () => pegar("https://boatos.coderstudio.club/data.json").then(d => ({ texto: d.calma })) },
    { id: "reservas", nome: "Reserva da Casa", papel: "O que fazer em casa", url: "https://reservas.coderstudio.club/",
      icone: "https://reservas.coderstudio.club/icone-192.png",
      status: () => Promise.resolve({ texto: "Calcule água e comida para a sua família e monte o plano, sem cadastro." }) },
    { id: "regeneracao", nome: "Regeneração", papel: "O que está dando certo", url: "https://regeneracao.coderstudio.club/",
      icone: "https://regeneracao.coderstudio.club/apple-touch-icon.png",
      status: () => pegar("https://regeneracao.coderstudio.club/data.json").then(d => ({ texto: d.destaque && d.destaque.titulo })) },
  ];

  function pegar(url) {
    const c = new AbortController();
    const t = setTimeout(() => c.abort(), 6000);
    return fetch(url, { signal: c.signal, cache: "no-cache" }).then(r => { clearTimeout(t); if (!r.ok) throw new Error(r.status); return r.json(); });
  }
  const el = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };
  const curto = (s, n) => !s ? "" : s.length > n ? s.slice(0, n).replace(/\s+\S*$/, "") + "…" : s;

  function estilo() {
    if (document.getElementById("familia-css")) return;
    const st = el("style"); st.id = "familia-css";
    st.textContent = `
#familia { padding: 28px 0 32px; border-top: 1px solid var(--line, #d6dee4); margin-top: 8px; }
#familia .fam-h { font: 700 22px/1.2 var(--font-display, Georgia, serif); margin: 0 0 4px; color: var(--ink, #16222c); }
#familia .fam-p { margin: 0 0 16px; color: var(--muted, #56656f); font-size: 14.5px; max-width: 70ch; }
#familia .fam-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr)); gap: 12px; }
#familia a.fam-app { display: grid; grid-template-columns: 44px 1fr; gap: 4px 12px; align-items: start; padding: 14px; background: var(--panel, #fff); border: 1px solid var(--line, #d6dee4); color: var(--ink, #16222c); text-decoration: none; min-width: 0; }
#familia a.fam-app:hover { border-color: var(--ink, #16222c); }
#familia a.fam-app:focus-visible { outline: 2px solid var(--accent, #1f6f5c); outline-offset: 2px; }
#familia .fam-app img { width: 44px; height: 44px; border-radius: 10px; grid-row: span 3; background: var(--line, #d6dee4); }
#familia .fam-nome { font-weight: 700; font-size: 15px; }
#familia .fam-papel { font: 500 11px/1.2 var(--font-mono, ui-monospace, monospace); letter-spacing: .08em; text-transform: uppercase; color: var(--muted, #56656f); }
#familia .fam-st { font-size: 13px; color: var(--muted, #56656f); min-height: 2.6em; }
#familia .fam-st i { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 6px; vertical-align: 1px; }`;
    document.head.append(st);
  }

  function montar() {
    const host = document.getElementById("familia");
    if (!host) return;
    estilo();
    const atual = host.dataset.atual;
    host.setAttribute("aria-labelledby", "fam-h");
    const h = el("h2", "fam-h", "Apps da família"); h.id = "fam-h";
    const p = el("p", "fam-p", "Cada um cuida de uma parte: o que é real, o que é boato, o que fazer em casa e o que está dando certo.");
    const grid = el("div", "fam-grid");
    APPS.filter(a => a.id !== atual).forEach(a => {
      const card = el("a", "fam-app"); card.href = a.url; card.target = "_blank"; card.rel = "noopener";
      const img = el("img"); img.src = a.icone; img.alt = ""; img.width = 44; img.height = 44; img.loading = "lazy"; img.decoding = "async";
      const st = el("div", "fam-st", a.papel + ".");
      card.append(img, el("div", "fam-nome", a.nome), el("div", "fam-papel", a.papel), st);
      card.setAttribute("aria-label", `${a.nome}: ${a.papel}`);
      grid.append(card);
      a.status().then(s => {
        if (!s || !s.texto) return;
        st.replaceChildren();
        if (s.cor) { const i = el("i"); i.style.background = s.cor; i.setAttribute("aria-hidden", "true"); st.append(i); }
        st.append(curto(s.texto, 130));
      }).catch(() => {});
    });
    host.replaceChildren(h, p, grid);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", montar); else montar();
})();
