<p align="center"><img src="boru_simge.png" width="120" alt="BÖRÜ"></p>

<h1 align="center">BÖRÜ</h1>
<p align="center"><b>A meticulous wolf that sits beside your AI model.</b><br>
It measures every step, explains it in writing, stops what breaks your rules, and asks <i>you</i> before anything permanent.</p>
<p align="center"><a href="README.tr.md">Türkçe</a> · <a href="https://github.com/anildagci/boru/releases">Download</a> · <a href="#roadmap">Roadmap</a></p>

---

> **I got tired of AI coding assistants confidently breaking things. So I built a watchdog for them.**
>
> Meet **BÖRÜ** — a free, open-source desktop companion for Claude Code and Codex.
>
> It watches project changes, checks risky actions against your rules, and asks for approval before critical operations.
>
> It also includes MCP tools for Blender workflows.
>
> Open source. Local-first. Built from real problems I encountered while developing games and 3D characters.
>
> **GitHub:** https://github.com/anildagci/boru

BÖRÜ is a free, open-source helper for people who work with AI coding assistants such as **Claude Code** and **Codex**.
It connects to them over [MCP](https://modelcontextprotocol.io) and lives on your desktop as a small wolf.

Its first specialist pack drives your installed **Blender** along the path *from a drawing to a game-ready 3D character*:
inspect a model, find the eyes, fit a generated head onto a body, merge into one model with one texture, export, verify,
deliver. The long-term goal is broader: a general **AI-usage assistant** that carries a proven working method
(clarify first, measure don't guess, never destroy work, ask before permanent actions) and, step by step, its own small
language model trained on what it learns.

| The model wants to deliver | The watchdog caught a change | First launch |
|---|---|---|
| <img src="docs/img/onay_en.png" width="250"> | <img src="docs/img/onay_tr.png" width="250"> | <img src="docs/img/baglanti_en.png" width="250"> |

## Why

AI models are fast and creative, and sometimes confidently wrong. BÖRÜ is the strict partner next to them:

- **Measures instead of guessing.** Every tool answers with numbered findings (triangle counts, parts, textures,
  alignment), lists what it did *not* touch, and returns images the model can look at.
- **Watchdog.** Before every call it compares the working folder with its last snapshot. Changed source files, deleted
  attempts, overwritten deliveries, dropped triangle counts or shrunk textures are reported; rule-breaking changes stop
  the work until you say *Continue*.
- **You approve, not the model.** Deliveries, rule changes and decisions are asked in BÖRÜ's own window. The answer
  comes only from your click.
- **Learns, carefully.** It keeps a local log and turns recurring situations into *lesson candidates* with evidence.
  Nothing changes BÖRÜ's behaviour on its own; approved lessons go into the next version.
- **Your mascot.** Pick the wolf, or create your own mascot in three steps (describe → generate → choose image).
- **Turkish and English.**

## Install

1. Download `BORU_Kurulum_<version>.exe` from [Releases](https://github.com/anildagci/boru/releases) and run it.
   No administrator rights needed. The installer is not code-signed yet, so Windows may say *Unknown publisher*:
   click *More info → Run anyway*.
2. Install [Blender 5](https://www.blender.org) for the 3D pack (BÖRÜ finds it on its own).
3. Open BÖRÜ. If Claude Code or Codex is installed and not connected, the wolf offers to connect
   (it backs up the settings file and writes only the `boru` entry). Restart that app.
4. In Claude Code or Codex, ask for example: *"Using BÖRÜ, inspect this model and fit the head onto the body."*

<details><summary>Manual connection</summary>

**Claude Code** — `.mcp.json` in your project (or `~/.claude.json` → `mcpServers`):
```json
{ "mcpServers": { "boru": { "type": "stdio", "command": "C:\\Users\\<you>\\AppData\\Local\\Programs\\BORU\\BORU.exe", "args": ["--mcp"] } } }
```
**Codex** — `~/.codex/config.toml`:
```toml
[mcp_servers.boru]
command = 'C:\Users\<you>\AppData\Local\Programs\BORU\BORU.exe'
args = ["--mcp"]
tool_timeout_sec = 900
```
Long 3D steps take minutes at full resolution; keep the tool timeout generous.
</details>

## Tools (MCP)

| Tool | What it does |
|---|---|
| `boru_basla` | Start: working folder + mode (`arac`: only BÖRÜ's tools, or `hibrit`: your own Blender scripts too) |
| `boru_durum` | Folder state: attempts, delivery, mode |
| `boru_incele` | Look at a GLB without touching it: triangles, parts, textures, 8-angle colour and clay renders |
| `boru_gozler` | Render the face from the front and find both eyes (alignment anchor) |
| `boru_oturt` | Fit a single-part head onto a body, aligned by the eyes; red/green check renders |
| `boru_birlestir` | One model, one texture; export; reopen and verify |
| `boru_teslim` | Deliver (backs up the previous one) — **asks you in the window** |
| `boru_kontrol` | Measure any .blend/.glb and render front/back |
| `boru_denetle` | Watchdog check; measures new models against the reference |
| `boru_not` / `boru_dersler` | Experience notes; lesson candidates with evidence |

### Working-with-AI assistant (any task, no folder needed)

| Tool | What it does |
|---|---|
| `boru_yontem` | Brings the working rules that fit your situation (when / do / don't / why). Empty question → catalogue |
| `boru_risk` | Give it a plan before a long job; it lists what to clarify first (deletion, overwrite, money, publishing, guessing, wide scope, no tests, no approval gate) |
| `boru_liste` | Checklists: project start, pre-delivery quality, briefing a helper agent, visual review |
| `boru_profil` | Reads *your* private working profile from `Documents\BORU\ozel\PROFIL.md`, if you write one. It never leaves your computer |

| `boru_sor` | Ask BÖRÜ's **local small model** a method question; it answers from the rules (and your private profile). Falls back to the rules when the model is off |
| `boru_model` | Local model status; setting it up asks **you** in the window |

### Local small model (optional)

BÖRÜ can run a small open model on your own graphics card through [Ollama](https://ollama.com) (free, open source).
Default model: **Qwen3 4B** (Apache-2.0, ~2.5 GB download, runs comfortably on a 6 GB+ GPU).

- Off by default. Right-click the wolf > **Local model…**. If Ollama isn't installed, BÖRÜ opens its download page
  (BÖRÜ never installs programs). The model is downloaded only after you click **Yes**.
- Right-click > **Ask BÖRÜ…** opens a small question window. Claude Code / Codex can ask through `boru_sor`.
- Everything stays on your computer. The model is loaded into GPU memory only when asked, and leaves after 5 idle minutes.
- Two modes (right-click > Local model): **accurate** (default; the thinking Qwen3 4B, ~30 s per answer) and **fast**
  (Qwen3 4B Instruct, extra ~2.5 GB download, ~1-5 s; good English, weaker Turkish, doesn't use your private profile).
  Measured on the same 6 questions, Nov 2026.
- It is a small model: answers are short and grounded in the 25 rules, but check them.

The rules live in [`bilgi/kurallar.json`](bilgi/kurallar.json) and are readable as
[a method guide](bilgi/YONTEM.en.md) ([Türkçe](bilgi/YONTEM.tr.md)). 25 rules, distilled from real AI-assisted projects
(game development, 3D characters, social video production, this tool). [`bilgi/ornekler.jsonl`](bilgi/ornekler.jsonl) is
the same knowledge as chat-format training examples for the small model planned in phases 5–6, also on
Hugging Face: [downstroke/boru-yontem](https://huggingface.co/datasets/downstroke/boru-yontem).

## Privacy

Everything stays on your computer: settings, log, lessons and your own mascots live in `Documents\BORU`.
**By default BÖRÜ sends nothing.** On first launch it asks once whether you want to send an *anonymous* weekly usage
summary (counts and lesson candidates; no file, folder or person names, no notes, no images). Everything it would send is
first written to `Documents\BORU\gonderilenler` so you can see it; you can turn it off any time. Details:
[PRIVACY.md](PRIVACY.md).

## Honest limits

- Without the optional local model, the assistant tools match keywords; they don't understand. The local model is a small 4B model, not a replacement for Claude or GPT.
- The head-to-body fit is tested on two collar types (t-shirt neckline, high jacket collar) and two characters.
- Eye detection thresholds were measured on four images; a face covered by hair may fail (BÖRÜ says so).
- Windows only for now. Unsigned installer.

## Build from source

Python 3.11+ with `pyinstaller numpy opencv-python pillow`, then `derle.bat` (→ `dist\BORU.exe`) and
`kurulum\kurulum_derle.bat` (Inno Setup 6, → `kurulum\cikti\`). Run from source: `python boru.py` (window) or
`python boru.py --mcp` (MCP server). GitHub Actions builds both on every tag.

## Roadmap

1. ✅ Publish: two languages, installer, this repo.
2. ✅ Opt-in anonymous feedback (consent, see-what-is-sent, off by default).
3. ✅ Knowledge: a written working method distilled from real AI-assisted projects.
4. ✅ Assistant tools: project start checklist, quality control, "let's clarify this first", alternatives.
5. ✅ A small local model (downloaded only with consent, runs on your GPU only when needed).
6. 🔧 Fine-tuning (in progress): `boru-4b`, Qwen3 4B Instruct tuned on BÖRÜ's method with data distilled from the local
   thinking model, released only if it passes a held-out test.
7. Independence: a bundled llama.cpp runtime instead of Ollama (started only when needed), models served from BÖRÜ's own
   Hugging Face repo. No outside service needed to run BÖRÜ.
8. BÖRÜ's own tiny models, trained from scratch on BÖRÜ data (a few MB, instant on CPU): rule picker (replaces keyword
   matching), risk detector, personal-data finder, quality scorer.
9. A smaller family: `boru-1.7b` and `boru-0.6b`, distilled from `boru-4b`, for computers without a GPU and, later, phones.
10. Opt-in example sharing, separate from feedback: questions and answers from the local model, shown before sending,
    personal data removed, off by default. The source of real Turkish/English examples.
11. A gated data loop, every release: tiny models clean incoming data → curated dataset → training → held-out test **and**
    human review (no release without both) → new version. When a better open base model appears, the same pipeline and
    the accumulated data turn it into BÖRÜ.

What this means: BÖRÜ's conversational model stays a descendant of Qwen (Apache-2.0, credited) — training a general
language model from scratch is beyond any single GPU. What becomes BÖRÜ's own is the data, the pipeline, the tiny
models and the method. Each user's BÖRÜ runs entirely on their own computer; nothing depends on the maintainer's machine.

### Skill packs (after phase 7)

12. **BÖRÜ skill packs**, usable offline. In a pack the *tool* does the work and the model only fills in the settings:
    method notes and checklists for the craft, offline scripts (e.g. video: cut/join/subtitles with ffmpeg; presentations:
    slides from templates), openly licensed sample material with recorded sources, and a hand-off: for something new, BÖRÜ
    asks the user for material or passes the job to Claude/Codex when connected and checks the result. The 3D pack is the
    first. Only packs whose licence allows redistribution; no copying of third-party skills that don't.
13. A pack-making guide so anyone can build and share packs.

### Getting BÖRÜ to people

- Listings in MCP directories (official MCP Registry, Smithery, Glama, awesome-mcp-servers).
- Short demo videos (30-60 s) of real moments, e.g. BÖRÜ stopping an AI from deleting files; storyboard first.
- Turkish first: a Turkish-speaking, fully local, open-source assistant for working with AI — shared in Turkish developer
  and game-dev communities.
- A build story after phase 6: fine-tuning a model on a single RTX 3060 (r/LocalLLaMA, r/ClaudeAI, Show HN; r/blender for
  the 3D pack).
- Identity: Börü, the wolf of Turkic myth; the mascot and the make-your-own-mascot wizard.
- A signed installer (free signing for open-source projects, e.g. SignPath Foundation) so Windows doesn't warn on install.

## License

GPL-3.0 (see [LICENSE](LICENSE)); the Blender scripts must stay GPL-compatible. © 2026 DownStroke Studios.
