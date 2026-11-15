// BÖRÜ anonim geri bildirim alıcısı (Cloudflare Worker + KV).
// POST /gonder : BÖRÜ'nün (kullanıcının açıkça izin verdiği) anonim özetini kaydeder.
// GET  /veri   : kayıtları sayfa sayfa döner (anonim olduğu için herkese açık; bkz. PRIVACY.md).
// GET  /       : kısa bilgi.
// Gizli anahtar gerekmez. Kötüye kullanıma karşı: boyut sınırı, şema denetimi, IP başına günlük sınır (IP saklanmaz, özeti tutulur).

const AZAMI_BOYUT = 32 * 1024;
const GUNLUK_SINIR = 20;
const IZINLI = ["sema", "surum", "dil", "os", "kurulum", "donem", "araclar", "onaylar", "dersler"];

function json(veri, durum = 200) {
  return new Response(JSON.stringify(veri, null, 1), { status: durum, headers: { "content-type": "application/json; charset=utf-8" } });
}

async function ozet(metin) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(metin));
  return [...new Uint8Array(b)].slice(0, 8).map((x) => x.toString(16).padStart(2, "0")).join("");
}

function gecerli(v) {
  if (typeof v !== "object" || v === null || Array.isArray(v)) return "nesne değil";
  if (v.sema !== 1) return "şema 1 değil";
  for (const k of Object.keys(v)) if (!IZINLI.includes(k)) return "izinsiz alan: " + k;
  if (typeof v.kurulum !== "string" || !/^[0-9a-f]{32}$/.test(v.kurulum)) return "kurulum kimliği geçersiz";
  if (v.dersler && (!Array.isArray(v.dersler) || v.dersler.length > 50)) return "dersler geçersiz";
  return null;
}

export default {
  async fetch(istek, env) {
    const url = new URL(istek.url);
    if (istek.method === "GET" && url.pathname === "/") {
      return json({ ad: "BÖRÜ geri bildirim", kaynak: "https://github.com/anildagci/boru", gizlilik: "https://github.com/anildagci/boru/blob/main/PRIVACY.md" });
    }
    if (istek.method === "POST" && url.pathname === "/gonder") {
      const govde = await istek.text();
      if (govde.length > AZAMI_BOYUT) return json({ hata: "çok büyük" }, 413);
      let v;
      try { v = JSON.parse(govde); } catch { return json({ hata: "JSON değil" }, 400); }
      const sorun = gecerli(v);
      if (sorun) return json({ hata: sorun }, 400);
      const gun = new Date().toISOString().slice(0, 10).replace(/-/g, "");
      const ip = await ozet((istek.headers.get("cf-connecting-ip") || "?") + gun);
      const sayacAnahtar = "sayac:" + gun + ":" + ip;
      const sayac = parseInt((await env.GERI.get(sayacAnahtar)) || "0", 10);
      if (sayac >= GUNLUK_SINIR) return json({ hata: "günlük sınır" }, 429);
      await env.GERI.put(sayacAnahtar, String(sayac + 1), { expirationTtl: 2 * 86400 });
      v.alindi = new Date().toISOString();
      const anahtar = "kayit:" + gun + ":" + crypto.randomUUID();
      await env.GERI.put(anahtar, JSON.stringify(v));
      return json({ tamam: true, anahtar });
    }
    if (istek.method === "GET" && url.pathname === "/veri") {
      const liste = await env.GERI.list({ prefix: "kayit:" + (url.searchParams.get("gun") || ""), cursor: url.searchParams.get("imlec") || undefined, limit: 100 });
      const kayitlar = [];
      for (const k of liste.keys) kayitlar.push(JSON.parse(await env.GERI.get(k.name)));
      return json({ kayitlar, imlec: liste.list_complete ? null : liste.cursor });
    }
    return json({ hata: "yok" }, 404);
  },
};
