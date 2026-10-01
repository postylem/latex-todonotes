#!/usr/bin/env python3
"""List the open items of a LaTeX paper that uses mytodonotes / agentnotes.

An open item is something that waits for somebody:

  note      a margin or inline note by an author (\\sam{...}, \\Sam{...},
            \\notewho{sam}{...}) or by an agent (\\claude[sam]{...}, ...), with
            the replies inside it (\\response{lee}, \\claudeResponse[sam]);
  proposal  wording an agent offers but has not applied: \\<agent>Suggest[...]{...}
            inline, or a \\begin{<Agent>Suggest} block;
  TODO      a TODO marker in the text.

Text an agent has already applied (\\<agent>change{...}) is not an open item.
A paper that defines \\<agent>Suggest or the <Agent>Suggest environment itself
(the older convention, where they mark applied text) is detected, and those are
left out as well; --suggest forces them in, --no-suggest out.

The authors and agents are read from the preamble: the `authors={...}` and
`agents={...}` package options, \\noteauthors{...}, \\newagent{...}, and the
three-line pattern  \\newcommand{\\sam}[2][]{\\note[#1]{sam}{...}{#2}}.

Each item is printed with file:line, the number of the note in the PDF (read
from the .aux file, so compile first), who spoke, and who spoke last.

  open_items.py [main.tex]                    every open item
  open_items.py --awaiting sam                items where sam did not speak last
  open_items.py --who claude                  items opened by claude
  open_items.py --json                        machine-readable

Exit status is 0 (also when there are no open items).
"""
import argparse
import json
import os
import re
import sys

PRESET_DISPLAY = {"claude": "Claude", "codex": "Codex", "gemini": "Gemini", "ai": "AI"}


def strip_comments(text):
    """Blank out comments, `comment' environments and what follows \\end{document},
    keeping every line break (so line numbers stay right)."""
    out = []
    in_comment_env = False
    ended = False
    for line in text.split("\n"):
        if ended:
            out.append("")
            continue
        if in_comment_env:
            if re.search(r"\\end\{comment\}", line):
                in_comment_env = False
            out.append("")
            continue
        m = re.search(r"(?<!\\)%", line)
        if m:
            line = line[:m.start()]
        if re.search(r"\\begin\{comment\}", line):
            in_comment_env = True
            line = line[:line.index("\\begin{comment}")]
        if "\\end{document}" in line:
            ended = True
            line = line[:line.index("\\end{document}")]
        out.append(line)
    return "\n".join(out)


def find_root(arg):
    if arg:
        return arg
    if os.path.exists("main.tex"):
        return "main.tex"
    roots = [f for f in sorted(os.listdir("."))
             if f.endswith(".tex") and "\\documentclass" in open(f, errors="replace").read()]
    if len(roots) == 1:
        return roots[0]
    sys.exit("open_items.py: name the main .tex file (found %d candidates)" % len(roots))


def collect_files(root):
    """The root file and everything it \\input's or \\include's, in order."""
    base = os.path.dirname(os.path.abspath(root))
    seen, order = set(), []

    def visit(path):
        full = os.path.normpath(os.path.join(base, path))
        if not os.path.exists(full) and os.path.exists(full + ".tex"):
            full += ".tex"
        if full in seen or not os.path.isfile(full):
            return
        seen.add(full)
        text = strip_comments(open(full, encoding="utf-8", errors="replace").read())
        order.append((os.path.relpath(full, base), text))
        for m in re.finditer(r"\\(?:input|include|subfile)\{([^}]+)\}", text):
            visit(m.group(1).strip())

    visit(os.path.basename(root))
    return base, order


def braced(text, i):
    """text[i] is '{': return (content, index after the matching '}')."""
    depth, j = 0, i
    while j < len(text):
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j], j + 1
        j += 1
    return text[i + 1:], len(text)


