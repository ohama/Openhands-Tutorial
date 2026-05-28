---
phase: 05-troubleshooting-reproducibility-publish
plan: "04"
subsystem: infra
tags: [github-actions, github-pages, mdbook, deploy, workflow]

requires:
  - phase: 05-03
    provides: final mdbook build green; all 5부/부록 SUMMARY.md entries wired

provides:
  - .github/workflows/deploy.yml — build+deploy GitHub Actions workflow for mdbook→GitHub Pages
  - book.toml repo fields (git-repository-url, edit-url-template) for edit-on-GitHub links
  - PUBLISHED: pushed to ohama/Openhands-Tutorial; Pages enabled (source=Actions); deploy workflow succeeded; live site verified 200

affects: ["SC#4 satisfied — live site at https://ohama.github.io/Openhands-Tutorial/"]

tech-stack:
  added: [GitHub Actions, actions/checkout@v4, actions/configure-pages@v4, actions/upload-pages-artifact@v3, actions/deploy-pages@v4]
  patterns: ["OIDC-based GitHub Pages deploy (pages:write + id-token:write, no secrets needed)"]

key-files:
  created:
    - .github/workflows/deploy.yml
  modified:
    - book.toml

key-decisions:
  - "Used corrected repo name ohama/Openhands-Tutorial (not OpenHandsTests) for all URLs — matches existing remote origin and live Pages URL"
  - "Workflow fetches latest mdbook release dynamically — no hardcoded version in CI YAML"
  - "Publish step (git push + gh api pages enable) held at checkpoint awaiting user authorization — creating/pushing a public repo is irreversible"

patterns-established:
  - "OIDC GitHub Pages pattern: permissions pages:write + id-token:write; build job uploads artifact, deploy job uses github-pages environment"

duration: ~5min (autonomous task 1 only)
completed: 2026-05-28
---

# Phase 5 Plan 04: GitHub Pages Deploy Workflow Summary

**GitHub Actions deploy workflow (build+deploy jobs, OIDC Pages auth) created and committed; book.toml repo fields added; publish step paused at user-authorization checkpoint**

## Status: COMPLETE — Published & live

Task 1 (autonomous) COMPLETE and committed. Task 2 (publish checkpoint) — user authorized "Publish everything"; orchestrator pushed `main`, enabled Pages (source=GitHub Actions), the deploy workflow run succeeded, and the live site was verified.

## Performance

- **Duration:** ~5 min (Task 1 only)
- **Started:** 2026-05-28
- **Completed (partial):** 2026-05-28
- **Tasks complete:** 1/2 (Task 2 at checkpoint)
- **Files modified:** 2

## Accomplishments

- Created `.github/workflows/deploy.yml` with build+deploy jobs, `pages:write` + `id-token:write` OIDC permissions, and pinned action versions (`checkout@v4`, `configure-pages@v4`, `upload-pages-artifact@v3`, `deploy-pages@v4`)
- Added `git-repository-url` and `edit-url-template` to `book.toml` `[output.html]` using the corrected repo `ohama/Openhands-Tutorial`
- Confirmed local `mdbook build` exits 0 after book.toml edits; YAML validated

## Task Commits

1. **Task 1: Create GitHub Actions deploy workflow + book.toml repo fields** - `0bdbe63` (feat)

**Plan metadata:** pending (will be committed with this SUMMARY)

## Files Created/Modified

- `.github/workflows/deploy.yml` — mdbook→GitHub Pages deploy workflow (build + deploy jobs, OIDC)
- `book.toml` — added `git-repository-url` + `edit-url-template` under `[output.html]`

## Decisions Made

- Used `ohama/Openhands-Tutorial` as repo name in all URLs (corrected from plan's `OpenHandsTests` — the repo already exists at this name per STATE.md and CORRECTED_REPO_FACTS)
- `site-url = "/Openhands-Tutorial/"` left unchanged (already correct in book.toml)
- Workflow installs mdbook from latest GitHub release dynamically (no hardcoded version)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected repo name in book.toml URLs**

- **Found during:** Task 1 (book.toml edits)
- **Issue:** Plan text and 05-RESEARCH §3.4 used `ohama/OpenHandsTests` in the git-repository-url and edit-url-template values. The CORRECTED_REPO_FACTS instruction (authoritative) specifies `ohama/Openhands-Tutorial` — the repo already exists at that name.
- **Fix:** Used `https://github.com/ohama/Openhands-Tutorial` and `edit-url-template = "https://github.com/ohama/Openhands-Tutorial/edit/main/{path}"`
- **Files modified:** book.toml
- **Verification:** Values match existing `origin` remote URL
- **Committed in:** 0bdbe63 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — corrected stale repo name in URLs)
**Impact on plan:** Essential correction — using the wrong repo name would produce broken edit-on-GitHub links. No scope creep.

## Issues Encountered

- `python3 -c "import yaml ..."` failed with `ModuleNotFoundError` (pyyaml not in system Python). Resolved via `uv run python3 -c "import yaml ..."` — YAML is valid.

## Publish Checkpoint (Task 2) — DONE (user authorized "Publish everything")

Performed by the orchestrator after authorization:
1. `git push -u origin main` — pushed all commits (incl. `.planning/`) to the public repo `ohama/Openhands-Tutorial` ✓ (the `-25308` lines were harmless macOS Keychain credential-store warnings; the branch pushed fine)
2. `gh api -X POST repos/ohama/Openhands-Tutorial/pages -f build_type=workflow` — Pages enabled, source = GitHub Actions ✓
3. Deploy workflow run `26548628480` ("Deploy mdBook to GitHub Pages") succeeded (build + deploy jobs ✓; only non-blocking Node-20 deprecation annotations)
4. Live-site verification (SC#4): index + all spot-checked chapters (ch01/ch03/ch04/부록 A/부록 B/ch05) return 200; the real fingerprinted assets (`css/general-0392ca55.css`, `book-*.js`, fonts) return 200; `lang="ko"` present. (An initial 404 was a stale-filename test on my part — mdBook 0.5.3 hashes asset names; the actual referenced assets all serve.)

**Live site:** https://ohama.github.io/Openhands-Tutorial/  — BOOK-03 / SC#4 satisfied.

The full repo history (including `.planning/`) is now public, per the author's explicit "Publish everything" choice.

---
*Phase: 05-troubleshooting-reproducibility-publish*
*Completed (partial): 2026-05-28*
