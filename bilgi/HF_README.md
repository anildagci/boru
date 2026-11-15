---
license: cc-by-4.0
language:
- tr
- en
pretty_name: BÖRÜ working-with-AI method
size_categories:
- n<1K
task_categories:
- text-generation
tags:
- ai-assistant
- prompting
- workflow
- mcp
configs:
- config_name: default
  data_files: ornekler.jsonl
---

# BÖRÜ: a method for working with AI (TR/EN)

25 bilingual working rules distilled from real AI-assisted projects (game development, 3D characters from drawings,
social video production, a desktop tool), and 100 chat-format examples built from them.

It is the knowledge behind [BÖRÜ](https://github.com/anildagci/boru), a free MCP helper for Claude Code and Codex,
and the seed dataset for its planned small local model.

## Files

- `kurallar.json`: the rules. Each has an id, category, title, when, do, don't, why (in `tr` and `en`) and keywords.
- `ornekler.jsonl`: `{"kural", "dil", "messages": [system, user, assistant]}` — two phrasings per rule per language.
- `YONTEM.en.md` / `YONTEM.tr.md`: the same rules as a readable guide.

## Examples of rules

- *If work could be wasted, say "we need to clarify this first".*
- *Don't guess, measure; diagnose with evidence.*
- *Show the acceptance test failing first, then fix.*
- *Don't dismiss; name the obstacle and list alternatives.*
- *Never present the untested as working.*

## Limits

Small and templated: the examples are generated from the rules, not real conversations. Personal data was removed; the
`kanit` (evidence) fields hold short anonymised quotes from the original sessions. Source of truth and generator:
`bilgi/` in the GitHub repo.
