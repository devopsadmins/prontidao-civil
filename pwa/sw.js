// Service worker do monitor. VERSAO é trocada a cada build, o que descarta o cache antigo.
const VERSAO = "__VERSAO__";
const CACHE = "prontidao-" + VERSAO;
const BASE = ["./", "index.html", "data.json", "manifest.webmanifest", "geo/countries-110m.json", "geo/brasil-uf.json",
  "icons/icon-192.png", "icons/icon-512.png"];

self.addEventListener("install", ev => {
  ev.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", ev => {
  ev.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k.startsWith("prontidao-") && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Página e dados: rede primeiro (o nível muda ao longo do dia), cache só quando estiver sem internet.
// Bibliotecas, fontes e mapas: cache primeiro, atualizando em segundo plano.
self.addEventListener("fetch", ev => {
  const req = ev.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const fresco = req.mode === "navigate" || (url.origin === location.origin && url.pathname.endsWith("/data.json"));
  if (fresco) {
    ev.respondWith(fetch(req).then(r => {
      if (r.ok) { const copia = r.clone(); caches.open(CACHE).then(c => c.put(req.mode === "navigate" ? "./" : req, copia)); }
      return r;
    }).catch(() => caches.match(req.mode === "navigate" ? "./" : req)));
    return;
  }
  ev.respondWith(caches.match(req).then(hit => {
    const rede = fetch(req).then(r => {
      if (r.ok || r.type === "opaque") { const copia = r.clone(); caches.open(CACHE).then(c => c.put(req, copia)); }
      return r;
    }).catch(() => hit);
    return hit || rede;
  }));
});