def optional(text, i):
    """Optional arguments [..][..] starting at i: return (list, index after)."""
    opts = []
    while True:
        j = i
        while j < len(text) and text[j] in " \t":
            j += 1
        if j < len(text) and text[j] == "[":
            k = text.find("]", j)
            if k < 0:
                break
            opts.append(text[j + 1:k].strip())
            i = k + 1
        else:
            break
    return opts, i


def titlecase_first(s):
    return s[:1].upper() + s[1:]


def read_setup(all_text):
    """Authors and agents declared in the preamble."""
    authors, agents = [], {}

    def add_author(name):
        name = name.split("=")[0].strip()
        if name and name not in authors:
            authors.append(name)

    for m in re.finditer(r"\bauthors\s*=\s*\{([^}]*)\}", all_text):
        for item in m.group(1).split(","):
            add_author(item)
    for m in re.finditer(r"\\noteauthors\{([^}]*)\}", all_text):
        for item in m.group(1).split(","):
            add_author(item)
    for m in re.finditer(r"\\newcommand\{?\\([A-Za-z]+)\}?\[2\]\[\]\{\\note\[", all_text):
        if m.group(1)[:1].islower():
            add_author(m.group(1))
    for m in re.finditer(r"\bagents\s*=\s*\{([^}]*)\}", all_text):
        for stem in m.group(1).split(","):
            stem = stem.strip()
            if stem:
                agents.setdefault(stem, PRESET_DISPLAY.get(stem, titlecase_first(stem)))
    for m in re.finditer(r"\\newagent\{([A-Za-z]+)\}(?:\s*\[([^\]]*)\])?", all_text):
        stem, keys = m.group(1), m.group(2) or ""
        name = re.search(r"\bname\s*=\s*([A-Za-z]+)", keys)
        agents[stem] = name.group(1) if name else PRESET_DISPLAY.get(stem, titlecase_first(stem))
    # the older convention: the paper defines the Suggest macros itself (applied text)
    legacy = set()
    for m in re.finditer(r"\\(?:re)?newcommand\{?\\([A-Za-z]+)Suggest\b", all_text):
        legacy.add(m.group(1))
    for m in re.finditer(r"\\(?:re)?newenvironment\{([A-Za-z]+)Suggest\}", all_text):
        legacy.add(m.group(1))
    return authors, agents, legacy


