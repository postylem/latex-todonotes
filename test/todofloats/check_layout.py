#!/usr/bin/env python3
"""Verify the margin-note layout produced by todofloats.sty from the .aux file.

Reads the zref records written by todofloats (one anchor label tdf@a@<id> and
one note label tdf@n@<id> per margin note, all values in scaled points) plus
the page geometry record, and asserts:

  * every note lies inside the page and inside the margin of the correct side
    (right of the text block for side r, left of it for side l);
  * the side follows the rule: two-column text -> the margin of the column
    the anchor is in (anchor x vs page center); one-column text -> right;
  * note and anchor are on the same page;
  * on every (page, side) consecutive notes do not overlap: the bottom of
    note i is at least `gap` above the top of note i+1;
  * every note lies inside the text area (top <= text top, bottom >= text
    bottom), i.e. the stacking stayed within the page.

A note that did not fit on its page is cut into pieces: the first piece is the
tdf@n@<id> record, piece k >= 2 is a tdf@c@<id>@<k> record (lower left corner,
height, width).  Every piece is checked like a note (inside the page, the
margin, and the text area; no overlap), and in addition:

  * the pieces of a note are in the same margin, numbered 2, 3, ... without
    gaps, and piece k is on a later page than piece k-1;
  * with --expect-cut N, at least N notes are cut (so the test document really
    exercises the cutting).

Usage: check_layout.py out/test_todofloats.aux [--gap 4pt] [--expect-cut N]
Exit status 1 if any assertion fails.
"""
import re
import sys
from collections import defaultdict

SP_PER_PT = 65536


def parse_dim(s):
    s = s.strip()
    if s.endswith("pt"):
        return int(round(float(s[:-2]) * SP_PER_PT))
    if s.endswith("sp"):
        return int(s[:-2])
    raise ValueError("dimension must end in pt or sp: %r" % s)


def pt(sp):
    return "%.1fpt" % (sp / SP_PER_PT)


