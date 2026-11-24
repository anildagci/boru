<p align="center"><img src="boru_simge.png" width="120" alt="BÖRÜ"></p>

<h1 align="center">BÖRÜ</h1>
<p align="center"><b>Yapay zekâyla çalışırken emeğini koruyan kurt.</b><br>
Hedefi: yapay zekâ bir şeyi silmeden önce sana sade Türkçeyle sorsun, sildiyse geri getirsin.</p>
<p align="center"><a href="README.md">English</a> · <a href="https://github.com/anildagci/boru/releases">İndir</a> · <a href="#yol-haritası">Yol haritası</a></p>

---

BÖRÜ, kod bilmeden **Claude** ya da **Codex** gibi yapay zekâ asistanlarıyla proje yürütenler için ücretsiz ve açık
kaynaklı bir yardımcıdır. Masaüstünde küçük bir kurt olarak durur, asistana [MCP](https://modelcontextprotocol.io) ile
bağlanır.

Yapay zekâ hızlıdır ama bazen emin bir şekilde yanılır: yanlış klasörü siler, iki haftalık işin üstüne yazar, "çalışıyor"
der ama çalışmıyordur. Programcı bunu fark eder; kod bilmeyen çoğu zaman iş işten geçince fark eder. BÖRÜ bu an için var:
ne olacağını teknik terim olmadan anlatır, kalıcı kararı sana bırakır ve emeğin yok olmasın diye önce yedek alır.

> **Bugünkü durum (0.6.2):** Bekçi şimdilik yalnız 3B paketinin klasörlerini izliyor ve BÖRÜ dışında yapılan
> değişiklikleri **sonradan** fark ediyor; önleyemiyor. İşlemden önce durdurma, her klasörde çalışma ve geri alma
> önümüzdeki 90 günün işi. Ayrıntı: [Dürüst sınırlar](#dürüst-sınırlar).

| Model teslim etmek istiyor | Bekçi bir değişiklik yakaladı | İlk açılış |
|---|---|---|
| <img src="docs/img/onay_en.png" width="250"> | <img src="docs/img/onay_tr.png" width="250"> | <img src="docs/img/baglanti_tr.png" width="250"> |

## Bugün ne yapıyor

- **Bekçi.** Her BÖRÜ aracı çağrısından önce klasörü son anıyla karşılaştırır. Değişen kaynak, silinen deneme, üstüne
  yazılan teslim, düşen üçgen ya da küçülen doku söylenir; kurala aykırı değişiklikte sen *Devam* diyene kadar iş durur.
- **Modeli değil seni dinler.** Teslim, kural değişikliği ve kararlar BÖRÜ'nün kendi penceresinde sorulur; yanıt
  yalnız senin tıklamanla gelir. Yapay zekâ bu onayı kendisi veremez.
- **Çalışma yöntemi.** Her işte (yalnız 3B değil) ve klasör gerekmeden: `boru_yontem` duruma uyan çalışma kurallarını
  getirir, `boru_risk` uzun bir işten önce planı tarayıp "önce şunu netleştirmemiz lazım" listesini çıkarır, `boru_liste`
  proje başlangıcı, teslim öncesi kalite, yardımcı ajana iş verme ve görsel inceleme listelerini verir, `boru_profil`
  yalnız senin bilgisayarında duran özel çalışma profilini (`Belgeler\BORU\ozel\PROFIL.md`) okur.
  Kurallar: [yöntem rehberi](bilgi/YONTEM.tr.md) (25 kural, gerçek projelerden damıtıldı).
- **İlk uzmanlık paketi: 3B karakter.** Kurulu **Blender**'ınla *çizimden oyuna hazır 3B karaktere* giden yolu yürütür:
  modeli incele, gözleri bul, üretilmiş başı gövdeye oturt, tek model ve tek dokuda topla, dışa aktar, doğrula, teslim et.
  Her adım numaralı bulgularla (üçgen, parça, doku, hizalama) yanıt verir ve neye *dokunmadığını* söyler.
- **Dikkatle öğrenir.** Yerel bir günlük tutar, tekrar eden durumları kanıtlı *ders adaylarına* çevirir. Hiçbiri
  BÖRÜ'yü kendiliğinden değiştirmez; onaylananlar bir sonraki sürüme girer.
- **Senin maskotun.** Kurdu seç ya da üç adımda kendi maskotunu oluştur (anlat → üret → görseli seç).
- **Türkçe ve İngilizce.**

## Kurulum

1. [Releases](https://github.com/anildagci/boru/releases) sayfasından `BORU_Kurulum_<sürüm>.exe`'yi indir ve çalıştır.
   Yönetici izni gerekmez. Yükleyici henüz imzalı değil; Windows *Bilinmeyen yayımcı* diyebilir:
   *Ek bilgi → Yine de çalıştır*. (İmzalı yükleyici 90 günlük planda.)
2. 3B paketi için [Blender 5](https://www.blender.org) kur (BÖRÜ yolunu kendisi bulur). Yalnız yöntem araçlarını
   kullanacaksan gerekmez.
3. BÖRÜ'yü aç. Claude Code ya da Codex kurulu ve bağlı değilse kurt bağlanmayı teklif eder (ayar dosyasını yedekler,
   yalnız `boru` girdisini yazar). O uygulamayı yeniden başlat.
4. Claude Code ya da Codex'te örneğin şunu iste: *"BÖRÜ'yü kullanarak bu işe başlamadan önce planımı riskler için tara."*

Elle bağlantı, araçların tam listesi ve kaynaktan derleme için [README.md](README.md) (İngilizce) bölümlerine bak; ayarlar aynı.

## Deneysel: yerel küçük model (donduruldu)

BÖRÜ, [Ollama](https://ollama.com) ile senin ekran kartında küçük bir model (Qwen3 4B) çalıştırabilir. Varsayılan kapalı;
yalnız sen **Evet** dersen indirilir, her şey bilgisayarında kalır (sağ tık > **Yerel model…** / **BÖRÜ'ye sor…**).
Bu özellik olduğu gibi çalışmaya devam ediyor ama **artık geliştirilmiyor**: kendi modelimizi eğitme denemesi hedefe
ulaşmadı (bkz. [`egitim/SONUCLAR.md`](egitim/SONUCLAR.md)) ve kullanıcının elinde zaten Claude ya da Codex var.
BÖRÜ'nün değeri modelde değil, bekçide ve yöntemde.

## Gizlilik

Her şey bilgisayarında kalır: ayarlar, günlük, dersler ve kendi maskotların `Belgeler\BORU` altında durur.
**BÖRÜ varsayılan olarak hiçbir şey göndermez.** İlk açılışta bir kez, haftalık *anonim* bir kullanım özeti göndermek
isteyip istemediğini sorar (sayılar ve ders adayları; dosya, klasör, kişi adı, not, görsel yok). Göndereceği her şeyi
önce `Belgeler\BORU\gonderilenler` altına yazar; istediğin an kapatırsın. Ayrıntı: [PRIVACY.md](PRIVACY.md).

## Dürüst sınırlar

- **Bekçinin bugünkü kapsamı:** yalnız 3B paketinin çalışma klasörlerine (`Source`, `Blender`, `Exports`, `Textures`,
  `Backups`) bakar; **her BÖRÜ aracı çağrısından önce** ve `boru_denetle` çağrılınca denetler. BÖRÜ dışında yapılan
  değişiklikleri (ör. yapay zekânın kendi betikleri ya da komutları) **sonradan** fark eder, önlemez ve geri getiremez.
  Henüz her proje için genel bir dosya koruması değildir. BÖRÜ'nün kendi kalıcı adımlarındaki (teslim, kural değişikliği)
  onay zorunludur.
- Yerel model kapalıyken yöntem araçları anahtar kelime eşler; anlamaz.
- Başı gövdeye oturtma iki yaka tipinde (tişört yakası, yüksek ceket yakası) ve iki karakterde sınandı. Göz bulma
  eşikleri dört görüntüde ölçüldü; saçla kapalı bir yüzde bulamayabilir (bunu söyler).
- Şimdilik yalnız Windows. Yükleyici imzasız.

## Yol haritası

**Tamamlananlar (0.4 - 0.6.2):** iki dilli yayın ve yükleyici; isteğe bağlı anonim geri bildirim; 25 kurallık çalışma
yöntemi ve asistan araçları; isteğe bağlı yerel model; `boru-4b` ince ayarı (ölçüldü, %80 kapısına ulaşmadı, yayınlanmadı;
bunun yerine kural araması iyileştirildi: doğru kural ölçüm sorularının %93'ünde ilk 4'te, önce %82).

### Önümüzdeki 90 gün (Kasım 2026 - Şubat 2027): kod bilmeyenler için bekçi

Yön değişikliği: yerel model geliştirmesi durduruldu; BÖRÜ'nün merkezi artık bekçi. Hedef kitle, kod bilmeden yapay
zekâyla proje yürütenler. Bu 90 gün stüdyonun bir oyun projesiyle paylaşılıyor; kapsam bilerek dar tutuldu.

**1. ay: doğrula ve temeli kur**
- **Hangi ortamda durdurabiliriz?** Kod bilmeyenler yapay zekâyı çoğunlukla masaüstü uygulamalarında kullanıyor.
  Claude Code (terminal ve masaüstü), Claude masaüstü / Cowork ve Codex'te işlemden önce araya girmeye (kanca) izin
  veren yollar tek tek sınanır; sonuç bir tabloyla yayınlanır. Kanca bağlayıcısı buna göre seçilir.
- **Her klasörde bekçi:** 3B klasörlerine bağlı kalmadan, kullanıcının seçtiği her proje klasörü.
- **Önce yedek, sonra geri al:** riskli bir işlemden önce BÖRÜ değişecek dosyaların yedeğini alır; pencerede tek
  tıkla *Geri getir*. Onay ekranına herkes *Evet* der; asıl güvence geri alabilmek.

**2. ay: işlemden önce durdur**
- **İşlemden önce denetim:** silme, üstüne yazma, korunan dosyaya dokunma, ana dala gönderme gibi işlemler
  gerçekleşmeden önce yakalanır ve BÖRÜ penceresinde sorulur. Önce Claude Code, sonra kanca desteği doğrulanan diğerleri.
- **Sade dil:** her soru teknik terim olmadan: *"Claude, 'Bölüm 3' klasöründeki 14 dosyayı silmek istiyor. Yedeğini
  aldım. İzin veriyor musun?"*
- **Yapay zekâ hata deneme alanı:** 30+ senaryolu güvenli bir deneme klasörü. Sonuç, yakalanamayanlar dahil, yayınlanır.

**3. ay: gerçek kullanım ve güven**
- **İmzalı yükleyici** (açık kaynak projelere ücretsiz imza, ör. SignPath Foundation), sağlama toplamları, temiz kaldırma.
  Kod bilmeyen biri "Bilinmeyen yayımcı" uyarısını görünce kurmaz; bu yüzden bu iş isteğe bağlı değil.
- **Gerçek kullanım:** geliştirici her gün kullanır, sonra kod bilmeyen 5-10 davetli. Ölçü: ikinci hafta da açıyorlar mı.
- **Belgelenmiş sınırlar:** neyin önlendiği, neyin yalnız sonradan fark edildiği, neyin kapsam dışı olduğu.

### Bu 90 günde yapılmayacaklar

- Yerel model geliştirmesi (gömülü llama.cpp, kendi minik modeller, daha küçük model ailesi, veri döngüsü). Mevcut
  özellik olduğu gibi kalır; ileride tamamen kaldırılabilir.
- Ücretli ürün. Önce gerçek ve tekrar eden kullanım; para konusu ondan sonra.
- Yeni uzmanlık paketleri ve paket ekosistemi. 3B paketi ilk paket olarak kalır; paket biçimi bekçi oturduktan sonra
  düşünülür.

### BÖRÜ'yü insanlara ulaştırmak

- **Tek cümle:** "Yapay zekâ dosyanı silmeden önce sana soran kurt." Uygulama, yükleyici ve README aynı şeyi söyler.
- **45 saniyelik tek video:** kurdun gerçek bir silme işlemini durdurduğu an. Hazır olunca, öncesinde değil.
- **"Yapay zekâya 30 hata yaptırdım, kurt kaçını yakaladı?"**: hata deneme alanının sonuçları, başarısızlıklarla birlikte.
- **Başarısız model hikâyesi:** "Tek ekran kartıyla kendi modelimi eğittim, olmadı, öğrendiklerim"
  ([`egitim/SONUCLAR.md`](egitim/SONUCLAR.md)); geliştirici toplulukları için.
- **25 kural:** kısa paylaşım serisi, Türkçe ve İngilizce.
- Önce Türkçe: kod bilmeden yapay zekâyla iş yapan Türkçe konuşan topluluklar. MCP dizinlerinde kayıt ikincil.

## DownStroke Studios'u takip et

BÖRÜ'nün arkasındaki stüdyonun proje haberleri ve geliştirme videoları için:

- [Instagram](https://www.instagram.com/downstrokestudios/)
- [YouTube](https://www.youtube.com/@downstrokestudios)
- [TikTok](https://www.tiktok.com/@downstrokestudios)

## Lisans

GPL-3.0 ([LICENSE](LICENSE)); Blender betikleri GPL ile uyumlu kalmalıdır. © 2026 DownStroke Studios.
