---
name: latex-todonotes
description: Edit LaTeX papers using todonotes for author-Claude collaboration. Respond to author margin comments, mark Claude's contributions with owner-tagged \claude/\Claude/\claudeSuggest macros, and enumerate open items after each task.
---

# LaTeX Todonotes Editing Workflow

## Responding to author comments

**CRITICAL: NEVER DELETE author todonotes.** The default author-macro style is the bare lowercase name — `\jac{...}` (margin) and `\Jac{...}` (inline); older projects use `\noteAuthor{}`/`\NoteAuthor{}`. Whatever the style, if the name is anyone other than Claude, the note is the author's: they will remove their own comments after review.

When addressing a comment:
1. **Make the requested edit** to the surrounding text/code
2. **Keep the original comment** exactly as written
3. **Add `\response{claude}`** inside the note explaining what you did

Example — if author writes:
```latex
Note 1 = 2.\jac{Wrong! Fix RHS of equation.}
```

Correct response:
```latex
Note 1 = 1.\jac{Wrong! Fix RHS of equation.
\response{claude} Fixed. Now the equation is correct.}
```

**WRONG** (deleting the comment):
```latex
Note 1 = 1.
```

## Marking Claude's contributions (owner-tagged, default style)

Claude's notes and edits carry an *owner* tag naming whose Claude session made
them — the human running the session, lowercase (e.g. `jac`). Determine the
owner from context (repo CLAUDE.md, git user name) or ask; do not guess.

- **Margin notes**: `\claude[<owner>]{note text}` — labeled `claude@<owner>`
- **Inline notes**: `\Claude[<owner>]{note text}`
- **Inline suggestions**: `\claudeSuggest[<owner>]{suggested text}` for small
  inline changes proposed but not applied
- **Claude-authored replacement text**: `\claudechange[<owner>]{...}` —
  renders in Claude purple; the owner argument is provenance
- **New block-level text**: wrap in `\begin{ClaudeSuggest}...\end{ClaudeSuggest}`
  (renders with a changebar)

All Claude notes share one Claude purple; the owner shows as an accent — the
note's frame and leader line take a darkened version of the owner's own note
color (`notecolor-<owner>`), looked up automatically from the author's
existing macro setup. Omitting `[<owner>]` (or naming an owner without a
`notecolor`) falls back to plain purple; prefer always tagging the owner so
multi-author projects can tell whose session made an edit.

**Legacy projects**: papers set up with the older convention use
`\noteClaude{...}`/`\NoteClaude{...}` and untagged `\claudeSuggest{...}`.
Follow whatever convention the project already uses; introduce the
owner-tagged macros only when setting up new projects or when asked to migrate.

## After completing each editing task

1. **Enumerate open items**: Scan the paper for author notes (`\jac{}`/`\Jac{}`-style lowercase-name macros, or legacy `\noteAuthor{}`/`\NoteAuthor{}`), Claude notes (`\claude[...]{}`, `\Claude[...]{}`, legacy `\noteClaude{}`), `\claudeSuggest`/`ClaudeSuggest` suggestions, and `TODO` markers
2. **Present the list**: Show numbered list of open items with brief descriptions and line references
3. **Suggest next task**: Recommend which item to tackle next

## Setting up a new paper

When asked to set up the todonotes workflow in a new LaTeX project:

1. Copy `mytodonotes.sty` **and** `claudenotes.sty` from this skill's directory (wherever this SKILL.md lives) into the paper directory
2. Load both in the preamble — all fixed Claude machinery lives in the package, nothing to paste inline:
   ```latex
   \usepackage{mytodonotes}   % todonotes config, \note, \response
   \usepackage{claudenotes}   % \claude[owner], \Claude, \claudeSuggest, \claudechange, ClaudeSuggest env
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
   `\response{claude}` example, the owner-tagged Claude macros and what they
   render as, the three-line new-author pattern, the open-items enumeration
   habit, and the sync protocol if the repo is Overleaf-synced. The skill's
   repo (https://github.com/postylem/latex-todonotes) may be mentioned as
   provenance, never as the place the instructions live.
