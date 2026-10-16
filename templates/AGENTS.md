# Editing conventions for this paper

This paper uses margin notes for the conversation between its authors and the
AI agents that work on it. The packages are in the repository
(`mytodonotes.sty`, `agentnotes.sty`, `todofloats.sty`); they come from
https://github.com/postylem/latex-todonotes.

## Who you are

Each agent has a line `\newagent{<stem>}` in the preamble (or an entry in the
`agents={...}` option of `mytodonotes`). Use the stem that is yours (`claude`,
`codex`, `gemini`; `ai` if none fits) and add the line if it is missing. Below,
`\claude` stands for your stem and `sam` for the **owner**: the person running
your session (lowercase, as in their own note macro). Take the owner from the
repository's instructions or the git user name, or ask; do not guess.

## Rules

1. **Never delete or change an author's note** (`\sam{...}`, `\Sam{...}`). Make
   the edit it asks for, keep the note as written, and append your reply inside
   it:
   ```latex
   Note 1 = 1.\sam{Wrong! Fix RHS of equation.
   \claudeResponse[sam] Fixed. Now the equation is correct.}
   ```
   Other agents' notes and replies are treated the same way.
2. **Mark what you write.**
   | you write | meaning | open item? |
   |---|---|---|
   | `\claude[sam]{...}` / `\Claude[sam]{...}` | a note of your own, in the margin / in the text | yes |
   | `\claudeResponse[sam] ...` | a reply inside somebody's note | part of that note |
   | `\claudeSuggest[sam]{...}` | wording you **propose**; the paper's sentence is left as it is | yes |
   | `\begin{ClaudeSuggest}[sam] ... \end{ClaudeSuggest}` | a block of new text you propose | yes |
   | `\claudechange[sam]{...}` | text you have **already written into** the paper (works in math) | no |
   | `\begin{ClaudeChange}[sam] ... \end{ClaudeChange}` | the same for a block; may contain floats and headings | no |
   Use `Suggest` when the author has to choose, `change` when you have made the
   edit. Prefer a proposal or a note to rewriting an author's sentences.
3. **Notes are numbered.** Every note opens with a tag (who, and its number).
   Never type a number: put `\label{note:<name>}` at the start of a note and
   refer to it with `\cref{note:<name>}` (or `\ref`), which prints the tag.
4. **New authors** go into the `authors={...}` list of `\usepackage[...]{mytodonotes}`
   (or `\noteauthors{...}`); `name=color` fixes a color. A name must not clash
   with an existing command (`max`, `sec`).
5. **Build before you report.** Use `latexmk`: the notes need three or four
   runs from scratch (the log says `Margin note positions have changed` until
   the layout is final). Notes break across pages by themselves; do not split
   a long note by hand. No `\footnote` inside a note.
6. **End every task with the open items**: the notes, with who spoke last, and
   the proposals that await a decision, as a numbered list with file and line.
   If the skill is installed, `tools/open_items.py main.tex` prints it;
   `--awaiting <name>` keeps the items where `<name>` did not have the last word.
