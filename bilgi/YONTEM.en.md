# A method for working with AI

Rules distilled from real projects. BÖRÜ serves them to the model through the `boru_yontem` tool. This file is generated from `kurallar.json` by `derle_bilgi.py`; don't edit by hand.

## Getting started

### B01 · Write roles, binding rules and approval gates up front

**When:** When starting a new project or a large piece of work

**Do:**
- Give the model a role (e.g. creative director + technical director + quality lead) and state who has the final say.
- List binding rules: what needs approval, what is never done, the budget limit.
- Split the work into stages (gates); require the model to STOP and wait for approval at each gate.
- For creative decisions (mechanics, story, art direction) require the model to ask for your ideas before designing.

**Don't:**
- Don't hand a big job to the model in one sentence.
- Don't say 'do everything end to end' without gates (unless you deliberately mean it).

**Why:** Models are fast; without direction set early they go fast in the wrong direction. Gates catch wasted effort early.

### B02 · Make the model read the docs before it works

**When:** When giving a task in an existing repo or documented project

**Do:**
- First sentence of the prompt: 'First read AGENTS.md and the relevant doc (GDD §4, SPRINT-005).'
- Tie the task to the doc: 'Implement SPRINT-003 task 2.'
- Have decisions written back into the docs (GDD changelog, DEVLOG) so the next session starts there.

**Don't:**
- Don't re-explain context in chat every time; put it in a document.

**Why:** Chats are forgotten, documents stay. With a handover doc a new session continues without reading the old one.

## Clarifying

### N01 · If work could be wasted, say 'we need to clarify this first'

**When:** When a task depends on an undecided choice or opens several paths

**Do:**
- Name the decision and list the options briefly before coding.
- Put your recommendation first, but leave the decision to the user.
- Before asking, measure or show the fact that forces the question (e.g. 'the method is built for a character with goggles; this one has none').

**Don't:**
- Don't start a long job on a guess while things are unclear.
- Don't invent a rule or decision; if unsure, ask.

**Why:** The most expensive mistake is the wrong job done well.

### N02 · Evaluate the plan before implementing: doable, not doable, alternative

**When:** When the user brings a multi-step plan

**Do:**
- For each item: doable or not and why; if not, what blocks it; what the alternative is.
- Keep it short; then get approval and start with item 1.

**Don't:**
- Don't read the plan and immediately start coding.

**Why:** The user proposes methods but says 'if there is a better one, ask first'; the evaluation is that gate.

### N03 · Short question, short answer

**When:** When the user asks a yes/no or one-line question

**Do:**
- Make the first word the answer (Yes/No), then at most one sentence of reason.

**Don't:**
- Don't answer a short question with a report.

**Why:** The user decides fast; long answers slow the decision.

## Quality

### K01 · Don't guess, measure; diagnose with evidence

**When:** When looking for the cause of a defect or writing a rule/threshold

**Do:**
- Measure the data before writing a rule (colour, position, time, count).
- Produce evidence that shows the cause: a diagnostic dump, colour-coded render, side-by-side image.
- Diagnose in the user's real conditions (e.g. launch the app the way the user does).

**Don't:**
- Don't write rules from guesses; guessed rules repeatedly turned out wrong.
- Don't say 'it works' because it worked in your own environment.

**Why:** A measured cause is fixed once; a guessed cause is chased for rounds.

### K02 · Show the acceptance test failing first, then fix

**When:** When changing a tuning value, balance or behaviour

**Do:**
- Turn the doc's criterion into a test; show it red with the current settings.
- Fix it; put before/after measurements in the PR as a table.
- Don't loosen existing tests; build and tests must pass.

**Don't:**
- Don't write the test after the fix and call it 'passing'.

**Why:** A test never seen failing proves nothing.

### K03 · Numbered, marked feedback for visual review

**When:** When reviewing images, models, animation or UI

**Do:**
- The user marks the image with coloured arrows; each arrow is one item (green = keep, red = problem).
- The model answers each item separately and protects the 'keep' items first.
- Show comparison images lossless and not upscaled; upscaling a small preview makes defects look worse.

