# Canlı kurt (kanca.py) sınaması. Pencere açmaz; Windows gerektirmez.
#   python sinama/kanca_sinama.py
# Sahte ev ve veri klasörü kullanır: gerçek ~/.claude/settings.json'a dokunmaz.
import os, sys, json, queue, socket, tempfile, urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GECICI = tempfile.mkdtemp(prefix="boru_kanca_")
os.environ["BORU_EV"] = os.path.join(GECICI, "ev"); os.environ["BORU_VERI"] = os.path.join(GECICI, "veri"); os.environ["BORU_DIL"] = "tr"
s = socket.socket(); s.bind(("127.0.0.1", 0)); os.environ["BORU_KANCA_PORT"] = str(s.getsockname()[1]); s.close()
sys.path.insert(0, KOK)
import kanca

hata = []


def bekle(kosul, ad):
    if not kosul:
        hata.append(ad); print("  OLMADI:", ad)
    else:
        print("  tamam:", ad)


print("1. Riskli komut tanıma")
riskli = ["rm -rf build", "cd x && rm file.txt", "sudo rm a", "Remove-Item -Recurse Assets", "del /s *.png", "rmdir /s /q eski",
          "git reset --hard HEAD~3", "git clean -fd", "git push --force origin main", "git push origin main",
          "python -c \"import shutil; shutil.rmtree('Assets')\"", "find . -name '*.tmp' -delete", "git checkout -- .",
          "Set-Content -Path save.json -Value ''", "git stash drop"]
guvenli = ["ls -la", "git status", "git log --format=%H", "python main.py", "godot --headless --export-release",
           "echo hello > /dev/null", "npm run build", "cat readme.md", "grep -r format src", "git diff", "python model.py --delete-cache-help"]
for k in riskli:
    bekle(kanca.risk(k) is not None, "riskli: " + k)
for k in guvenli:
    bekle(kanca.risk(k) is None, "güvenli: " + k)

print("2. Olay yorumlama")
m, t, _k = kanca.yorumla({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "rm -rf Assets"}})
bekle(m == "endiseli" and "Dikkat" in t, "riskli komutta kurt endişeli")
m, t, _k = kanca.yorumla({"hook_event_name": "PreToolUse", "tool_name": "Edit", "tool_input": {"file_path": "C:\\oyun\\player.gd"}})
bekle(m == "calisiyor" and "player.gd" in t, "düzenlemede dosya adı")
m, t, _k = kanca.yorumla({"hook_event_name": "Stop"})
bekle(m == "sevincli", "iş bitince sevinçli")
m, t, _k = kanca.yorumla({"hook_event_name": "PreToolUse", "tool_name": "mcp__boru__boru_incele", "tool_input": {}})
bekle(m is None and t is None, "BÖRÜ'nün kendi aracında sessiz")

print("3. Dinleyici")
q = queue.Queue(); sunucu = kanca.dinle(q)
bekle(sunucu is not None, "dinleyici açıldı")
bekle(kanca.dinle(queue.Queue()) is None, "ikinci dinleyici aynı kapıyı almıyor")
istek = urllib.request.Request(kanca._url(), data=json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                               "tool_input": {"command": "git push --force"}}).encode(), headers={"Content-Type": "application/json"})
yanit = urllib.request.urlopen(istek, timeout=5)
bekle(yanit.status == 200 and json.loads(yanit.read()) == {}, "yanıt boş: hiçbir karar dönmüyor")
gelen = [q.get(timeout=2), q.get(timeout=2)]
bekle(("mod", "endiseli") in gelen and any(t == "kurt" and "üstüne yazıyor" in m for t, m in gelen), "kurda haber gitti")
gunluk = os.path.join(os.environ["BORU_VERI"], "kanca_gunlugu.jsonl")
bekle(os.path.isfile(gunluk) and json.loads(open(gunluk, encoding="utf-8").readline())["arac"] == "Bash", "günlüğe yazıldı")
sunucu.shutdown()

print("4. Claude Code ayarına kurma ve kaldırma")
p = kanca.ayar_dosyasi(); os.makedirs(os.path.dirname(p))
baska = {"model": "opus", "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "benim-kancam"}]}]}}
json.dump(baska, open(p, "w", encoding="utf-8"))
y = kanca.kur(); d = json.load(open(p, encoding="utf-8"))
bekle(y and os.path.isfile(y), "önce yedek alındı")
bekle(kanca.kurulu_mu(), "kuruldu")
bekle(d["model"] == "opus" and d["hooks"]["PreToolUse"][0]["hooks"][0]["command"] == "benim-kancam", "başka ayarlara dokunulmadı")
bekle(set(d["hooks"]) == {"PreToolUse", "UserPromptSubmit", "Notification", "Stop"}, "dört olay eklendi")
kanca.kur(); d = json.load(open(p, encoding="utf-8"))
bekle(sum(kanca._bizim(h) for g in d["hooks"]["PreToolUse"] for h in g["hooks"]) == 1, "iki kez kurmak çift girdi yapmıyor")
kanca.kaldir(); d = json.load(open(p, encoding="utf-8"))
bekle(not kanca.kurulu_mu() and d == baska, "kaldırınca dosya eski haline döndü")
os.remove(p); kanca.kur(); kanca.kaldir()
bekle(json.load(open(p, encoding="utf-8")) == {}, "dosya yokken de çalışıyor")

print()
print("SONUÇ:", "hepsi tamam" if not hata else "%d sorun" % len(hata))
sys.exit(1 if hata else 0)
