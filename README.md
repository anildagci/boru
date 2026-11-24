<p align="center"><img src="boru_simge.png" width="120" alt="BÖRÜ"></p>

<h1 align="center">BÖRÜ</h1>
<p align="center"><b>The wolf on your desktop that looks after you and your project while you make games with AI.</b><br>
It watches Claude work, reacts, and warns you if it tries to delete your project.</p>
<p align="center"><a href="README.tr.md">Türkçe</a> · <a href="https://github.com/anildagci/boru/releases">Download</a> · <a href="#roadmap">Roadmap</a> · <a href="#downstroke-studios">DownStroke Studios</a></p>

---

BÖRÜ is a free, open-source desktop companion for people who build games (and other projects) with AI assistants such
as **Claude Code** and **Codex**. It sits in the corner of your screen as a small wolf:

- **Live wolf.** It gets busy while Claude edits files, pricks up its ears and warns you about a risky command, and
  cheers when the job is done.
- **Watchdog.** AI can be confidently wrong: it deletes the wrong folder or overwrites a scene you spent weeks on. BÖRÜ
  is there for those moments, and leaves permanent decisions to you.
- **Method.** 25 working rules and checklists distilled from real projects, so you lose less work with AI.
- **3D pack.** Drives your installed Blender from a drawing to a game-ready 3D character.

<p align="center"><img src="docs/img/canli_kurt_tr.png" width="760" alt="Live wolf: busy while a file is edited, worried at a delete command, happy when the step is done"></p>

