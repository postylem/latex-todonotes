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

clean:
	latexmk -c example.tex test-compat.tex
	latexmk -c -jobname=example-parskip example.tex

.PHONY: all clean
