# Canlı kurt: Claude Code'un kancaları (hooks) BÖRÜ'ye her hareketi haber verir, kurt buna göre tepki verir.
# Bu ilk sürüm yalnız İZLER: hiçbir işlemi durdurmaz, hiçbir karar dönmez (yanıt her zaman boş "{}").
# Yol: Claude Code "http" kancası -> http://127.0.0.1:<PORT>/kanca (yalnız bu bilgisayar) -> kuyruk -> kurt.
# BÖRÜ kapalıysa Claude Code'un isteği ulaşmaz; Claude Code bunu engel saymaz, işine devam eder.
# Günlük: Belgeler\BORU\kanca_gunlugu.jsonl (yalnız bu bilgisayarda; olay türü, araç adı, kısa özet). Sınama listesi için de kullanılır.
from dil import _
import os, re, json, time, threading, shutil

PORT = int(os.environ.get("BORU_KANCA_PORT") or 47391)
YOL = "/kanca"
OLAYLAR = ("UserPromptSubmit", "PreToolUse", "Notification", "Stop")
GUNLUK_SINIR = 2 * 1024 * 1024                       # 2 MB'ı geçince eski günlük .eski olur

# Riskli görünen komutlar (yalnız uyarı için; kalıp eşleme güvenlik sınırı değildir, bkz. docs/KANCA_ARASTIRMASI.md)
BAS = r"(?:^|[;&|(]\s*|\b(?:sudo|xargs|exec)\s+)"      # komutun başı: satır başı, ; && || | ( ya da sudo/xargs sonrası
RISKLI = [
    (BAS + r"(?:rm|rmdir|shred|unlink)\s", _("dosya siliyor")),
    (BAS + r"(?:Remove-Item|rd|del|erase|ri)\b", _("dosya siliyor")),
    (r"\bfind\b.*\s-delete\b", _("dosya siliyor")),
    (r"\bgit\s+(?:reset\s+--hard|clean\s+-\w*f|checkout\s+--\s|checkout\s+\.(?:\s|$)|restore\b|stash\s+(?:drop|clear))", _("yapılmış değişiklikleri geri alıyor")),
    (r"\bgit\s+push\b.*(?:--force|\s-f\b)", _("uzaktaki geçmişin üstüne yazıyor")),
    (r"\bgit\s+push\b", _("işi GitHub'a gönderiyor")),
    (r"(?:shutil\.rmtree|os\.remove|os\.unlink|os\.rmdir|\.unlink\(|rimraf|fs\.rm|fs\.unlink)", _("program içinden dosya siliyor")),
    (BAS + r"(?:format|diskpart|mkfs\S*)\s", _("diski biçimlendirebilir")),
    (r"\b(?:Set-Content|Out-File|Clear-Content)\b", _("bir dosyanın üstüne yazıyor")),
]


def _kisa(s, n=60):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[:n - 1] + "…"


def _dosya_adi(girdi):
    for k in ("file_path", "notebook_path", "path"):
        if isinstance(girdi, dict) and girdi.get(k):
            return os.path.basename(str(girdi[k]).rstrip("/\\")) or str(girdi[k])
    return ""


def risk(komut):
    """Komut riskli görünüyorsa nedenini, değilse None döner."""
    for desen, neden in RISKLI:
        if re.search(desen, komut or "", re.IGNORECASE):
            return neden
    return None


def yorumla(olay):
    """Kanca olayı -> (mod, metin, kayıt). mod: bos/calisiyor/sevincli/endiseli; metin None ise balon değişmez."""
    ad = olay.get("hook_event_name") or ""; arac = olay.get("tool_name") or ""; girdi = olay.get("tool_input") or {}
    kayit = {"zaman": time.strftime("%Y-%m-%d %H:%M:%S"), "olay": ad, "arac": arac}
    if ad == "UserPromptSubmit":
        return "calisiyor", _("Claude işe koyuldu. Ben de izliyorum."), kayit
    if ad == "Stop":
        return "sevincli", _("Claude bu adımı bitirdi."), kayit
    if ad == "Notification":
        kayit["ozet"] = _kisa(olay.get("message"), 120)
        return "endiseli", _("Claude senden bir şey bekliyor: %s") % _kisa(olay.get("message"), 120), kayit
    if ad != "PreToolUse":
        return None, None, kayit
    if arac in ("Bash", "PowerShell"):
        komut = girdi.get("command") if isinstance(girdi, dict) else ""
        kayit["ozet"] = _kisa(komut, 200); neden = risk(komut)
        if neden:
            kayit["risk"] = neden
            return "endiseli", _("Dikkat: Claude %s.\n%s") % (neden, _kisa(komut, 140)), kayit
        return "calisiyor", _("Claude bir komut çalıştırıyor: %s") % _kisa(komut), kayit
    if arac in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        d = _dosya_adi(girdi); kayit["ozet"] = d
        if arac == "Write":
            return "calisiyor", _("Claude bir dosya yazıyor: %s") % d, kayit
        return "calisiyor", _("Claude bir dosyayı düzenliyor: %s") % d, kayit
    if arac in ("Read", "Grep", "Glob", "LS"):
        return "calisiyor", None, kayit                          # okuma: kurt çalışır görünür, balonu doldurmaz
    if arac.startswith("mcp__boru__"):
        return None, None, kayit                                 # BÖRÜ'nün kendi araçları zaten kendisi konuşur
    if arac.startswith("mcp__"):
        return "calisiyor", _("Claude bir eklenti aracı kullanıyor: %s") % arac.split("__")[-1], kayit
    return "calisiyor", None, kayit


