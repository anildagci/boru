# Yapay zekâ ile çalışma yöntemi

Gerçek projelerden damıtılmış kurallar. BÖRÜ bunları `boru_yontem` aracıyla modele sunar. Bu dosya `derle_bilgi.py` ile `kurallar.json`'dan üretilir; elle düzenleme.

## Başlangıç

### B01 · Rolleri, bağlayıcı kuralları ve onay kapılarını baştan yaz

**Ne zaman:** Yeni bir projeye ya da büyük bir işe başlarken

**Yap:**
- Modele bir rol ver (ör. yaratıcı yönetmen + teknik yönetmen + kalite sorumlusu) ve son kararın kimde olduğunu yaz.
- Bağlayıcı kuralları madde madde yaz: neye onay gerekir, ne asla yapılmaz, bütçe sınırı.
- İşi aşamalara (kapılara) böl; her kapıda modelin DURUP onay beklemesini iste.
- Mekanik, hikâye, görsel yön gibi yaratıcı kararlar için modelin tasarlamadan önce senin fikrini sormasını şart koş.

**Yapma:**
- Tek cümlelik bir istekle büyük işi modele bırakma.
- Kapısız, onaysız uçtan uca 'hepsini yap' deme (bilinçli olarak istemediğin sürece).

**Neden:** Model hızlıdır; yönü baştan çizilmezse hızla yanlış yere gider. Kapılar, emeğin boşa gitmesini erken yakalar.

### B02 · Önce belgeyi okut, sonra iş yaptır

**Ne zaman:** Var olan bir depoda ya da belgeli bir projede görev verirken

**Yap:**
- İstemin ilk cümlesi: 'Önce AGENTS.md'yi ve ilgili belgeyi (GDD §4, SPRINT-005) oku.'
- Görevi belgeye bağla: 'SPRINT-003 İş 2'yi uygula.'
- Kararları belgeye yazdır (GDD sürüm geçmişi, DEVLOG) ki bir sonraki oturum oradan başlasın.

**Yapma:**
- Bağlamı her seferinde sohbette yeniden anlatma; belgeye koy.

**Neden:** Sohbet unutulur, belge kalır. Devir teslim belgesiyle yeni bir oturum, öncekini okumadan işe devam edebilir.

## Netleştirme

### N01 · Emek boşa gidebilecekse önce 'şunu netleştirmemiz lazım' de

**Ne zaman:** Bir iş, henüz verilmemiş bir karara bağlıysa ya da birden çok yola açılıyorsa

**Yap:**
- Kodlamaya başlamadan kararı adlandır ve seçenekleri kısaca yaz.
- Kendi önerini ilk sıraya koy, ama kararı kullanıcıya bırak.
- Sorudan önce, soruyu gerektiren gerçeği ölç ya da göster (ör. 'yöntem Raicon'a göre kurulu, Bolt'ta gözlük yok').

**Yapma:**
- Belirsizken tahminle uzun bir işe girişme.
- Bir kuralı ya da kararı uydurma; emin değilsen sor.

**Neden:** En pahalı hata, doğru yapılmış yanlış iştir.

### N02 · Uygulamadan önce planı değerlendir: yapılabilir, yapılamaz, alternatif

**Ne zaman:** Kullanıcı madde madde bir plan getirdiğinde

**Yap:**
- Her madde için: yapılabilir mi, neden; yapılamıyorsa engel ne; alternatif ne.
- Kısa tut; sonra onay al ve 1. maddeden başla.

**Yapma:**
- Planı okuyup hemen kodlamaya başlama.

**Neden:** Kullanıcı yöntem önerir ama 'daha iyisi varsa önce sor' der; değerlendirme bu kapıdır.

### N03 · Kısa soruya kısa cevap

**Ne zaman:** Kullanıcı evet/hayır ya da tek cümlelik bir soru sorduğunda

**Yap:**
- İlk kelime cevap olsun (Evet/Hayır), gerekirse tek cümle gerekçe.

**Yapma:**
- Kısa soruya rapor yazma.

**Neden:** Kullanıcı hızlı karar verir; uzun cevap kararı yavaşlatır.

## Kalite

### K01 · Tahmin etme, ölç; teşhisi kanıtla koy

**Ne zaman:** Bir kusurun nedenini ararken ya da kural/eşik yazarken

**Yap:**
- Kural yazmadan önce veriyi ölç (renk, konum, süre, sayı).
- Nedeni gösteren bir kanıt üret: tanı çıktısı, renk kodlu render, karşılaştırma görüntüsü.
- Tanıyı kullanıcının gerçek koşulunda yap (ör. uygulamayı kullanıcının açtığı gibi aç).

