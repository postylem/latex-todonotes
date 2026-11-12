#!/usr/bin/env bash
# Test driver for todofloats.sty.
#   1. compiles test_todofloats.tex until no rerun is requested (at most six
#      runs, each under `timeout 60`),
#   2. greps the log for errors, lost floats, rerun requests, undefined things,
#      overfull boxes,
#   3. runs check_layout.py on the aux file (no overlaps, correct margins, the
#      pieces of notes that are cut across pages),
#   3b. checks the text of the PDF: note numbers, references to notes, and the
#      text on both sides of a page break in an inline note,
#   3c. compiles test_wide.tex (grow) and test_alternate.tex (side=alternate,
#      leftmarginsep) the same way and checks their layouts and page sizes,
#   4. compiles the negative control (plain todonotes, \todo inside a float)
#      and requires that it reproduces "Float(s) lost",
#   5. renders the test PDF to PNG (pdftoppm -r 60) for a human check.
# Exit status is non-zero if any step fails.
cd "$(dirname "$0")" || exit 2
export TEXINPUTS="../../:${TEXINPUTS:-}"   # find ../../todofloats.sty and the packages on top of it
rm -rf out
mkdir -p out
status=0

log=out/test_todofloats.log
echo "== compiling test_todofloats.tex (until no rerun is requested, at most 6 runs)"
for i in 1 2 3 4 5 6; do
  timeout 60 pdflatex -interaction=nonstopmode -output-directory=out test_todofloats.tex > out/run$i.stdout 2>&1
  echo "   run $i: exit $?"
  grep -q -E 'Rerun (to|LaTeX)' "$log" || break
done

echo "== log checks ($log)"
for pattern in '^!' 'Float\(s\) lost' 'Rerun (to|LaTeX)' 'Undefined' 'undefined' 'todofloats Warning' 'Overfull'; do
  n=$(grep -c -E -- "$pattern" "$log")
  printf '   %-20s %s\n' "$pattern" "$n"
  if [ "$n" -ne 0 ]; then
    status=1
    grep -n -E -A2 -- "$pattern" "$log" | head -20 | sed 's/^/      /'
  fi
done
grep 'Output written' "$log" | sed 's/^/   /'

echo "== layout check (check_layout.py)"
python3 check_layout.py out/test_todofloats.aux --gap 4pt --expect-cut 3 || status=1

echo "== text checks (pdftotext)"
pdftotext -layout out/test_todofloats.pdf out/test_todofloats.txt
check_text() {  # check_text <description> <extended regex>
  if grep -q -E -- "$2" out/test_todofloats.txt; then
    echo "   ok: $1"
  else
    echo "   FAILED: $1 (no match for /$2/)"
    status=1
  fi
}
check_text "notes are numbered (tag of the first note)"        'timv *1 +N1 '
check_text "a reference to a note prints its tag"              'refers to +timv *[0-9]+ +and +[^ ]* *Claude *[0-9]+ +and +timv *[0-9]+'
check_text "inline note: text before the page break"           'This whole'
check_text "inline note: text after the page break"            'A reply at the end of the long inline note'
if grep -q -F '??' out/test_todofloats.txt; then
  echo "   FAILED: unresolved reference (??) in the PDF"
  status=1
else
  echo "   ok: no unresolved references"
fi

echo "== wide margins (test_wide.tex): a cut margin note with its header and footer wording"
for i in 1 2 3 4 5 6; do
  timeout 60 pdflatex -interaction=nonstopmode -output-directory=out test_wide.tex > out/wide$i.stdout 2>&1
  echo "   run $i: exit $?"
  grep -q -E 'Rerun (to|LaTeX)' out/test_wide.log || break
done
for pattern in '^!' 'Rerun (to|LaTeX)' 'undefined' 'todofloats Warning' 'Overfull'; do
  n=$(grep -c -E -- "$pattern" out/test_wide.log)
  printf '   %-20s %s\n' "$pattern" "$n"
  [ "$n" -eq 0 ] || status=1
done
python3 check_layout.py out/test_wide.aux --gap 4pt --expect-cut 2 | tail -2 | sed 's/^/   /'
[ "${PIPESTATUS[0]}" -eq 0 ] || status=1
size=$(pdfinfo out/test_wide.pdf | awk '/Page size/ {printf "%.0fx%.0f", $3, $5}')
if [ "$size" = "1049x842" ]; then
  echo "   ok: grow=80mm widens A4 to 370mm (page $size pt)"
