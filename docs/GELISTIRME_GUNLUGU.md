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

Sıra proje sahibiyle 24 Kasım 2026'da onaylandı. Yukarıdan aşağı ilerle; bir madde Windows ya da proje sahibi
beklediği için tıkanırsa bir sonrakine geç ve tıkanıklığı son mesajda söyle.

1. **Windows sınaması (proje sahibiyle):** canlı kurdu Claude masaüstü *Code* sekmesinde ve terminalde dene; sonuçları
   docs/KANCA_ARASTIRMASI.md'ye işle. Proje sahibi kod bilmiyor: adımları tek tek, kopyala-yapıştır olarak ver.
2. **0.7 sürümü: kurt daha canlı.**
   - Uyku ve uyanma: uzun süre iş yokken ya da uzun bir komut sürerken kurt kıvrılıp uyur, iş bitince uyanır. Yeni
     "uyuyor" karesi gerekir; maskot setinde olmayan kare için yedek kare kullan (eski maskotlar bozulmasın).
   - Sesler: riskli komutta kısa havlama, iş bitince küçük sevinç sesi, uzun iş bitince uluma. Varsayılan kısık, menüden
     tamamen kapatılabilir; yalnız önemli anlarda. Yalnız serbest lisanslı (CC0) ya da stüdyonun kendi kaydı; kaynak ve
     lisans bir dosyada yazılı. Windows'ta `winsound` (ek kütüphane yok).
   - Daha sıcak konuşma dili: uyarının ciddiyeti korunarak kişilikli metinler (ör. "Emin misin patron?"). TR ve EN.
   - Sürüm numaraları (`boru.py` SURUM, `surum_bilgisi.txt`, `kurulum/boru.iss`), sürüm notu; etiket için proje sahibine sor.
3. **README için hareketli GIF:** kurdun kendi çizimiyle (xvfb + `--shot` kareleri ya da doğrudan çizim) düzenleme →
   silme uyarısı → sevinç akışı. 0.7 ile birlikte.
4. **Kara kutu, "BÖRÜ, geri getir!":** Write/Edit öncesi dosyanın kopyası; riskli komut öncesi proje klasörünün anlık
   kopyası (aynı içeriği iki kez saklamayan depo; büyük asset'lere dikkat; boyut sınırı ve eski kopyaları temizleme).
   Kurda tıklayınca son değişiklikler listesi ve *Geri getir*.
5. **"Emin misin patron?": işlemden önce sor.** Claude Code `PreToolUse` ile silme, üstüne yazma, `git push -f`,
   `git reset --hard` gibi işlemlerde kurt kendi penceresinde sorar; *Hayır* → `deny`. Oyun projesi kuralları (`Assets`,
   `.tscn`, `.unity`, `.blend`, kayıt dosyaları). Sonra Codex (yalnız `deny` destekli).
6. **Koku alma: gizli anahtar uyarısı.** `.env` ve benzeri gizli dosyalar okunurken uyarı; `git push`/`commit` öncesi
   gönderilecek değişikliklerde API anahtarı ve şifre taraması. 5. madde gelince gönderimi durdurabilir.
7. **Maskot paylaşma ve galeri:** maskotu tek dosyayla dışa/içe aktarma, depoda galeri, katkı rehberi (CONTRIBUTING.md).
8. **Token ateşi:** kancanın verdiği `transcript_path` kaydından harcanan token'lar; kurt ateşe kemik atar. Dolar değil
   (abonelikle kullananlar token başına ödemez); gerçek tutar gösterilebiliyorsa ayrıca doğrula. Aynı komutun art arda
   denenmesi (döngü) → ateş büyür, kurt terler.
9. **Böcek kovalama:** komut hata verince kurt böcek kovalar, aynı komut başarılı olunca yakalar (PostToolUse).
10. **Sonra:** anı yakala (GIF kaydedici; balonda dosya adı/komut sızmasına dikkat), isteğe bağlı mola hatırlatıcısı.

Sürekli: her sürüm için 30-45 sn video senaryosu (storyboard) taslağı `docs/icerik/` altına; topluluk için
"good first issue" adayları.

## Kayıtlar

### 24 Kasım 2026: yön değişikliği ve canlı kurt
- README ve yol haritası yeni yöne göre yeniden yazıldı (oyun geliştiriciler, canlı kurt, stüdyo maskotu).
- Kanca araştırması yapıldı (docs/KANCA_ARASTIRMASI.md).
- Canlı kurt ilk sürüm: `kanca.py`, sağ tık > Canlı kurt (Claude Code). Yalnız izler. Sınama: `sinama/kanca_sinama.py`.
- Linux'ta sanal ekranla üç durum görüldü (düzenleme, silme uyarısı, iş bitti): docs/img/canli_kurt_tr.png.
- Windows'ta henüz denenmedi.
- Tanıtım metinleri eşitlendi (yükleyici, açılış mesajları, HF kartı kaynağı); v0.4.0 sürüm notundaki "durdurur" abartısı düzeltildi.
- GitHub depo açıklaması ve HF kartı proje sahibinin elle değiştirmesine bırakıldı (araç izni yok).
- Proje sahibinden gelen iki fikir listesi değerlendirildi; birleşik sıra onaylandı (yukarıda "Sıradakiler").
