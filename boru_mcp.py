# BÖRÜ'nün MCP sunucusu: Claude Code, Codex ya da MCP konuşan herhangi bir istemci BÖRÜ'nün adımlarını araç olarak çağırır.
# Protokolün gereken kısmı elle yazıldı (JSON-RPC 2.0, satır başına bir ileti, stdin/stdout); dış kütüphane yok.
# Kural: stdout yalnız protokole aittir. Betiklerin ve Blender'ın her çıktısı stderr'e ya da günlüğe gider.
from dil import _
import sys, os, json, time, base64, traceback, threading, re
import bekci, dersler, yontem, model

SURUMLER = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")

TALIMAT = _("""BÖRÜ: 3D model düzenleme kurdu, oldukça detaycıdır. Çizimden oyuna hazır 3B karaktere giden yolu kurulu Blender'la yürütür.

Nasıl çalışılır:
1. Önce boru_basla çağrılır: karakter klasörü ve kip seçilir. Kipleri kullanıcıya sor; kendin seçme.
   - "arac" (araç kipi): yalnız BÖRÜ'nün araçlarıyla çalışılır; BÖRÜ her adımı yapılmadan önce denetler.
   - "hibrit": BÖRÜ'nün araçlarının yanında kendi Blender betiklerini de yazabilirsin; BÖRÜ onları engelleyemez, sonucuna sonradan bakar.
     Kendi betiğini çalıştırdıktan sonra boru_denetle çağır.
   Her iki kipte de BÖRÜ her araç çağrısından önce klasöre bakar (bekçi). Kurala aykırı bir değişiklik bulursa kullanıcıya
   "Devam / Dur" diye sorar; "Dur" derse adım yapılmaz. Bulguları kullanıcıya aktar ve geri almayı kendi başına deneme.
2. Her araç numaralı bulgular, dokunmadıkları, görseller ve önerisiyle yanıt verir. Görsellere bak; bulguları kullanıcıya aktar.
3. Kurallar (kullanıcının): kaynak dosyalara dokunulmaz; onaylı sürümün üstüne yazılmaz; hiçbir deneme silinmez;
   üçgen sayısı ve doku çözünürlüğü azaltılmaz (PC önceliği); sınanmamış şey "çalışıyor" diye sunulmaz.
4. Teslim, üstüne yazma, silme ve kural değiştirme gibi kalıcı işler kullanıcı onayı ister. Bu onayı sen veremezsin:
   BÖRÜ soruyu kendi penceresinde sorar, yanıt yalnız kullanıcının düğmesiyle gelir. Kullanıcı "hayır" derse ya da yanıt
   vermezse aynı işi zorlamak için yeniden çağırma; kullanıcıya nedenini sor.
5. Bir adım üç kez üst üste tutmazsa BÖRÜ bırakır ve elde kalan en iyi denemeyi söyler; zorlamaya devam etme, kullanıcıya sor.
Adımların sırası genelde: boru_incele -> boru_oturt (gözleri kendisi bulur) -> boru_birlestir -> boru_teslim.

Yapay zekâ ile çalışma yardımcısı (her işte, 3B dışında da; klasör gerekmez):
- boru_yontem: gerçek projelerden damıtılmış çalışma kurallarından duruma uyanları getirir. Yeni bir işe başlarken,
  bir karar belirsizken ya da "yapılamaz" demek üzereyken çağır.
- boru_risk: uzun bir işe başlamadan planını ver; emeğin boşa gidebileceği yerleri "önce şunu netleştirmemiz lazım" diye söyler.
  Bulguları kullanıcıya sor; kendin karar verme.
- boru_liste: proje başlangıcı, teslim öncesi kalite, yardımcı ajana iş verme ve görsel inceleme kontrol listeleri.
- boru_profil: kullanıcının kendi bilgisayarında tuttuğu özel çalışma profilini okur (varsa). Bu profil hiçbir yere gönderilmez;
  içeriğini dışarıya (web, depo, geri bildirim) yazma.
- boru_sor: BÖRÜ'nün bu bilgisayarda çalışan küçük modeline (kullanıcı açtıysa) yöntem sorusu sorar; model kapalıysa kurallara döner.
  Yanıtı küçük bir model yazar: kendi yargınla birlikte kullan, kullanıcıya "BÖRÜ'nün yerel modeli şöyle diyor" diye aktar.
- boru_model: yerel modelin durumu. İndirme ve açma yalnız kullanıcının BÖRÜ penceresindeki onayıyla olur; sen karar veremezsin.""")

_n = lambda x: format(int(x), ",").replace(",", ".")


def _ozellik(d, gerekli=()):
    return {"type": "object", "properties": d, "required": list(gerekli)}

