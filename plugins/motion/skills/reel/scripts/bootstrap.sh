#!/usr/bin/env bash
# Prepares the workspace (~/Motion) the reel skill renders in. Idempotent: it does real
# work only when the plugin version differs from the workspace's stamp, so it runs on every
# call and costs nothing once ready. Prints READY <path> on success.
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MOTION_HOME="${MOTION_HOME:-$HOME/Motion}"
STAMP="$MOTION_HOME/.studio-version"

if ! command -v node >/dev/null 2>&1 || [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 18 ]; then
  echo "NODE_MISSING: install Node LTS from https://nodejs.org (the macOS installer), reopen Claude Code and ask again."
  exit 1
fi

VERSION="$(node -p "require('$SKILL_DIR/../../.claude-plugin/plugin.json').version")"
if [ -f "$STAMP" ] && [ "$(cat "$STAMP")" = "$VERSION" ]; then
  echo "READY $MOTION_HOME"
  exit 0
fi
FIRST_RUN=$([ -f "$STAMP" ] && echo no || echo yes)

echo "→ Preparing the studio at $MOTION_HOME (first time takes a few minutes)"
mkdir -p "$MOTION_HOME"
# ponytail: merges into the workspace; the engine and the bundled reference scenes are refreshed, the person's own scenes and out/ stay.
cp -R "$SKILL_DIR/studio/." "$MOTION_HOME/"
cd "$MOTION_HOME"
npm install --no-fund --no-audit --loglevel=error
npx --yes playwright install chromium

if [ "$FIRST_RUN" = yes ]; then
  echo "→ Smoke test"
  npm test >/dev/null
  npm run render -- scenes/demo --fps 2 >/dev/null # demo paints a fixed 1920x1080 canvas: a smaller size renders black
  [ -s out/demo.mp4 ]
fi

# Written last: a run that failed halfway retries on the next call.
echo "$VERSION" > "$STAMP"
echo "READY $MOTION_HOME"
