# Faz 6: Qwen3-4B-Instruct-2507'yi BÖRÜ verisiyle QLoRA (4-bit) ince ayarlar, LoRA'yı birleştirip safetensors olarak kaydeder.
# RTX 3060 12 GB için ayarlı. Kayıp yalnız yanıt (assistant) kısmında hesaplanır; sistem bağlamı ve soru maskelenir.
# Kullanım (eğitim ortamının python'u ile):
#   python egitim/egit.py --temel <Qwen3-4B-Instruct-2507 klasörü> --veri egitim.jsonl [--veri ornekler.jsonl] --cikti <klasör>
import os, sys, json, math, random, argparse, time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, get_cosine_schedule_with_warmup
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, PeftModel

ap = argparse.ArgumentParser()
ap.add_argument("--temel", required=True); ap.add_argument("--veri", action="append", required=True); ap.add_argument("--cikti", required=True)
ap.add_argument("--tur", type=float, default=2); ap.add_argument("--oran", type=float, default=2e-4); ap.add_argument("--r", type=int, default=16)
ap.add_argument("--uzunluk", type=int, default=3072); ap.add_argument("--birikim", type=int, default=8); ap.add_argument("--dogrulama", type=float, default=0.05)
a = ap.parse_args(); os.makedirs(a.cikti, exist_ok=True); random.seed(6); torch.manual_seed(6)

# ölçüm setindeki sorular eğitime sızmasın
import glob
OLCUM = {s["soru"] for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "olcum_*.json"))
         for s in json.load(open(f, encoding="utf-8"))["sorular"]}
ornek = []
for f in a.veri:
    for l in open(f, encoding="utf-8"):
        d = json.loads(l)
        if d["messages"][-2]["content"] not in OLCUM:
            ornek.append(d["messages"])
random.shuffle(ornek)
nd = max(4, int(len(ornek) * a.dogrulama)); dogru, egitim = ornek[:nd], ornek[nd:]
print("örnek: eğitim %d, doğrulama %d" % (len(egitim), len(dogru)), flush=True)

tok = AutoTokenizer.from_pretrained(a.temel)


def kodla(m):
    istem = tok.apply_chat_template(m[:-1], tokenize=False, add_generation_prompt=True)
    tam = istem + m[-1]["content"] + "<|im_end|>\n"
    i = tok(istem, add_special_tokens=False)["input_ids"]; t = tok(tam, add_special_tokens=False)["input_ids"][:a.uzunluk]
    etiket = [-100] * min(len(i), len(t)) + t[len(i):]
    return torch.tensor([t]), torch.tensor([etiket])


E = [kodla(m) for m in egitim]; D = [kodla(m) for m in dogru]
print("en uzun örnek %d token" % max(x[0].shape[1] for x in E + D), flush=True)

nicem = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
mdl = AutoModelForCausalLM.from_pretrained(a.temel, quantization_config=nicem, dtype=torch.bfloat16, device_map={"": 0})
mdl = prepare_model_for_kbit_training(mdl, use_gradient_checkpointing=True)
mdl = get_peft_model(mdl, LoraConfig(r=a.r, lora_alpha=2 * a.r, lora_dropout=0.05, task_type="CAUSAL_LM",
                                     target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
mdl.print_trainable_parameters()
opt = torch.optim.AdamW([p for p in mdl.parameters() if p.requires_grad], lr=a.oran, weight_decay=0.0)
adim = math.ceil(len(E) * a.tur / a.birikim); plan = get_cosine_schedule_with_warmup(opt, max(1, adim // 10), adim)


def dogrula():
    mdl.eval(); top = 0.0
    with torch.no_grad():
        for x, y in D:
            top += mdl(input_ids=x.cuda(), labels=y.cuda()).loss.item()
    mdl.train(); return top / len(D)


gunluk = []; print("başlangıç doğrulama kaybı %.4f" % dogrula(), flush=True); t0 = time.time(); k = 0; toplam = 0.0
mdl.train()
for tur in range(math.ceil(a.tur)):
    sira = list(range(len(E))); random.shuffle(sira)
    if tur + 1 > a.tur:
        sira = sira[:int(len(E) * (a.tur - tur))]
    for j, i in enumerate(sira):
        x, y = E[i]
        kayip = mdl(input_ids=x.cuda(), labels=y.cuda()).loss / a.birikim; kayip.backward(); toplam += kayip.item()
        if (j + 1) % a.birikim == 0:
            torch.nn.utils.clip_grad_norm_(mdl.parameters(), 1.0); opt.step(); plan.step(); opt.zero_grad(); k += 1
            if k % 5 == 0:
                print("adım %d/%d  kayıp %.4f  %.0f sn" % (k, adim, toplam / 5, time.time() - t0), flush=True); gunluk.append({"adim": k, "kayip": toplam / 5}); toplam = 0.0
    dk = dogrula(); print("tur %d bitti: doğrulama kaybı %.4f" % (tur + 1, dk), flush=True); gunluk.append({"tur": tur + 1, "dogrulama": dk})

lora = os.path.join(a.cikti, "lora"); mdl.save_pretrained(lora); tok.save_pretrained(lora)
json.dump({"arg": vars(a), "gunluk": gunluk, "egitim": len(E), "dogrulama": len(D), "sure_sn": round(time.time() - t0)},
          open(os.path.join(a.cikti, "egitim_gunlugu.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# birleştir: bf16 temel model (CPU) + LoRA -> tam model
del mdl, opt; torch.cuda.empty_cache()
temel = AutoModelForCausalLM.from_pretrained(a.temel, dtype=torch.bfloat16, device_map={"": "cpu"})
tam = PeftModel.from_pretrained(temel, lora).merge_and_unload()
hedef = os.path.join(a.cikti, "birlesik"); tam.save_pretrained(hedef, safe_serialization=True); tok.save_pretrained(hedef)
print("BİTTİ:", hedef, flush=True)
