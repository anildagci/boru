# BÖRÜ'nün dil desteği. Kaynak dil Türkçe; kullanıcıya görünen her metin _("...") ile sarılır, İngilizcesi dil_en.json'dadır.
# Dil seçimi: BORU_DIL ortam değişkeni > Belgeler\BORU\ayar.json içindeki "dil" > Windows arayüz dili (Türkçe değilse İngilizce).
# Dil açılışta bir kez seçilir; değişiklik bir sonraki açılışta geçerli olur. Çevirisi olmayan metin Türkçe kalır.
import os, sys, json

DILLER = {"tr": "Türkçe", "en": "English"}
KOK = os.environ.get("BORU_VERI") or os.path.join(os.path.expanduser("~"), "Documents", "BORU")     # dersler.KOK ile aynı
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def _algila():
    d = os.environ.get("BORU_DIL")
    if d in DILLER:
        return d
    try:
        d = json.load(open(os.path.join(KOK, "ayar.json"), encoding="utf-8")).get("dil")
        if d in DILLER:
            return d
    except Exception:
        pass
    try:
        import ctypes
        return "tr" if (ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF) == 0x1F else "en"
    except Exception:
        import locale
        return "tr" if (locale.getlocale()[0] or "").lower().startswith(("tr", "turkish")) else "en"


DIL = _algila()
try:
    EN = json.load(open(os.path.join(BASE, "dil_en.json"), encoding="utf-8"))
except Exception:
    EN = {}


def _(s):
    """Türkçe kaynak metnin seçili dildeki karşılığı."""
    return EN.get(s, s) if DIL == "en" else s
