# Making the skill agent-agnostic

Design doc, 2026-09-14.

## Goal

Let the skill work for any agentic AI system, not just Claude Code, by
factoring the agent's identity out of the LaTeX packages and the workflow
prose. A paper must be able to carry notes from several agents at once
(`\claude[sam]{...}` beside `\gemini[sam]{...}`), and every paper already set
up with this skill must keep building untouched.

## Decisions taken

1. **Multiple agents per paper.** A generic core package plus a `\newagent`
   instantiation macro that mints a whole macro family, mirroring the
   three-line-per-author pattern the package already uses for humans. Not a
   single package parameterized by load-time option, which could not express
   two agents in one file.
2. **One agent-neutral workflow body**, with a thin entry point in front of it.
   Originally: Claude Code keeps a Claude-specific `SKILL.md` and everyone else
   reads `AGENTS.md`. **Corrected during implementation** — see "Codex also
   loads SKILL.md" below.
3. **Four presets: `claude`, `gemini`, `codex`, `ai`.** The OpenAI stem is
   `codex` (the agentic tool, the closer parallel to `claude` meaning Claude
   Code here) and takes the generic mark, because no ZapfDingbats glyph
   resembles OpenAI's hexagonal knot.
4. **Marks** (all verified present in pifont): Claude `\ding{91}` (✻, as
   today), Gemini `\ding{70}` (✦, its four-pointed sparkle), generic
   `\ding{71}` (✧). ✧ is also the fallback for any agent without a
   distinctive glyph, which is why `codex` uses it.

## Non-goals

- Per-agent *model* identity (`Claude Opus` vs `Claude`).
- Generated per-vendor `.sty` files; the preset table replaces them.
- A template or build step that emits the markdown entry points.
- Any change to how human author notes work.

## Architecture

### `agentnotes.sty` — the generic core

A rename of `claudenotes.sty` with identity factored out. The label and block
machinery is **renamed, not rewritten**: the chip-rule label overlay, the
flag-on-a-flagpole overlay, the owner stripe and its L-shaped cap, the pole
drawn on every page of a breakable block, and the footnote recoloring are all
agent-independent and carry over as-is, with `\claude@*` becoming `\agent@*`.
This is the bulk of the file and the part that was hard to get right.

Per-agent state, keyed by stem, deliberately mirroring the `notecolor-<name>`
convention already used for human authors so that both halves of a label
resolve the same way:

- `agentcolor-<stem>`, with `agenttext-<stem>` and `agentbg-<stem>` derived
  by the existing `!80!black` and `!17` formulas. Hyphen, not `@`: these are
  document-level color names that a paper may redefine to re-tint an agent, so
  they follow the `notecolor-<name>` spelling authors already use rather than
  the `@` of the package's internals.
- `\agent@mark@<stem>` and `\agent@word@<stem>`, via `\@namedef`

#### `\newagent`

```latex
\newagent{claude}                                    % preset
\newagent{claude}[color=PaperTerracotta]             % preset, re-tinted
\newagent{qwen}[name=Qwen, color=teal!70!black, mark=\ding{92}]   % custom
```

Signature `\NewDocumentCommand{\newagent}{m O{}}`, with `name`, `color` and
`mark` as `pgfkeys` keys under `/agent` (pgfkeys is already loaded via
tcolorbox). Key-value rather than positional arguments: it makes a preset, a
partial override and a fully custom agent one syntax, and leaves room for
further keys without changing the signature.

Resolution order for each of the three properties: the caller's key overrides
the preset, which overrides the neutral default.

For stem `claude` and display name `Claude` it mints:

| generated | from |
|---|---|
| `\claude[owner][todonotes-opts]{body}` | stem |
| `\claudeResponse[owner]` | stem |
| `\claudeSuggest[owner]{text}` | stem |
| `\claudechange[owner]{text}` | stem |
| `\claudespark` | stem |
| `\Claude[owner][opts]{body}` | **display name** |
| `ClaudeSuggest` environment | **display name** |

The naming rule: **lowercase forms come from `<stem>`, capitalized forms come
from `<Display>`.** Deriving the capitalized forms from the display name
rather than by upcasing the stem is what makes `ai` yield `\AI` and
`AISuggest` instead of `\Ai` and `AiSuggest`.