**Yapma:**
- Tahminle kural yazma; tahmini kurallar defalarca yanlış çıktı.
- Kendi ortamında çalıştı diye 'çalışıyor' deme.

**Neden:** Ölçülmüş bir neden bir kez düzeltilir; tahmin edilmiş bir neden turlar boyunca kovalanır.

### K02 · Kabul testini önce başarısız göster, sonra düzelt

**Ne zaman:** Bir ayar, denge ya da davranış değiştirilirken

**Yap:**
- Belgedeki ölçütü teste çevir; mevcut ayarla kırmızı olduğunu göster.
- Düzelt; önceki ve sonraki ölçümleri PR'a tablo olarak yaz.
- Var olan testleri gevşetme; build ve testler geçmeli.

**Yapma:**
- Testi düzeltmeden sonra yazıp 'geçti' deme.

**Neden:** Başarısız görülmemiş bir test, hiçbir şeyi kanıtlamaz.

### K03 · Görsel incelemede numaralı, işaretli geri bildirim

**Ne zaman:** Görsel, model, animasyon ya da arayüz değerlendirilirken

**Yap:**
- Kullanıcı görsel üstünde renkli oklarla işaretler; her ok bir maddeye karşılık gelir (yeşil = korunacak, kırmızı = sorun).
- Model her maddeye ayrı cevap verir; önce korunacakları korur.
- Karşılaştırma görsellerini kayıpsız ve büyütmeden göster; küçük önizlemeyi büyütmek kusuru olduğundan kötü gösterir.

**Yapma:**
- 'Biraz daha iyi yap' gibi belirsiz revizyon verme.
- JPEG'e sıkıştırılmış ya da büyütülmüş görselle karar verdirme.

**Neden:** Numaralı işaret, revizyonu ölçülebilir yapar ve iyi olanın bozulmasını önler.

### K04 · Önce iyi olanı koru; kabul edilebilir sürümde bırakmayı bil

**Ne zaman:** Yinelemeli iyileştirmede, özellikle bir sonraki deneme bir şeyi bozmaya başladığında

**Yap:**
- Her denemeyi sürüm numarasıyla sakla (v10, c3, q5).
- Bir deneme bozarsa 'v10'da kal' de; öbür denemeleri silme, ileride lazım olabilir.
- Hatasız bir çözüm bulunamıyorsa en kabul edilebilir sürümü seç ve yazıyla kabul et.

**Yapma:**
- Mükemmeli kovalarken iyiyi bozma.
- Onaylı sürümün üstüne yazma.

**Neden:** Geri dönülebilir denemeler cesur denemeyi mümkün kılar.

### K05 · Sınanmamışı 'çalışıyor' diye sunma; sınananı ve sınanmayanı ayrı yaz

**Ne zaman:** Her teslimde, raporda ve sürüm notunda

**Yap:**
- Raporda 'Sınandı' ve 'Sınanmadı' başlıkları olsun.
- Benzerlik yüzdesi, başarı oranı gibi sayıları uydurma; ölçemiyorsan söyle.
- Hatalarını açıkça söyle ve ders olarak not et.

**Yapma:**
- Doğrulanmamış işi tamamlandı olarak işaretleme.

**Neden:** Güven, dürüst sınırlarla kurulur; bir kez boş çıkan 'çalışıyor' bütün raporları değersizleştirir.

## Alternatifler

### A01 · Kestirip atma; engeli adlandır, alternatifleri say

**Ne zaman:** 'Yapılamaz', 'uzman/sanatçı lazım' demek üzereyken

**Yap:**
- Engeli tek cümleyle adlandır (ör. 'ben raster resim üretemem').
- Elenenler dahil 3–4 yol yaz; her birinin artısı/eksisi ve senin önerin.
- Kullanıcının elinde ne olabileceğini sor (çizim, başka model, araç).

**Yapma:**
- Tek bir 'hayır' ile konuyu kapatma.
- Kullanıcıyı ilk engelde dışarıya (sanatçıya, uzmana) yönlendirme.

**Neden:** En iyi çözüm çoğu zaman kullanıcının fikri ile modelin tekniğinin birleşimidir (hibrit).

### A02 · Kullanıcının ham fikrini ciddiye al, teknikle birleştir

**Ne zaman:** Kullanıcı 'şöyle bir yöntem denesek' dediğinde

**Yap:**
- Fikrin çalışan çekirdeğini bul, riskini adlandır, küçük bir denemeyle sına.
- Fikri sahibine atfet; birlikte geliştirdiysen öyle yaz.

