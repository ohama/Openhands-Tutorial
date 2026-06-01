# Phase 10 Preflight Report

Date: 2026-06-01T05:34:36Z

## Toolchain

- scala-cli installed by preflight: NO (was already present at plan start — scala-cli 1.14.0 was pre-installed; `brew install` step was a no-op per precondition facts)
- scala-cli: Scala CLI version: 1.14.0 / Scala version (default): 3.8.3
- JDK: openjdk version "17.0.19" 2026-04-21 (OpenJDK Runtime Environment Homebrew, build 17.0.19+0)

## Cache pre-warm (trivial run)

- command: `scala-cli run /tmp/Preflight.scala` (file contains `@main def preflight() = println("PREFLIGHT_OK")`)
- First-run behavior: scala-cli downloaded compiler artifacts on first invocation (Bloop BSP server, Zinc incremental compiler, Scala 3.8.3 compiler JARs, temurin JDK). Download completed successfully — all artifacts fetched from coursier/maven-nightlies/sonatype mirrors. A few `Failed to download` lines appeared for snapshot repositories (normal — coursier tries multiple mirrors in parallel and falls back).
- output (tail): `Compiling project (Scala 3.8.3, JVM (17))` / `Compiled project (Scala 3.8.3, JVM (17))` / `PREFLIGHT_OK`
- PREFLIGHT_OK printed: YES
- exit code: 0
- artifact cache warm: YES (first-run download completed in preflight; second run from cached artifacts was instantaneous — only `PREFLIGHT_OK` printed, no download output)

## Scratch dir

- /Users/ohama/projs/OpenHandsTests/oh-workdir-scala/ exists: YES
- empty: YES (total 0; contains only `.` and `..`)

## Gitignore

- oh-workdir-scala ignored: YES (git check-ignore output: `oh-workdir-scala`)
- oh-workdir-rust ignored: YES (git check-ignore output: `oh-workdir-rust`)
- oh-workdir-122b ignored: YES (git check-ignore output: `oh-workdir-122b`)
- oh-workdir ignored: YES (git check-ignore output: `oh-workdir`)
- .gitignore entry added: `oh-workdir-scala/` (appended alongside existing book/, oh-workdir/, oh-workdir-122b/, oh-workdir-rust/ — all 5 entries confirmed present)

## Proxy

- curl http://127.0.0.1:4000/v1/models response: `{"data": [{"id": "qwen-35b", ...}, {"id": "qwen-122b", ...}, {"id": "qwen-local", ...}]}`
- qwen-35b present: YES
- qwen-122b present: YES (bonus — confirms proxy healthy)

## Notes

- scala-cli was NOT freshly installed during this preflight (it was already present at 1.14.0 per host precondition facts). The plan's step 1 (`brew install scala-cli`) was skipped with a no-op detect. No reinstall was needed.
- The trivial run did trigger a first-run artifact download (scala-cli had never been run on this host before, even though the binary was present). The cache is now warm.
- JDK used: the host JDK (openjdk@17 from Homebrew) was picked up automatically by scala-cli. No `--jvm` flag needed.
- The "Failed to download" lines in the first-run output are normal: coursier tries snapshot repos first (maven-snapshots), which don't have stable releases, then falls back to maven-nightlies / central. All required artifacts were ultimately downloaded.

## Verdict

PREFLIGHT GREEN — 10-02 can launch.
