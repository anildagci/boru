# Kanca araştırması: BÖRÜ bir işlemi olmadan önce nerede durdurabilir?

Tarih: 24 Kasım 2026. 90 günlük planın 1. ay ilk maddesi.

**Durum: masa başı araştırma.** Kaynaklar resmî belgeler (Claude) ve açık kaynak kod (Codex). Hiçbiri henüz gerçek bir
Windows bilgisayarında BÖRÜ ile sınanmadı; aşağıdaki "Sınanacaklar" listesi o iş için.

## Özet tablo

| Ortam | İşlemden önce durdurabilir mi? | Nasıl | Güven |
|---|---|---|---|
| Claude Code, terminal | **Evet** | `PreToolUse` / `PermissionRequest` kancası | Yüksek (resmî belge) |
| Claude Code, Claude masaüstü uygulamasının *Code* sekmesi | **Büyük ihtimalle evet** | Aynı ayar dosyaları ve kancalar | Orta-yüksek (belge açıkça söylemiyor; sınanacak) |
| Claude Code, VS Code eklentisi | Büyük ihtimalle evet | Aynı `settings.json` | Orta-yüksek |
| Claude Code, web (bulut) | **Hayır** (kullanıcının bilgisayarında çalışmaz) | – | Yüksek |
| Claude masaüstü sohbet | **Hayır** | Belgelenmiş kanca yok | Orta |
| Claude Cowork | **Hayır** | Belgelenmiş kanca yok; kendi silme onayı var | Yüksek |
| Codex CLI | **Evet, yalnız engelleme** | `PreToolUse` (yalnız `deny`) | Yüksek (kaynak kod) |
| Codex masaüstü uygulaması / IDE eklentisi | Büyük ihtimalle evet | Aynı kanca motoru (app-server) | Orta (koddan çıkarım; sınanacak) |

## Claude Code

