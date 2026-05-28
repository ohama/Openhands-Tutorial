# Phase 8 Preflight Report

Date: 2026-05-28T08:36:42Z

## Toolchain
- rustc: rustc 1.95.0 (59807616e 2026-04-14)
- cargo: cargo 1.95.0 (f2d3ce0bd 2026-03-21)

## Port 8080
- lsof -ti :8080: (empty)
- status: FREE

## Scratch dir
- /Users/ohama/projs/OpenHandsTests/oh-workdir-rust/ exists: YES
- empty: YES (only . and .. present)

## Gitignore
- oh-workdir-rust ignored: YES (git check-ignore output: oh-workdir-rust)
- oh-workdir-122b ignored: YES (git check-ignore output: oh-workdir-122b)
- oh-workdir ignored: YES (git check-ignore output: oh-workdir)

## Proxy
- curl http://127.0.0.1:4000/v1/models response: lists 3 models: qwen-35b, qwen-122b, qwen-local
- qwen-35b present: YES

## Verdict
PREFLIGHT GREEN — 08-02 can launch.
