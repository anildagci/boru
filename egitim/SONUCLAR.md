# Faz 6: boru-4b ince ayarı — sonuçlar (16 Kasım 2026)

**Karar: yayınlanmadı.** Model, geliştiricinin yazdığı görülmemiş sorularda %80'lik kapıya ulaşmadı.

## Ne yapıldı
- **Temel model:** Qwen3-4B-Instruct-2507. QLoRA (4-bit nf4, r=16, alpha 32, 2 tur), tek bir RTX 3060 (12 GB).
- **Veri (damıtma):** Sorular hızlı modelle, her kuralın "tetik" olaylarından üretildi. Yanıtları yerel düşünen model (qwen3:4b) BÖRÜ'nün çalışma bağlamıyla yazdı. Otomatik elek dili, döngüyü, uzunluğu ve doğru kuralın anılıp anılmadığını denetledi. Eğitim verisinde Claude ya da başka bir bulut modelinin metni yok.
  - v1: 144 örnek.
  - v2: 480 örnek. Kod ve oyun alanları eklendi; hedef kural bağlamda rastgele sıraya kondu.
- **Ölçüm:** [`olc.py`](olc.py) her modele soruyu BÖRÜ'nün gerçek bağlamıyla sorar. Ölçütler:
  - yanıt sorunun dilinde mi,
  - kabul edilen bir kural kimliği anılmış mı,
  - döngü var mı,
  - kural tersine uygulanmış mı (yasak kalıplar).

  Kapı: dil %100, kural ≥ %80, döngü 0, ters 0.
- **Ölçüm setleri:** Kabul edilen kurallar ve yasak kalıplar, yanıtlar görülmeden işaretlendi.
  - [`olcum_seti.json`](olcum_seti.json): 60 soru. Bu seti Claude yazdı ve sonuçları gördü; iyimser.
  - [`olcum_taze.json`](olcum_taze.json) ve [`olcum_taze2.json`](olcum_taze2.json): 20'şer soru, geliştirici yazdı.

## Sonuçlar (doğru kural oranı; hepsinde dil %100, ters 0)

| Set | boru-4b v2 | boru-4b v1 | Qwen3 4B Instruct | Qwen3 4B düşünme (öğretmen) |
|---|---|---|---|---|
| 60 soru (Claude yazdı) | %86 | %84 | %82 | %79 |
| Taze 20 (proje soruları) | %75 | %75 | %80 (1 döngü) | %85 |
| Taze 20 (geniş, açık uçlu) | %55 | %65 | %45 | %55 (1 döngü) |
| **Geliştiricinin 40 sorusu** | %65 | **%70** | %63 | **%70** |
| Ortalama süre | ~1,5 sn | ~1,5 sn | 2-13 sn | 25-43 sn |

## Ne öğrendik
1. **Öğrenci öğretmenini geçmiyor.** 4B'lik öğretmenden damıtılan model öğretmeninin isabetine ulaştı. Üstelik 20-30 kat hızlı, döngüsüz ve dil kaymasız. Ama onu geçmedi; veriyi üçe katlamak da tavanı kaldırmadı.
2. **Asıl darboğaz kural aramasıydı.** Yeni arama doğru kuralı ölçüm sorularının %93'ünde ilk 4'e getiriyor (önce %82). Bu değişiklik 0.6.2'de ve yerel model açık olsun olmasın herkese yarıyor. Yeni arama şunları yapıyor:
   - tetikleri ve yap/yapma metinlerini de tarar,
   - Türkçe ekleri kaba bir kökle eşler,
   - nadir sözcüklere daha çok ağırlık verir.
3. **Kendi yazdığın test iyimserdir.** Claude'un yazdığı 60 soruda v1 kapıyı geçti (%84), geliştiricinin sorularında kaldı (%75). Yayın kararı yalnız görülmemiş, başkasının yazdığı sorularla verildi.
4. **Geniş istekler kural kapsamının dışında.** "30 günlük plan" ya da "3 içerik fikri" gibi isteklere modeller makul yanıt verip kural anmadı. Bu, ürünün sınırı hakkında bir bulgu.

## Sonraki olası adım (90 günlük odaktan sonra, veriye göre)
Daha büyük bir öğretmen, örneğin 14B (12 GB karta sığar), ya da insan gözünden geçmiş örnekler.

## Dosyalar
| Dosya | Ne yapar |
|---|---|
| [`tetikler.py`](tetikler.py) | Kurallara tetik olaylarını yazar |
| [`veri_uret.py`](veri_uret.py) | Soru ve yanıt üretimi, elek |
| [`egit.py`](egit.py) | QLoRA eğitimi; ölçüm sorularını dışarıda bırakır |
| [`aktar.ps1`](aktar.ps1) | llama.cpp ile GGUF, Q4_K_M ve Ollama |
| [`olc.py`](olc.py) | Ölçüm; `BORU_OLCUM_SET` ile başka bir set seçilir |
