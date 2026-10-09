# About this skill

**Type:** Agent Skill (not a library, not an app)
**Name:** `time-investment-report`
**Version:** 0.1.0
**License:** MIT
**Language:** 中文 / English

---

## In one sentence

An **agent skill** that turns any "should I spend 10+ hours on this?" decision
into seven grids of checkable structural facts — and then refuses to tell you
whether it's worth it.

---

## What kind of thing is this?

This is a **skill package for AI agents**. It is a folder of instructions,
templates and one small script that an agent loads when it recognises your
intent. There is no server, no build step, no API key, no npm install.

```
you  →  "should I commit to this 200-hour course?"
agent →  loads this skill  →  runs the grids  →  hands you a report
```

It works with any agent that supports the
`SKILL.md` folder convention — WorkBuddy, CodeBuddy, Claude Code, Codex, and
others.

---

## Who it's for

- People about to commit **10 hours or more** to something irreversible:
  a paid course, a long series, a dense book, a research report, a paid community
- People who've been burned before by "the rating said 8.8"
- Indie builders and coaches who want to *sell* this as a manual service before
  automating anything

## Who it's not for

- Short-form decisions (a 3-minute video, one article). The net value is
  negative — you're better off just swiping away.
- Anyone who wants a single score. That is deliberately not on offer.

---

## The one idea worth stealing

> **Look at the distribution, not the average.**

A series averaging 8.8 tells you nothing: it hides seven stable seasons *and* a
final season that collapses to 6.4. The same is true of courses (one module is
usually the weak one), books (one third is usually padding), and reports
(the executive summary often already contains the conclusion).

Anything that can be split along a timeline should be read as a **curve**, not
a number.

---

## The three hard rules

1. **Never score "is it worth it."** Taste can't be delegated. People argue with
   scores; they don't argue with facts.
2. **Always keep the "walk away" option.** A report that says "go ahead" every
   time is an ad.
3. **Label every fact with a confidence level** — `[official]` `[aggregated]`
   `[derived]` `[unverified]`. Fabricated data is an unrecoverable error.

---

## Quick install

```bash
git clone https://github.com/DavidAlpha007/time-investment-report-agent-skill.git
cp -r time-investment-report-agent-skill ~/.workbuddy/skills/time-investment-report
```

Or just use the calculator — pure Python standard library, nothing to install:

```bash
python3 scripts/tir.py budget --hours 70.2 --per-week 6
```

---

## At a glance

| | |
|---|---|
| Entry point | `SKILL.md` |
| Deterministic calculator | `scripts/tir.py` (`timeline` / `budget` / `scaffold`) |
| Report templates | `assets/report-template.md`, `.en.md`, `.html` |
| Method docs | `references/` (methodology, playbook, redlines, examples) |
| Runtime deps | none (Python 3 standard library only) |
| Network | none |
| Side effects | none — the script only reads input and prints to stdout |

---

## Why it's free and open

This started as a manual service: three reports made by hand, sent to real
people, charged ¥19 each to test whether anyone would actually pay.
The method is the valuable part, and methods get better when other people
stress-test them.

If you use it, the most useful thing you can send back is:
**which of the seven grids actually helped you decide.**

---

[README (English)](README.en.md) · [README 中文](README.md)
