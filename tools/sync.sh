#!/usr/bin/env bash
# Bring the note packages of every registered paper up to date with this skill.
#   sync.sh --add <main.tex>...   register papers, by the main .tex file of each
#   sync.sh --list                print the registry
#   sync.sh --check               report which papers are behind (exit 1 if any)
#   sync.sh [<main.tex>...]       update the papers that are behind: all registered
#                                 ones, or only those named
#
# The registry is one main .tex path per line ('#' starts a comment), in
# $LATEX_TODONOTES_PAPERS, by default ~/.config/latex-todonotes/papers. It lives
# outside this repository because it lists papers on your machine. setup.sh
# registers a paper's main.tex when it copies the packages in.
#
# A paper is behind when a package it has (todofloats.sty, mytodonotes.sty,
# agentnotes.sty) differs from this skill's copy on the paper's upstream branch,
# or when it has mytodonotes.sty but not todofloats.sty, which mytodonotes loads.
# Updating a paper:
#   1. adds a new git worktree of the paper's upstream branch (e.g. origin/main),
#      so uncommitted edits in the paper's own checkout are never touched;
#   2. builds the paper there with latexmk, as it is;
#   3. replaces those packages with this skill's files, checked byte for byte;
#   4. builds again;
#   5. commits only those files, naming this skill's commit, and pushes. If the
#      paper moved meanwhile, it rebases once, builds again, and pushes again;
#   6. checks that the commit is on the upstream branch and removes the worktree.
# It stops, with the reason, at the first failure: a build that fails, more
# errors or undefined references after the update than before, a rebase
# conflict, or a second rejected push. Nothing is pushed for that paper, and its
# worktree is kept for inspection. Papers updated before it stay updated.
# The paper's own checkout is not moved; pull it when convenient.
#
# This skill's package files must be committed, and the commit must be on a
# remote branch, so that the commit a paper's history names exists for others.
# $SYNC_TRAILER, if set, is appended to each commit message (e.g. Co-Authored-By
# lines).
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
reg="${LATEX_TODONOTES_PAPERS:-${XDG_CONFIG_HOME:-$HOME/.config}/latex-todonotes/papers}"
pkgs=(todofloats.sty mytodonotes.sty agentnotes.sty)

die() { echo "sync.sh: $*" >&2; exit 1; }
papers() { [ -f "$reg" ] || die "no registry at $reg; add papers with --add <main.tex>"; grep -v '^[[:space:]]*\(#\|$\)' "$reg" || true; }
version() { grep -m1 -o 'v[0-9][0-9.]*' "$1" 2>/dev/null || echo new; }

# resolve <main.tex>: set dir, main, top, rel (path of dir inside the repo, with
# a trailing slash, or empty), up (e.g. origin/main), remote, branch.
resolve() {
  [ -f "$1" ] || die "$1: no such file"
  dir=$(cd "$(dirname "$1")" && pwd); main=$(basename "$1")
  top=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) || die "$1: not in a git repository"
  rel=$(git -C "$dir" rev-parse --show-prefix)
  up=$(git -C "$dir" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null) \
    || die "$1: the checked-out branch has no upstream branch"
  remote=${up%%/*}; branch=${up#*/}
}

# behind <ref>: the packages that differ at <ref> in the current paper
behind() {
  local f
  for f in "${pkgs[@]}"; do
    if git -C "$top" cat-file -e "$1:$rel$f" 2>/dev/null; then
      git -C "$top" show "$1:$rel$f" | cmp -s - "$here/$f" || echo "$f"
    elif [ "$f" = todofloats.sty ] && git -C "$top" cat-file -e "$1:${rel}mytodonotes.sty" 2>/dev/null; then
      echo "$f"
    fi
  done
}

# build <dir>: latexmk on $main in <dir>, forcing a full run (-g); prints
# "errors undefined pages". The log and PDF are found wherever the paper's
# latexmkrc puts them ($out_dir, $aux_dir): the ones written by this run.
build() {
  local opt=-pdf stamp log pdf e u p
  grep -qs pdf_mode "$1/.latexmkrc" "$1/latexmkrc" && opt=
  stamp=$(mktemp)
  ( cd "$1" && timeout 1200 latexmk -g $opt -interaction=nonstopmode -halt-on-error "$main" >/dev/null 2>&1 ) \
    || { rm -f "$stamp"; return 1; }
  log=$(find "$1" -name "${main%.tex}.log" -newer "$stamp" -print -quit)
  pdf=$(find "$1" -name "${main%.tex}.pdf" -newer "$stamp" -print -quit)
  rm -f "$stamp"
  [ -n "$log" ] || { echo "sync.sh: latexmk wrote no ${main%.tex}.log under $1" >&2; return 1; }
  e=$(grep -c '^!' "$log" || true); u=$(grep -c 'undefined' "$log" || true)
  p=$(pdfinfo "$pdf" 2>/dev/null | awk '/^Pages:/{print $2}')
  echo "$e $u ${p:-?}"
}

