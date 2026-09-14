# latex-todonotes

This repository is a **skill**: a margin-comment workflow for collaborating with
a human author on a LaTeX paper, built on
[todonotes](https://ctan.org/pkg/todonotes), usable by any agent.

To use it, read these two files in order:

1. **[SKILL.md](SKILL.md)** — tells you which agent you are, and so which macros
   are yours. Both Claude Code and Codex load this file directly as a skill.
2. **[WORKFLOW.md](WORKFLOW.md)** — the workflow itself, and the authoritative
   copy of it.

> **Not a contributor guide.** If you are here to *develop this skill* rather
> than to edit a paper with it, neither file applies to you; read `README.md`
> and `docs/` instead.

One rule matters more than the rest, because getting it wrong destroys the
author's work: **never delete an author's todonote.** Append a response inside
it instead. `WORKFLOW.md` gives the exact form.
