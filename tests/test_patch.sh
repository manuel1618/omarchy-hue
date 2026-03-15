#!/bin/bash
# Test patch_set_theme and unpatch_set_theme from actual scripts

set -e

THEME_SET_ORIGINAL='#!/bin/bash
omarchy-hook theme-set
echo "Theme set to: $1"'

THEME_SET_PATCHED='#!/bin/bash
# Omarchy-Hue Integration - Sync lights with theme (runs in parallel)
if command -v omarchy-hue-sync &>/dev/null; then
  (omarchy-hue-sync 2>&1 | logger -t omarchy-hue) &
fi

omarchy-hook theme-set
echo "Theme set to: $1"'

THEME_SET_UNPATCHED='#!/bin/bash

omarchy-hook theme-set
echo "Theme set to: $1"'

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

source lib/patch-theme.sh

echo "=== Testing patch/unpatch logic ==="
echo

echo "Test 1: Patch original -> should produce patched version"
echo "$THEME_SET_ORIGINAL" > "$TMPDIR/test1"
THEME_SET_SCRIPT="$TMPDIR/test1" patch_set_theme 2>/dev/null
patched=$(cat "$TMPDIR/test1")
if [[ "$patched" == "$THEME_SET_PATCHED" ]]; then
    echo "✓ Patch test PASSED"
else
    echo "✗ Patch test FAILED"
    echo "Expected:"
    echo "$THEME_SET_PATCHED"
    echo "Got:"
    echo "$patched"
    exit 1
fi
echo

echo "Test 2: Patch already patched -> should skip"
output=$(THEME_SET_SCRIPT="$TMPDIR/test1" patch_set_theme 2>&1)
if echo "$output" | grep -q "already patched"; then
    echo "✓ Double-patch test PASSED"
else
    echo "✗ Double-patch test FAILED"
    exit 1
fi
echo

echo "Test 3: Unpatch patched -> should restore original (with blank line)"
THEME_SET_SCRIPT="$TMPDIR/test1" unpatch_set_theme 2>/dev/null
unpatched=$(cat "$TMPDIR/test1")
if [[ "$unpatched" == "$THEME_SET_UNPATCHED" ]]; then
    echo "✓ Unpatch test PASSED"
else
    echo "✗ Unpatch test FAILED"
    echo "Expected:"
    echo "$THEME_SET_UNPATCHED"
    echo "Got:"
    echo "$unpatched"
    exit 1
fi
echo

echo "Test 4: Unpatch original (no patch) -> should be unchanged"
echo "$THEME_SET_ORIGINAL" > "$TMPDIR/test4"
THEME_SET_SCRIPT="$TMPDIR/test4" unpatch_set_theme 2>/dev/null
no_change=$(cat "$TMPDIR/test4")
if [[ "$no_change" == "$THEME_SET_ORIGINAL" ]]; then
    echo "✓ Unpatch-no-patch test PASSED"
else
    echo "✗ Unpatch-no-patch test FAILED"
    exit 1
fi
echo

echo "=== All tests PASSED ==="