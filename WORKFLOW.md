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
- **New block-level text**: wrap in
  `\begin{<Agent>Suggest}[<owner>]...\end{<Agent>Suggest}` (renders like
  regular document text, just in your color: full text width, with a changebar
  in your background tint hanging in the left gutter — plus a thin stripe in
  the owner's note color abutting it on every page the block spans, capping the
  label flag on the first — headed by a small `<Agent>@<owner>` label)

Every one of these labels is set the same way: your mark and your name in your
color on your own tint, then `@<owner>` in the ordinary text color on
`notecolor-<owner>` itself, unmodified. The owner half therefore looks exactly
like that author's name already does in their own `\<author>{...}` note or
`\response{<author>}`. The colorlet is looked up automatically from the
author's existing macro setup, so no agent-specific setup is needed.

Author note colors are chosen to sit *behind* text, so they are used as
backgrounds and never as text colors. An earlier version of this package tinted
the `@<owner>` text with a darkened author color instead, which read poorly in
general and became nearly invisible in the commonest case of all: a
`\<agent>Response[<owner>]` inside a note belonging to that same owner. Where an
owner color marks non-text elements — the margin note's frame and leader line,
the block pole's stripe and flag cap — it is `notecolor-<owner>` itself,
unmodified, so the owner reads as one color everywhere.

The backgrounds are painted as rules in a zero-width, zero-height overlay, so a
label's metrics are exactly those of the plain text — adding one never shifts
anything horizontally or vertically.

Omitting `[<owner>]` (or naming an owner without a `notecolor`) falls back to
your plain color with no `@` suffix; prefer always tagging the owner so
multi-author projects can tell whose session made an edit.

**Legacy projects**: papers set up with the oldest convention use
`\noteClaude{...}`/`\NoteClaude{...}`, untagged `\claudeSuggest{...}`, and
`\response{claude}`. Follow whatever convention the project already uses;
introduce the owner-tagged macros only when setting up new projects or when
asked to migrate.

### `\<agent>Suggest` or `\<agent>change`?

They answer different questions, and picking the wrong one misleads the author:

| | meaning | author must act? | open item? |
|---|---|---|---|
| `\<agent>Suggest` | a proposal, **not applied** — wording you are offering | yes, accept or reject | **yes** |
| `\<agent>change` | text you **already wrote** into the document | no, review at leisure | no |

So a suggestion is a question to the author and reads as an aside, with a label
and a colon. A change *is* the prose, so it stays in the text flow and is
flagged in the margin instead. If you are proposing wording, use `Suggest`; if
you have edited the document, use `change`. Marking an applied edit as a
suggestion leaves the author hunting for a decision that has already been made.

## Mechanical notes

- **`\<agent>{}` cannot appear inside an `<Agent>Suggest` box.** It is a
  `\marginpar`, and tcolorbox swallows it — the failure surfaces as
  `! LaTeX Error: Float(s) lost`, not as a missing note. Put the margin note
  immediately *before* `\begin{<Agent>Suggest}`.
- **Prefer suggestion blocks and margin notes to rewriting prose in place.**
  Editing an author's sentences directly is hard for them to review; an
  `<Agent>Suggest` block leaves the original intact and is trivial to accept or
  drop. When a block is meant to *replace* nearby text rather than add to it,
  say so in its first sentence.
- **Inline notes break across pages.** `[inline]` notes are typeset as a
  breakable box (todonotes' own inline notes are single unbreakable TikZ
  nodes), so a long inline comment flows onto the next page instead of
  overflowing it. Other todonotes options passed alongside `inline` are
  ignored on this path.
- **Paragraphs inside notes follow the document's style.** Note bodies restore
  the document's `\parindent`/`\parskip` (captured at begin-document), and
  `<Agent>Suggest` blocks keep them directly (`parbox=false`), so
  multi-paragraph notes and blocks separate their paragraphs the same way the
  paper does — indentation by default, skips under `\usepackage{parskip}`.
  Between `\response` turns, a rule with a fixed 3pt on each side does the
  separating instead of `\parskip`.
