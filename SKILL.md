---
name: latex-todonotes
description: Edit LaTeX papers using todonotes for author-Claude collaboration. Respond to author margin comments, mark Claude's contributions with owner-tagged \claude/\Claude/\claudeSuggest/\claudeResponse macros, and enumerate open items after each task.
---

# LaTeX Todonotes Editing Workflow

## Responding to author comments

**CRITICAL: NEVER DELETE author todonotes.** The default author-macro style is the bare lowercase name — `\jac{...}` (margin) and `\Jac{...}` (inline); older projects use `\noteAuthor{}`/`\NoteAuthor{}`. Whatever the style, if the name is anyone other than Claude, the note is the author's: they will remove their own comments after review.

When addressing a comment:
1. **Make the requested edit** to the surrounding text/code
2. **Keep the original comment** exactly as written
3. **Add `\claudeResponse[<owner>]`** inside the note explaining what you did

Example — if author writes:
```latex
Note 1 = 2.\jac{Wrong! Fix RHS of equation.}
```

Correct response:
```latex
Note 1 = 1.\jac{Wrong! Fix RHS of equation.
\claudeResponse[jac] Fixed. Now the equation is correct.}
```

**WRONG** (deleting the comment):
```latex
Note 1 = 1.
```

Append rather than replace: a note may already carry responses from other people and from other Claude sessions, and each is part of the record.

## Marking Claude's contributions (owner-tagged, default style)

Claude's notes and edits carry an *owner* tag naming whose Claude session made
them — the human running the session, lowercase (e.g. `jac`). Determine the
owner from context (repo CLAUDE.md, git user name) or ask; do not guess.

- **Margin notes**: `\claude[<owner>]{note text}` — labeled `claude@<owner>`
- **Inline notes**: `\Claude[<owner>]{note text}`
- **Replies in another author's note**: `\claudeResponse[<owner>]` — the
  `\response` rule and spacing, headed `claude@<owner>`
- **Inline suggestions**: `\claudeSuggest[<owner>]{suggested text}` for small
  inline changes proposed but not applied
- **Claude-authored replacement text**: `\claudechange[<owner>]{...}` —
  renders in Claude purple; the owner argument is provenance
- **New block-level text**: wrap in
  `\begin{ClaudeSuggest}[<owner>]...\end{ClaudeSuggest}` (renders like
  regular document text, just in Claude purple: full text width, with a
  purple changebar hanging in the left gutter, headed by a small
  `claude@<owner>` label)

Every one of these labels is set the same way: `claude` in Claude purple on
Claude's own tint, then `@<owner>` in the ordinary text color on
`notecolor-<owner>` itself, unmodified. The owner half therefore looks exactly
like that author's name already does in their own `\<author>{...}` note or
`\response{<author>}`. The colorlet is looked up automatically from the
author's existing macro setup, so no Claude-specific setup is needed.

Author note colors are chosen to sit *behind* text, so they are used as
backgrounds and never as text colors. An earlier version of this package tinted
the `@<owner>` text with a darkened author color instead, which read poorly in
general and became nearly invisible in the commonest case of all: a
`\claudeResponse[<owner>]` inside a note belonging to that same owner. The one
place a darkened author color is still used is `\claude`'s note frame and
leader line, where a saturated color is what is wanted.

The backgrounds are painted as rules in a zero-width, zero-height overlay, so a
label's metrics are exactly those of the plain text — adding one never shifts
anything horizontally or vertically.

Omitting `[<owner>]` (or naming an owner without a `notecolor`) falls back to
plain purple with no `@` suffix; prefer always tagging the owner so multi-author
projects can tell whose session made an edit.

**Legacy projects**: papers set up with the older convention use
`\noteClaude{...}`/`\NoteClaude{...}`, untagged `\claudeSuggest{...}`, and
`\response{claude}`. Follow whatever convention the project already uses;
introduce the owner-tagged macros only when setting up new projects or when
asked to migrate.

## Mechanical notes

- **`\claude{}` cannot appear inside a `ClaudeSuggest` box.** It is a
  `\marginpar`, and tcolorbox swallows it — the failure surfaces as
  `! LaTeX Error: Float(s) lost`, not as a missing note. Put the margin note
  immediately *before* `\begin{ClaudeSuggest}`.
- **Prefer suggestion blocks and margin notes to rewriting prose in place.**
  Editing an author's sentences directly is hard for them to review; a
  `ClaudeSuggest` block leaves the original intact and is trivial to accept or
  drop. When a block is meant to *replace* nearby text rather than add to it,
  say so in its first sentence.