S = lambda acik: {"type": "string", "description": acik}
ARACLAR = [
    ("boru_basla", _("Çalışmayı başlatır: karakter klasörünü ve kipi (arac / hibrit) belirler, kuralları ve klasörün durumunu bildirir. "
                   "Kipi kullanıcıya sorarak seç."),
     _ozellik({"klasor": S(_("Karakter çalışma klasörünün mutlak yolu (yoksa açılır)")), "kip": {"type": "string", "enum": ["arac", "hibrit"]}}, ("klasor", "kip"))),
    ("boru_durum", _("Klasörün durumunu söyler: son denemeler, teslim, kip, kaynak dosyalar."), _ozellik({})),
    ("boru_incele", _("Bir GLB modele dokunmadan bakar: üçgen, parça, doku; sekiz açıdan renkli ve kil render. Görsel döner."),
     _ozellik({"model": S(_("GLB dosyasının mutlak yolu"))}, ("model",))),
    ("boru_gozler", _("Modelin yüzünü önden render alır ve iki gözü bulur (hizalama çapası). İşaretli görsel döner."),
     _ozellik({"model": S(_("GLB dosyasının mutlak yolu"))}, ("model",))),
    ("boru_oturt", _("Tek parça baş modelini gövdeye oturtur: gözlerden hizalar, eski başı ve başın kendi giysisini çıkarır, "
                   "yüze/saça/dokuya dokunmaz. Kırmızı (gövde) - yeşil (baş) kontrol render'ı döner. Birkaç dakika sürer."),
     _ozellik({"govde": S(_("Gövde GLB mutlak yolu")), "bas": S(_("Baş GLB mutlak yolu")),
               "renk": {"type": "string", "enum": ["otomatik", "raicon"], "description": _("Renk kuralları. otomatik: tişört yakası gibi; raicon: yüksek ceket yakası (Raicon'a göre ölçülmüş). Verilmezse klasörde kayıtlı olan ya da otomatik.")}},
              ("govde", "bas"))),
    ("boru_birlestir", _("Son oturtmayı tek model ve tek dokuda toplar, dışa aktarır, dosyayı yeniden açıp sayarak doğrular. Teslim etmez."), _ozellik({})),
    ("boru_teslim", _("Son birleştirilmiş modeli teslim eder (önceki teslimi yedekler). Kullanıcıya BÖRÜ penceresinden Evet/Hayır sorar "
                    "ve yanıtı bekler (en çok 10 dakika). Çağırmadan önce kullanıcıya pencereye bakmasını söyle."), _ozellik({})),
    ("boru_kontrol", _("Herhangi bir .blend ya da .glb dosyasını ölçer (parça, üçgen, UV katmanı, malzeme, doku) ve önden/arkadan düz renkli render alır."),
     _ozellik({"dosya": S(_(".blend ya da .glb mutlak yolu"))}, ("dosya",))),
    ("boru_denetle", _("Bekçi: son adımdan beri BÖRÜ dışında ne değiştiğine bakar (kaynak, silinen, üstüne yazılan, yeni dosya); yeni ya da "
                     "değişmiş modelleri ölçüp üçgen ve doku referansıyla karşılaştırır. Kurala aykırıysa kullanıcıya sorar. Hibrit kipte kendi "
                     "betiğinden sonra çağır."), _ozellik({})),
    ("boru_not", _("Deneyim notu düşer (günlüğe). Kullanıcının bir kararı, bir kusurun nedeni, işe yarayan bir yol gibi."),
     _ozellik({"metin": S(_("Not"))}, ("metin",))),
    ("boru_dersler", _("Günlükte tekrar eden durumlardan çıkan ders adaylarını kanıtlarıyla listeler ve raporu yazar. Adaylar BÖRÜ'yü "
                     "değiştirmez; kullanıcı değerlendirir, onaylananlar bir sonraki sürümde uygulanır. 'id' ve 'karar' verilirse karar "
                     "kullanıcıya BÖRÜ penceresinden sorulur; sen karar veremezsin."),
     _ozellik({"id": S(_("Ders adayının kimliği (8 harf)")), "karar": {"type": "string", "enum": ["onayla", "reddet"]},
               "not": S(_("Kararın gerekçesi (kullanıcının sözleriyle)"))})),
    ("boru_yontem", _("Yapay zekâ ile çalışma yöntemi: duruma uyan kuralları (ne zaman, yap, yapma, neden) getirir. 'soru' boşsa kural "
                    "kataloğunu verir; bir kural kimliği (ör. N01) ya da kategori de verilebilir."),
     _ozellik({"soru": S(_("Durum ya da soru, serbest metin (ör. 'yeni proje başlıyorum', 'model yapılamaz diyor')"))})),
    ("boru_risk", _("Plan risk taraması: plan metnindeki silme, üstüne yazma, para, yayın, tahmin, geniş kapsam, kalite azaltma gibi "
                  "işaretleri ve eksik sınama/onay kapılarını bulur; 'önce şunu netleştirmemiz lazım' listesi döner."),
     _ozellik({"plan": S(_("Yapılacak işin planı, serbest metin"))}, ("plan",))),
    ("boru_liste", _("Kontrol listesi: baslangic (proje başlangıcı), teslim (teslim öncesi kalite), yardimci (yardımcı ajana iş verme istemi), "
                   "gorsel (görsel inceleme)."),
     _ozellik({"tur": {"type": "string", "enum": ["baslangic", "teslim", "yardimci", "gorsel"]}}, ("tur",))),
    ("boru_profil", _("Kullanıcının bu bilgisayardaki özel çalışma profilini okur (Belgeler\\BORU\\ozel\\PROFIL.md). Yalnız bu "
                    "oturumda kullan; içeriğini hiçbir yere yazma ya da gönderme."), _ozellik({})),
]
ARACLAR += [
    ("boru_sor", _("Yöntem sorusunu BÖRÜ'nün yerel küçük modeline sorar (kullanıcının bilgisayarında, Ollama ile). Model uygun kuralları ve "
                 "varsa kullanıcının özel profilini okuyup kısa yanıt yazar. Model kapalı ya da yoksa uygun kuralları döner."),
     _ozellik({"soru": S(_("Soru, serbest metin"))}, ("soru",))),
    ("boru_model", _("Yerel küçük modelin durumu (Ollama, indirilmiş mi, açık mı). istek='kur' verilirse kullanıcıya BÖRÜ penceresinden "
                   "indirme/açma onayı sorulur ve yanıt beklenir; 'kapat' modeli kapatır ve ekran kartı belleğinden indirir."),
     _ozellik({"istek": {"type": "string", "enum": ["durum", "kur", "kapat"]}})),
]
KLASORSUZ = ("boru_basla", "boru_not", "boru_denetle", "boru_dersler", "boru_yontem", "boru_risk", "boru_liste", "boru_profil", "boru_sor", "boru_model")


