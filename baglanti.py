# BÖRÜ'nün Claude Code ve Codex'e bağlanması: durum tespiti ve (kullanıcı izin verirse) ayar dosyasına yazma.
# - Claude Code: ~/.claude.json, üst düzey "mcpServers" (kullanıcı kapsamı: her projede görünür).
# - Codex:       ~/.codex/config.toml, [mcp_servers.boru] bölümü.
# İkisi de ev klasöründe: Windows paket (MSIX) yönlendirmesinden etkilenmez (bkz. dersler.KOK notu).
# Kurallar: yazmadan önce yedek (<dosya>.boru-yedek-<zaman>); geçici dosyaya yazıp tek hamlede yerine koyma; yazdıktan sonra
# yeniden okuyup doğrulama, tutmazsa yedeği geri koyma; yalnız "boru" girdisine dokunma.
from dil import _
import os, sys, json, re, time, shutil

try:
    import tomllib
except Exception:                                   # Python < 3.11
    tomllib = None

AD = "boru"


def ev():
    return os.environ.get("BORU_EV") or os.path.expanduser("~")      # BORU_EV: yalnız sınama için sahte ev klasörü


def komut():
    """BÖRÜ'yü MCP kipinde başlatan komut: (çalıştırılabilir, argümanlar)."""
    if getattr(sys, "frozen", False):
        return sys.executable, ["--mcp"]
    return sys.executable, [os.path.join(os.path.dirname(os.path.abspath(__file__)), "boru.py"), "--mcp"]


def _claude():
    return os.path.join(ev(), ".claude.json")


def _codex():
    return os.path.join(ev(), ".codex", "config.toml")


def _ayni(a, b):
    return bool(a) and bool(b) and os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def durum():
    """[{kimlik, ad, kurulu, bagli, dogru, dosya, mevcut}] — mevcut: ayardaki BÖRÜ komutu (varsa)."""
    cmd, args = komut(); out = []
    # Claude Code
    p = _claude(); kurulu = os.path.isfile(p) or os.path.isdir(os.path.join(ev(), ".claude")); mevcut = None
    if os.path.isfile(p):
        try:
            mevcut = (json.load(open(p, encoding="utf-8")).get("mcpServers") or {}).get(AD)
        except Exception:
            mevcut = {"_okunamadi": True}
    out.append({"kimlik": "claude", "ad": "Claude Code", "kurulu": kurulu, "bagli": bool(mevcut), "dosya": p, "mevcut": mevcut,
                "dogru": bool(mevcut) and _ayni(mevcut.get("command"), cmd) and list(mevcut.get("args") or []) == args})
    # Codex
    p = _codex(); kurulu = os.path.isdir(os.path.join(ev(), ".codex")); mevcut = None
    if os.path.isfile(p):
        try:
            metin = open(p, encoding="utf-8").read()
            mevcut = (tomllib.loads(metin).get("mcp_servers") or {}).get(AD) if tomllib else ({"command": "?"} if "[mcp_servers.boru]" in metin else None)
        except Exception:
            mevcut = {"_okunamadi": True}
    out.append({"kimlik": "codex", "ad": "Codex", "kurulu": kurulu, "bagli": bool(mevcut), "dosya": p, "mevcut": mevcut,
                "dogru": bool(mevcut) and _ayni(mevcut.get("command"), cmd) and list(mevcut.get("args") or []) == args})
    return out


def _yedek(p):
    if not os.path.isfile(p):
        return None
    kok = p + ".boru-yedek-" + time.strftime("%Y%m%d_%H%M%S"); y, i = kok, 1
    while os.path.exists(y):                       # aynı saniyede ikinci yedek öncekinin (belki özgün dosyanın) üstüne yazmasın
        i += 1; y = "%s_%d" % (kok, i)
    shutil.copy2(p, y); return y


def _yaz(p, metin):
    os.makedirs(os.path.dirname(p), exist_ok=True); g = p + ".boru-gecici"
    with open(g, "w", encoding="utf-8", newline="") as f:
        f.write(metin)
    os.replace(g, p)


def baglan_claude():
    p = _claude(); cmd, args = komut(); y = _yedek(p)
    d = json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else {}
    if d.get("_okunamadi"):
        raise RuntimeError(_("okunamadı"))
    d.setdefault("mcpServers", {})[AD] = {"type": "stdio", "command": cmd, "args": args, "env": {}}
    _yaz(p, json.dumps(d, ensure_ascii=False, indent=2))
    try:
        assert (json.load(open(p, encoding="utf-8"))["mcpServers"][AD]["command"]) == cmd
    except Exception:
        if y:
            shutil.copy2(y, p)
        raise RuntimeError(_("yazdıktan sonra doğrulanamadı; yedek geri kondu"))
    return y


def baglan_codex():
    p = _codex(); cmd, args = komut(); y = _yedek(p)
    metin = open(p, encoding="utf-8").read() if os.path.isfile(p) else ""
    if "'" in cmd:
        raise RuntimeError(_("exe yolunda tek tırnak var; TOML'a güvenle yazılamaz"))
    blok = ("[mcp_servers.%s]\ncommand = '%s'\nargs = [%s]\nstartup_timeout_sec = 30\ntool_timeout_sec = 900\n"
            % (AD, cmd, ", ".join(json.dumps(x) for x in args)))
    satirlar = metin.splitlines(keepends=True); yeni, atla, bulundu = [], False, False
    for s in satirlar:                                                      # eski boru bölümünü (ve alt bölümlerini) çıkar
        b = s.strip()
        if b.startswith("["):
            atla = bool(re.match(r"\[\s*mcp_servers\.%s(\.|\s*\])" % AD, b))
            if atla and not bulundu:
                yeni.append(blok); bulundu = True
        if not atla:
            yeni.append(s)
    sonuc = "".join(yeni)
    if not bulundu:
        sonuc = sonuc + ("" if sonuc.endswith("\n") or not sonuc else "\n") + "\n" + blok
    if tomllib:
        tomllib.loads(sonuc)                                                 # bozuk TOML yazılmaz (hata fırlatır)
    _yaz(p, sonuc)
    if tomllib:
        try:
            assert tomllib.loads(open(p, encoding="utf-8").read())["mcp_servers"][AD]["command"] == cmd
        except Exception:
            if y:
                shutil.copy2(y, p)
            raise RuntimeError(_("yazdıktan sonra doğrulanamadı; yedek geri kondu"))
    return y


def baglan(kimlik):
    return {"claude": baglan_claude, "codex": baglan_codex}[kimlik]()


def ozet(d=None):
    d = d or durum(); s = []
    for h in d:
        if not h["kurulu"]:
            s.append(_("%s: bu bilgisayarda yok") % h["ad"])
        elif not h["bagli"]:
            s.append(_("%s: kurulu, bana bağlı değil") % h["ad"])
        elif not h["dogru"]:
            s.append(_("%s: bağlı ama başka bir BÖRÜ'yü gösteriyor (%s)") % (h["ad"], (h["mevcut"] or {}).get("command", "?")))
        else:
            s.append(_("%s: bağlı") % h["ad"])
    return s
