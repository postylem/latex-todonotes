#!/usr/bin/env bash
# Copy the note packages into a paper.
#   setup.sh [<paper directory>]     copy what is missing or older; never overwrite
#                                    a file that differs without --force
#   setup.sh --check [<directory>]   only report how the paper's copies compare
# After copying it prints the preamble block to paste (templates/preamble.tex)
# and puts templates/AGENTS.md into the paper if it has no AGENTS.md.
here="$(cd "$(dirname "$0")/.." && pwd)"
force=0; check=0; dir=.
for a in "$@"; do
  case "$a" in
    --force) force=1 ;;
    --check) check=1 ;;
    *) dir="$a" ;;
  esac
done
[ -d "$dir" ] || { echo "setup.sh: no such directory: $dir" >&2; exit 2; }
status=0
for f in todofloats.sty mytodonotes.sty agentnotes.sty; do
  if [ ! -e "$dir/$f" ]; then
    if [ "$check" = 1 ]; then echo "missing    $f"; status=1
    else cp "$here/$f" "$dir/$f" && echo "copied     $f"; fi
  elif cmp -s "$here/$f" "$dir/$f"; then
    echo "up to date $f"
  elif [ "$check" = 1 ]; then
    echo "differs    $f"; status=1
  elif [ "$force" = 1 ]; then
    cp "$here/$f" "$dir/$f" && echo "replaced   $f"
  else
    echo "differs    $f  (kept; --force replaces it with the skill's copy)"; status=1
  fi
done
[ "$check" = 1 ] && exit $status
if [ ! -e "$dir/AGENTS.md" ]; then
  cp "$here/templates/AGENTS.md" "$dir/AGENTS.md" && echo "copied     AGENTS.md (adapt the names in it)"
fi
echo
echo "Preamble block (after xcolor/tikz, before cleveref):"
sed 's/^/  /' "$here/templates/preamble.tex"
exit $status