class Sunucu:
    ONAY_SURE = int(os.environ.get("BORU_ONAY_SURE", "600"))   # kullanıcı bu kadar saniyede yanıtlamazsa "hayır" sayılır

    def __init__(self, Motor, Dur, cikis, giris, kuyruk=None):
        self.cikis, self.giris, self.kilit = cikis, giris, threading.Lock()
        self.kuyruk = kuyruk           # kurt penceresi (yoksa None: onay sorulamaz, kalıcı işler yapılmaz)
        self.stderr = sys.stderr       # gerçek stderr: betikler çalışırken sys.stderr yönlendirilir, oraya yazmak döngü kurar
        self.work, self.kip = None, None
        self.mesaj, self.log, self.ilerleme = [], [], None
        self.motor = Motor(self._soyle); self.Dur = Dur

    # ---- protokol
    def yaz(self, d):
        b = (json.dumps(d, ensure_ascii=False) + "\n").encode("utf-8")
        with self.kilit:
            self.cikis.write(b); self.cikis.flush()

    def _soyle(self, tur, metin):
        if self.kuyruk is not None and tur in ("kurt", "mod"):    # kurt penceresi de söylesin
            self.kuyruk.put((tur, metin))
        if tur == "mod":
            return
        (self.mesaj if tur == "kurt" else self.log).append(metin)
        try:
            self.stderr.write((_("[BÖRÜ] ") if tur == "kurt" else "") + metin + "\n"); self.stderr.flush()
        except Exception:
            pass
        if tur == "kurt" and self.ilerleme is not None:          # uzun adımlarda istemciye ara haber
            self.adim += 1
            self.yaz({"jsonrpc": "2.0", "method": "notifications/progress",
                      "params": {"progressToken": self.ilerleme, "progress": self.adim, "message": metin.split("\n")[0]}})

    def calis(self):
        for satir in self.giris:
            satir = satir.strip()
            if not satir:
                continue
            try:
                m = json.loads(satir.decode("utf-8"))
            except Exception:
                self.yaz({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}); continue
            for ileti in (m if isinstance(m, list) else [m]):
                self.isle(ileti)

    def isle(self, m):
        yontem, kimlik = m.get("method"), m.get("id")
        if kimlik is None:                                     # bildirim: yanıt verilmez
            return
        try:
            if yontem == "initialize":
                istenen = (m.get("params") or {}).get("protocolVersion")
                sonuc = {"protocolVersion": istenen if istenen in SURUMLER else SURUMLER[0],
                         "capabilities": {"tools": {"listChanged": False}},
                         "serverInfo": {"name": "boru", "title": _("BÖRÜ"), "version": self.surum},
                         "instructions": TALIMAT}
            elif yontem == "ping":
                sonuc = {}
            elif yontem == "tools/list":
                sonuc = {"tools": [{"name": a, "description": d, "inputSchema": s} for a, d, s in ARACLAR]}
            elif yontem == "tools/call":
                p = m.get("params") or {}
                self.ilerleme = (p.get("_meta") or {}).get("progressToken"); self.adim = 0
                try:
                    sonuc = self.cagir(p.get("name"), p.get("arguments") or {})
                finally:
                    self.ilerleme = None
            else:
                self.yaz({"jsonrpc": "2.0", "id": kimlik, "error": {"code": -32601, "message": _("bilinmeyen yöntem: %s") % yontem}}); return
            self.yaz({"jsonrpc": "2.0", "id": kimlik, "result": sonuc})
        except Exception as ex:
            self.stderr.write(traceback.format_exc())
            self.yaz({"jsonrpc": "2.0", "id": kimlik, "error": {"code": -32603, "message": str(ex)}})

    # ---- araçlar
    def cagir(self, ad, a):
        self.mesaj, self.log = [], []; t0 = time.time(); gorsel, hata = [], False; temiz = False
        try:
            fn = getattr(self, "_" + ad[5:]) if ad and ad.startswith("boru_") else None
            if not fn:
                raise self.Dur(_("Böyle bir aracım yok: %s") % ad)
            if self.work and ad not in KLASORSUZ:
                if not self._bekci_on():                        # ihlal var ve kullanıcı devam demedi: adım yapılmaz
                    raise self.Dur(_("Bu adımı (%s) yapmadım.") % ad)
            temiz = bool(self.work)
            gorsel = fn(a) or []
            hata = bool(getattr(self, "_basarisiz", False)); self._basarisiz = False
        except self.Dur as ex:
            self.mesaj.append(str(ex)); hata = True
        except Exception as ex:
            self.mesaj.append(_("Beklenmedik hata: %s: %s") % (type(ex).__name__, ex)); self.log.append(traceback.format_exc()); hata = True
        if temiz and ad not in KLASORSUZ and self.work:
            try:                                                 # BÖRÜ'nün kendi yaptıkları yeni an olur; yalnız dışarıdan yapılanlar yakalanır
                bekci.yaz(self.work, bekci.tara(self.work, bekci.oku(self.work)))
            except Exception as ex:
                self.log.append(_("bekçi anı yazılamadı: %s") % ex)
        metin = "\n\n".join(self.mesaj) or _("(BÖRÜ bir şey söylemedi)")
        if hata and self.log:
            metin += _("\n\nSon günlük satırları:\n") + "\n".join(l for l in self.log[-8:] if l.strip())
        icerik = [{"type": "text", "text": metin}]
        for yol in gorsel:
            icerik += self._gorsel(yol)
        self._gunluk({"arac": ad, "arg": a, "hata": hata, "sure": round(time.time() - t0, 1), "yanit": "(özel profil: günlüğe yazılmaz)" if ad == "boru_profil" else metin[:2000],
                      "neden": dersler._neden({"yanit": metin}) if hata else None,
                      "gorsel": gorsel})
        return {"content": icerik, "isError": hata}

    def _gorsel(self, yol, en=1400):
        """Görseli küçültmeden, gerekirse yalnız sığdırarak gönderir; yolunu da yazar."""
        try:
            import cv2
            g = cv2.imread(yol)
            if g is None:
                return []
            h, w = g.shape[:2]; k = min(1.0, en / max(h, w))
            if k < 1.0:
                g = cv2.resize(g, (int(w * k), int(h * k)), interpolation=cv2.INTER_AREA)
            ok, b = cv2.imencode(".png", g)
            return [{"type": "text", "text": _("Görsel: %s%s") % (yol, _(" (sığdırmak için %%%d boyutta)") % round(k * 100) if k < 1 else "")},
                    {"type": "image", "data": base64.b64encode(b.tobytes()).decode("ascii"), "mimeType": "image/png"}]
        except Exception as ex:
            return [{"type": "text", "text": _("Görseli ekleyemedim (%s): %s") % (ex, yol)}]

    def _gunluk(self, kayit):
        kayit = dict(kayit, zaman=time.strftime("%Y-%m-%d %H:%M:%S"), klasor=self.work, kip=self.kip, oturum=self.oturum,
                     surum=self.surum, sinama=self.sinama or None)
        yollar = [os.path.join(dersler.GUNLUK, time.strftime("%Y-%m") + ".jsonl")]
        if self.work and os.path.isdir(self.work):
            yollar.append(os.path.join(self.work, "boru_gunluk.jsonl"))
        for y in yollar:
            try:
                os.makedirs(os.path.dirname(y), exist_ok=True)
                with open(y, "a", encoding="utf-8") as f:
                    f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
            except Exception:
                pass

    # ---- bekçi
    def _bekci_bul(self, olc=False):
        """Son andan beri BÖRÜ dışında ne değişti. Döner: (yeni an, bulgular, ölçümler)."""
        eski = bekci.oku(self.work)
        yeni = bekci.tara(self.work, eski)
        if eski is None:
            return yeni, [], []
        f = bekci.fark(eski, yeni); bulgu = bekci.siniflandir(f, self.kip)
        olcum = []
        if olc:
            d = self.motor.durum(self.work); ref_u, ref_d = d.get("ucgen_ref"), d.get("doku_ref")
            for r in bekci.olculecek(f):
                s = self._say(os.path.join(self.work, r))
                if not s:
                    bulgu.append(("uyari", _("Ölçemedim: %s") % r)); continue
                olcum.append((r, s))
                if ref_u and s["ucgen"] < ref_u * 0.99:
                    bulgu.append(("ihlal", _("Üçgen sayısı düştü: %s %s üçgen, son onaylı oturtma/birleştirme %s (%%%d). PC kuralı: üreticinin sayısı korunur.")
                                  % (r, _n(s["ucgen"]), _n(ref_u), round(100.0 * s["ucgen"] / ref_u))))
                if ref_d and 0 < s["doku"] < ref_d:
                    bulgu.append(("ihlal", _("Doku küçüldü: %s en büyük renk dokusu %d piksel, son birleştirmede %d.") % (r, s["doku"], ref_d)))
                if r.startswith("Exports/") and r.lower().endswith((".fbx", ".glb")) and (s["parca"] != 1 or s["malzeme"] != 1 or s["uv"] != 1):
                    bulgu.append(("uyari", _("Dışa aktarılan dosya tek parça/tek malzeme/tek UV değil: %s (%d parça, %d malzeme, %d UV)") % (r, s["parca"], s["malzeme"], s["uv"])))
        return yeni, bulgu, olcum

    def _say(self, yol):
        try:
            glb = not yol.lower().endswith(".blend")
            satir = self.motor.blender(None if glb else yol, "say.py", ["olc"] + ([yol] if glb else []), env={"SAY_RENDER": "0"})
        except self.Dur:
            return None
        m = next((re.search(r"SAYI parca (\d+) ucgen (\d+) uv (\d+) malzeme (\d+) doku (\d+)", l) for l in satir if l.startswith("SAYI")), None)
        return dict(zip(("parca", "ucgen", "uv", "malzeme", "doku"), map(int, m.groups()))) if m else None

    def _bekci_karar(self, yeni, bulgu, baslik):
        """Bulguları yazar; ihlal varsa kullanıcıya sorar. True: devam (an güncellenir)."""
        if not bulgu:
            bekci.yaz(self.work, yeni); return True
        sev = {"ihlal": _("İHLAL"), "uyari": _("uyarı"), "bilgi": _("bilgi")}
        metin = baslik + "\n" + "\n".join("%d. [%s] %s" % (i + 1, sev[s], m) for i, (s, m) in enumerate(bulgu))
        ihlal = [m for s, m in bulgu if s == "ihlal"]
        if not ihlal:
            self.mesaj.append(metin); bekci.yaz(self.work, yeni); return True
        if self.kuyruk is None:
            self.mesaj.append(metin + _("\nKurala aykırı değişiklik var ve kullanıcıya soracağım pencere açık değil: durdum.")); return False
        cevap = self.onay(_("Bekçi: kurallara aykırı değişiklik buldum (BÖRÜ dışında yapılmış).\n\n") +
                          "\n".join("• " + m for m in ihlal[:6]) + (_("\n• ... (%d tane daha)") % (len(ihlal) - 6) if len(ihlal) > 6 else "") +
                          _("\n\nHiçbir şeyi geri almadım, silmedim.\nModel çalışmaya devam etsin mi?"), (_("Devam"), _("Dur")), tur="bekci")
        if cevap != _("Devam"):
            self.mesaj.append(metin + _("\nKullanıcı %s. Durdum. Kullanıcıya bu değişiklikleri kimin, neden yaptığını sor; geri alınması gerekiyorsa "
                              "kullanıcının kararıyla yapılır.") % (_("'Dur' dedi") if cevap else _("yanıt vermedi")))
            return False
        self.mesaj.append(metin + _("\nKullanıcı bunları gördü ve 'Devam' dedi."))
        bekci.yaz(self.work, yeni); return True

    def _bekci_on(self):
        yeni, bulgu, _x = self._bekci_bul()
        return self._bekci_karar(yeni, bulgu, _("Bekçi: son adımdan beri BÖRÜ dışında şunlar değişti:"))

    def _denetle(self, a):
        work = self._klasor(); yeni, bulgu, olcum = self._bekci_bul(olc=True)
        olc_m = "\n".join(_("- %s: %d parça, %s üçgen, %d UV, %d malzeme, en büyük renk dokusu %d") % (r, s["parca"], _n(s["ucgen"]), s["uv"], s["malzeme"], s["doku"]) for r, s in olcum)
        d = self.motor.durum(work)
        temel = (_("Denetledim (%s kipi). Referans: %s üçgen, doku %s.%s") % (self.kip, _n(d["ucgen_ref"]) if d.get("ucgen_ref") else "yok",
                 d.get("doku_ref", _("yok")), (_("\nÖlçtüklerim:\n") + olc_m) if olc_m else ""))
        if not bulgu:
            self.mesaj.append(temel + _("\nSon adımdan beri BÖRÜ dışında bir değişiklik yok; kurallara aykırı bir şey görmedim.")); bekci.yaz(work, yeni); return
        self.mesaj.append(temel)
        if not self._bekci_karar(yeni, bulgu, _("Bulgular:")):
            self._basarisiz = True

    def _sure(self):
        return _("%d dakika") % (self.ONAY_SURE // 60) if self.ONAY_SURE >= 60 else _("%d saniye") % self.ONAY_SURE

    def onay(self, metin, secenekler=(_("Evet"), _("Hayır")), tur="diger"):
        """Kullanıcıya kurt penceresinden sorar ve yanıtı bekler. Model bu yanıtı veremez: soru yalnız pencerede görünür,
        yanıt yalnız düğmeyle gelir. Döner: seçilen seçenek, ya da None (pencere yok / süre doldu)."""
        if self.kuyruk is None:
            return None
        soru = {"metin": metin, "secenekler": list(secenekler), "olay": threading.Event(), "cevap": None}
        self.kuyruk.put(("sor", soru))
        if self.ilerleme is not None:
            self.adim += 1
            self.yaz({"jsonrpc": "2.0", "method": "notifications/progress",
                      "params": {"progressToken": self.ilerleme, "progress": self.adim, "message": _("Kullanıcının onayını bekliyorum (BÖRÜ penceresi).")}})
        if not soru["olay"].wait(self.ONAY_SURE):
            self.kuyruk.put(("sor_iptal", soru))
        self._gunluk({"onay": metin, "onay_tur": tur, "cevap": soru["cevap"], "secenekler": list(secenekler)})
        return soru["cevap"]

    def _klasor(self):
        if not self.work:
            raise self.Dur(_("Önce boru_basla ile karakter klasörünü ve kipi seçmek gerekiyor."))
        return self.work

    def _yap(self, ad, fn, *args):
        """Motor adımını yürütür. Motor hatayı kendi söyler ve None döner."""
        sonuc = self.motor.calistir(ad, fn, *args)
        if sonuc is None:
            self._basarisiz = True
        return sonuc

    @staticmethod
    def _glb(yol):
        if not yol or not os.path.isfile(yol):
            raise Sunucu.DurYok(_("Dosyayı bulamadım: %s") % yol)
        if not yol.lower().endswith(".glb"):
            raise Sunucu.DurYok(_("Şimdilik yalnız .glb okuyorum: %s") % yol)
        return yol

    def _basla(self, a):
        work = os.path.abspath(a.get("klasor", "")); kip = a.get("kip")
        if kip not in ("arac", "hibrit"):
            raise self.Dur(_("Kip 'arac' ya da 'hibrit' olmalı. Kullanıcıya sor."))
        yeni = not os.path.isdir(work)
        self.motor.hazirla(work); self.work, self.kip = work, kip
        d = self.motor.durum(work, {"kip": kip})
        kaynak = sorted(os.listdir(os.path.join(work, "Source")))
        satir = [_("Başladım: %s (%s).") % (work, _("yeni klasör açtım") if yeni else _("var olan klasör")),
                 _("1. Kip: %s.") % (_("araç kipi: yalnız benim araçlarımla çalışacağız; her adımı yapmadan önce denetlerim") if kip == "arac" else
                                  _("hibrit: kendi Blender betiklerini de yazabilirsin. Onları engelleyemem; sonucuna sonradan bakarım. "
                                  "Kendi betiğini çalıştırdıktan sonra boru_denetle çağır; her araç çağrısından önce de kendiliğimden bakarım")),
                 _("2. Kaynak dosyalar: %s.") % (", ".join(kaynak) if kaynak else _("yok (araçlar verdiğin dosyayı Source altına kopyalar; aslına dokunmam)")),
                 _("3. Son durum: oturtma %s, birleştirme %s, teslim %s, renk kuralı %s.") % (d.get("graft", _("yok")), d.get("atlas", _("yok")), d.get("teslim", _("yok")), d.get("renk", "otomatik")),
                 _("4. Kurallar: kaynaklara dokunmam, onaylı sürümün üstüne yazmam, deneme silmem, üçgen ve doku azaltmam. "
                 "Teslim gibi kalıcı işleri kullanıcıya sorarım."),
                 (_("5. Kullanıcıya soru penceresi açık: teslim ve kural değişikliklerini kullanıcı BÖRÜ penceresinden onaylar. "
                  "Onay sorarken yanıt gelene kadar beklerim (en çok %s); kullanıcıya pencereye bakmasını söyle.") % self._sure())
                 if self.kuyruk is not None else
                 _("5. Penceresiz çalışıyorum: kullanıcıya soramam, bu yüzden teslim ve kural değişikliği yapmam.")]
        self.mesaj.append("\n".join(satir))
        if bekci.oku(work) is None:
            bekci.yaz(work, bekci.tara(work))
            self.mesaj.append(_("Bekçi: klasörün anını aldım (kaynakların içerik özeti, denemeler, teslim). Bundan sonra BÖRÜ dışında yapılan "
                              "değişiklikleri her adımda görürüm; kurala aykırıysa kullanıcıya sorarım."))
        elif not self._bekci_karar(*self._bekci_bul()[:2], baslik=_("Bekçi: önceki oturumdan beri BÖRÜ dışında şunlar değişti:")):
            self._basarisiz = True

    def _durum(self, a):
        work = self._klasor(); d = self.motor.durum(work)
        self.mesaj.append(_("Klasör: %s\nKip: %s\nDurum: %s") % (work, self.kip, json.dumps(d, ensure_ascii=False, indent=1)))

    def _incele(self, a):
        work = self._klasor(); cikti = self._yap("incele", self.motor.incele, work, self._glb(a.get("model")))
        if not cikti:
            return []
        return [self._izgara(cikti, ["m_a000", "m_a045", "m_a090", "m_a180"], "inceleme_renkli.png", 2),
                self._izgara(cikti, ["m_clay000", "m_clay045", "m_clay090", "m_clay180"], "inceleme_kil.png", 2)]

    def _gozler(self, a):
        work = self._klasor(); glb = self._glb(a.get("model")); ad = self.motor.kaynaga_al(work, glb)
        j = self._yap("gozler", self.motor.gozler, work, ad)
        if not j:
            return []
        g = json.load(open(j, encoding="utf-8")); kok = os.path.splitext(ad)[0]
        self.mesaj.append(_("İki gözü buldum (%s).\n1. Sol göz x %.4f, z %.4f; sağ göz x %.4f, z %.4f (dünya birimi).\n2. Gözler arası %.4f.\n"
                          "3. Başka aday %s.\n4. Modele dokunmadım; yalnız önden render aldım.\nİşaretli görselde yeşil halkalar gözlerin üstünde mi, bak.")
                          % (kok, g["sol"][0], g["sol"][1], g["sag"][0], g["sag"][1], g["sag"][0] - g["sol"][0], _("de vardı; en iyi eşi seçtim") if g.get("baska_aday") else "yoktu"))
        return [os.path.join(work, "Renders", "gozler", kok + "_goz.png")]

    def _oturt(self, a):
        work = self._klasor(); eski = self.motor.durum(work).get("renk")
        if a.get("renk") and a["renk"] != (eski or "otomatik"):
            if eski:                                   # kayıtlı bir kural değişecek: kural değişikliği kullanıcıya sorulur
                cevap = self.onay(_("Model, bu klasörün renk kuralını değiştirmek istiyor: '%s' yerine '%s'.\n\n"
                                  "otomatik: tişört yakası gibi alçak yakalar. raicon: yüksek ceket yakası (Raicon'a göre ölçüldü).\n"
                                  "Yanlış kural yakayı bozar.\n\nDeğiştireyim mi?") % (eski, a["renk"]), tur="renk")
                if cevap != _("Evet"):
                    self._basarisiz = True
                    self.mesaj.append(_("Renk kuralını değiştirmedim ('%s' kaldı): kullanıcı %s. Oturtmayı da yapmadım.")
                                      % (eski, _("'Hayır' dedi") if cevap else _("yanıt vermedi"))); return []
            self.motor.durum(work, {"renk": a["renk"]})
        on = self._yap("oturt", self.motor.oturt, work, self._glb(a.get("govde")), self._glb(a.get("bas")))
        if not on:
            return []
        d = self.motor.durum(work)             # bekçinin referansı: bu sayının altına düşen bir model "üçgen azaldı" sayılır
        if d.get("govde_ucgen") and d.get("bas_ucgen"):
            self.motor.durum(work, {"ucgen_ref": d["govde_ucgen"] + d["bas_ucgen"]})
        kok = on[:-len("_front.png")]          # her görünüş ayrı ve tam boyutta: yaka kusurları küçültülünce seçilmiyor
        return [kok + "_" + v + ".png" for v in ("front", "side", "back")]

    def _birlestir(self, a):
        work = self._klasor()
        if self._yap("birlestir", self.motor.birlestir, work):
            ref = {}
            if self.motor.durum(work).get("birlesik_ucgen"):
                ref["ucgen_ref"] = self.motor.durum(work)["birlesik_ucgen"]
            try:
                from PIL import Image
                ref["doku_ref"] = max(Image.open(os.path.join(work, "Textures", "Model_BaseColor_%s.png" % self.motor.durum(work)["doku"])).size)
            except Exception:
                pass
            self.motor.durum(work, ref)
        return []

    def _teslim(self, a):
        work = self._klasor(); d = self.motor.durum(work); ad = os.path.basename(work.rstrip("/\\")); at = d.get("atlas")
        if not at:
            raise self.Dur(_("Teslim edilecek birleştirilmiş model yok. Önce boru_birlestir."))
        if self.kuyruk is None:
            raise self.Dur(_("Teslim etmedim: kullanıcıya soracağım pencere açık değil (BÖRÜ penceresiz çalışıyor). Teslim kullanıcı onayı ister."))
        eski = [f for f in ("Blender/%s_Final_Master.blend" % ad, "Exports/%s_Mixamo_Upload.fbx" % ad, "Exports/%s_Preview.glb" % ad,
                            "Textures/%s_BaseColor_Final.png" % ad) if os.path.exists(os.path.join(work, f))]
        soru = (_("Model, %s karakterini teslim etmek istiyor.\n\nDeneme: %s (oturtma %s).\nŞunlar yazılacak: %s_Final_Master.blend, "
                "%s_Mixamo_Upload.fbx, %s_Preview.glb, %s_BaseColor_Final.png.\n%s\nDenemelerin hiçbiri silinmeyecek.\n\nTeslim edeyim mi?")
                % (ad, at, d.get("graft", "?"), ad, ad, ad, ad,
                   (_("Önceki teslim (%s) Backups altına yedeklenip yerine yenisi konacak.") % d.get("teslim", "?")) if eski else _("Önceki teslim yok.")))
        cevap = self.onay(soru, tur="teslim")
        if cevap != _("Evet"):
            self._basarisiz = True
            self.mesaj.append(_("Teslim etmedim: kullanıcı %s.\nHiçbir dosyaya dokunmadım. Kullanıcıya nedenini ya da neyin değişmesini istediğini sor.")
                              % (_("'Hayır' dedi") if cevap else _("%s içinde yanıt vermedi") % self._sure()))
            return []
        self.mesaj.append(_("Kullanıcı BÖRÜ penceresinden 'Evet' dedi (%s).") % time.strftime("%H:%M:%S"))
        self._yap("teslim", self.motor.teslim, work); return []

    def _kontrol(self, a):
        work = self._klasor(); yol = a.get("dosya", "")
        if not os.path.isfile(yol) or not yol.lower().endswith((".blend", ".glb")):
            raise self.Dur(_("Ölçmek için var olan bir .blend ya da .glb dosyası gerekiyor: %s") % yol)
        kok = os.path.splitext(os.path.basename(yol))[0]; cikti = os.path.join(work, "Renders", "kontrol", "olc_" + kok)
        glb = yol.lower().endswith(".glb")
        satir = self.motor.blender(None if glb else yol, "say.py", [cikti] + ([yol] if glb else []))
        bulgu = [l[4:] for l in satir if l.startswith("SAY ")]
        self.mesaj.append(_("Dosyayı ölçtüm, dokunmadım: %s\n%s\nÖnden ve arkadan düz renkli render aldım (gölgelendirici yok; dokunun kendisi görünür).")
                          % (os.path.basename(yol), "\n".join("%d. %s" % (i + 1, b) for i, b in enumerate(bulgu)) or _("Ölçüm satırı çıkmadı.")))
        return [cikti + "_front.png", cikti + "_back.png"]

    def _dersler(self, a):
        yol, A = dersler.rapor()
        if a.get("id") or a.get("karar"):
            hedef = next((x for x in A if x["id"] == a.get("id")), None)
            if not hedef or a.get("karar") not in ("onayla", "reddet"):
                raise self.Dur(_("Karar için var olan bir ders kimliği ve 'onayla' ya da 'reddet' gerekiyor."))
            if self.kuyruk is None:
                raise self.Dur(_("Kararı kaydetmedim: kullanıcıya soracağım pencere açık değil."))
            cevap = self.onay(_("Model, şu ders adayını %s istiyor:\n\n%s\n(%d kanıt; tür: %s)\nÖneri: %s%s\n\n%s?")
                              % (_("onaylamak") if a["karar"] == "onayla" else _("reddetmek"), hedef["baslik"], len(hedef["kanit"]), hedef["tur"],
                                 hedef["oneri"], (_("\nGerekçe: ") + a["not"]) if a.get("not") else "",
                                 _("Onaylanırsa bir sonraki sürümde uygulanacak. Onaylıyor musun") if a["karar"] == "onayla" else _("Reddediyor musun")),
                              tur="ders")
            if cevap != _("Evet"):
                self._basarisiz = True
                self.mesaj.append(_("Kararı kaydetmedim: kullanıcı %s.") % (_("'Hayır' dedi") if cevap else _("yanıt vermedi"))); return []
            dersler.karar_yaz(hedef["id"], _("onaylandı") if a["karar"] == "onayla" else _("reddedildi"), a.get("not", ""))
            yol, A = dersler.rapor()
            self.mesaj.append(_("Kullanıcı onayladı; kararı kaydettim: [%s] %s → %s.") % (hedef["id"], hedef["baslik"], _("onaylandı") if a["karar"] == "onayla" else _("reddedildi")))
        yeni = [x for x in A if x["karar"] == "yeni"]
        satir = [_("Ders adayları: %d (%d yeni). Rapor: %s") % (len(A), len(yeni), yol),
                 _("Bunlar BÖRÜ'yü kendiliğinden değiştirmez; kullanıcı değerlendirir, onaylananlar bir sonraki sürümde uygulanır.")]
        for i, x in enumerate(A[:12]):
            satir.append(_("%d. [%s] %s — %d kanıt, karar: %s%s\n   Öneri: %s") % (i + 1, x["id"], x["baslik"], len(x["kanit"]), x["karar"],
                                                                         _(" (kanıtların %%%d'i sınama kaydı)") % round(100 * x["sinama_orani"]) if x["sinama_orani"] else "", x["oneri"]))
        if len(A) > 12:
            satir.append(_("... ve %d aday daha (raporda).") % (len(A) - 12))
        self.mesaj.append("\n".join(satir)); return []

    # ---- yapay zekâ ile çalışma yardımcısı (klasör gerekmez)
    def _yontem(self, a):
        soru = (a.get("soru") or "").strip()
        if not yontem.kurallar():
            raise self.Dur(_("Kural dosyasını (bilgi/kurallar.json) bulamadım."))
        if not soru:
            self.mesaj.append(_("Kural kataloğu (bir kimlik ya da durum yazarak ayrıntısını iste):\n") + yontem.katalog()); return []
        b = yontem.bul(soru)
        if not b:
            self.mesaj.append(_("Bu duruma doğrudan uyan bir kural bulamadım. Katalog:\n") + yontem.katalog()); return []
        self.mesaj.append(_("Duruma uyan kurallar (en uygunu ilk sırada):") + "\n\n" + "\n\n".join(
            "%d. %s" % (i + 1, yontem.yaz(k, kisa=i > 0)) for i, (_p, k) in enumerate(b)))
        return []

    def _risk(self, a):
        plan = (a.get("plan") or "").strip()
        if not plan:
            raise self.Dur(_("Bir plan metni ver."))
        b = yontem.risk(plan)
        if not b:
            self.mesaj.append(_("Planda belirgin bir risk işareti görmedim. Yine de teslimden önce boru_liste teslim ile bak.")); return []
        self.mesaj.append(_("Önce şunları netleştirmemiz lazım (kullanıcıya sor; kendin karar verme):") + "\n" +
                          "\n".join("%d. %s (%s)" % (i + 1, m, kid) for i, (kid, m) in enumerate(b)) +
                          _("\n\nAyrıntı için boru_yontem'e kural kimliğini ver."))
        self._model_ek(_("Bu planda, yukarıdakilere ek olarak, başlamadan önce kullanıcıya sorulması gereken en çok 3 netleştirme sorusu ne? "
                         "Yalnız soruları madde madde yaz.\n\nPLAN:\n") + plan)
        return []

    def _model_ek(self, soru):
        """Yerel model açık ve hazırsa onun yanıtını ayrı bir bölüm olarak ekler (kapalıysa sessiz geçer)."""
        try:
            if not model.durum()["hazir"]:
                return
            y, _k, sn = model.sor(soru, sure=120)
            if y:
                self.mesaj.append(_("BÖRÜ'nün yerel modeli (%s, %s sn; küçük bir model, kendi yargınla kullan):\n") % (model.ayar()["ad"], sn) + y)
        except Exception as ex:
            self.log.append(_("yerel model yanıt vermedi: %s") % ex)

    def _sor(self, a):
        soru = (a.get("soru") or "").strip()
        if not soru:
            raise self.Dur(_("Bir soru ver."))
        d = model.durum()
        if d["hazir"]:
            try:
                y, kim, sn = model.sor(soru)
                self.mesaj.append(_("BÖRÜ'nün yerel modeli (%s, %s sn; dayandığı kurallar: %s). Küçük bir model: kendi yargınla birlikte kullan.\n\n")
                                  % (d["model"], sn, ", ".join(kim) or "-") + y)
                return []
            except Exception as ex:
                self.mesaj.append(_("Yerel model yanıt vermedi (%s); kurallara bakıyorum.") % ex)
        else:
            self.mesaj.append(_("Yerel model kullanılmıyor (%s). Kurallara bakıyorum.") % self._model_neden(d))
        b = yontem.bul(soru)
        self.mesaj.append("\n\n".join("%d. %s" % (i + 1, yontem.yaz(k, kisa=i > 0)) for i, (_p, k) in enumerate(b))
                          if b else _("Bu duruma doğrudan uyan bir kural bulamadım. Katalog:\n") + yontem.katalog())
        return []

    @staticmethod
    def _model_neden(d):
        if not d["sunucu"]:
            return _("Ollama bu bilgisayarda çalışmıyor; kullanıcı %s adresinden kurabilir") % model.OLLAMA_INDIR
        if not d["indirilmis"]:
            return _("%s indirilmemiş") % d["model"]
        return _("kullanıcı yerel modeli kapalı tutuyor")

    def _model(self, a):
        istek = a.get("istek") or "durum"; d = model.durum()
        if istek == "kapat":
            model.ayar_yaz(acik=False); model.bosalt()
            self.mesaj.append(_("Yerel modeli kapattım ve ekran kartı belleğinden indirdim.")); return []
        if istek == "kur" and not d["hazir"]:
            if not d["sunucu"]:
                raise self.Dur(_("Ollama bu bilgisayarda çalışmıyor. Kullanıcı %s adresinden kurmalı (BÖRÜ program kurmaz); sonra yeniden dene.") % model.OLLAMA_INDIR)
            if self.kuyruk is None:
                raise self.Dur(_("Kullanıcıya soracağım pencere açık değil; yerel modeli kurmadım."))
            ad, gb, lis = model.MODELLER.get(d["model"], (d["model"], "?", "?"))
            metin = (_("Model, BÖRÜ'nün yerel küçük modelini açmak istiyor.\n\n%s (lisans %s) %sbu bilgisayarda çalışacak; ekran kartını yalnız "
                       "soru sorulunca kullanır. Hiçbir şey dışarı gönderilmez.\n\nOnaylıyor musun?")
                     % (ad, lis, "" if d["indirilmis"] else _("Ollama ile indirilip (~%s GB) ") % gb))
            if self.onay(metin, tur="model") != _("Evet"):
                self._basarisiz = True
                self.mesaj.append(_("Yerel modeli kurmadım: kullanıcı onaylamadı.")); return []
            if not d["indirilmis"]:
                self._soyle("kurt", _("%s indiriliyor…") % ad)
                son = [-10]

                def haber(y, durum):             # yanıtı doldurmasın: yalnız her %10'da bir haber
                    if y is None or y >= son[0] + 10:
                        son[0] = y if y is not None else son[0]
                        self._soyle("kurt", _("İndiriyorum: %s%s") % (durum, " %%%d" % y if y is not None else ""))
                model.indir(haber)
            model.ayar_yaz(acik=True); d = model.durum()
        self.mesaj.append(_("Yerel model: %s\n1. Ollama: %s\n2. Model: %s (%s)\n3. Açık: %s\n4. Hazır: %s")
                          % (_("hazır") if d["hazir"] else self._model_neden(d), d["sunucu"] or _("yok"), d["model"],
                             _("indirilmiş") if d["indirilmis"] else _("indirilmemiş"), _("evet") if d["acik"] else _("hayır"),
                             _("evet") if d["hazir"] else _("hayır")))
        return []

    def _liste(self, a):
        L = yontem.LISTELER.get(a.get("tur"))
        if not L:
            raise self.Dur(_("Tür şunlardan biri olmalı: %s") % ", ".join(yontem.LISTELER))
        baslik, maddeler = L["en" if yontem.DIL == "en" else "tr"]
        self.mesaj.append(baslik + "\n" + "\n".join("[ ] " + m for m in maddeler)); return []

    def _profil(self, a):
        if not os.path.isfile(yontem.PROFIL):
            self.mesaj.append(_("Özel profil yok (%s). Kullanıcı isterse kendi çalışma tarzını bu dosyaya yazabilir; dosya bu bilgisayardan çıkmaz.") % yontem.PROFIL)
            return []
        self.mesaj.append(_("Kullanıcının özel profili (yalnız bu oturumda kullan, hiçbir yere yazma):\n\n") +
                          open(yontem.PROFIL, encoding="utf-8").read()[:12000]); return []

    def _not(self, a):
        self._gunluk({"not": a.get("metin", "")}); self.mesaj.append(_("Notu günlüğe yazdım."))

    def _izgara(self, klasor, adlar, cikti, sutun):
        """Birkaç render'ı tek görselde yan yana toplar (her biri aynı boyutta; büyütme yok)."""
        import cv2, numpy as np
        g = [cv2.imread(os.path.join(klasor, a + ".png")) for a in adlar]; g = [x for x in g if x is not None]
        if not g:
            return os.path.join(klasor, adlar[0] + ".png")
        h = min(x.shape[0] for x in g); g = [cv2.resize(x, (int(x.shape[1] * h / x.shape[0]), h), interpolation=cv2.INTER_AREA) if x.shape[0] != h else x for x in g]
        w = max(x.shape[1] for x in g); g = [np.hstack([x, np.zeros((h, w - x.shape[1], 3), np.uint8)]) if x.shape[1] < w else x for x in g]
        while len(g) % sutun:
            g.append(np.zeros_like(g[0]))
        satirlar = [np.hstack(g[i:i + sutun]) for i in range(0, len(g), sutun)]
        yol = os.path.join(klasor, cikti); cv2.imwrite(yol, np.vstack(satirlar)); return yol


def baslat(Motor, Dur, surum, pencere=None, sinama=None):
    """stdout'u protokole ayırır, geri kalan her çıktıyı stderr'e yönlendirir ve sunucuyu çalıştırır.
    pencere verilirse kurt penceresi ana iş parçacığında açılır (onay soruları oradan sorulur), sunucu ayrı iş parçacığında koşar.
    İstemci bağlantıyı kapatınca (stdin biter) pencere de kapanır."""
    import queue
    cikis = sys.stdout.buffer if sys.stdout else os.fdopen(1, "wb")
    giris = sys.stdin.buffer if sys.stdin else os.fdopen(0, "rb")
    hata = sys.stderr if sys.stderr else open(os.devnull, "w", encoding="utf-8")
    sys.stdout = hata; sys.stderr = hata
    Sunucu.DurYok = Dur
    kuyruk = queue.Queue() if pencere else None
    s = Sunucu(Motor, Dur, cikis, giris, kuyruk); s.surum = surum; s._basarisiz = False; s.sinama = bool(sinama); s.oturum = time.strftime("%Y%m%d_%H%M%S")
    if not pencere:
        s.calis(); return 0

    def koş():
        try:
            s.calis()
        finally:
            kuyruk.put(("kapat", None))
    threading.Thread(target=koş, daemon=True).start()
    pencere(mcp={"kuyruk": kuyruk}, sinama=sinama)
    return 0
