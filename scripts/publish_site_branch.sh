#!/usr/bin/env bash
# Publish a prebuilt static site directory to the GitHub Pages source branch.
#
# The source tree remains on normal development branches; this script creates a
# clean one-commit artifact branch containing only the files Pages should serve.
# It is intentionally usable from both the fast code-only deploy and the weekly
# data-refresh deploy so they cannot drift.

set -euo pipefail

src="${1:-_site}"
deploy_branch="${DEPLOY_BRANCH:-web-deployment}"

if [[ ! -d "$src" ]]; then
  echo "publish_site_branch: source directory not found: $src" >&2
  exit 2
fi

: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"
: "${GITHUB_TOKEN:?GITHUB_TOKEN is required}"

tmp="$(mktemp -d)"
cleanup() { rm -rf "$tmp"; }
trap cleanup EXIT

cp -a "$src"/. "$tmp"/
touch "$tmp/.nojekyll"

git init "$tmp"
cd "$tmp"
git checkout -b "$deploy_branch"
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
git commit -m "Deploy site (${GITHUB_SHA:-manual})"
git -c http.extraheader="AUTHORIZATION: bearer ${GITHUB_TOKEN}" \
  push --force "https://github.com/${GITHUB_REPOSITORY}.git" "$deploy_branch"