> **Where it stands today:** the live wolf is new and for now **only watches and warns; it never stops anything**. The
> watchdog only covers the 3D pack's folders and detects outside changes afterwards. Stopping actions before they happen
> and one-click undo are the work of the next 90 days. Details: [Honest limits](#honest-limits).

## What it does

### Live wolf (new, Claude Code)
Right-click the wolf > **Live wolf (Claude Code)…** > **Turn on**, then restart Claude Code (in the terminal or in the
*Code* tab of the Claude desktop app). From then on:

| What Claude does | What the wolf does |
|---|---|
| Starts on a request | Gets to work: "I'm watching too." |
| Edits or writes a file | Stays busy, names the file |
| Runs a risky command (delete, `git reset --hard`, force push…) | Gets worried: "Careful: Claude is deleting files." |
| Is waiting for you | Calls you |
| Finishes the step | Cheers |

Updates stay on your computer (`127.0.0.1`); if BÖRÜ is closed, Claude Code just carries on. BÖRÜ adds only its own
entries to Claude Code's settings file (`~/.claude/settings.json`), after a backup, and removes only those when you turn
it off from the same menu.

### Watchdog and approval
Before every BÖRÜ tool call it compares the working folder with its last snapshot. Changed source files, deleted
attempts, overwritten deliveries, dropped triangle counts or shrunk textures are reported; rule-breaking changes stop the
work until you say *Continue*. Deliveries and rule changes are asked in BÖRÜ's own window; the answer comes only from
your click.

### Working with AI (any task)
`boru_yontem` brings the working rules that fit your situation, `boru_risk` scans a plan before a long job and lists what
to clarify first, `boru_liste` gives checklists, `boru_profil` reads your private working profile. 25 rules:
[method guide](bilgi/YONTEM.en.md) ([Türkçe](bilgi/YONTEM.tr.md)).

### 3D pack: from a drawing to a game-ready character
With your installed **Blender**: inspect, find the eyes, fit a generated head onto a body, merge into one model with one
texture, export, verify, deliver. Every step answers with numbered findings and lists what it did *not* touch.

### Your mascot
Pick the wolf, or create your own mascot in three steps (describe → generate → choose image). Made your own wolf, cat
or dragon? Share it; we'll show the best ones here.

## Install

1. Download `BORU_Kurulum_<version>.exe` from [Releases](https://github.com/anildagci/boru/releases) and run it.
   No administrator rights needed. The installer is not code-signed yet, so Windows may say *Unknown publisher*:
   click *More info → Run anyway*. (A signed installer is in the 90-day plan.)
2. Open BÖRÜ. If Claude Code or Codex is installed and not connected, the wolf offers to connect (it backs up the
   settings file and writes only the `boru` entry). Restart that app.
3. Optionally turn on the live wolf: right-click > **Live wolf (Claude Code)…**.
4. For the 3D pack, install [Blender 5](https://www.blender.org) (BÖRÜ finds it on its own).

The live wolf is in the source code now and ships in the installer with the next release (0.7).

<details><summary>Manual connection</summary>

**Claude Code** — `.mcp.json` in your project (or `~/.claude.json` → `mcpServers`):
```json
{ "mcpServers": { "boru": { "type": "stdio", "command": "C:\\Users\\<you>\\AppData\\Local\\Programs\\BORU\\BORU.exe", "args": ["--mcp"] } } }
```
**Live wolf** — `~/.claude/settings.json` → `hooks` (BÖRÜ writes this for you):
```json
{ "hooks": {
  "UserPromptSubmit": [{ "hooks": [{ "type": "http", "url": "http://127.0.0.1:47391/kanca", "timeout": 3 }] }],
  "PreToolUse":       [{ "matcher": "*", "hooks": [{ "type": "http", "url": "http://127.0.0.1:47391/kanca", "timeout": 3 }] }],
  "Notification":     [{ "hooks": [{ "type": "http", "url": "http://127.0.0.1:47391/kanca", "timeout": 3 }] }],
  "Stop":             [{ "hooks": [{ "type": "http", "url": "http://127.0.0.1:47391/kanca", "timeout": 3 }] }] } }
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

### Working with AI (any task, no folder needed)

| Tool | What it does |
|---|---|
| `boru_yontem` | Brings the working rules that fit your situation (when / do / don't / why). Empty question → catalogue |
| `boru_risk` | Give it a plan before a long job; it lists what to clarify first (deletion, overwrite, money, publishing, guessing, wide scope, no tests, no approval gate) |
| `boru_liste` | Checklists: project start, pre-delivery quality, briefing a helper agent, visual review |
| `boru_profil` | Reads *your* private working profile from `Documents\BORU\ozel\PROFIL.md`, if you write one. It never leaves your computer |
| `boru_sor` / `boru_model` | Experimental local model (see below): ask a method question / model status |

### 3D pack

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

## Experimental: local small model (frozen)

BÖRÜ can run a small model (Qwen3 4B) on your own graphics card through [Ollama](https://ollama.com). Off by default;
downloaded only after you click **Yes**. It keeps working as it is but is **no longer developed**: the attempt to
fine-tune our own model did not reach its target (see [`egitim/SONUCLAR.md`](egitim/SONUCLAR.md), in Turkish), and users
already have Claude or Codex. The rules are also a dataset on Hugging Face:
[downstroke/boru-yontem](https://huggingface.co/datasets/downstroke/boru-yontem).

## Privacy

Everything stays on your computer: settings, log, the live-wolf log (`kanca_gunlugu.jsonl`), lessons and your own mascots
live in `Documents\BORU`. **By default BÖRÜ sends nothing.** On first launch it asks once whether you want to send an
*anonymous* weekly usage summary; everything it would send is first written to `Documents\BORU\gonderilenler`. Details:
[PRIVACY.md](PRIVACY.md).

## Honest limits

- **The live wolf only watches.** It notices a risky command and warns, but does not stop it. Risky-command detection is a
  pattern list; it may miss a delete done by a script file, or a file whose contents are emptied. Claude Code only for
  now; the Claude desktop chat and Cowork have no hook support (see the [hook research](docs/KANCA_ARASTIRMASI.md), in Turkish).
- **What the watchdog covers today:** only the 3D pack's working folders (`Source`, `Blender`, `Exports`, `Textures`,
  `Backups`); changes made outside BÖRÜ are detected **afterwards**, not prevented, and cannot be undone by BÖRÜ yet.
- The head-to-body fit is tested on two collar types and two characters; eye detection was measured on four images.
- Windows only for now. Unsigned installer.

## Build from source

Python 3.11+ with `pyinstaller numpy opencv-python pillow`, then `derle.bat` (→ `dist\BORU.exe`) and
`kurulum\kurulum_derle.bat` (Inno Setup 6, → `kurulum\cikti\`). Run from source: `python boru.py` (window) or
`python boru.py --mcp` (MCP server). Live-wolf test (no window, any OS): `python sinama/kanca_sinama.py`.
GitHub Actions builds both on every tag.

## Roadmap

**Done (0.4 - 0.6.2):** two-language release and installer; opt-in anonymous feedback; a 25-rule working method and
assistant tools; an optional local model; `boru-4b` fine-tuning (measured, missed the 80% gate, not released); hook
research ([results](docs/KANCA_ARASTIRMASI.md)).

### Next 90 days (Nov 2026 - Feb 2027): the wolf for people making games with AI

Audience: independent developers and artists making games with Claude Code or Codex (Godot, Unity, Blender). Local
model development has stopped. These 90 days are shared with one of the studio's game projects, so the scope is narrow.

**Month 1: bring the wolf to life**
- ✅ Live wolf, first version (watch only, Claude Code). In the source; ships with 0.7.
- Real testing on Windows: the Claude desktop *Code* tab, the terminal, long waits, behaviour while BÖRÜ is closed.
- More reactions: sleeping when nothing happens, celebrating a streak of successful steps, impatience on long jobs.
- Release 0.7 and the first short video: "My wolf watches Claude while it works."

**Month 2: let the wolf protect (and come to Blender)**
- **Blender add-on:** the wolf reacts to your own work, not just the AI's: it sleeps while you render, wakes when the
  render is done, barks if it crashes, and warns when the scene gets too heavy or a huge texture comes in. Works without Claude.
- **Backup first, then undo:** before a risky action, back up the files that will change; one click on the wolf to
  *Bring it back*. This is the real safety net for deletes the pattern list misses.
- **Ask before acting:** for deleting, overwriting or pushing to the main branch, the wolf asks and nothing happens
  until you say *Yes*.
- **Game project rules:** `Assets`, scene files (`.tscn`, `.unity`, `.blend`), save files, version control.
- **Live wolf for Codex** (Codex only lets hooks block; the wolf asks the question itself).
- **AI damage playground:** 30+ "AI mistake" scenarios in a sample game project; how many the wolf caught, misses included.

**Month 3: reach people**
- **Signed installer** (e.g. SignPath Foundation), checksums, clean uninstall.
- **Real use:** the maintainer uses it daily, then 5-10 invited game developers. The measure: do they still open it in
  the second week.
- **Godot and Unity add-ons:** wake up when a build finishes, bark on errors.
- **Community:** a contributing guide, "good first issue" tasks, mascot and rule contributions.

### Not in these 90 days
- Local model work. The existing feature stays as it is.
- A paid product. BÖRÜ stays free and open source.
- New specialist packs. The 3D pack stays as the first one.

## DownStroke Studios

BÖRÜ is the mascot and first open-source project of **DownStroke Studios**, an independent game and app studio. The wolf
will show up in our devlogs, our games and, one day, a lot more. To follow our games and development, contribute to BÖRÜ,
or build something with the studio later on:

- [Instagram](https://www.instagram.com/downstrokestudios/)
- [YouTube](https://www.youtube.com/@downstrokestudios)
- [TikTok](https://www.tiktok.com/@downstrokestudios)

## License

GPL-3.0 (see [LICENSE](LICENSE)); the Blender scripts must stay GPL-compatible. © 2026 DownStroke Studios.
