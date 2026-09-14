# latex-todonotes

A skill for author–agent collaboration in LaTeX papers, built on
[todonotes](https://ctan.org/pkg/todonotes), and based on an initial version by
[Tim Vieira](https://timvieira.github.io/).

It teaches an AI agent a margin-comment workflow:

- **Respond to author comments in place** — never delete an author's
  `\jac{...}`-style todonote; append a `\claudeResponse[owner]` (or
  `\codexResponse[owner]`, …) inside it instead.
- **Mark the agent's contributions** with owner-tagged macros
  (`\claude[owner]{...}`, `\Claude[owner]{...}`, `\claudeResponse[owner]`,
  `\claudeSuggest[owner]{...}`, `\claudechange[owner]{...}`, and the
  `ClaudeSuggest` block environment), each in its agent's own color with a
  per-owner background tint, so multi-author projects can tell whose session
  made an edit.
- **Enumerate open items** (author notes, agent notes, suggestions, TODOs)
  after each editing task.

## Any agent, several at once

The workflow is written agent-neutrally, and the LaTeX side is parameterized, so
the same packages serve Claude, Codex, Gemini or anything else — and more than
one of them in a single paper. One line per agent:

```latex
\usepackage{mytodonotes}
\usepackage{agentnotes}
\newagent{claude}
\newagent{codex}
\newagent{qwen}[name=Qwen, color=orange!60, mark=\ding{92}]
```

`\newagent{claude}` mints `\claude`, `\Claude`, `\claudeResponse`,
`\claudeSuggest`, `\claudechange`, `\claudespark` and the `ClaudeSuggest`
environment; `\newagent{codex}` mints the `\codex` family beside it. Built-in
presets are `claude` (✻, terracotta), `gemini` (✦, blue), `codex` (✧,
graphite) and `ai` (✧, neutral gray); any other stem supplies its own name,
color and mark. An agent can be re-tinted per paper with
`\newagent{claude}[color=<color>]`.

Each label renders as the agent's mark and name in the agent's color on its own
tint, then `@owner` in the ordinary text color on that author's own note
color — so `✻Claude@jac` and `✧Codex@sam` are distinguishable at a glance, and
the owner half looks just like their name does in their own notes. The color is
looked up from the `notecolor-<owner>` colorlet that sits beside each author's
note macro, so adding an author needs no agent-specific setup. Author colors are
used as backgrounds rather than text colors, since they are picked to sit behind
text and are usually too pale to read against one.

## What's in here

- `mytodonotes.sty` — todonotes configuration, the generic `\note` macro, and
  `\response`
- `agentnotes.sty` — `\newagent` and the owner-tagged macro family it mints
  (loads on top of `mytodonotes.sty`)
- `claudenotes.sty` — a compatibility shim for papers that predate
  `agentnotes.sty`: it loads the core and instantiates Claude, which is what
  `\usepackage{claudenotes}` used to do on its own. New papers don't need it.
- `WORKFLOW.md` — the agent-neutral workflow, and the authoritative one
- `SKILL.md` / `AGENTS.md` — thin per-platform entry points that say which agent
  you are and send you to `WORKFLOW.md`
- `test/` — the example gallery and the backwards-compatibility guard, with a
  `Makefile` that rebuilds both
- `docs/` — design notes

Copy `mytodonotes.sty` and `agentnotes.sty` into the paper directory and commit
them, so collaborators who clone the repo can build it.

`test/example.tex` exercises every note style across five agents with
lorem-ipsum content — the built PDFs are committed for browsing without
building: [example.pdf](test/example.pdf) (indented paragraphs) and
[example-parskip.pdf](test/example-parskip.pdf) (under `\usepackage{parskip}`).

`test/test-compat.tex` is a build guard, deliberately written in the
pre-`\newagent` style: it must keep building, and its rendering must not change,
so that papers already set up with this skill keep working. Don't modernize it.

After any change to the packages, rebuild both:

```bash
cd test && make
```

See [WORKFLOW.md](WORKFLOW.md) for the full workflow, including the three-line
per-author macro pattern, how to set up a new paper, and how to migrate one that
predates either `agentnotes.sty` or owner tagging.

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

For an agent without a skill mechanism, point it at `AGENTS.md` in the clone.

Note that papers set up with this skill get a self-contained `AGENTS.md`
describing the conventions (with one-line `CLAUDE.md`/`GEMINI.md` pointers), so
collaborators' agents follow the workflow even without the skill installed —
installing it is only needed to *set up* new papers or to get the workflow
outside such a repo.
