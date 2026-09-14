---
name: latex-todonotes
description: Edit LaTeX papers using todonotes for author-agent collaboration. Respond to author margin comments, mark your own contributions with owner-tagged \claude/\Claude/\claudeSuggest/\claudeResponse macros, and enumerate open items after each task.
---

# LaTeX Todonotes Editing Workflow

## You are Claude

Your agent **stem** is `claude` and your **display name** is `Claude`. The
workflow is written generically, so substitute as you read it:

| the workflow says | you write |
|---|---|
| `\<agent>[<owner>]{...}` | `\claude[jac]{...}` |
| `\<Agent>[<owner>]{...}` | `\Claude[jac]{...}` |
| `\<agent>Response[<owner>]` | `\claudeResponse[jac]` |
| `\<agent>Suggest[<owner>]{...}` | `\claudeSuggest[jac]{...}` |
| `\<agent>change[<owner>]{...}` | `\claudechange[jac]{...}` |
| `<Agent>Suggest` environment | `ClaudeSuggest` |

Your labels render as `✻Claude@<owner>`, opened by Claude Code's terminal
starburst.

A paper may also host other agents — `\codex[sam]{...}`, `\gemini[sam]{...}` —
whose notes sit alongside yours without collision. Treat their notes and
suggestions as you would an author's: read them, never delete them, and include
them when you enumerate open items.

## Read the workflow

**[WORKFLOW.md](WORKFLOW.md) in this skill's directory is the authoritative
workflow. Read it before editing any paper.** It covers responding to author
comments without deleting them, marking your own contributions, the mechanical
pitfalls of these macros, enumerating open items after each task, setting up a
new paper, and migrating an existing one.

One rule is repeated here because getting it wrong destroys the author's work:
**never delete an author's todonote.** Append a `\claudeResponse[<owner>]`
inside it instead. Everything else — including the exact form of that response —
is in `WORKFLOW.md`.