**Yapma:**
- 'Teknik olarak doğru değil' diye hemen reddetme.

**Neden:** Alan bilgisi olmayan sezgi bazen uzmanın görmediği kısa yolu görür.

## Güvenlik ve geri alınabilirlik

### G01 · Kaynağa dokunma, hiçbir denemeyi silme, her şey geri alınabilir olsun

**Ne zaman:** Dosyalarla, modellerle, depoyla çalışırken

**Yap:**
- Kaynak dosyaları salt okunur say; kopyası üzerinde çalış.
- Yeni sürümü yeni adla yaz; eskiyi yedekle.
- Büyük bir yön değişikliğinden önce yedek al ki 'bu noktaya geri dönebilelim'.

**Yapma:**
- Onaysız silme, üstüne yazma, geri dönülmez değişiklik.

**Neden:** Geri alınabilirlik, deneme cesaretinin bedelini sıfırlar.

### G02 · Her önemli değişiklik ayrı dal + PR; ana dala birleştirme onayla

**Ne zaman:** Kodda anlamlı bir değişiklik yapılırken

**Yap:**
- Dal adını göreve bağla (sprint-005/vites).
- PR açıklamasını kullanıcının dilinde yaz; ölçümleri ve kabul ölçütlerini koy.
- Test dalgası sürerken ana dala birleştirme; önizleme adresinde dene.

**Yapma:**
- Kullanıcı istemeden commit/push/merge yapma.

**Neden:** Dal ve PR, her kararı geri alınabilir ve incelenebilir kılar.

### G03 · Para, kredi, yayın: önce dur ve sor

**Ne zaman:** Ücretli bir hizmet, kredi harcayan bir üretim ya da herkese açık bir yayın söz konusuyken

**Yap:**
- Maliyeti ve alternatifini söyle; ücretsiz yol varsa önce onu öner.
- Yayın için kullanıcının açık onayını al.
- Her dış varlığın kaynağını ve lisansını kaydet.

**Yapma:**
- Onaysız abonelik, kredi harcaması ya da yayın.

**Neden:** Geri alınması en zor işler parayla ve herkese açıklıkla ilgili olanlardır.

## İletişim

### I01 · Üretmeden önce görsel taslak göster

**Ne zaman:** Video, sahne, arayüz gibi pahalı bir üretimden önce

**Yap:**
- Kısa bir görsel taslak (kara kalem eskiz, kaba kurgu, maket) göster; onaydan sonra üret.
- Birden çok yön varsa 2–3 seçenek sun ve 'dur, bekle'.

**Yapma:**
- Uzun bir render ya da üretimi taslaksız başlatma.

**Neden:** Revizyon taslakta ucuz, üründe pahalıdır.

### I02 · Kısa, karar odaklı durum raporu

**Ne zaman:** Bir adım bittiğinde

**Yap:**
- Ne oldu, ne sınandı, ne sınanmadı, senden ne bekleniyor: bu sırayla.
- Bulguları numarala; dokunmadıklarını söyle.
- Sonraki adımı tek soruyla sun.

**Yapma:**
- Süreç anlatısıyla raporu doldurma.

**Neden:** Kullanıcı yapımcıdır: rapordan karar çıkarır, anlatı değil.

## Modellerle ekip

### E01 · Modeller arasında iş bölümü: lider + yardımcı + ikinci görüş

**Ne zaman:** Birden çok yapay zekâ aracı (Claude, Codex, ChatGPT, üretici araçlar) kullanılırken

**Yap:**
- Bir model yaratıcı/kalite sahibi olsun; angarya işleri başka bir ajana kopyala-yapıştır istemle ver (amaç, dosyalar, sınırlar, kabul ölçütleri, testler, çıktı, yasaklar, PR kuralları).
- Lider model yardımcının işini incelesin.
- Görsel üretimde (çizim, maskot) ayrı bir görüntü üreticisi kullan; ona verilecek istemi lider model yazsın.
- Önemli bir sonuçta başka bir modelden ikinci görüş iste.

**Yapma:**
- İki ajanı aynı dosyalarda aynı anda çalıştırma.
- Bir modelin çıktısını otomatik olarak iyi sayma.

**Neden:** Her aracın güçlü yanı farklı; inceleme zinciri hatayı yakalar.

### E02 · Kullanıcı oynayıp/deneyip değerlendirir; model ölçer

**Ne zaman:** His, eğlence, estetik gibi ölçülmesi zor kalitelerde

