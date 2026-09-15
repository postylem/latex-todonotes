# Build the example gallery and the compatibility guard.
#
#   make          rebuild everything
#   make clean    drop build artifacts (keeps the committed PDFs)
#
# TEXINPUTS is set in latexmkrc, so a bare `latexmk -pdf example.tex` in this
# directory works too, and picks up the repo's .sty files rather than any
# installed copy.

PACKAGES := ../mytodonotes.sty ../agentnotes.sty ../claudenotes.sty

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

clean:
	latexmk -c example.tex test-compat.tex
	latexmk -c -jobname=example-parskip example.tex

.PHONY: all clean compat-check compat-build compat-render compat-bless