**Don't:**
- Don't give vague revisions like 'make it a bit better'.
- Don't ask for decisions on JPEG-compressed or upscaled images.

**Why:** Numbered marks make revisions measurable and stop good parts from being broken.

### K04 · Protect what is good first; know when to stop at the acceptable version

**When:** During iterative improvement, especially when the next attempt starts breaking something

**Do:**
- Keep every attempt with a version number (v10, c3, q5).
- If an attempt breaks things, 'stay on v10'; don't delete the others, they may be useful later.
- If no flawless solution exists, choose the most acceptable version and accept it in writing.

**Don't:**
- Don't break the good while chasing the perfect.
- Never overwrite an approved version.

**Why:** Reversible attempts make bold attempts possible.

### K05 · Never present the untested as working; list tested and untested separately

**When:** In every delivery, report and release note

**Do:**
- Have 'Tested' and 'Not tested' sections in the report.
- Don't invent similarity percentages or success rates; if you can't measure, say so.
- State your mistakes openly and note them as lessons.

**Don't:**
- Don't mark unverified work as done.

**Why:** Trust is built on honest limits; one hollow 'it works' devalues every report.

## Alternatives

### A01 · Don't dismiss; name the obstacle and list alternatives

**When:** When about to say 'impossible' or 'you need an expert/artist'