- **Inline notes break across pages.** `[inline]` notes are typeset as a
  breakable box (todonotes' own inline notes are single unbreakable TikZ
  nodes), so a long inline comment flows onto the next page instead of
  overflowing it. Other todonotes options passed alongside `inline` are
  ignored on this path.
- **Paragraphs inside notes follow the document's style.** Note bodies
  restore the document's `\parindent`/`\parskip` (captured at
  begin-document), and `ClaudeSuggest` blocks keep them directly
  (`parbox=false`), so multi-paragraph notes and blocks separate their
  paragraphs the same way the paper does — indentation by default, skips
  under `\usepackage{parskip}`. Between `\response` turns, a rule with a
  fixed 3pt on each side does the separating instead of `\parskip`.
- **Build before reporting.** These macros are easy to get subtly wrong
  (colors that vanish across a page break, notes that swallow floats), and a
  broken preamble breaks the collaborator's build too. `example.tex` in this
  skill's directory exercises every note style — rebuild it after changing the
  packages.

## After completing each editing task

1. **Enumerate open items**: Scan the paper for author notes (`\jac{}`/`\Jac{}`-style lowercase-name macros, or legacy `\noteAuthor{}`/`\NoteAuthor{}`), Claude notes (`\claude[...]{}`, `\Claude[...]{}`, legacy `\noteClaude{}`), `\claudeSuggest`/`ClaudeSuggest` suggestions awaiting a decision, and `TODO` markers
2. **Present the list**: Show numbered list of open items with brief descriptions and line references
3. **Suggest next task**: Recommend which item to tackle next

## Setting up a new paper

When asked to set up the todonotes workflow in a new LaTeX project:

1. Copy `mytodonotes.sty` **and** `claudenotes.sty` from this skill's directory (wherever this SKILL.md lives) into the paper directory, and commit them — collaborators who clone the repo need them to build
2. Load both in the preamble — all fixed Claude machinery lives in the packages, nothing to paste inline:
   ```latex
   \usepackage{mytodonotes}   % todonotes config, \note, \response, \notewho
   \usepackage{claudenotes}   % \claude[owner], \Claude, \claudeResponse, \claudeSuggest, \claudechange, ClaudeSuggest env
   ```
3. Define per-author note macros in the document preamble (the paper-by-paper part), in the bare-name style, **three lines per author**:
   ```latex
   \colorlet{notecolor-jac}{red!40}
   \newcommand{\jac}[2][]{\note[#1]{jac}{notecolor-jac}{#2}}
   \newcommand{\Jac}[2][]{\jac[inline,#1]{#2}}
   ```
   The `notecolor-<name>` colorlet is load-bearing: `\claude[<name>]` derives
   its accent from it automatically, so a new author needs **no
   Claude-specific setup**. Check that a name doesn't clash with an existing
   LaTeX command (an author named `max` or `sec` needs a variant) before
   defining it
4. Write a **self-contained CLAUDE.md** in the paper repo describing the
   workflow. Collaborators cloning the repo (e.g. from Overleaf) will not
   have this skill on their machine — their Claude sessions see only the
   repo — so the CLAUDE.md must spell the rules out rather than point to
   this skill's local path: the never-delete-author-notes rule with the
   `\claudeResponse[<owner>]` example, the owner-tagged Claude macros and what
   they render as, the three-line new-author pattern, the mechanical notes
   above, the open-items enumeration habit, and the sync protocol if the repo
   is Overleaf-synced. The skill's repo
   (https://github.com/postylem/latex-todonotes) may be mentioned as
   provenance, never as the place the instructions live.

## Migrating a paper that predates owner tagging

Papers set up before owner tagging have the todonote machinery pasted inline in
the preamble and an untagged `\claude`. To migrate:

1. Copy in the two `.sty` files and replace the inline block with the two
   `\usepackage` lines plus the three-line-per-author pattern, converting each
   author's literal color into a `notecolor-<name>` colorlet
2. Tag the existing Claude material by owner. Ownership is usually recoverable
   from history rather than by eye — diff against the commit or tag before a
   given session's work and attribute each `ClaudeSuggest` block and response
   accordingly, rather than guessing from the prose
3. Rebuild and compare the rendering: plain author notes should look unchanged
   (`mytodonotes.sty` sets `bordercolor = fill`, so only `\claude` notes gain a
   visible accent frame)
