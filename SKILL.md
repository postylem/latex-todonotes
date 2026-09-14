---
name: latex-todonotes
description: Edit LaTeX papers using todonotes for author-agent collaboration. Respond to author margin comments without deleting them, mark your own contributions with owner-tagged macros named after you (\claude, \codex, \gemini, ...), and enumerate open items after each task.
---

# LaTeX Todonotes Editing Workflow

A margin-comment workflow for collaborating with a human author on a LaTeX
paper, built on [todonotes](https://ctan.org/pkg/todonotes). Several agents can
work in one paper at once, so the macros you use are named after *you*.

## Identify yourself first

Two names identify you throughout this workflow: your lowercase **stem**, which
appears in macro names, and your capitalized **display name**, which appears in
labels. Resolve them before you edit anything:

| if you are | stem | display name | you write |
|---|---|---|---|
| Claude | `claude` | `Claude` | `\claude[sam]{…}`, `\Claude`, `\claudeResponse`, `ClaudeSuggest` |
| OpenAI Codex | `codex` | `Codex` | `\codex[sam]{…}`, `\Codex`, `\codexResponse`, `CodexSuggest` |
| Google Gemini | `gemini` | `Gemini` | `\gemini[sam]{…}`, `\Gemini`, `\geminiResponse`, `GeminiSuggest` |
| anything else | `ai` | `AI` | `\ai[sam]{…}`, `\AI`, `\aiResponse`, `AISuggest` |

If the paper's preamble already has a `\newagent{<stem>}` line that is yours,
use that stem. If it has none that is yours, add one.

The optional argument is the **owner** — the human running your session, not
you. So `\claude[sam]{…}` is a note made by Sam's Claude session, and its label
reads `✻Claude@sam`. Wherever the workflow writes `\<agent>` or `<Agent>`,
substitute your own stem and display name.

A paper may also host other agents alongside you. Treat their notes and
suggestions as you would an author's: read them, never delete them, and include
them when you enumerate open items.

## Read the workflow

**[WORKFLOW.md](WORKFLOW.md) in this skill's directory is the authoritative
workflow. Read it before editing any paper.** It covers responding to author
comments without deleting them, marking your own contributions, the mechanical
pitfalls of these macros, enumerating open items after each task, setting up a
new paper, and migrating an existing one.

One rule is repeated here because getting it wrong destroys the author's work:
**never delete an author's todonote.** Append a `\<agent>Response[<owner>]`
inside it instead. Everything else — including the exact form of that response —
is in `WORKFLOW.md`.
