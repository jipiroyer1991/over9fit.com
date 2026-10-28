#!/usr/bin/env bash
# Publie le site sur Netlify (projet over9fit, domaine over9fit.com).
#
#     _src/publier.sh
#
# Ne publie que les pages et les images : ni `_src`, ni `.git`, ni les fichiers de GitHub Pages
# (`CNAME`, `.nojekyll`). Refuse un arbre de travail modifié, pour que ce qui est en ligne soit
# toujours un commit. Chaque publication coûte 15 des 300 crédits mensuels du forfait gratuit :
# grouper les changements.
#
# La première fois sur un ordinateur : `npx netlify-cli login`.
set -euo pipefail

PROJET=1ad142ff-8572-4d00-bbee-0493871e953b
RACINE="$(cd "$(dirname "$0")/.." && pwd)"
COPIE="${XDG_CACHE_HOME:-$HOME/.cache}/over9fit-publication"

if [ -n "$(git -C "$RACINE" status --porcelain)" ]; then
  echo "✗ arbre de travail modifié : commiter avant de publier" >&2
  exit 1
fi
COMMIT="$(git -C "$RACINE" rev-parse --short HEAD)"

mkdir -p "$COPIE"
rsync -a --delete --exclude .git --exclude _src --exclude CNAME --exclude .nojekyll \
  "$RACINE/" "$COPIE/"

npx --yes netlify-cli deploy --site "$PROJET" --dir "$COPIE" --prod --no-build \
  --message "over9fit.com@$COMMIT"
