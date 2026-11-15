# BÖRÜ maskotu: görüntü üretici için prompt ve kare listesi

Amaç: kurt penceresindeki çizimin yerine, referans görselin kalitesinde ama **özgün** bir kurt. Altı hal aynı karakter,
aynı ölçek, aynı duruşta olmalı ki karelerin arası geçişte "zıplama" olmasın.

## Neden tek sayfa

Üreticiler aynı karakteri ayrı ayrı istenen görsellerde birebir tutturamıyor. Altı hali **tek görselde, 3×2 ızgarada**
istemek tutarlılığı en çok artıran yol. Sayfayı ben keserim (BÖRÜ'nün "kes" adımıyla aynı mantık).

## 1. Prompt (ChatGPT'ye olduğu gibi yapıştır)

```
Create a character sheet of ONE original anime-style wolf mascot, shown 6 times in a 3 columns x 2 rows grid.
Transparent background (if not possible: plain flat white background). No text, no labels, no scenery, no props except
those listed. Every cell: the SAME wolf, same size, same camera angle (front, very slightly three-quarter), sitting
upright, whole body visible including tail and paws, centered in its cell with empty space around it. Cells must not
touch or overlap.

The wolf: a young but wise wolf, painted anime illustration quality with soft cel shading and visible fur tufts.
Dark charcoal fur with a cool navy tint. White facial mask: white muzzle, white cheeks, two small white marks above
the eyes. Bright ice-blue eyes with a clear highlight. Large fluffy white chest ruff. White tip on a bushy tail.
Inner ears light grey-pink. A thin dark outline around the whole figure.
Signature item: a short deep-red neckerchief with a small gold geometric kilim-like pattern (stays identical in all cells).

Cells, left to right, top to bottom:
1. Calm: sitting, gentle confident look, slight closed-mouth smile, ears up.
2. Blink: EXACTLY the same pose and expression as cell 1, only the eyes closed.
3. Working: focused eyes looking slightly down at a small glowing blue wireframe cube floating in front of its chest,
   one front paw raised toward it.
4. Happy: eyes closed in a happy smile, mouth open, ears perked, tail raised.
5. Worried: ears pulled back, brows raised, small frown, tail low.
6. Asking: head tilted, one front paw slightly raised, curious open eyes, as if asking a question.

Keep proportions, colors, markings and the neckerchief identical across all six cells.
```

İstersen sonuna şunu ekle: `Square image, high resolution.`

## 2. Kontrol listesi (üretince bak)

1. Altı hücrede de **aynı kurt** mu: renkler, beyaz maske, göğüs yelesi, kırmızı boyunluk aynı mı?
2. 1 ve 2 numara **birebir aynı** mı (yalnız gözler kapalı)? Değilse göz kırpma zıplar; bu hücreyi yeniden istemek gerekir.
3. Hücreler birbirine değmiyor mu, kuyruk ya da kulak kesilmiş mi?
4. Zemin şeffaf ya da düz beyaz mı (gölge, zemin çizgisi yok)?
5. Yazı, imza, filigran yok mu?

Tutmayan bir hücre olursa ChatGPT'ye "keep everything the same, only redo cell 2 so that it matches cell 1 exactly
except closed eyes" gibi tek düzeltme iste.

## 3. Teslim

Görseli (PNG tercih) bu klasöre koy: `paceborn-3d/BORU/maskot/`. Adı önemli değil. Birden fazla deneme koyabilirsin;
en iyisini birlikte seçeriz. Ben keserim, kenarlarını pencereye uygun hale getiririm ve BÖRÜ'ye yerleştiririm.

## 4. Hak notu

- Referans görselin kendisi ya da başka bir karakterin adı / tarzı prompt'a yazılmadı; kurt özgün tarif edildi.
- Satıştan önce kullandığın üreticinin ticari kullanım şartlarına bak (hukuki görüş değildir).
