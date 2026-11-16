# Faz 6: birleştirilmiş (safetensors) modeli GGUF'a çevirir, Q4_K_M'ye indirger ve Ollama'ya ekler.
# Kullanım: powershell -File egitim\aktar.ps1 -Kaynak <safetensors klasörü> -Ad boru-4b [-Egitim "D:\Game Projects\boru-egitim"]
param([Parameter(Mandatory)][string]$Kaynak, [Parameter(Mandatory)][string]$Ad, [string]$Egitim = "D:\Game Projects\boru-egitim")
$ErrorActionPreference = "Stop"
$py = Join-Path $Egitim ".venv\Scripts\python.exe"; $lc = Join-Path $Egitim "llama.cpp"
$f16 = Join-Path $Egitim "$Ad-f16.gguf"; $q4 = Join-Path $Egitim "$Ad-Q4_K_M.gguf"
$env:PYTHONPATH = Join-Path $lc "kaynak\gguf-py"
& $py (Join-Path $lc "kaynak\convert_hf_to_gguf.py") $Kaynak --outfile $f16 --outtype f16
if ($LASTEXITCODE) { throw "GGUF çevirisi olmadı" }
& (Join-Path $lc "bin\llama-quantize.exe") $f16 $q4 Q4_K_M
if ($LASTEXITCODE) { throw "nicemleme olmadı" }
Remove-Item $f16                                   # 8 GB'lık ara dosya; Q4_K_M ve safetensors kaynak kalır
# şablon ve duruş parametreleri Ollama'daki Qwen3 4B Instruct'tan (aynı temel model)
$o = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
$mf = (& $o show qwen3:4b-instruct-2507-q4_K_M --modelfile) -join "`n"
$mf = [regex]::Replace($mf, '(?m)^FROM .*$', "FROM `"$q4`"")
$yol = Join-Path $Egitim "$Ad.Modelfile"; [IO.File]::WriteAllText($yol, $mf, (New-Object Text.UTF8Encoding $false))
& $o create $Ad -f $yol
if ($LASTEXITCODE) { throw "ollama create olmadı" }
Write-Output "TAMAM: $Ad ($q4)"