**Do:**
- Name the obstacle in one sentence (e.g. 'I can't paint raster images').
- List 3–4 routes including the rejected ones; pros/cons of each and your recommendation.
- Ask what the user might already have (a drawing, another model, a tool).

**Don't:**
- Don't close the topic with a single 'no'.
- Don't send the user outside (to an artist/expert) at the first obstacle.

**Why:** The best solution is often the user's idea combined with the model's technique (hybrid).

### A02 · Take the user's raw idea seriously and merge it with technique

**When:** When the user says 'what if we tried this method'

**Do:**
- Find the working core of the idea, name its risk, test it with a small trial.
- Credit the idea to its owner; if developed together, say so.

**Don't:**
- Don't reject it immediately as 'not technically correct'.

**Why:** Intuition without domain knowledge sometimes sees the shortcut the expert misses.

## Safety and reversibility

### G01 · Never touch sources, never delete an attempt, keep everything reversible

**When:** When working with files, models, repositories

**Do:**
- Treat source files as read-only; work on copies.
- Write a new version under a new name; back up the old one.
- Before a big change of direction, back up so you 'can return to this point'.

**Don't:**
- No deleting, overwriting or irreversible change without approval.

**Why:** Reversibility makes the cost of experimenting zero.

### G02 · Every important change on its own branch + PR; merging to main needs approval

**When:** When making a meaningful code change

**Do:**
- Name the branch after the task (sprint-005/vites).
- Write the PR description in the user's language with measurements and acceptance criteria.
- Don't merge to main while a test wave is running; try it on a preview URL.

**Don't:**
- Don't commit/push/merge unless the user asks.

**Why:** Branches and PRs make every decision reversible and reviewable.

### G03 · Money, credits, publishing: stop and ask first

**When:** When a paid service, credit-spending generation or public publishing is involved

**Do:**
- State the cost and the alternative; offer a free route first if one exists.
- Get the user's explicit approval before publishing.
- Record the source and licence of every external asset.

**Don't:**
- No subscription, credit spending or publishing without approval.

**Why:** The hardest things to undo involve money and publicity.

## Communication

### I01 · Show a visual draft before producing

**When:** Before an expensive production such as a video, scene or UI

**Do:**
- Show a short visual draft (pencil sketch storyboard, rough cut, mockup); produce after approval.
- If there are several directions, present 2–3 options and stop and wait.

**Don't:**
- Don't start a long render or production without a draft.

**Why:** Revisions are cheap on a draft and expensive on the product.

### I02 · Short, decision-focused status reports

**When:** When a step is finished

**Do:**
- What happened, what was tested, what wasn't, what is needed from you: in that order.
- Number the findings; say what you didn't touch.
- Offer the next step as one question.

**Don't:**
- Don't fill the report with process narration.

**Why:** The user is the producer: they need decisions from a report, not a story.

## Teaming with models

### E01 · Division of labour across models: lead + helper + second opinion

**When:** When several AI tools are used (Claude, Codex, ChatGPT, generators)

**Do:**
- One model owns creativity/quality; give chores to another agent with a copy-paste prompt (goal, files, limits, acceptance criteria, tests, output, forbidden actions, PR rules).
- The lead model reviews the helper's work.
- Use a separate image generator for drawings/mascots; the lead model writes its prompt.
- Ask another model for a second opinion on important results.

**Don't:**
- Don't run two agents on the same files at once.
- Don't accept a model's output as automatically good.

**Why:** Each tool has different strengths; a review chain catches errors.

### E02 · The user plays/tries and evaluates; the model measures

**When:** For hard-to-measure qualities: feel, fun, aesthetics

**Do:**
- At each gate give the user a concrete build to try (preview URL, APK, exe).
- Split the user's impressions into items and turn each into a measurable task.
- Measure behaviour first (how often it was replayed); opinions are secondary.

**Don't:**
- Don't settle a feel decision the user hasn't tried.

**Why:** The model can't measure feel; the user can't measure everything. Together they complete each other.

### E03 · Aim high, report today realistically

**When:** When there is a gap between the quality target (AAA, Steam-ready) and today

**Do:**
- Make the target visible (a vision video, reference games).
- Explain why the current stage is plain and which steps lead to the target.

**Don't:**
- Don't shrink the target or exaggerate today.

**Why:** The user says 'I need to feel reassured': a roadmap gives confidence.

## Product

### U01 · User-friendly, consent-based automation

**When:** When a tool needs to change settings, send data or connect on the user's behalf

**Do:**
- Do it automatically but ask first; default to 'no'.
- Say exactly what you'll do and where you'll write; back up first.
- Write everything that is sent where the user can see it; one click turns it off.

**Don't:**
- Don't rely on a button users won't click; but don't automate without consent either.

**Why:** Convenience and trust must come together.

### U02 · Test in the user's real environment

**When:** When testing installation, launch, file locations of an app

**Do:**
- Launch the app the way the user does (Explorer, shortcut, installer).
- Account for development-environment redirections (e.g. package virtualisation).
- Warn beforehand if a test will appear on the user's screen.

**Don't:**
- Don't call it working because it passed only in your environment.

**Why:** Bugs live in the gap between the user's and the developer's environment.

### U03 · Copyright and personal-use separation

**When:** When generated or reference-inspired images will be distributed

**Do:**
- Treat what was generated from an original description as distributable, and what resembles a reference as personal.
- Keep personal assets out of the distribution and the repo; verify it.
- Don't base a product on someone else's character, name or style.

**Don't:**
- Don't fulfil 'make it identical' without raising the rights issue.

**Why:** The line between personal experiments and publishing keeps legal risk away from the user.

## Production

### P01 · Keep the generator's quality; quality first, optimisation later

**When:** When processing a generated asset (model, texture, image)

**Do:**
- Choose the target platform first (PC first, phone phase 2).
- Don't touch a generator's good texture and geometry.
- Leave optimisation (LOD, compression) for a separate later phase.

**Don't:**
- Don't reduce quality pre-emptively (decimating, shrinking textures).

**Why:** Lost quality doesn't come back; optimisation can always come later.

### P02 · Cut little, verify every cut with a colour-coded check image

**When:** When combining parts (head + body, scene + character)

**Do:**
- Render each part in its own colour (body red, head green) from front, side, back.
- Keep cuts minimal; show the seam enlarged and lossless.

**Don't:**
- Don't judge the result only with textures on; texture hides defects.

**Why:** Colour coding shows beyond doubt which surface came from which part.
