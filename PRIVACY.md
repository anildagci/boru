# Privacy / Gizlilik

[Türkçe aşağıda](#türkçe)

## English

**By default BÖRÜ sends nothing.** Everything it keeps (settings, log, lesson candidates, your own mascots) stays on your
computer in `Documents\BORU`.

### Optional anonymous feedback (off unless you turn it on)

On first launch BÖRÜ asks once whether you want to help improve it. Only if you answer **Yes** (or later tick
*right-click → Send anonymous feedback*) does it send, **at most once a week**, an anonymous summary of the log entries
since the last summary.

**Sent:** BÖRÜ version, language, Windows version, a random installation id (generated on your computer, not linked to
you), per-tool call / error counts and median duration, how approval questions ended (accepted / rejected / unanswered),
lesson candidates (type, title with file paths, numbers and anything in quotes removed, number of evidence).

**Never sent:** file or folder names, person or character names, your or the model's notes, BÖRÜ's full replies, images,
models, test runs.

**Before sending,** BÖRÜ writes the exact package to `Documents\BORU\gonderilenler\` so you can see what left your
computer (*right-click → Show what was sent*). You can turn it off at any time.

**Where it goes:** a Cloudflare Worker (`boru-geribildirim.anilcan-dagci.workers.dev`, source in
[`sunucu/geribildirim`](sunucu/geribildirim)). Your IP address is not stored; only a daily, non-reversible hash is kept for
two days to limit abuse. Because the data is anonymous, it is **public**: anyone can read it at `/veri`, and curated parts
will be published as an open dataset (e.g. on Hugging Face) to improve BÖRÜ and, later, to train its small model.

### Claude Code / Codex settings

BÖRÜ changes `~\.claude.json` or `~\.codex\config.toml` only after you click *Connect*; it backs the file up first and
writes only the `boru` entry.

## Türkçe

**BÖRÜ varsayılan olarak hiçbir şey göndermez.** Tuttuğu her şey (ayarlar, günlük, ders adayları, kendi maskotların)
bilgisayarında, `Belgeler\BORU` altında kalır.

### İsteğe bağlı anonim geri bildirim (sen açmadıkça kapalı)

İlk açılışta BÖRÜ bir kez, geliştirmemize yardım etmek isteyip istemediğini sorar. Yalnız **Evet** dersen (ya da sonradan
*sağ tık → Anonim geri bildirim gönder*'i işaretlersen) **haftada en çok bir kez**, son özetten bu yana günlük kayıtlarının
anonim bir özetini gönderir.

**Gönderilen:** BÖRÜ sürümü, dil, Windows sürümü, rastgele bir kurulum kimliği (bilgisayarında üretilir, sana bağlanmaz),
araç başına çağrı/hata sayısı ve ortanca süre, onay sorularının sonucu (kabul/ret/yanıtsız), ders adayları (tür; dosya yolu,
sayı ve tırnak içi her şey silinmiş başlık; kanıt sayısı).

**Asla gönderilmeyen:** dosya ya da klasör adları, kişi ya da karakter adları, senin ya da modelin notları, BÖRÜ'nün tam
yanıtları, görseller, modeller, sınama kayıtları.

**Göndermeden önce** BÖRÜ paketin tam halini `Belgeler\BORU\gonderilenler\` altına yazar; bilgisayarından neyin çıktığını
görürsün (*sağ tık → Gönderilenleri göster*). İstediğin an kapatabilirsin.

**Nereye gider:** bir Cloudflare Worker (`boru-geribildirim.anilcan-dagci.workers.dev`, kaynak
[`sunucu/geribildirim`](sunucu/geribildirim)). IP adresin saklanmaz; kötüye kullanımı sınırlamak için yalnız günlük, geri
çevrilemez bir özeti iki gün tutulur. Veriler anonim olduğu için **herkese açıktır**: `/veri` adresinden okunabilir; seçilmiş
kısımları BÖRÜ'yü geliştirmek ve ileride küçük modelini eğitmek için açık veri seti olarak (ör. Hugging Face) yayınlanır.

### Claude Code / Codex ayarları

BÖRÜ `~\.claude.json` ya da `~\.codex\config.toml` dosyasını yalnız sen *Bağla* dedikten sonra değiştirir; önce yedekler,
yalnız `boru` girdisini yazar.
