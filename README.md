# latex-todonotes

A [Claude Code](https://code.claude.com) skill for author–Claude collaboration
in LaTeX papers, built on [todonotes](https://ctan.org/pkg/todonotes).

It teaches Claude a margin-comment workflow:

- **Respond to author comments in place** — never delete an author's
  `\jac{...}`-style todonote; append a `\response{claude}` inside it instead.
- **Mark Claude's contributions** with owner-tagged macros
  (`\claude[owner]{...}`, `\claudeSuggest[owner]{...}`, `\claudechange`,
  `ClaudeSuggest` block environment), all in a shared Claude purple with a
  per-owner accent color, so multi-author projects can tell whose Claude
  session made an edit.
- **Enumerate open items** (author notes, Claude notes, suggestions, TODOs)
  after each editing task.

The LaTeX side lives in two packages shipped with the skill:

- `mytodonotes.sty` — todonotes configuration, the generic `\note` macro,
  and `\response`
- `claudenotes.sty` — the owner-tagged Claude macros (loads on top of
  `mytodonotes.sty`)

See [SKILL.md](SKILL.md) for the full workflow, including the three-line
per-author macro pattern and how to set up a new paper.

## Install

As a Claude Code plugin (one-time setup):

```bash
claude plugin marketplace add postylem/latex-todonotes
claude plugin install latex-todonotes@postylem-skills
```

Or manually: clone (or copy the directory) into `~/.claude/skills/`:

```bash
git clone https://github.com/postylem/latex-todonotes ~/.claude/skills/latex-todonotes
```

Note that papers set up with this skill get a self-contained `CLAUDE.md`
describing the conventions, so collaborators' Claude sessions follow the
workflow even without the skill installed — installing it is only needed to
*set up* new papers or to get the workflow outside such a repo.