def excerpt(tex, width):
    t = re.sub(r"\\label\{[^}]*\}", "", tex)
    t = re.sub(r"\\(?:[A-Za-z]+Response)(?:\[[^\]]*\])?|\\response\{[^}]*\}", " / ", t)
    t = re.sub(r"\\(?:cref|Cref|ref|cite[a-z]*|eqref)\{([^}]*)\}", r"[\1]", t)
    t = re.sub(r"\\[A-Za-z@]+\*?", "", t)
    t = re.sub(r"[{}$~]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= width else t[:width - 1].rstrip() + "…"


def replies(body, agents):
    """Who replied inside a note, in order."""
    found = []
    stems = "|".join(sorted(agents, key=len, reverse=True)) or "(?!x)x"
    pattern = r"\\response\{([^}]*)\}|\\(%s)Response(?![A-Za-z])(?:\[([^\]]*)\])?" % stems
    for m in re.finditer(pattern, body):
        if m.group(1) is not None:
            name = m.group(1).strip()
            found.append(agents.get(name, name))
        else:
            who = agents[m.group(2)]
            if m.group(3):
                who += "@" + m.group(3).strip()
            found.append(who)
    return found


def note_numbers(base, root, aux=None):
    """(file, last line of the note) -> number, from the \\note@aux records of
    the newest .aux file of the paper (next to it or in a build directory)."""
    job = os.path.splitext(os.path.basename(root))[0]
    if aux:
        candidates = [aux]
    else:
        candidates = [os.path.join(base, job + ".aux")]
        candidates += [os.path.join(base, d, job + ".aux") for d in sorted(os.listdir(base))
                       if os.path.isdir(os.path.join(base, d)) and not d.startswith(".")]
        candidates = sorted((c for c in candidates if os.path.exists(c)),
                            key=os.path.getmtime, reverse=True)
    for path in candidates:
        text = open(path, encoding="utf-8", errors="replace").read()
        records = re.findall(r"\\note@aux\{(\d+)\}\{([^}]*)\}\{(\d+)\}", text)
        if not records:
            continue
        numbers = {}
        for n, f, line in records:
            f = os.path.normpath(f) if f else os.path.basename(root)
            if not os.path.splitext(f)[1]:
                f += ".tex"
            numbers.setdefault((f, int(line)), []).append(int(n))
        return numbers
    return {}


def scan(files, authors, agents, legacy, want_suggest):
    items, spans = [], []
    macros = {}   # macro name -> (kind, who, place)
    for a in authors:
        macros[a] = ("author", a, "margin")
        if titlecase_first(a) != a:
            macros[titlecase_first(a)] = ("author", a, "inline")
    for stem, disp in agents.items():
        macros[stem] = ("agent", stem, "margin")
        if disp != stem:
            macros[disp] = ("agent", stem, "inline")
    macros["notewho"] = ("who", None, "margin")
    macros["Notewho"] = ("who", None, "inline")
    names = "|".join(sorted((re.escape(k) for k in macros), key=len, reverse=True))
    note_re = re.compile(r"\\(%s)(?![A-Za-z@])" % names)

    for fname, text in files:
        def lineno(pos):
            return text.count("\n", 0, pos) + 1

        for m in note_re.finditer(text):
            if any(a <= m.start() < b for f, a, b in spans if f == fname):
                continue   # a note macro inside another note
            kind, who, place = macros[m.group(1)]
            opts, i = optional(text, m.end())
            owner = None
            if kind == "who":
                if i >= len(text) or text[i] != "{":
                    continue
                who, i = braced(text, i)
                who = who.strip()
            elif kind == "agent":
                owner = opts[0] if opts and "=" not in opts[0] and opts[0] != "inline" else None
            if i >= len(text) or text[i] != "{":
                continue   # the macro is only mentioned (e.g. in its own definition)
            body, end = braced(text, i)
            if "#" in body[:3]:
                continue   # a definition, not a use
            opener = agents[who] + ("@" + owner if owner else "") if kind == "agent" else who
            thread = replies(body, agents)
            spans.append((fname, m.start(), end))
            items.append(dict(kind="note", place=place, file=fname, line=lineno(m.start()),
                              endline=lineno(end - 1), who=opener, replies=thread,
                              last=(thread[-1] if thread else opener),
                              text=excerpt(re.split(r"\\response\{|\\[A-Za-z]+Response\b", body)[0], 200)))

        for stem, disp in agents.items():
            is_legacy = stem in legacy or disp in legacy
            if (is_legacy and want_suggest is not True) or want_suggest is False:
                continue
            for m in re.finditer(r"\\%sSuggest(?![A-Za-z@])" % re.escape(stem), text):
                opts, i = optional(text, m.end())
                if i >= len(text) or text[i] != "{":
                    continue
                body, end = braced(text, i)
                who = disp + ("@" + opts[0] if opts else "")
                items.append(dict(kind="proposal", place="inline", file=fname, line=lineno(m.start()),
                                  endline=lineno(end - 1), who=who, replies=[], last=who,
                                  text=excerpt(body, 200)))
            for m in re.finditer(r"\\begin\{%sSuggest\}" % re.escape(disp), text):
                opts, i = optional(text, m.end())
                close = text.find("\\end{%sSuggest}" % disp, i)
                body = text[i:close if close >= 0 else len(text)]
                who = disp + ("@" + opts[0] if opts else "")
                items.append(dict(kind="proposal", place="block", file=fname, line=lineno(m.start()),
                                  endline=lineno(close if close >= 0 else len(text) - 1), who=who,
                                  replies=[], last=who, text=excerpt(body, 200)))

        for m in re.finditer(r"\bTODO\b[:\s]*([^\n]*)", text):
            if any(a <= m.start() < b for f, a, b in spans if f == fname):
                continue
            items.append(dict(kind="TODO", place="text", file=fname, line=lineno(m.start()),
                              endline=lineno(m.start()), who="", replies=[], last="",
                              text=excerpt(m.group(1), 200)))

    order = {f: k for k, (f, _) in enumerate(files)}
    items.sort(key=lambda it: (order[it["file"]], it["line"]))
    return items


def main():
    ap = argparse.ArgumentParser(description="List the open items of a LaTeX paper (notes, proposals, TODOs).")
    ap.add_argument("root", nargs="?", help="main .tex file (default: main.tex)")
    ap.add_argument("--awaiting", metavar="NAME", help="only items where NAME did not speak last")
    ap.add_argument("--who", metavar="NAME", help="only items opened by NAME")
    ap.add_argument("--suggest", dest="suggest", action="store_true", default=None,
                    help="list <agent>Suggest even if the paper defines it itself")
    ap.add_argument("--no-suggest", dest="suggest", action="store_false",
                    help="never list <agent>Suggest")
    ap.add_argument("--aux", metavar="FILE", help=".aux file to read the note numbers from "
                    "(default: the newest one of the paper that has them)")
    ap.add_argument("--width", type=int, default=72, help="width of the text excerpt")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args()

    root = find_root(args.root)
    base, files = collect_files(root)
    all_text = "\n".join(t for _, t in files)
    authors, agents, legacy = read_setup(all_text)
    items = scan(files, authors, agents, legacy, args.suggest)
    numbers = note_numbers(base, root, args.aux)
    # Match notes to the \\note@aux records.  A record carries the line TeX had
    # read when the note was typeset: the line where the note ends, or a later
    # one when the note sits inside something that collects its text first
    # (the argument of another macro, a restated theorem, a caption).  So each
    # note, in order, goes to the nearest line at or after its end that still
    # has a free record; where a line has more records than notes (text that
    # is typeset twice), the last ones are the numbers that show in the PDF.
    free = {key: len(ns) for key, ns in numbers.items()}
    groups = {}
    for it in items:
        it["number"] = None
        if it["kind"] != "note":
            continue
        f = os.path.normpath(it["file"])
        lines = sorted(line for (g, line), n in free.items() if g == f and line >= it["endline"] and n > 0)
        if lines:
            free[(f, lines[0])] -= 1
            groups.setdefault((f, lines[0]), []).append(it)
    for key, notes in groups.items():
        for it, n in zip(notes, numbers[key][-len(notes):]):
            it["number"] = n

    def bare(name):
        return name.split("@")[0].lower()

    if args.who:
        items = [it for it in items if bare(it["who"]) == args.who.lower()]
    if args.awaiting:
        items = [it for it in items if it["kind"] != "note" or bare(it["last"]) != args.awaiting.lower()]

    if args.json:
        json.dump(items, sys.stdout, indent=1, ensure_ascii=False)
        print()
        return 0
    if not items:
        print("no open items")
        return 0
    for k, it in enumerate(items, 1):
        where = "%s:%d" % (it["file"], it["line"])
        if it["kind"] == "note":
            tag = "%s %s" % (it["who"], it["number"]) if it["number"] else it["who"]
            head = "[%s]%s" % (tag, " inline" if it["place"] == "inline" else "")
            tail = ""
            if it["replies"]:
                tail = "  (replies: %s; last: %s)" % (", ".join(it["replies"]), it["last"])
        elif it["kind"] == "proposal":
            head = "[%s] proposal%s" % (it["who"], " block" if it["place"] == "block" else "")
            tail = ""
        else:
            head, tail = "TODO", ""
        print("%d. %s  %s — %s%s" % (k, where, head, excerpt(it["text"], args.width), tail))
    n_notes = sum(it["kind"] == "note" for it in items)
    n_prop = sum(it["kind"] == "proposal" for it in items)
    n_todo = sum(it["kind"] == "TODO" for it in items)
    print("%d open items: %d notes, %d proposals, %d TODO markers" % (len(items), n_notes, n_prop, n_todo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
