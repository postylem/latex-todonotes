# LaTeX todonotes editing workflow

The workflow for author–agent collaboration in LaTeX papers, shared by every
agent. `SKILL.md` — which Claude Code and Codex both load as a skill — tells you
which agent you are; everything else is here.

## Who you are

Two names identify you throughout this document:

- **`<agent>`** — your lowercase *stem*, which is what appears in macro names
- **`<Agent>`** — your capitalized *display name*, which appears in labels

Read them off the paper's preamble: each `\newagent{<stem>}` line instantiates
one agent. If the paper instantiates a stem that is yours, use it. If it
instantiates none that is yours, add one. If you cannot tell which you are,
you are `ai`, displayed as `AI`.

Built-in stems are `claude` (Claude), `gemini` (Gemini), `codex` (Codex) and
`ai` (AI). So a Claude session reads `<agent>` as `claude` and `<Agent>` as
`Claude`, and writes `\claude[sam]{...}` and `ClaudeSuggest`. A Gemini session
writes `\gemini[sam]{...}` and `GeminiSuggest`. Substitute throughout.

Several agents can work in one paper at once, and their notes do not collide.
A note's label names both the agent and the human whose session made it, so
`✻Claude@sam` and `✧Codex@lee` are distinguishable at a glance — as are
`✻Claude@sam` and `✧Codex@sam`, the same person's two agents.

## Responding to author comments

**CRITICAL: NEVER DELETE author todonotes.** The default author-macro style is
the bare lowercase name — `\sam{...}` (margin) and `\Sam{...}` (inline); older
projects use `\noteAuthor{}`/`\NoteAuthor{}`. Whatever the style, if the name
is a person rather than an agent, the note is theirs: they will remove their
own comments after review.

When addressing a comment:

1. **Make the requested edit** to the surrounding text/code
2. **Keep the original comment** exactly as written
3. **Add `\<agent>Response[<owner>]`** inside the note explaining what you did

Example — if the author writes:

```latex
Note 1 = 2.\sam{Wrong! Fix RHS of equation.}
```

Correct response:

```latex
Note 1 = 1.\sam{Wrong! Fix RHS of equation.
\claudeResponse[sam] Fixed. Now the equation is correct.}
```

**WRONG** (deleting the comment):

```latex
Note 1 = 1.
```

Append rather than replace: a note may already carry responses from other
people, from other sessions of your own, and from other agents entirely, and
each is part of the record.

## Marking your contributions

