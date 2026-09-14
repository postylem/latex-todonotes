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

# Verify the compatibility guarantee: build test-compat.tex against the packages
# as they were before agentnotes.sty existed, and check that it renders the same.
# The reference point is the parent of the commit that ADDED agentnotes.sty, so
# this keeps working once the branch is merged and main moves on.
compat-check: test-compat.pdf
	@set -e; \
	pre=$$(git log --format=%H --diff-filter=A -- ../agentnotes.sty | tail -1)^; \
	tmp=$$(mktemp -d); \
	git show $$pre:claudenotes.sty > $$tmp/claudenotes.sty; \
	git show $$pre:mytodonotes.sty > $$tmp/mytodonotes.sty; \
	cp test-compat.tex $$tmp/; \
	(cd $$tmp && latexmk -pdf -interaction=nonstopmode test-compat.tex >/dev/null 2>&1); \
	pdftoppm -r 150 -png $$tmp/test-compat.pdf $$tmp/pre; \
	pdftoppm -r 150 -png test-compat.pdf $$tmp/post; \
	if cmp -s $$tmp/pre-1.png $$tmp/post-1.png; then \
	  echo "compat OK: renders the same as before agentnotes.sty existed"; \
	else \
	  echo "COMPAT REGRESSION: render differs; artifacts in $$tmp"; exit 1; \
	fi

clean:
	latexmk -c example.tex test-compat.tex
	latexmk -c -jobname=example-parskip example.tex

.PHONY: all clean compat-check
