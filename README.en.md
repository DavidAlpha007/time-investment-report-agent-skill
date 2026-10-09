# Time Investment Report — an Agent Skill

> Turn "should I spend my time on this?" from a gut feeling into a checkable ledger.

**A course costs 95 hours. A TV series costs 70 hours. A book costs 576 pages.**
These are *highly irreversible* time commitments, and most people decide them
based on a single number — "8.8 on Douban" — or a friend's one-line opinion.

But 8.8 tells you neither that seasons 1–7 were consistently excellent,
nor that the final season collapses to 6.4. **The average flattens exactly the
information that matters.**

This is an **Agent Skill**: drop it into your agent's skills directory and your
agent produces a seven-grid structural report before you buy, start, or commit.

---

## What it does vs. what it refuses to do

| ✅ Does | ❌ Never does |
|---|---|
| Computes total time and the finish date at your own pace | No score, no star rating, no "recommended / not recommended" |
| Breaks the timeline into segments with share-of-total | Doesn't decide for you |
| Locates density anomalies: setup stretches, collapse points, filler | No verdict on "is it worth it" |
| Assesses time decay (how stale, what's missing) | Never invents data to fill a grid |
| Finds shorter substitutes (especially the author's own condensed version) | — |
| Gives three options: **All in / Core only / Walk away** | Never drops the "walk away" option |

**Core idea:** people argue with a score, but they don't argue with a checkable fact.
So the output is always *"from episode 68 onward, ratings fall below 6.0"* —
never *"this show isn't worth watching."*

---

## Three hard rules

1. **Never score "is it worth it."** Taste cannot be delegated.
2. **Always keep the third "walk away" option.** A report that recommends
   "watch it" every single time is an advertisement, not a report.
3. **Label every grid with a confidence level.** Get caught fabricating data once
   and trust goes to zero — permanently.

---

## Install

This is a **skill package**, not a library. Copy the whole folder into your
agent's skills directory:

```bash
git clone https://github.com/DavidAlpha007/time-investment-report-agent-skill.git

# WorkBuddy / CodeBuddy
cp -r time-investment-report-agent-skill ~/.workbuddy/skills/time-investment-report

# Claude Code
cp -r time-investment-report-agent-skill ~/.claude/skills/time-investment-report

# Codex
cp -r time-investment-report-agent-skill ~/.codex/skills/time-investment-report
```

Then just ask your agent:

> "I'm hesitating about buying this course / starting this series / reading this
> book. Give me a time investment report."

The skill triggers on intent like *"is it worth my time"*, *"should I commit to
this"*, *"how long will this actually take"*.

### Use the calculator standalone

Pure Python standard library, zero dependencies:

```bash
python3 scripts/tir.py budget   --hours 70.2 --per-week 6
python3 scripts/tir.py timeline --input assets/example-segments.json
python3 scripts/tir.py scaffold --title "..." --type course
```

---

## The seven grids

| # | Grid | Question |
|---|---|---|
| 0 | Basic ledger | Total length, price, rating volume, last updated |
| 1 | Time bill | Raw length ÷ your weekly pace = how many weeks |
| 2 | Structure breakdown | Split by chapter / season / module — where does the time actually go |
| 3 | Density anomalies | Setup stretches, collapse point, filler (look at the **distribution**, not the average) |
| 4 | Time decay | How long since the last update? Does your goal depend on something it omits? |
| 5 | Shorter substitutes | Is there a condensed version, an official summary, a highlights cut? |
| 6 | Three options | **All in / Core only / Walk away** |

---

## The calculator

### `tir.py budget` — time bill and net value

```bash
python3 scripts/tir.py budget --hours 70.2 --per-week 6
```

Returns weeks needed, projected finish date, and whether this object
**deserves a report at all**:

| Object | Net value |
|---|---|
| 1-minute short video | **−9.6 minutes** (you'd do better just swiping away) |
| 70-hour series | 1,670 minutes (27.8 hours) |
| 200-hour bootcamp | 4,790 minutes (79.8 hours) |

The spread between long and short is roughly **2,000×**. That is why this method
only serves commitments of **10 hours or more**.

### `tir.py timeline` — distribution along the timeline

Input your segments:

```json
{
  "object": "Game of Thrones",
  "good": 7.0,
  "bad": 6.0,
  "segments": [
    {"label": "S1", "minutes": 550, "rating": 9.1},
    {"label": "S2", "minutes": 560, "rating": 9.3}
  ]
}
```

Outputs: **duration-weighted mean**, share of runtime in the good band,
share in the bad band, the **collapse point** (reproducible definition: the tail's
weighted mean drops ≥ 1.0 below the global weighted mean and the tail is ≥ 5% of
total), and a warning when the weighted and unweighted means diverge.

### `tir.py scaffold` — report skeleton

```bash
python3 scripts/tir.py scaffold --title "..." --type course
```

Supports `course` / `series` / `book` / `report` / `podcast` / `community`,
each with its **own checklist** (for books, it always checks whether the author
published a shorter version).

---

## Repo layout

```
├── SKILL.md                    # Agent entry point: workflow, hard rules, gates
├── README.en.md                # This file
├── README.md                   # 中文版
├── ABOUT.md                    # Short identity card (EN)
├── LICENSE                     # MIT
├── scripts/
│   └── tir.py                  # Deterministic calculator (stdlib only)
├── references/
│   ├── methodology.md          # Net value model, distribution > average, granularity, peak-end rule, decay tiers
│   ├── playbook.md             # 10-step manual workflow + per-type data checklists + pricing + go/no-go
│   ├── redlines.md             # Hard rules, four confidence levels, honesty statement, self-check
│   └── examples.md             # Three worked examples compared side by side
└── assets/
    ├── report-template.md      # Markdown report template (中文)
    ├── report-template.en.md   # Markdown report template (EN)
    ├── report-template.html    # HTML report template (self-contained, print to PDF)
    └── example-segments.json   # Sample input for `timeline`
```

> **Language note (v0.1):** the skill entry point, both READMEs, ABOUT and the
> report template are bilingual. The four `references/` documents are
> Chinese-only for now — agents read them fine, but human translations are
> welcome via PR.

---

## Why long-form only

The value of a filter equals the loss it avoids. Assume 80% accuracy and
10 minutes to read the report:

- A 1-minute video: expected saving 0.4 minutes, **net −9.6 minutes**. Swiping
  away yourself takes 0.5 seconds.
- A 200-hour bootcamp: expected saving 4,800 minutes, **net 79.8 hours**.

**In the short-video case the filter isn't useless — it's redundant.**

And people scrolling a feed aren't hunting for value, they're killing time.
Filter their content out and they don't know what to do next. **In that setting
the filter works against the user.**

---

## Known limits

- **Only for commitments ≥ 10 hours.** Smaller requests should be declined.
- **No public data, no report.** Internal material or unreleased content gets
  downgraded to a "decision checklist" instead.
- **Narrative vs. knowledge content behave differently.** Series and novels are
  governed by the peak-end rule, so a small ending still dominates the whole
  experience; courses and reports can be weighted by share of time.
- **This complements ratings, it doesn't replace them.** A rating tells you what
  people thought. This tells you where your hours actually go.

---

## Contributing

Issues and PRs welcome. Hard requirements for changes:

- Any new threshold must come with a justification in `references/methodology.md`
- New content types must update `TYPE_HINTS` in `scripts/tir.py` **and** the
  checklist in `references/playbook.md`
- No feature or wording may introduce a "worth it" score

---

## License

MIT · see [LICENSE](LICENSE)

---

[中文版 README](README.md) · [About this skill](ABOUT.md)