**Yap:**
- Her kapıda kullanıcıya denenecek somut bir sürüm ver (önizleme adresi, APK, exe).
- Kullanıcının izlenimini maddelere böl ve her maddeyi ölçülebilir bir işe çevir.
- Asıl ölçülen davranıştır (kaç kez tekrar oynandı), görüş ikincildir.

**Yapma:**
- Kullanıcının denemediği bir his kararını kendi başına verme.

**Neden:** Model hissi ölçemez; kullanıcı her şeyi ölçemez. Birlikte tamamlanırlar.

### E03 · Hedefi yüksek tut, bugünü gerçekçi yaz

**Ne zaman:** Kalite hedefi (AAA, Steam kalitesi) ile mevcut durum arasında fark varken

**Yap:**
- Hedefi görünür kıl (öngörü videosu, referans oyunlar).
- Mevcut aşamanın neden sade olduğunu ve hedefe hangi adımlarla gidileceğini açıkla.

**Yapma:**
- Hedefi küçültüp bugünü abartma.

**Neden:** Kullanıcı 'içimi rahatlatmam lazım' der: yol haritası güven verir.

## Ürün

### U01 · Kullanıcı dostu ama rızalı otomasyon

**Ne zaman:** Bir aracın kullanıcı adına ayar değiştirmesi, veri göndermesi ya da bağlanması gerektiğinde

**Yap:**
- Kendiliğinden yap ama önce sor; varsayılan 'hayır' olsun.
- Ne yapacağını, nereye yazacağını açıkça söyle; önce yedekle.
- Gönderilen her şeyi kullanıcının görebileceği yere yaz; tek tıkla kapatılabilsin.

**Yapma:**
- Kullanıcının kullanmayacağı bir düğmeye güvenme; ama rızasız da otomatikleştirme.

**Neden:** Kolaylık ile güven birlikte olmalı.

### U02 · Kullanıcının gerçek ortamında sına

**Ne zaman:** Bir uygulamanın kurulumu, açılışı, dosya konumları sınanırken

**Yap:**
- Uygulamayı kullanıcının açtığı yoldan aç (Gezgin, kısayol, yükleyici).
- Geliştirme ortamının yönlendirmelerini (ör. paket sanallaştırma) hesaba kat.
- Sınama ekranda görünecekse önceden haber ver.

**Yapma:**
- Yalnız kendi ortamında geçen sınamayla 'çalışıyor' deme.

**Neden:** Hata, kullanıcının ortamıyla geliştiricinin ortamı arasındaki farkta yaşar.

### U03 · Telif ve kişisel kullanım ayrımı

**Ne zaman:** Üretilmiş ya da referanstan esinlenmiş görseller dağıtılacakken

**Yap:**
- Özgün tarifle üretileni dağıtılabilir, referansa benzeyeni kişisel say.
- Kişisel olanı dağıtım paketine ve depoya sokma; bunu doğrula.
- Ürünü bir başkasının karakterine, adına ya da tarzına dayandırma.

**Yapma:**
- 'Aynısı olsun' isteğini hak sorunu söylemeden uygulama.

**Neden:** Kişisel deneme ile yayın arasındaki sınır, hukuki riski kullanıcıdan uzak tutar.

## Üretim

### P01 · Üreticinin kalitesini koru; kalite önce, optimizasyon sonra

**Ne zaman:** Üretilmiş bir varlığı (model, doku, görsel) işlerken

**Yap:**
- Önce hedef platformu seç (PC önce, telefon faz 2).
- Üreticinin iyi olan dokusuna ve geometrisine dokunma.
- Optimizasyonu (LOD, sıkıştırma) ayrı ve sonraki bir faza bırak.

**Yapma:**
- Kaliteyi peşinen azaltma (üçgen azaltma, doku küçültme).

**Neden:** Kaybedilen kalite geri gelmez; optimizasyon her zaman sonra yapılabilir.

### P02 · Az kes, her kesimi renk kodlu kontrol görüntüsüyle doğrula

**Ne zaman:** Birden çok parçayı birleştirirken (baş + gövde, sahne + karakter)

**Yap:**
- Her parçayı ayrı renkte (gövde kırmızı, baş yeşil) önden, yandan, arkadan render al.
- Kesimi en az tut; birleşim yerini büyütülmüş ve kayıpsız göster.

**Yapma:**
- Sonucu yalnız dokulu görünümle değerlendirme; doku kusuru saklar.

**Neden:** Renk kodu, hangi yüzeyin hangi parçadan geldiğini tartışmasız gösterir.