The display name is the caller's `name=`, else the preset's, else **the stem
with its first letter titlecased** (expl3's `\text_titlecase_first:n`). That
last fallback is required, not cosmetic — see finding 3 below.

`\newagent` must raise a `\PackageError` rather than silently clobber if
`\<stem>` or `\<Display>` already exists. This is the same clash hazard
`SKILL.md` already warns about for author names such as `max` or `sec`.

#### Owner-suffix sentinel

Today `\@namedef{claude@who@claude}{claude}` suppresses the `@owner` half of
the label when the owner is the agent itself. This generalizes to a single
comparison — owner equals stem implies no suffix — so no table is needed.
`\claude{...}` renders `✻Claude`; `\claude[sam]{...}` renders `✻Claude@sam`.

#### Preset table

Each preset is three `\@namedef`s (`agent@pname@`, `agent@pcolor@`,
`agent@pmark@`), set by an internal
`\agent@defpreset{stem}{Display}{color}{mark}`:

| stem | display | color | mark |
|---|---|---|---|
| `claude` | Claude | `RGB 212,108,77` terracotta (unchanged) | `\ding{91}` ✻ |
| `gemini` | Gemini | `RGB 66,133,244` blue | `\ding{70}` ✦ |
| `codex` | Codex | `RGB 64,65,79` graphite | `\ding{71}` ✧ |
| `ai` | AI | `black!55` neutral gray | `\ding{71}` ✧ |

Each base color is used as paint only; the label's text takes `!80!black` and
its background `!17`, exactly as Claude's does today. `ai` is spelled as a
percentage of black rather than an `RGB` triple **deliberately**: it is the
natural way to write a neutral gray, and it means a shipped preset exercises
finding 2, which an all-`RGB` table would leave untested. The Gemini and Codex
values are deliberate choices in the neighbourhood of those products' hues,
not asserted brand colors, and carry no more precision than that.

Gemini's ✦ and the generic ✧ differ only by fill, which is subtle at
`\scriptsize`. Accepted: the word beside the mark carries the identification,
and filled-for-vendor / hollow-for-generic is a coherent relationship.

### `claudenotes.sty` — compatibility shim

Reduced to `\RequirePackage{agentnotes}` plus `\newagent{claude}`, retaining
`ClaudeColor`, `ClaudeTextColor` and `ClaudeNoteBG` as aliases of the new
per-agent colors, since existing papers may reference them for re-tinting.
Every paper already set up with this skill keeps building with no edit. This
is a hard requirement and the primary acceptance test.

### `mytodonotes.sty` — unchanged

`\note`, `\response`, `\notewho`, `\noteframecolor` and the
`\parskip`/`\if@nobreak` machinery are already agent-neutral. Only the header
comment that mentions `claudenotes` changes; no version bump.

## Verified mechanics

Probed against TeX Live 2025 before writing this document. Generating macros
and a `tcolorbox` environment from a computed stem works, and the owner
sentinel and titlecase fallback behave. Four findings the implementation must
respect:

1. **`g` (trailing optional brace group) is not a valid argument type** — it
   was removed from the kernel's document-command interface. Hence the
   key-value signature above rather than
   `\newagent{stem}{Display}{color}{mark}` with optional trailing groups.
2. **Derived colors must come from the defined name, not the expression.**
   `\colorlet{agenttext-ai}{black!55!80!black}` fails with ``Undefined color
   `80'`` because xcolor's chain syntax needs a color name where `80` sits.
   Define `agentcolor-<stem>` first, then derive from that single plain name.
   The original `claudenotes.sty` already did this correctly; naive
   parameterization reintroduces the bug. `teal!70!black` masks it by
   happening to end in a color name, so a test must include a base expression
   ending in a percentage, such as `black!55`.
3. **A preset-less stem collides with itself** if the display name defaults to
   the stem: `\newagent{zed}` then tries to define `\zed` as both the margin
   macro (from the stem) and the inline macro (from the display name).
   Titlecasing the stem for the fallback display name fixes it, and matches
   the existing lowercase-margin / Capitalized-inline convention.
4. **`\colorlet` does not expand its expression argument**, so a `\def`'d or
   `\edef`'d expression handed to it directly is not parsed. Where an
   expression must be passed through, build the whole call with `\edef` and
   `\noexpand`, then execute it.

The residual risk is concentrated in the generated `<Display>Suggest`
environment, whose tcolorbox overlay closes over the owner argument; the probe
covered name generation but not the full overlay with the pole and L-cap.

## Instruction layer

### Codex also loads SKILL.md

The original plan gave Claude Code a `SKILL.md` opening "You are Claude" and
routed every other agent through `AGENTS.md`. That was based on a wrong premise.
Codex CLI (checked against 0.154.0) has its own skills mechanism at
`~/.codex/skills/<name>/SKILL.md`, using the same filename and the same
`name`/`description` frontmatter as Claude Code; `AGENTS.md` is its *repo-level*
instruction file, not its skill entry point. Installing this repo as a Codex
skill would therefore have handed Codex a file telling it that it was Claude,
and it would have written `\claude[...]` notes — mislabeling its own work and
defeating the entire change.

So `SKILL.md` carries the identify-yourself table and is agent-neutral, serving
both skill loaders. `AGENTS.md` shrinks to a pointer at `SKILL.md` and
`WORKFLOW.md`, for an agent given this clone but no skill mechanism. The
per-paper `AGENTS.md` that setup writes is unaffected — that is repo-level
instruction, which is what `AGENTS.md` is actually for.

- **`WORKFLOW.md`** — the entire workflow, agent-neutral, written against the
  `\<agent>` / `\<Agent>` / `\<agent>Response` / `\<agent>Suggest` /
  `\<agent>change` / `<Agent>Suggest` convention, opening with: your stem is
  whatever `\newagent` instantiated for you; absent that, you are `ai`. It
  carries everything substantive — the never-delete-author-notes rule, the
  mechanical notes, the open-items habit, new-paper setup, migration.
- **`SKILL.md`** — Claude Code frontmatter, "you are Claude, stem `claude`",
  and a pointer to the body.
- **`AGENTS.md`** — "Codex uses stem `codex`, Gemini `gemini`, anything else
  `ai`", and the same pointer.

### Paper-side setup

Step 4 of "Setting up a new paper" changes from writing a self-contained
`CLAUDE.md` to writing a self-contained **`AGENTS.md`**, plus one-line
`CLAUDE.md` and `GEMINI.md` files pointing at it. Pointer files rather than
symlinks, which Overleaf's git bridge handles poorly. The self-containment
requirement is unchanged and remains the point: a collaborator who clones the
repo has no skill installed, so the instructions must live in the repo.

Verify during implementation whether current Claude Code reads `AGENTS.md`
natively; the `CLAUDE.md` pointer is correct either way.

## Example and tests

`example.tex` currently exercises one agent and so cannot catch multi-agent
bugs. It gains `\gemini[bob]`, `\codex`, an untagged `\ai` block, and one
custom `\newagent`, including two adjacent block suggestions with different
owner stripes. Both PDFs (`example.pdf`, `example-parskip.pdf`) are rebuilt
and recommitted.

The custom agent must be declared with a base color **ending in a percentage**
— `\newagent{qwen}[name=Qwen, color=orange!60, mark=\ding{92}]` — since all
four presets use plain `RGB` values and so cannot exercise finding 2. A color
expression ending in a color name, such as `teal!70!black`, masks that bug.

The build files live in `test/` rather than the repo root, with a `latexmkrc`
that puts the repo's own `.sty` files first on `TEXINPUTS` and a `Makefile`
covering all three builds, so the root holds only the packages and the prose.

A new `test-compat.tex` holds the *old* preamble verbatim —
`\usepackage{claudenotes}` with the pre-`\newagent` author macros — so
backwards compatibility is something that builds rather than something
claimed.

Acceptance criteria:

- `test-compat.tex` builds clean against the shim
- `example.tex` builds clean with four agents plus one custom
- `test-compat.pdf` renders **byte-identically** to its pre-refactor build,
  checked by rasterizing both at 150dpi and comparing the page images, not by
  eye. This replaces the originally planned "Claude-only sections of
  `example.pdf` are unchanged" check, which is not achievable: adding agents to
  `example.tex` reflows its pagination, so a page-image diff of that file would
  report differences that are entirely expected. `test-compat.tex` is the
  stronger guard anyway, since it is held fixed by design.
- a base color expression ending in a percentage is covered by at least one
  agent, so finding 2 cannot regress silently — by the `ai` preset (`black!55`)
  and again by the custom `qwen` agent in `example.tex` (`orange!60`)

## Naming and distribution

`latex-todonotes`, both skill and repo name, is already neutral and stays.
`README.md` and both plugin manifests drop the "author–Claude" framing for
"author–agent". `.claude-plugin/plugin.json` remains a Claude Code manifest,
because that is what it is.
