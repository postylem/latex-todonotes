# latex-todonotes

A skill for author–agent collaboration in LaTeX papers, built on
[todonotes](https://ctan.org/pkg/todonotes), and based on an initial version by
[Tim Vieira](https://timvieira.github.io/).

It teaches an AI agent a margin-comment workflow:

- **Clearly mark the agent's contributions with owner-tagged macros** so you
  know who to blame / credit (both human and AI). For example, Claude will use macros
  `\claude[owner]{...}`, `\Claude[owner]{...}`, `\claudeResponse[owner]`,
  `\claudeSuggest[owner]{...}`, `\claudechange[owner]{...}`, and the
  `ClaudeSuggest` block environment. Each will render in the agent's own color with a
  per-owner background tint, so multi-author projects can tell whose session
  made an edit.
- **The agent will respond to author comments in place**. Say an author named Alex
  writes a todonote like `\alex{...}`, and then another author Sam has their agent
  respond. The agent uses `\claudeResponse[sam]` (or `\codexResponse[sam]`, …).
- **Proposals and applied edits look different.** `\claudeSuggest[sam]{...}` is
  wording the agent offers without touching your sentence; `\claudechange[sam]{...}`
  is text it has already written in. Only the first needs a decision from you.
- **An open-items list after every task**: the notes, with who spoke last, and
  the proposals awaiting a decision. `tools/open_items.py` prints it from the
  source, with the number each note has in the PDF.

## Notes that are numbered, break across pages, and work everywhere

`mytodonotes.sty` draws its notes with `todofloats.sty`, not with todonotes'
own unbreakable boxes:

- Margin notes work inside floats, minipages, table cells and algorithms (no
  `Float(s) lost`), never overlap, and a page whose margin is full continues its
  notes in the margin of the next page. Inline notes break across columns and
  pages like text.
- Every note opens with a tag: its author, on the saturated hue of the note
  color, and its number. Put `\label{note:<name>}` in the text of a note, and
  `\cref{note:<name>}` (or `\ref`) prints the same tag, linked to the note.
- Authors come from a list, `\usepackage[authors={sam, lee=teal!20}]{mytodonotes}`
  or `\noteauthors{...}`: each gets `\sam`, `\Sam` and `notecolor-sam`. An
  author without a color gets one derived from the name, the same in every
  paper, kept away from the hues already in use.
- `grow` is a review layout: the paper becomes 80mm wider on each side and the
  notes get the space, while the text block, and so every line and page break,
  stays as it is. `disable` turns the notes and the growing off.
- `side=alternate` puts the notes of each page of a one-column paper in the
  right and left margins in turn, which halves the stack on each side, so a
  smaller `grow` (say `grow=40mm`) is enough. `leftmarginsep=<dimen>` moves the
  left notes away from the text, e.g. past line numbers in a review copy.

## Any agent, several at once

The workflow is written agent-neutrally, and the LaTeX side is parameterized, so
the same packages serve Claude, Codex, Gemini or anything else, and more than
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
presets are `claude`, `gemini`, `codex`, and generic `ai`, each distinguished by
their own colors and icons (unicode dingbats). You can also specify
a custom name for a new agent, supplying its name, color and mark. 
An agent can be re-tinted per paper with `\newagent{claude}[color=<color>]`.

Each label renders as the agent's mark and name in the agent's color on its own
tint, then `@owner` in the ordinary text color on that author's own note
color — so `✻Claude@sam` and `✧Codex@lee` are distinguishable at a glance, and
the owner half looks just like their name does in their own notes. The color is
looked up from the `notecolor-<owner>` colorlet that sits beside each author's
note macro, so adding an author needs no agent-specific setup. Author colors are
used as backgrounds rather than text colors, since they are picked to sit behind
text and are usually too pale to read against one.

## What's in here

- `mytodonotes.sty` — the generic `\note` macro, the numbered tags, authors
  from a list, and `\response`
- `todofloats.sty` — the engine under it: notes that break across pages and
  survive inside floats, the review layout (`grow`). Usable on its own in place
  of todonotes.
- `tools/open_items.py` — the open-items list of a paper; `tools/setup.sh` —
  copies the packages into a paper; `tools/sync.sh` — brings the copies in
  every registered paper up to the skill's version
- `templates/` — the preamble block and the `AGENTS.md` a new paper starts from
- `agentnotes.sty` — `\newagent` and the owner-tagged macro family it mints
  (loads on top of `mytodonotes.sty`)
- `claudenotes.sty` — a compatibility shim for papers that predate
  `agentnotes.sty`: it loads the core and instantiates Claude, which is what
  `\usepackage{claudenotes}` used to do on its own. New papers don't need it.
- `WORKFLOW.md` — the agent-neutral workflow, and the authoritative one
- `SKILL.md` / `AGENTS.md` — thin per-platform entry points that say which agent
  you are and send you to `WORKFLOW.md`
- `test/` — the example gallery and the backwards-compatibility guard, with a
  `Makefile` that rebuilds both; `test/todofloats/` stress-tests the engine
  (`make engine-check`)
- `docs/` — design notes

Copy `todofloats.sty`, `mytodonotes.sty` and `agentnotes.sty` into the paper
directory and commit them, so collaborators who clone the repo can build it
(`tools/setup.sh <paper directory>` does the copying, and registers the paper).
When the packages change, `tools/sync.sh --check` lists the papers that are
behind, and `tools/sync.sh` updates them: for each, in a separate worktree of
its upstream branch, it replaces the copies, builds the paper before and after,
and commits and pushes only if the build is no worse. The registry is
`~/.config/latex-todonotes/papers`; add a paper with `tools/sync.sh --add <main.tex>`.

`test/example.tex` exercises every note style across five agents with
lorem-ipsum content — the built PDFs are committed for browsing without
building: [example.pdf](test/example.pdf) (indented paragraphs) and
[example-parskip.pdf](test/example-parskip.pdf) (under `\usepackage{parskip}`).

`test/test-compat.tex` is a build guard, deliberately written in the
pre-`\newagent` style: it must keep building, and its rendering must not change,
so that papers already set up with this skill keep working. Don't modernize it.

After any change to the packages, rebuild both and run the engine tests:

```bash
cd test && make && make compat-check && make engine-check
```

A note's layout comes from positions recorded in the previous run, so a paper
needs three or four LaTeX runs from scratch (`latexmk` does them; the log says
`Margin note positions have changed` until it is done).

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
git clone git@github.com:postylem/latex-todonotes.git ~/.claude/skills/latex-todonotes
```

For an agent without a skill mechanism, point it at `AGENTS.md` in the clone.

Note that papers set up with this skill get a self-contained `AGENTS.md`
describing the conventions (with one-line `CLAUDE.md`/`GEMINI.md` pointers), so
collaborators' agents follow the workflow even without the skill installed —
installing it is only needed to *set up* new papers or to get the workflow
outside such a repo.