def _gunluk_yolu():
    import dersler
    return os.path.join(dersler.KOK, "kanca_gunlugu.jsonl")


def gunluge_yaz(kayit):
    try:
        p = _gunluk_yolu(); os.makedirs(os.path.dirname(p), exist_ok=True)
        if os.path.isfile(p) and os.path.getsize(p) > GUNLUK_SINIR:
            os.replace(p, p + ".eski")
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
    except Exception:
        pass                                                     # günlük yazılamasa da kurt çalışmaya devam eder


def dinle(kuyruk, port=None):
    """127.0.0.1 üstünde kanca dinleyicisini arka planda başlatır. Kapı doluysa (ör. ikinci BÖRÜ açık) None döner."""
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    zamanlayici = {"t": None}

    def sakinles():
        kuyruk.put(("mod", "bos"))

    class Isleyici(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                n = min(int(self.headers.get("Content-Length") or 0), 1024 * 1024)
                olay = json.loads(self.rfile.read(n) or b"{}") if self.path.split("?")[0] == YOL else None
            except Exception:
                olay = None
            if isinstance(olay, dict):
                mod, metin, kayit = yorumla(olay)
                gunluge_yaz(kayit)
                if mod:
                    kuyruk.put(("mod", mod))
                if metin:
                    kuyruk.put(("kurt", metin))
                if zamanlayici["t"]:
                    zamanlayici["t"].cancel()
                zamanlayici["t"] = threading.Timer(8.0 if mod == "sevincli" else 20.0, sakinles)
                zamanlayici["t"].daemon = True; zamanlayici["t"].start()
            govde = b"{}"                                       # karar yok: Claude Code kendi akışıyla devam eder
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(govde))); self.end_headers(); self.wfile.write(govde)

        def log_message(self, *a):
            pass

    try:
        sunucu = ThreadingHTTPServer(("127.0.0.1", port or PORT), Isleyici)
    except OSError:
        return None
    sunucu.daemon_threads = True
    threading.Thread(target=sunucu.serve_forever, daemon=True).start()
    return sunucu


# ---- Claude Code ayarı: ~/.claude/settings.json içindeki "hooks" bölümüne yalnız BÖRÜ'nün girdilerini yazar/siler

def ayar_dosyasi():
    import baglanti
    return os.path.join(baglanti.ev(), ".claude", "settings.json")


def _url(port=None):
    return "http://127.0.0.1:%d%s" % (port or PORT, YOL)


def _bizim(h):
    return isinstance(h, dict) and h.get("type") == "http" and str(h.get("url", "")).startswith("http://127.0.0.1:") and str(h.get("url", "")).endswith(YOL)


def kurulu_mu():
    p = ayar_dosyasi()
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return False
    return any(_bizim(h) for grup in (d.get("hooks") or {}).get("PreToolUse", []) for h in grup.get("hooks", []))


def _temizle(hooks):
    """BÖRÜ'nün eski girdilerini çıkarır; başkalarının kancalarına dokunmaz."""
    for olay in list(hooks):
        gruplar = []
        for grup in hooks.get(olay) or []:
            kalan = [h for h in grup.get("hooks", []) if not _bizim(h)]
            if kalan:
                g = dict(grup); g["hooks"] = kalan; gruplar.append(g)
            elif not grup.get("hooks"):
                gruplar.append(grup)
        if gruplar:
            hooks[olay] = gruplar
        else:
            del hooks[olay]
    return hooks


def _degistir(ekle):
    import baglanti
    p = ayar_dosyasi(); y = baglanti._yedek(p)
    d = json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else {}
    if not isinstance(d, dict):
        raise RuntimeError(_("ayar dosyası beklenen biçimde değil; dokunmadım"))
    hooks = _temizle(dict(d.get("hooks") or {}))
    if ekle:
        for olay in OLAYLAR:
            grup = {"hooks": [{"type": "http", "url": _url(), "timeout": 3}]}
            if olay == "PreToolUse":
                grup["matcher"] = "*"
            hooks.setdefault(olay, []).append(grup)
    if hooks:
        d["hooks"] = hooks
    else:
        d.pop("hooks", None)
    baglanti._yaz(p, json.dumps(d, ensure_ascii=False, indent=2))
    if kurulu_mu() != ekle:
        if y:
            shutil.copy2(y, p)
        raise RuntimeError(_("yazdıktan sonra doğrulanamadı; yedek geri kondu"))
    return y


def kur():
    """Canlı kurt kancalarını ekler. Yedek dosyasının yolunu (varsa) döner."""
    return _degistir(True)


def kaldir():
    return _degistir(False)