skill_commit() {
  [ -z "$(git -C "$here" status --porcelain -- "${pkgs[@]}")" ] \
    || die "the skill's package files have uncommitted changes; commit them first"
  [ -n "$(git -C "$here" branch -r --contains HEAD 2>/dev/null)" ] \
    || die "the skill's commit $(git -C "$here" rev-parse --short HEAD) is on no remote branch; push it first"
  sha=$(git -C "$here" rev-parse --short HEAD)
}

update() {
  local need wt w f before after be bu bp ae au ap changes="" msg head
  resolve "$1"
  git -C "$top" fetch -q "$remote"
  need=$(behind "$up")
  [ -n "$need" ] || { echo "up to date  $1"; return 0; }
  wt=$(mktemp -d "${TMPDIR:-/tmp}/latex-todonotes-sync-XXXXXX")
  git -C "$top" worktree add -q --detach "$wt/w" "$up"
  w="$wt/w/$rel"; w=${w%/}
  keep="the worktree is kept at $wt/w (remove it with: git -C $top worktree remove --force $wt/w)"
  echo "updating    $1:" $need
  before=$(build "$w") || die "$1: the paper does not build before the update (its log is under $w); nothing changed; $keep"
  for f in $need; do
    changes="$changes  $f $(version "$w/$f") -> $(version "$here/$f")"$'\n'
    cp "$here/$f" "$w/$f"; cmp -s "$here/$f" "$w/$f" || die "$1: the copy of $f differs from the skill's"
  done
  after=$(build "$w") || die "$1: the build fails with the new packages (its log is under $w); nothing committed; $keep"
  read -r be bu bp <<<"$before"; read -r ae au ap <<<"$after"
  [ "$ae" -le "$be" ] && [ "$au" -le "$bu" ] \
    || die "$1: more errors or undefined references after the update (before: $be errors, $bu undefined; after: $ae, $au); nothing committed; $keep"
  msg="Update the note packages to latex-todonotes $sha"$'\n\n'"$changes"$'\n'
  msg+="Copied unchanged from the latex-todonotes skill, commit $sha, by tools/sync.sh."$'\n'
  msg+="Build before and after: $be/$ae errors, $bu/$au lines with 'undefined', $bp/$ap pages."
  [ -n "${SYNC_TRAILER:-}" ] && msg+=$'\n\n'"$SYNC_TRAILER"
  ( cd "$wt/w" && git add -- $(for f in $need; do echo "$rel$f"; done) && git commit -q -m "$msg" )
  if ! git -C "$wt/w" push -q "$remote" "HEAD:$branch" 2>/dev/null; then
    echo "            push rejected; rebasing on $up and building again"
    git -C "$wt/w" fetch -q "$remote"
    git -C "$wt/w" rebase -q "$up" || { git -C "$wt/w" rebase --abort; die "$1: rebase conflict; nothing pushed; $keep"; }
    build "$w" >/dev/null || die "$1: the build fails after the rebase; nothing pushed; $keep"
    git -C "$wt/w" push -q "$remote" "HEAD:$branch" || die "$1: push rejected twice; nothing pushed; $keep"
  fi
  head=$(git -C "$wt/w" rev-parse HEAD)
  git -C "$top" fetch -q "$remote"
  git -C "$top" merge-base --is-ancestor "$head" "$up" || die "$1: commit ${head:0:7} is not on $up after the push; $keep"
  git -C "$top" worktree remove --force "$wt/w"; rmdir "$wt"
  echo "pushed      $1: ${head:0:7} on $up ($bp -> $ap pages)"
}

case "${1:-}" in
  --add)
    shift; [ $# -gt 0 ] || die "--add needs the main .tex file of a paper"
    mkdir -p "$(dirname "$reg")"; touch "$reg"
    for p in "$@"; do
      [ -f "$p" ] || die "$p: no such file"
      p="$(cd "$(dirname "$p")" && pwd)/$(basename "$p")"
      if grep -qxF "$p" "$reg"; then echo "registered  $p (already)"; else echo "$p" >>"$reg"; echo "registered  $p"; fi
    done ;;
  --list) papers ;;
  --check)
    status=0
    while read -r p; do
      resolve "$p"; git -C "$top" fetch -q "$remote"
      need=$(behind "$up")
      if [ -z "$need" ]; then echo "up to date  $p"
      else status=1; echo "behind      $p:" $(for f in $need; do printf '%s ' "$f"; done); fi
    done < <(papers)
    exit $status ;;
  -*) die "unknown option $1" ;;
  *)
    skill_commit
    if [ $# -gt 0 ]; then list=("$@"); else mapfile -t list < <(papers); fi
    for p in "${list[@]}"; do update "$p"; done ;;
esac