def parse_aux(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    geo = None
    m = re.search(r"\\gdef\\tdf@aux@geometry\{((?:\{-?\d+\})+)\}", text)
    if m:
        vals = [int(v) for v in re.findall(r"\{(-?\d+)\}", m.group(1))]
        keys = ["paperwidth", "paperheight", "textleft", "textright",
                "ceiling", "floor", "marginparwidth", "marginparsep"]
        geo = dict(zip(keys, vals))
    labels = {}
    for name, props in re.findall(r"\\zref@newlabel\{(tdf@(?:[an]@\d+|c@\d+@\d+))\}\{(.*?)\}\n", text):
        labels[name] = {k: int(v) for k, v in re.findall(r"\\(\w+)\{(-?\d+)\}", props)}
    return geo, labels


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    aux = argv[1]
    gap = parse_dim("4pt")
    if "--gap" in argv:
        gap = parse_dim(argv[argv.index("--gap") + 1])
    tol = 2  # sp, rounding slack

    geo, labels = parse_aux(aux)
    failures = []
    if geo is None:
        failures.append("no \\tdf@aux@geometry record in %s" % aux)
        print("\n".join(failures))
        return 1

    notes = []
    for name, props in labels.items():
        if not name.startswith("tdf@n@"):
            continue
        nid = int(name.split("@")[-1])
        anchor = labels.get("tdf@a@%d" % nid)
        if anchor is None:
            failures.append("note %d has no anchor record" % nid)
            continue
        x, y = props["posx"], props["posy"]
        n = dict(id=nid, page=props["abspage"], x=x, y=y,
                 top=y + props["tdfht"], bottom=y - props["tdfdp"],
                 wd=props["tdfwd"], twocol=props["tdftwocol"],
                 ax=anchor["posx"], ay=anchor["posy"], apage=anchor["abspage"])
        n["side"] = "l" if x < geo["paperwidth"] // 2 else "r"
        n["piece"] = 1
        notes.append(n)
    # continuation pieces of notes that were cut
    first = {n["id"]: n for n in notes}
    pieces = defaultdict(dict)
    for name, props in labels.items():
        if name.startswith("tdf@c@"):
            _, _, nid, k = name.split("@")
            pieces[int(nid)][int(k)] = props
    for nid, ks in sorted(pieces.items()):
        head = first.get(nid)
        if head is None:
            failures.append("note %d has continuation pieces but no first piece" % nid)
            continue
        if sorted(ks) != list(range(2, len(ks) + 2)):
            failures.append("note %d: pieces are numbered %s" % (nid, sorted(ks)))
        prev_page = head["page"]
        for k in sorted(ks):
            props = ks[k]
            x, y = props["posx"], props["posy"]
            c = dict(id=nid, piece=k, page=props["abspage"], x=x, y=y,
                     top=y + props["tdfht"], bottom=y, wd=props["tdfwd"],
                     twocol=head["twocol"], ax=head["ax"], ay=y + props["tdfht"],
                     apage=props["abspage"])
            c["side"] = "l" if x < geo["paperwidth"] // 2 else "r"
            if c["side"] != head["side"]:
                failures.append("note %d piece %d is in margin %s, the first piece in %s"
                                % (nid, k, c["side"], head["side"]))
            if c["page"] <= prev_page:
                failures.append("note %d piece %d is on page %d, the previous piece on page %d"
                                % (nid, k, c["page"], prev_page))
            prev_page = c["page"]
            notes.append(c)
    notes.sort(key=lambda n: (n["id"], n["piece"]))
    if not notes:
        failures.append("no note records found in %s" % aux)

    center = geo["paperwidth"] // 2
    for n in notes:
        tag = "note %d%s (page %d, side %s)" % (
            n["id"], "" if n["piece"] == 1 else " piece %d" % n["piece"], n["page"], n["side"])
        # inside the page
        if not (0 <= n["bottom"] and n["top"] <= geo["paperheight"]):
            failures.append("%s is vertically outside the page: top=%s bottom=%s"
                            % (tag, pt(n["top"]), pt(n["bottom"])))
        if not (0 <= n["x"] and n["x"] + n["wd"] <= geo["paperwidth"]):
            failures.append("%s is horizontally outside the page: x=%s wd=%s"
                            % (tag, pt(n["x"]), pt(n["wd"])))
        # in the margin of its side
        if n["side"] == "r" and n["x"] + tol < geo["textright"]:
            failures.append("%s overlaps the text block from the right margin (x=%s < textright=%s)"
                            % (tag, pt(n["x"]), pt(geo["textright"])))
        if n["side"] == "l" and n["x"] + n["wd"] > geo["textleft"] + tol:
            failures.append("%s overlaps the text block from the left margin (x+wd=%s > textleft=%s)"
                            % (tag, pt(n["x"] + n["wd"]), pt(geo["textleft"])))
        # side rule
        want = ("l" if n["ax"] < center else "r") if n["twocol"] else "r"
        if n["piece"] == 1 and want != n["side"]:
            failures.append("%s should be on side %s (anchor x=%s, twocol=%d)"
                            % (tag, want, pt(n["ax"]), n["twocol"]))
        # same page as anchor
        if n["apage"] != n["page"]:
            failures.append("%s is on a different page than its anchor (page %d)"
                            % (tag, n["apage"]))
        # inside the text area
        if n["top"] > geo["ceiling"] + tol:
            failures.append("%s is above the text area: top=%s > %s"
                            % (tag, pt(n["top"]), pt(geo["ceiling"])))
        if n["bottom"] < geo["floor"] - tol:
            failures.append("%s is below the text area: bottom=%s < %s"
                            % (tag, pt(n["bottom"]), pt(geo["floor"])))

    # no overlaps per (page, side)
    groups = defaultdict(list)
    for n in notes:
        groups[(n["page"], n["side"])].append(n)
    print("%-6s %-5s %-4s %9s %9s %9s %9s  %s" %
          ("id", "page", "side", "top", "bottom", "anchor_y", "shift", "status"))
    for key in sorted(groups):
        grp = sorted(groups[key], key=lambda n: -n["top"])
        prev = None
        for n in grp:
            status = "ok"
            if prev is not None and prev["bottom"] - n["top"] < gap - tol:
                status = "OVERLAP with %d (distance %s < gap %s)" % (
                    prev["id"], pt(prev["bottom"] - n["top"]), pt(gap))
                failures.append("page %d side %s: note %d %s" % (key[0], key[1], n["id"], status))
            shift = n["y"] - n["ay"]   # actual baseline minus anchor baseline (+ = lifted)
            ident = str(n["id"]) if n["piece"] == 1 else "%d.%d" % (n["id"], n["piece"])
            if n["piece"] == 1:
                print("%-6s %-5d %-4s %9s %9s %9s %9s  %s" %
                      (ident, n["page"], n["side"], pt(n["top"]), pt(n["bottom"]),
                       pt(n["ay"]), pt(shift), status))
            else:
                print("%-6s %-5d %-4s %9s %9s %9s %9s  %s" %
                      (ident, n["page"], n["side"], pt(n["top"]), pt(n["bottom"]),
                       "-", "-", status))
            prev = n

    ncut = len(pieces)
    print("%d notes (%d cut, %d pieces) on %d page/side groups checked; gap=%s; text area y in [%s, %s]"
          % (len(first), ncut, len(notes), len(groups), pt(gap), pt(geo["floor"]), pt(geo["ceiling"])))
    if "--expect-cut" in argv:
        want_cut = int(argv[argv.index("--expect-cut") + 1])
        if ncut < want_cut:
            failures.append("only %d notes are cut, expected at least %d" % (ncut, want_cut))
    if failures:
        print("FAILURES:")
        for f in failures:
            print("  " + f)
        return 1
    print("layout OK: no overlaps, all notes inside the page/text area and in the correct margin")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
