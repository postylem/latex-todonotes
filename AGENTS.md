# LaTeX todonotes editing workflow — agent entry point

This is the generic entry point to the **latex-todonotes** skill: a
margin-comment workflow for collaborating with a human author on a LaTeX paper,
built on [todonotes](https://ctan.org/pkg/todonotes).

> **Not a contributor guide.** If you are here to *develop this skill* rather
> than to edit a paper with it, this file does not apply to you; read
> `README.md` and `docs/` instead.

## Identify yourself

The workflow refers to `<agent>` (your lowercase stem, used in macro names) and
`<Agent>` (your capitalized display name, used in labels). Resolve them as:

| if you are | stem | display name | macros |
|---|---|---|---|
| OpenAI Codex | `codex` | `Codex` | `\codex`, `\Codex`, `CodexSuggest`, … |
| Google Gemini | `gemini` | `Gemini` | `\gemini`, `\Gemini`, `GeminiSuggest`, … |
| Claude | `claude` | `Claude` | `\claude`, `\Claude`, `ClaudeSuggest`, … |
| anything else | `ai` | `AI` | `\ai`, `\AI`, `AISuggest`, … |

If the paper's preamble already has a `\newagent{<stem>}` line that is yours,
use that stem. If it has none that is yours, add one. Any other stem may be
declared with a name, color and mark of its own — see `WORKFLOW.md`.

## Read the workflow

**[WORKFLOW.md](WORKFLOW.md) is the authoritative workflow. Read it before
editing any paper.** It covers responding to author comments without deleting
them, marking your own contributions, the mechanical pitfalls of these macros,
enumerating open items after each task, setting up a new paper, and migrating an
existing one.

One rule is repeated here because getting it wrong destroys the author's work:
**never delete an author's todonote.** Append a `\<agent>Response[<owner>]`
inside it instead.