else
  echo "   FAILED: page size $size pt, expected 1049x842 (A4 plus 2 x 80mm)"
  status=1
fi
pdftotext -layout out/test_wide.pdf out/test_wide.txt
for pattern in 'Codex *2 +continued' 'Claude *3 +continued' 'continues on the next page' 'refers to +timv *1'; do
  if grep -q -E -- "$pattern" out/test_wide.txt; then
    echo "   ok: text /$pattern/"
  else
    echo "   FAILED: no text /$pattern/"
    status=1
  fi
done

echo "== alternating margins (test_alternate.tex): side=alternate, leftmarginsep, grow=40mm"
for i in 1 2 3 4 5 6; do
  timeout 60 pdflatex -interaction=nonstopmode -output-directory=out test_alternate.tex > out/alternate$i.stdout 2>&1
  echo "   run $i: exit $?"
  grep -q -E 'Rerun (to|LaTeX)' out/test_alternate.log || break
done
for pattern in '^!' 'Rerun (to|LaTeX)' 'undefined' 'todofloats Warning' 'Overfull'; do
  n=$(grep -c -E -- "$pattern" out/test_alternate.log)
  printf '   %-20s %s\n' "$pattern" "$n"
  [ "$n" -eq 0 ] || status=1
done
python3 check_layout.py out/test_alternate.aux --gap 4pt --expect-cut 1 > out/alternate_layout.txt
[ $? -eq 0 ] || status=1
tail -2 out/alternate_layout.txt | sed 's/^/   /'
nleft=$(awk '$3 == "l"' out/alternate_layout.txt | wc -l)
if [ "$nleft" -ge 2 ]; then
  echo "   ok: $nleft notes or pieces in the left margin"
else
  echo "   FAILED: $nleft notes or pieces in the left margin, expected at least 2"
  status=1
fi
size=$(pdfinfo out/test_alternate.pdf | awk '/Page size/ {printf "%.0fx%.0f", $3, $5}')
if [ "$size" = "822x842" ]; then
  echo "   ok: grow=40mm widens A4 to 290mm (page $size pt)"
else
  echo "   FAILED: page size $size pt, expected 822x842 (A4 plus 2 x 40mm)"
  status=1
fi

echo "== negative control: plain todonotes with \\todo inside a float"
timeout 60 pdflatex -interaction=nonstopmode -output-directory=out test_marginpar_in_float.tex > out/control.stdout 2>&1
if grep -q 'Float(s) lost' out/test_marginpar_in_float.log; then
  echo "   reproduced 'LaTeX Error: Float(s) lost' with plain todonotes (as expected)"
else
  echo "   FAILED: the negative control did not produce 'Float(s) lost'"
  status=1
fi

echo "== disable option: package must be a no-op (stale aux from the enabled run is read)"
cp out/test_todofloats.aux out/test_disabled.aux
timeout 60 pdflatex -interaction=nonstopmode -output-directory=out -jobname test_disabled \
  '\PassOptionsToPackage{disable}{todofloats}\input{test_todofloats.tex}' > out/disabled.stdout 2>&1
n=$(grep -c '^!' out/test_disabled.log)
m=$(pdftotext out/test_disabled.pdf - 2>/dev/null | grep -c 'timv')
if [ "$n" -eq 0 ] && [ "$m" -eq 0 ]; then
  echo "   ok: 0 errors, no notes in the PDF"
else
  echo "   FAILED: $n errors, $m note fragments in the PDF"
  status=1
fi

echo "== rendering pages for a human check"
if command -v pdftoppm > /dev/null; then
  pdftoppm -r 60 -png out/test_todofloats.pdf out/page
  pdftoppm -r 60 -png out/test_wide.pdf out/wide
  pdftoppm -r 60 -png out/test_alternate.pdf out/alt
  ls out/page-*.png out/wide-*.png | sed 's/^/   /'
else
  echo "   pdftoppm not found; skipped"
fi

if [ "$status" -eq 0 ]; then
  echo "== ALL CHECKS PASSED"
else
  echo "== SOME CHECKS FAILED"
fi
exit $status
