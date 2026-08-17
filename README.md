# latex-todonotes

A [Claude Code](https://code.claude.com) skill for author–Claude collaboration
in LaTeX papers, built on [todonotes](https://ctan.org/pkg/todonotes), and based on 
an initial version by [Tim Vieira](https://timvieira.github.io/).

It teaches Claude a margin-comment workflow:

- **Respond to author comments in place** — never delete an author's
  `\jac{...}`-style todonote; append a `\claudeResponse[owner]` inside it
  instead.
- **Mark Claude's contributions** with owner-tagged macros
  (`\claude[owner]{...}`, `\Claude[owner]{...}`, `\claudeResponse[owner]`,
  `\claudeSuggest[owner]{...}`, `\claudechange[owner]{...}`, and the
  `ClaudeSuggest` block environment), all in a shared Claude purple with a
  per-owner background tint, so multi-author projects can tell whose Claude
  session made an edit.
- **Enumerate open items** (author notes, Claude notes, suggestions, TODOs)
  after each editing task.

Every Claude label renders as `claude@owner`: `claude` in Claude purple on
Claude's own tint, then `@owner` in the ordinary text color on that author's own
note color — so the owner half looks just like their name does in their own
notes. The color is looked up from the `notecolor-<owner>` colorlet that sits
beside each author's note macro, so adding an author needs no Claude-specific
setup. Author colors are used as backgrounds rather than text colors, since they
are picked to sit behind text and are usually too pale to read against one.

The LaTeX side lives in two packages shipped with the skill:

- `mytodonotes.sty` — todonotes configuration, the generic `\note` macro,
  and `\response`
- `claudenotes.sty` — the owner-tagged Claude macros (loads on top of
  `mytodonotes.sty`)

Copy both into the paper directory and commit them, so collaborators who clone
the repo can build it.

`example.tex` exercises every note style with lorem-ipsum content — build it in
the skill directory with `latexmk -pdf example.tex` (see its header comment for
the parskip variant) to preview the whole menagerie after any change to the
packages.

See [SKILL.md](SKILL.md) for the full workflow, including the three-line
per-author macro pattern, how to set up a new paper, and how to migrate one
that predates owner tagging.

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