Your notes and edits carry an *owner* tag naming whose session made them — the
human running the session, lowercase (e.g. `sam`). Determine the owner from
context (the repo's instruction file, git user name) or ask; do not guess.

- **Margin notes**: `\<agent>[<owner>]{note text}` — labeled `<Agent>@<owner>`
- **Inline notes**: `\<Agent>[<owner>]{note text}`
- **Replies in another author's note**: `\<agent>Response[<owner>]` — the
  `\response` rule and spacing, headed `<Agent>@<owner>`
- **Inline suggestions**: `\<agent>Suggest[<owner>]{suggested text}` for small
  inline changes proposed but not applied
- **Agent-authored replacement text**: `\<agent>change[<owner>]{...}` — text you
  wrote that is *already part of the document*. It takes your color inline and
  flags the margin with `<Agent>@<owner> change`, marking that line as holding
  agent prose nobody has reviewed. One flag per paragraph per agent-and-owner
  pair, and deliberately **no inline label**, so it stays usable inside math,
  where a label would be wider than the symbol it marks
- **Agent-authored block-level text that is already applied**:
  `\begin{<Agent>Change}[<owner>]...\end{<Agent>Change}` — the block version of
  `\<agent>change`: your color, one flag in the margin where it starts. It is
  not a box, so it may contain floats, headings and displays, and may start or
  end in mid-paragraph
- **New block-level text**: wrap in
  `\begin{<Agent>Suggest}[<owner>]...\end{<Agent>Suggest}` (renders like
  regular document text, just in your color: full text width, with a changebar
  in your background tint hanging in the left gutter — plus a thin stripe in
  the owner's note color abutting it on every page the block spans, capping the
  label flag on the first — headed by a small `<Agent>@<owner>` label)

Every one of these labels is a **tag**, set the same way: your mark and your
name in white on your color, then `@<owner>` in white on the owner's color, the
same color that author's own tag has. At the head of a note the tag ends with
the note's number. The owner's color is looked up from `notecolor-<owner>`,
which the author's own setup defines, so no agent-specific setup is needed; an
owner who has no color yet gets one derived from the name.

Author note colors are chosen to sit *behind* text, so they are never used as
text colors: a tag uses the same hue made dark enough to carry white text.

Omitting `[<owner>]` gives a tag with your name alone; prefer always tagging the
owner so multi-author projects can tell whose session made an edit.

### Numbers and references

Notes are numbered in the order they appear, and the number is part of the tag.
Never type a number, since numbers shift when notes are added or removed. To
refer to a note, put `\label{note:<name>}` at the start of its text and write
`\cref{note:<name>}` (or `\ref`), which prints the note's tag, linked to it:

```latex
\sam{\label{note:rhs} Wrong! Fix RHS of equation.
\claudeResponse[sam] Fixed; the same slip was in \cref{note:lhs}.}
```

**Legacy projects**: papers set up with the oldest convention use
`\noteClaude{...}`/`\NoteClaude{...}`, untagged `\claudeSuggest{...}`, and
`\response{claude}` (which is set as your tag when `claude` is an agent of the
paper). Some define `\claudeSuggest` and the `ClaudeSuggest` environment
themselves and use them for text that is *already applied*, to be unwrapped by
the author on review; there, a proposal goes into a note instead. Follow
whatever convention the project already uses, as its own instruction file
describes it; introduce the owner-tagged macros only when setting up new
projects or when asked to migrate.

### `\<agent>Suggest` or `\<agent>change`?

They answer different questions, and picking the wrong one misleads the author:

| | meaning | author must act? | open item? |
|---|---|---|---|
| `\<agent>Suggest` | a proposal, **not applied** — wording you are offering | yes, accept or reject | **yes** |
| `\<agent>change` | text you **already wrote** into the document | no, review at leisure | no |

`<Agent>Change` and the `<Agent>Suggest` block stand in the same relation: the
first is text that is in the paper now, the second a block the author accepts or
drops.

So a suggestion is a question to the author and reads as an aside, with a
label. A change *is* the prose, so it stays in the text flow and is
flagged in the margin instead. If you are proposing wording, use `Suggest`; if
you have edited the document, use `change`. Marking an applied edit as a
suggestion leaves the author hunting for a decision that has already been made.

## Mechanical notes

- **Notes work everywhere and break across pages.** They are drawn by
  `todofloats.sty`, not by todonotes' own unbreakable boxes: a margin note may
  sit inside a float, a minipage, a table cell, an algorithm, or an
  `<Agent>Suggest` block, and an inline note is broken across columns and
  pages like text. When the notes of a page do not fit in its margin, they are
  cut between lines and continue at the top of the same margin on the next
  page, under a "continued" header. So never split a long note by hand.
- **No floats inside an `<Agent>Suggest` block.** The block is a box, and a
  `figure` or `table` environment cannot float out of one. Put the float
  outside the block, or mark its caption with `\<agent>change`.
- **No `\footnote` inside a note**; use parentheses.
- **Prefer suggestion blocks and margin notes to rewriting prose in place.**
  Editing an author's sentences directly is hard for them to review; an
  `<Agent>Suggest` block leaves the original intact and is trivial to accept or
  drop. When a block is meant to *replace* nearby text rather than add to it,
  say so in its first sentence.
- **Paragraphs inside notes follow the document's style.** Note bodies restore
  the document's `\parindent`/`\parskip` (captured at begin-document), and
  `<Agent>Suggest` blocks keep them directly (`parbox=false`), so
  multi-paragraph notes and blocks separate their paragraphs the same way the
  paper does — indentation by default, skips under `\usepackage{parskip}`.
  Between `\response` turns, a rule with a fixed 3pt on each side does the
  separating instead of `\parskip`.
- **A note never changes the surrounding indentation.** A margin note issued
  between paragraphs starts a paragraph of its own for its anchor, which would
  use up the "first paragraph after a heading" state, so `\note` snapshots that
  flag and restores it after the note: the next paragraph indents exactly as it
  would have without the note. The text right after an *inline* note is not
  indented.
- **Deriving a color from an agent's base color needs the color *name*.**
  `agenttext-<stem>` and `agentbg-<stem>` are derived from `agentcolor-<stem>`
  rather than from the expression that defined it, because a base expression
  may itself contain `!` — `black!55!80!black` is a malformed xcolor chain and
  fails with ``Undefined color `80'``. An expression that happens to end in a
  color name, such as `teal!70!black`, masks the problem.
- **The margin needs more than one pass.** Where a note or a change flag goes
  is computed from the positions recorded in the previous run, so nothing is
  placed right on the first pass. Build with `latexmk`; from scratch it takes
  three or four runs, and the log says `Margin note positions have changed.
  Rerun LaTeX` until the layout is final.
- **A note cannot be issued from math mode** (`\<agent>{}` there ends up inside
  the formula). `\<agent>change` can: its flag goes to the margin from inline
  math, displays, and `align`. Put a note right after the formula instead.
- **Build before reporting.** These macros are easy to get subtly wrong (colors
  that vanish across a page break, notes that swallow floats), and a broken
  preamble breaks the collaborator's build too. Run `make`, `make compat-check` and
  `make engine-check` in this skill's `test/` directory after changing the
  packages, and commit the refreshed
  `test/example.pdf` and `test/example-parskip.pdf` (they are in the repo so
  humans can browse the styles without building). `test/example.tex` exercises
  every note style across several agents; `test/test-compat.tex` guards
  backwards compatibility for papers that predate `agentnotes.sty` — it must
  keep building, and its rendering must not change, so do not modernize it.

## After completing each editing task

1. **Enumerate open items**: run `tools/open_items.py <main.tex>` from this
   skill's directory (after a build, so that it can print the number each note
   has in the PDF). It lists author notes and agent notes from *any* agent with
   the replies inside them and who spoke last, and the `\<agent>Suggest` /
   `<Agent>Suggest` proposals awaiting a decision; `--awaiting <name>` keeps
   the items where `<name>` did not have the last word. Without the tool, scan
   the paper for the same things by hand, and for `TODO` markers
2. **Present the list**: Show a numbered list of open items with brief
   descriptions and line references
3. **Suggest next task**: Recommend which item to tackle next

Applied text (`\<agent>change`) is not an open item, and neither is
`\<agent>Suggest` in a paper that defines it itself as applied text (the tool
detects that).

Enumerate other agents' notes as well as your own. A suggestion left by
another agent is still an open item for the author.

## Setting up a new paper

When asked to set up the todonotes workflow in a new LaTeX project:

1. Run `tools/setup.sh <paper directory>` from this skill's directory. It copies
   `todofloats.sty`, `mytodonotes.sty` and `agentnotes.sty` into the paper (and
   a starting `AGENTS.md`, see step 4), and registers the paper's `main.tex`
   for `tools/sync.sh`, which updates the copies when the packages change.
   Commit them: collaborators who clone the repo need them to build. (Copy `claudenotes.sty` too only if the paper
   already loads it; new papers do not need it.)
2. Load the package in the preamble, after `xcolor`/`tikz` and before
   `cleveref` — one line, from `templates/preamble.tex`:
   ```latex
   \usepackage[authors={sam, lee}, agents={claude, codex}, grow]{mytodonotes} % [disable]
   ```
   - `authors={...}` declares the people: each gets `\sam{...}` (margin),
     `\Sam{...}` (inline) and the color `notecolor-sam`. A color is derived
     from the name unless one is given (`lee=teal!20`). Check that a name does
     not clash with an existing LaTeX command (an author named `max` or `sec`
     needs a variant; the package reports the clash). `\noteauthors{...}` does
     the same after the package is loaded, and the three-line pattern
     (`\colorlet{notecolor-sam}{red!40}` plus two `\newcommand`s on `\note`)
     still works.
   - `agents={...}` declares the agents, as `\newagent{<stem>}` does. A stem
     with a built-in preset needs nothing more; anything else, or a re-tinted
     preset, takes its own line after the package:
     ```latex
     \newagent{qwen}[name=Qwen, color=orange!60, mark=\ding{92}]
     \newagent{claude}[color=<color>]
     ```
   - `\newagent{claude}[flag=false]` turns off the margin flags of that agent's
     applied text (`\claudechange`, `ClaudeChange`). Use it in a paper where
     most of the text is the agent's: a flag on every paragraph says nothing,
     and each flag is a margin item that LaTeX has to place.
   - `grow` is the review layout: 80mm more paper on each side (`grow=<dimen>`
     for another width), all of it for the notes, around an unchanged text
     block. Leave it out to keep the page as it is; notes then use the margin
     the class provides.
   - `disable` (in place of nothing, as the trailing comment suggests) removes
     the notes and the growing: the paper as it will be submitted.
   - `textsize=<size command name>` sets the size of the note text (default
     `scriptsize`).
3. Nothing else is needed per author: every agent takes its owner styling from
   `notecolor-<name>`, so a new author is one more name in the list.
4. Write a **self-contained `AGENTS.md`** in the paper repo describing the
   workflow (start from `templates/AGENTS.md`, which `setup.sh` has copied in:
   replace `sam` and `claude` by the paper's own names and add what is specific
   to the repo), plus one-line `CLAUDE.md` and `GEMINI.md` files pointing at it:
   ```markdown
   See AGENTS.md for this repository's editing conventions.
   ```
   Use pointer files rather than symlinks, which Overleaf's git bridge handles
   poorly.

   Collaborators cloning the repo (e.g. from Overleaf) will not have this skill
   on their machine — their agent sees only the repo — so `AGENTS.md` must spell
   the rules out rather than point to this skill's local path: the
   never-delete-author-notes rule with the `\<agent>Response[<owner>]` example,
   the owner-tagged macros and what they render as, how to add an agent with
   `\newagent` and an author through the `authors` list, the mechanical notes
   above, the open-items enumeration habit, and the sync protocol if the repo is
   Overleaf-synced. Write it agent-neutrally, the way this document is written,
   so that whichever agent a collaborator uses can follow it. The skill's repo
   (git@github.com:postylem/latex-todonotes.git) may be mentioned as provenance,
   never as the place the instructions live.

## Migrating an existing paper

### From `claudenotes.sty` to `agentnotes.sty`

Papers that load `claudenotes.sty` keep working untouched — it is a shim over
`agentnotes.sty` that instantiates Claude. Migrate only when asked, or when
adding a second agent:

1. Replace `\usepackage{claudenotes}` with `\usepackage{agentnotes}` followed by
   `\newagent{claude}`, and copy `agentnotes.sty` into the paper directory
2. Add a `\newagent` line for each further agent
3. If the paper re-tinted Claude by redefining `ClaudeColor`, `ClaudeTextColor`
   or `ClaudeNoteBG`, replace that with `\newagent{claude}[color=<color>]`
4. Rebuild and compare: the rendering should be unchanged

Every existing `\claude`, `\Claude`, `\claudeResponse`, `\claudeSuggest`,
`\claudechange` and `ClaudeSuggest` in the body stays exactly as it is.

### From a paper that predates owner tagging

Papers set up before owner tagging have the todonote machinery pasted inline in
the preamble and an untagged `\claude`. To migrate:

1. Copy in the packages (`tools/setup.sh`) and replace the inline block with the
   `\usepackage[authors={...}, agents={...}]{mytodonotes}` line, giving each
   author's literal color in the list (`sam=red!40`)
2. Tag the existing agent material by owner. Ownership is usually recoverable
   from history rather than by eye — diff against the commit or tag before a
   given session's work and attribute each suggestion block and response
   accordingly, rather than guessing from the prose
3. Rebuild and compare the rendering