Kaynak: [hooks](https://code.claude.com/docs/en/hooks), [permissions](https://code.claude.com/docs/en/permissions),
[desktop](https://code.claude.com/docs/en/desktop).

- **Olaylar:** `PreToolUse` araç çalışmadan önce gelir. `PermissionRequest`, Claude Code kendi izin penceresini açacağı
  zaman gelir. `PostToolUse` sonradır, engelleyemez.
- **Karar:** `PreToolUse` JSON ile `permissionDecision`: `allow` / `deny` / `ask` / `defer`, gerekçe
  `permissionDecisionReason`. Çıkış kodu 2 de engeller (gerekçe stderr'de). Diğer hata kodları **engellemez**.
- **Kapsam:** `Bash`, `PowerShell`, `Write`, `Edit`, `NotebookEdit` ve MCP araçları (`mcp__<sunucu>__<araç>`).
- **Süre:** komut kancası varsayılan 600 sn bekler. Süre dolarsa ya da kanca çökerse **işlem devam eder** (fail-open);
  `"onFailure": "block"` ile kapatılabilir (v2.1.295+). Yani kanca, kullanıcı BÖRÜ penceresinde tıklayana kadar
  bekleyebilir; 10 dakika yeter.
- **Kanca türü:** `command` (bir program çalıştırır) ya da `http` (olayı bir adrese POST eder). BÖRÜ zaten açık duran bir
  uygulama olduğu için `http://127.0.0.1:<port>` en temiz yol olabilir.
- **Nereye yazılır:** `~/.claude/settings.json` (tüm projeler). Ayrı bir kanca onayı yok; etkileşimli oturumda klasör
  güven penceresi kabul edilince çalışır. BÖRÜ'nün bağlantı sihirbazı bugün MCP girdisini yazdığı gibi kanca girdisini de
  yedek alarak yazabilir ve ne eklediğini gösterir.
- **Windows:** Git Bash yoksa kabuk PowerShell olur. Yol ve tırnak sorunlarına karşı ASCII bir yol (`BORU.exe`) kullanılmalı.
- **Ek koruma:** izin kuralları (`permissions.deny`), ör. `PowerShell(Remove-Item *)`. Kanca `allow` dese bile `deny`
  kuralı geçerlidir.

## Codex

Kaynak: `openai/codex` deposu, `codex-rs/hooks` (24 Kasım 2026, `9863043`). OpenAI'ın belge sitesine bu ortamdan
erişilemedi; bilgiler koddan okundu.

- **Olaylar:** `preToolUse`, `permissionRequest`, `postToolUse` ve 11 olay daha.
- **Kapsam:** `Bash` (kabuk), `apply_patch` (dosya düzenleme; eşleştiricide `Write` ve `Edit` adlarıyla da yakalanır),
  MCP araçları.
- **Önemli fark: Codex'te `PreToolUse` yalnız engelleyebilir.** `permissionDecision: "allow"` ve `"ask"`
  "desteklenmiyor" diye **yok sayılır** ve işlem devam eder. Yani "Codex'in kendi onay penceresini aç" denemez; BÖRÜ
  soruyu kendi penceresinde sorup kullanıcı *Hayır* derse `deny` döner, *Evet* derse hiçbir şey dönmez.
- **Süre:** komut kancası varsayılan 600 sn. `onFailure: "block"` eşzamanlı kancalarda destekleniyor.
- **Güven onayı:** yeni ya da değişmiş kanca, kullanıcı Codex'te `/hooks` ile onaylayana kadar **çalışmaz** (içerik
  özeti, `trusted_hash`). BÖRÜ bu onayı kendisi yazmamalı; kurulumdan sonra kullanıcıya "Codex'te /hooks yazıp BÖRÜ'yü
  onayla" demeli. Doğru olan da bu.
- **Windows:** kanca `COMSPEC` (genelde `cmd.exe`) ile çalıştırılır.
- **Masaüstü uygulaması:** Codex masaüstü uygulaması ve IDE eklentisi aynı çekirdeği (app-server) kullanıyor; app-server
  protokolünde kanca listeleme ve kanca bildirimleri var. Bu yüzden kancaların orada da çalışması beklenir; sınanmalı.

## Bilinen sınırlar (iki istemcide de)

- **Kalıp eşleme güvenlik sınırı değildir.** `rm` ya da `Remove-Item` yakalanır; ama `python -c "shutil.rmtree(...)"`,
  bir betik dosyası ya da `bash -c '...'` ile yapılan silme kaçabilir. Claude belgeleri bunu açıkça söylüyor.
- **Üstüne yazma da silmedir.** `Write`/`Edit`/`apply_patch` bir dosyanın içini boşaltabilir; komutta "sil" geçmez.
- Bu iki boşluk yüzünden **yedek + geri al** kalıp eşlemeden daha önemli: BÖRÜ riskli görünen her işlemden önce proje
  klasöründe değişecek dosyaların (ya da klasörün) anlık yedeğini alırsa, yakalayamadığı bir silmeyi de geri getirebilir.

## Strateji için sonuç

> Not (24 Kasım 2026, sonradan): bu araştırmadan sonra hedef kitle "yapay zekâyla oyun geliştirenler" olarak güncellendi
> (bkz. README > Yol haritası). Aşağıdaki teknik sonuçlar geçerli; "kod bilmeyenler" ifadesi o günkü hedef kitleyi anlatır.
> Kanca altyapısı canlı kurtta (`kanca.py`) kullanılmaya başlandı.

1. **Cowork ve Claude sohbet kapsam dışı.** Kod bilmeyenlerin önemli bir kısmı oradayken BÖRÜ onları koruyamaz. Cowork
   zaten kalıcı silmeden önce kendisi izin istiyor.
2. **Ulaşabildiğimiz kod bilmeyenler:** Claude masaüstü uygulamasındaki *Code* sekmesini ve Codex masaüstü uygulamasını
   kullananlar. Hedef kitle tanımı bu iki uygulamaya göre daraltılmalı ve README'de açıkça yazılmalı.
3. **Önce Claude Code:** `ask` ve `PermissionRequest` desteği, belgelerin olgunluğu ve klasör güveni dışında ayrı onay
   olmaması nedeniyle. Codex ikinci; orada BÖRÜ'nün kendi penceresi tek yol.
4. **Tasarım kararı (açık):** BÖRÜ kapalıyken kanca ne yapsın? Fail-open (iş devam eder, korunmasız) mı, fail-closed (BÖRÜ
   açılana kadar her riskli işlem durur) mu? Kod bilmeyen kullanıcı için önerim: fail-open, ama kurt tepside "kapalıydım,
   şu işlemler korumasız geçti" desin.

## Sınanacaklar (Windows'ta, gerçek kurulumla)

1. Claude masaüstü *Code* sekmesinde `~/.claude/settings.json` içindeki bir `PreToolUse` kancası çalışıyor mu?
2. Kanca 2-3 dakika bekletilince (kullanıcı pencereyi geç tıklarsa) ne oluyor?
3. `http` kancası `127.0.0.1` adresine ulaşıyor mu; BÖRÜ kapalıyken ne oluyor?
4. Codex masaüstü uygulamasında kanca, `/hooks` onayından sonra çalışıyor mu?
5. `python -c` ile silme ve `Write` ile içi boşaltma: kanca ne görüyor, yedek bunları geri getirebiliyor mu?