- **A note never changes the surrounding indentation.** `\marginpar` (and hence
  todonotes' `\todo`) issued in vertical mode clears `\if@nobreak`, so a note
  placed between a heading and its first paragraph used to silently re-enable
  that paragraph's indent. `\note` (mytodonotes v1.6) snapshots the flag and
  restores it after the note, for margin and inline notes alike: the next
  paragraph indents exactly as it would have without the note.
- **Deriving a color from an agent's base color needs the color *name*.**
  `agenttext-<stem>` and `agentbg-<stem>` are derived from `agentcolor-<stem>`
  rather than from the expression that defined it, because a base expression
  may itself contain `!` — `black!55!80!black` is a malformed xcolor chain and
  fails with ``Undefined color `80'``. An expression that happens to end in a
  color name, such as `teal!70!black`, masks the problem.
- **Margin flags need more than one pass.** `\<agent>change`'s margin flag is a
  `\marginnote`, which routes its position through the `.aux` file and renders
  **nothing at all** on a first pass. Build with `latexmk`, or run the engine
  twice; a single run makes the flags look broken when they are merely not
  placed yet.
- **`\marginpar` cannot be used from math mode**, which is why the flag is a
  `\marginnote`. `\marginpar` — and so todonotes' `\todo`, and so
  `\<agent>{}` — fails there with `! LaTeX Error: Not in outer par mode.`
  `\marginnote` is also non-floating, so unlike `\<agent>{}` it survives
  inside a suggestion block.
- **Build before reporting.** These macros are easy to get subtly wrong (colors
  that vanish across a page break, notes that swallow floats), and a broken
  preamble breaks the collaborator's build too. Run `make` in this skill's
  `test/` directory after changing the packages, and commit the refreshed
  `test/example.pdf` and `test/example-parskip.pdf` (they are in the repo so
  humans can browse the styles without building). `test/example.tex` exercises
  every note style across several agents; `test/test-compat.tex` guards
  backwards compatibility for papers that predate `agentnotes.sty` — it must
  keep building, and its rendering must not change, so do not modernize it.

## After completing each editing task

1. **Enumerate open items**: Scan the paper for author notes
   (`\sam{}`/`\Sam{}`-style lowercase-name macros, or legacy
   `\noteAuthor{}`/`\NoteAuthor{}`), agent notes from *any* agent in the paper
   (`\claude[...]{}`, `\codex[...]{}`, `\gemini[...]{}`, `\ai[...]{}`, their
   capitalized inline forms, legacy `\noteClaude{}`),
   `\<agent>Suggest`/`<Agent>Suggest` suggestions awaiting a decision, and
   `TODO` markers
2. **Present the list**: Show a numbered list of open items with brief
   descriptions and line references
3. **Suggest next task**: Recommend which item to tackle next

Enumerate other agents' notes as well as your own. A suggestion left by
another agent is still an open item for the author.

## Setting up a new paper

When asked to set up the todonotes workflow in a new LaTeX project:

1. Copy `mytodonotes.sty` **and** `agentnotes.sty` from this skill's directory
   into the paper directory, and commit them — collaborators who clone the repo
   need them to build. (Copy `claudenotes.sty` too only if the paper already
   loads it; new papers do not need it.)
2. Load both in the preamble and instantiate each agent working on the paper —
   all fixed machinery lives in the packages, nothing to paste inline:
   ```latex
   \usepackage{mytodonotes}   % todonotes config, \note, \response, \notewho
   \usepackage{agentnotes}    % \newagent and the macro family it mints
   \newagent{claude}          % one line per agent; add \newagent{codex} etc.
   ```
   A stem with a built-in preset needs nothing more. Anything else supplies its
   own name, color and mark:
   ```latex
   \newagent{qwen}[name=Qwen, color=orange!60, mark=\ding{92}]
   ```
   and any agent can be re-tinted for one paper with
   `\newagent{claude}[color=<color>]`.
3. Define per-author note macros in the document preamble (the paper-by-paper
   part), in the bare-name style, **three lines per author**:
   ```latex
   \colorlet{notecolor-sam}{red!40}
   \newcommand{\sam}[2][]{\note[#1]{sam}{notecolor-sam}{#2}}
   \newcommand{\Sam}[2][]{\sam[inline,#1]{#2}}
   ```
   The `notecolor-<name>` colorlet is not just decoration: every agent takes
   its owner styling from it automatically (borders, leader lines, and the block
   pole's owner stripe all use the color unmodified), so a new author needs
   **no agent-specific setup**. Check that a name doesn't clash with an existing
   LaTeX command (an author named `max` or `sec` needs a variant) before
   defining it. The same caution applies to agent stems.
4. Write a **self-contained `AGENTS.md`** in the paper repo describing the
   workflow, plus one-line `CLAUDE.md` and `GEMINI.md` files pointing at it:
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
   `\newagent` and an author with the three-line pattern, the mechanical notes
   above, the open-items enumeration habit, and the sync protocol if the repo is
   Overleaf-synced. Write it agent-neutrally, the way this document is written,
   so that whichever agent a collaborator uses can follow it. The skill's repo
   (https://github.com/postylem/latex-todonotes) may be mentioned as provenance,
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

1. Copy in `mytodonotes.sty` and `agentnotes.sty` and replace the inline block
   with the two `\usepackage` lines, the `\newagent` lines, and the
   three-line-per-author pattern, converting each author's literal color into a
   `notecolor-<name>` colorlet
2. Tag the existing agent material by owner. Ownership is usually recoverable
   from history rather than by eye — diff against the commit or tag before a
   given session's work and attribute each suggestion block and response
   accordingly, rather than guessing from the prose
3. Rebuild and compare the rendering: plain author notes should look unchanged
   (`mytodonotes.sty` sets `bordercolor = fill`, so only agent notes gain a
   visible owner-colored frame)
