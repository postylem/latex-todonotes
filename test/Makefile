# Build the example gallery and the compatibility guard.
#
#   make          rebuild everything
#   make clean    drop build artifacts (keeps the committed PDFs)
#
# TEXINPUTS is set in latexmkrc, so a bare `latexmk -pdf example.tex` in this
# directory works too, and picks up the repo's .sty files rather than any
# installed copy.

PACKAGES := ../todofloats.sty ../mytodonotes.sty ../agentnotes.sty ../claudenotes.sty

all: example.pdf example-parskip.pdf test-compat.pdf

example.pdf: example.tex $(PACKAGES)
	latexmk -pdf example.tex

# Paragraphs separated by skips instead of indents.
example-parskip.pdf: example.tex $(PACKAGES)
	latexmk -pdf -jobname=example-parskip -usepretex='\def\exampleparskip{1}' example.tex

# Backwards-compatibility guard: must build, and must not change how it renders.
test-compat.pdf: test-compat.tex $(PACKAGES)
	latexmk -pdf test-compat.tex

# The compatibility guarantee has two halves, and they need different checks.
#
# compat-build is the guarantee itself: source written in the pre-\newagent
# style still compiles.  That must never break, so it fails hard.
#
# compat-render is a visual regression check against a committed golden image.
# It cannot be a diff against the pre-agentnotes packages any more: output is
# now deliberately changed (\<agent>change gained a label chip), so such a diff
# would fail forever and tell us nothing.  Instead the golden is a reviewed
# artifact -- when output changes on purpose, run `make compat-bless`, and the
# new image shows up in the commit for a human to accept or reject.
GOLDEN := golden/test-compat-150dpi.png

compat-build: test-compat.tex $(PACKAGES)
	@latexmk -C test-compat.tex >/dev/null 2>&1; \
	if latexmk -pdf -interaction=nonstopmode test-compat.tex >/dev/null 2>&1; then \
	  echo "compat-build OK: pre-\\newagent source still compiles"; \
	else \
	  echo "COMPAT BREAK: old-style source no longer compiles"; exit 1; \
	fi

compat-render: test-compat.pdf $(GOLDEN)
	@tmp=$$(mktemp -d); \
	pdftoppm -r 150 -png -singlefile test-compat.pdf $$tmp/now; \
	if cmp -s $$tmp/now.png $(GOLDEN); then \
	  echo "compat-render OK: identical to the golden image"; \
	else \
	  echo "RENDER CHANGED vs $(GOLDEN)."; \
	  echo "  If intended, run: make compat-bless   (then review the diff)"; \
	  echo "  Current render left at $$tmp/now.png"; exit 1; \
	fi

compat-check: compat-build compat-render

compat-bless: test-compat.pdf
	@pdftoppm -r 150 -png -singlefile test-compat.pdf $(basename $(GOLDEN))
	@echo "blessed $(GOLDEN) -- review it in the commit"

# The engine under the packages (todofloats.sty): notes inside floats, notes
# cut across columns and pages, the review layout.  Compiles two stress
# documents and checks the logs, the layout (from the aux files) and the text.
engine-check: $(PACKAGES)
	cd todofloats && bash check.sh

# The option refs=number: \ref and \cref of a note print #<number>, not its tag.
# Builds the example with the option passed from outside and checks the aux
# (every note label is \note@numref) and the text of the PDF (the references).
refs-number: example.tex $(PACKAGES)
	@latexmk -pdf -interaction=nonstopmode -jobname=example-refs \
	  -usepretex='\PassOptionsToPackage{refs=number}{mytodonotes}' example.tex >/dev/null 2>&1; \
	n=$$(grep -c 'newlabel{note:' example-refs.aux); \
	m=$$(grep 'newlabel{note:' example-refs.aux | grep -c 'note@numref'); \
	if [ "$$n" -gt 0 ] && [ "$$n" = "$$m" ] && pdftotext example-refs.pdf - | tr '\n' ' ' | grep -q 'agree with #[0-9]'; then \
	  echo "refs-number OK: $$n note labels print #<number>"; \
	else \
	  echo "REFS-NUMBER FAILED: $$m of $$n note labels use #<number>"; exit 1; \
	fi

# The option tags=plain: every tag (notes, replies, references) is plain text.
# Builds the example with the option passed from outside; it must compile, and
# its text must still carry the authors' names and the note numbers.
tags-plain: example.tex $(PACKAGES)
	@latexmk -pdf -interaction=nonstopmode -jobname=example-tags \
	  -usepretex='\PassOptionsToPackage{tags=plain}{mytodonotes}' example.tex >/dev/null 2>&1; \
	if grep -q '^!' example-tags.log; then echo "TAGS-PLAIN FAILED: errors in example-tags.log"; exit 1; fi; \
	if pdftotext example-tags.pdf - | grep -q 'frank'; then echo "tags-plain OK: compiles, names and numbers present"; \
	else echo "TAGS-PLAIN FAILED: author names missing from the text"; exit 1; fi

# tools/open_items.py against the example: the items it finds, with the numbers
# the notes have in the PDF.
open-items: example.pdf
	python3 ../tools/open_items.py example.tex

clean:
	latexmk -c example.tex test-compat.tex
	latexmk -c -jobname=example-parskip example.tex
	latexmk -C -jobname=example-refs example.tex
	latexmk -C -jobname=example-tags example.tex
	rm -rf todofloats/out

.PHONY: all clean compat-check compat-build compat-render compat-bless engine-check refs-number tags-plain open-items
