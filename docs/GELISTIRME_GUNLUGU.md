# BÖRÜ geliştirme günlüğü

Haftalık otomatik geliştirme oturumları bu dosyayı okuyup kaldığı yerden devam eder ve sonuna kendi kaydını ekler.
Proje sahibi kod bilmiyor: her kayıt kısa ve sade Türkçe olmalı.

## Yön (Kasım 2026'da kararlaştırıldı)

- **Amaç:** BÖRÜ, DownStroke Studios'un maskotu ve ilk açık kaynak projesi. Ücretsiz kalır. Görevi, sevilen ve gerçekten
  kullanılan bir araç olarak stüdyonun sosyal medyasına ve oyunlarına kitle getirmek; ileride gönüllü katkıcıları stüdyoya
  çekmek.
- **Hedef kitle:** Claude Code ya da Codex ile oyun geliştiren bağımsız geliştiriciler ve sanatçılar (Godot, Unity, Blender).
- **Ürün:** masaüstünde yapay zekâyı izleyen canlı kurt (tatlı taraf, video içeriği) + projeyi koruyan bekçi (yedek, geri al,
  işlemden önce sor) + çalışma yöntemi + 3B paketi.
- **Yapılmayacaklar:** yerel model geliştirmesi (donduruldu), ücretli ürün, Steam.
- Ayrıntılı plan: README.tr.md > Yol haritası. Kanca bilgisi: docs/KANCA_ARASTIRMASI.md.

## Çalışma kuralları (otomatik oturumlar için)

- Haftada bir oturum; oturum başına 1-2 küçük, bitmiş ve sınanmış iş. Büyük işi parçala, gerisini "Sıradakiler"e yaz.
- Kod değişikliğinde `python sinama/kanca_sinama.py` ve ilgili sınamalar geçmeli; yeni özelliğe sınama ekle.
- Pencereyi Linux'ta görmek için: `apt` ile gelen `/usr/bin/python3.12` (tkinter var) + `xvfb-run` + `boru.py --shot`.
  Sahte ev/veri: `BORU_EV`, `BORU_VERI`. Bağlantı sorusu çıkmasın diye veri klasörüne `ayar.json` = `{"baglanti_sorma": true}`.
- Kullanıcıya görünen her yeni metin `_()` ile sarılır ve İngilizcesi `dil_en.json`'a eklenir.
- Gizlilik: hiçbir şey varsayılan olarak bilgisayardan çıkmaz; yeni bir veri yolu PRIVACY.md'ye yazılır.
- Dürüstlük: README'deki "Dürüst sınırlar" her zaman gerçeği söyler.
- Sürüm etiketi (`v*`) atmak kullanıcıya ulaşan bir yayındır: önce proje sahibine sor.
- Sürüm notu: `docs/surum_notlari/<etiket>.md` yaz, sonra `surum_notu` iş akışını (Actions, workflow_dispatch, girdi `etiket`) çalıştır.
- İki haftada bir (çift ISO haftalarında) oturumun başında kısa bir araştırma: benzer araçlar, Claude Code/Codex'teki
  yenilikler, oyun geliştirici topluluklarında yapay zekâ dertleri, içerik fikirleri. Bulguları buraya "Araştırma" başlığıyla yaz.

## Sıradakiler

1. **Windows sınaması (proje sahibiyle):** canlı kurdu Claude masaüstü *Code* sekmesinde ve terminalde dene; sonuçları
   docs/KANCA_ARASTIRMASI.md'ye işle. Proje sahibi kod bilmiyor: adımları tek tek, kopyala-yapıştır olarak ver.
2. **Kurtta daha çok tepki:** uzun süre iş yokken uyuma, art arda başarılı adımlarda sevinç, çok uzun işte sabırsızlık.
3. **0.7 sürümü** (canlı kurt): sürüm numaraları (`boru.py` SURUM, `surum_bilgisi.txt`, `kurulum/boru.iss`), sürüm notu;
   etiket için proje sahibine sor.
4. **Önce yedek, sonra geri al** (2. ay): riskli işlemden önce değişecek dosyaların yedeği, kurtta *Geri getir*.
5. **İşlemden önce sor** (Claude Code `PreToolUse` `ask`/`deny`), oyun projesi kuralları, Codex desteği.
6. **Hata deneme alanı:** örnek oyun projesinde 30+ senaryo.
7. **Topluluk:** CONTRIBUTING.md, "good first issue" listesi, maskot galerisi.
8. **İçerik:** her sürüm için 30-45 sn video senaryosu (storyboard) taslağı `docs/icerik/` altına.

## Kayıtlar

### 24 Kasım 2026: yön değişikliği ve canlı kurt
- README ve yol haritası yeni yöne göre yeniden yazıldı (oyun geliştiriciler, canlı kurt, stüdyo maskotu).
- Kanca araştırması yapıldı (docs/KANCA_ARASTIRMASI.md).
- Canlı kurt ilk sürüm: `kanca.py`, sağ tık > Canlı kurt (Claude Code). Yalnız izler. Sınama: `sinama/kanca_sinama.py`.
- Linux'ta sanal ekranla üç durum görüldü (düzenleme, silme uyarısı, iş bitti): docs/img/canli_kurt_tr.png.
- Windows'ta henüz denenmedi.
- Tanıtım metinleri eşitlendi (yükleyici, açılış mesajları, HF kartı kaynağı); v0.4.0 sürüm notundaki "durdurur" abartısı düzeltildi.
- GitHub depo açıklaması ve HF kartı proje sahibinin elle değiştirmesine bırakıldı (araç izni yok).
