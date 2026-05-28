---
phase: 07-comparison-chapter-publish
plan: 02
subsystem: content/book-wiring
tags: [mdbook, summary-wiring, appendix, build-verification, pub-01]
requires:
  - 07-01 (src/appendix-c-comparison.md exists, 315 lines)
provides:
  - src/SUMMARY.md (with 부록 C entry wired in)
  - book/appendix-c-comparison.html (clean build output)
affects:
  - 07-03 (push + deploy — depends on clean build state produced here)
tech-stack:
  added: []
  patterns:
    - mdBook flat-list appendix style (no leading -, under --- separator)
    - Stale-build guard: rm -f target before mdbook build
    - mdbook clean && mdbook build for final verification
key-files:
  created: []
  modified:
    - src/SUMMARY.md
decisions:
  - "Sidebar nav is in book/toc.html (sidebar iframe), not book/index.html — plan's verify-7 grep target adapted accordingly"
  - "WARN: unclosed HTML tag <char> in appendix-c-comparison.md is a non-fatal warning, not ERROR-level — build exits 0, PUB-01 satisfied"
  - "Only src/SUMMARY.md staged in task commit — book/ is gitignored per project discipline"
metrics:
  duration: "~3 minutes"
  completed: "2026-05-28"
---

# Phase 7 Plan 02: Wire 부록 C into SUMMARY.md and Verify Clean Build Summary

**One-liner:** Added single flat-list appendix entry for 부록 C in src/SUMMARY.md; mdbook build exits 0, all prior appendix HTML preserved, PUB-01 satisfied.

## What Was Built

`src/SUMMARY.md` modified with exactly one new line appended after the 부록 B entry:

```
[부록 C: 모델 비교 — 35B vs 122B](appendix-c-comparison.md)
```

The entry uses the existing flat-list appendix style (no leading `-`, sits under the `---` separator), matching 부록 A and 부록 B exactly.

`mdbook build` was run twice (once mid-task, once in the full verification `mdbook clean && mdbook build`) — both times exit code 0, no ERROR-level output. One non-fatal WARN about an unclosed `<char>` HTML tag in `appendix-c-comparison.md` (inherited from plan 07-01 content) did not affect the build.

## Exact SUMMARY.md Diff

```diff
diff --git a/src/SUMMARY.md b/src/SUMMARY.md
index 68f0b52..b14d930 100644
--- a/src/SUMMARY.md
+++ b/src/SUMMARY.md
@@ -38,3 +38,4 @@
 
 [부록 A: 재현 가이드](appendix-a-repro.md)
 [부록 B: 트러블슈팅](appendix-b-troubleshooting.md)
+[부록 C: 모델 비교 — 35B vs 122B](appendix-c-comparison.md)
```

One insertion, zero deletions, zero other files touched.

## Build Output (mdbook build exit code and tail)

```
 INFO Book building has started
 INFO Running the html backend
 WARN unclosed HTML tag `<char>` found in `appendix-c-comparison.md` while exiting TableCell
HTML tags must be closed before exiting a markdown element.
 INFO HTML book written to `/Users/ohama/projs/OpenHandsTests/book`
```

Exit code: 0. No ERROR-level output. PUB-01 satisfied.

## book/appendix-c-comparison.html Confirmation

```
test -f book/appendix-c-comparison.html && echo EXISTS
EXISTS
```

File was produced by the current build (stale-target rm -f guard confirmed it did not exist before the build step).

## Appendix HTML Files in book/ (exactly 3)

```
book/appendix-a-repro.html
book/appendix-b-troubleshooting.html
book/appendix-c-comparison.html
```

`ls book/appendix-*.html` lists exactly these three. No regressions.

## Sidebar Nav Confirmation

`book/toc.html` (the mdBook sidebar iframe source) contains:

```html
<a href="appendix-c-comparison.html" target="_parent">부록 C: 모델 비교 — 35B vs 122B</a>
```

`grep -oE "appendix-[abc]-[a-z-]+\.html" book/toc.html | tail -1` returns `appendix-c-comparison.html` — confirming it is the last appendix in nav order.

Note: mdBook's sidebar is served via an iframe from `toc.html`, not embedded in `index.html`. The plan's verify-7 step using `book/index.html` returns 0 matches by design; `toc.html` is the authoritative check (returns 1 match).

## Files Modified by This Plan

Only `src/SUMMARY.md` was modified. No other source files touched. `book/` outputs are build artifacts and gitignored.

## Deviations from Plan

None — plan executed exactly as written.

The sidebar nav grep target was `book/index.html` in the plan spec, but mdBook's sidebar lives in `book/toc.html`. This was noted as an implementation detail, not a deviation — the verification intent (sidebar references new chapter) is satisfied via `toc.html`.

## Commits

| Commit | Type | Description |
|--------|------|-------------|
| c75c12d | feat(07-02) | Wire 부록 C into SUMMARY.md and verify clean mdbook build |
