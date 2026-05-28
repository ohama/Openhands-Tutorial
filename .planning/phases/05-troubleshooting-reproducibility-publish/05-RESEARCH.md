# Phase 5 Research: Troubleshooting, Reproducibility & Publish

**Researched:** 2026-05-28  
**Researcher:** gsd-phase-researcher agent  
**Phase goal:** Complete the book with troubleshooting and reproducibility chapters, do a final full mdbook build, and deploy to GitHub Pages.  
**Requirements addressed:** TROUBLE-01, REPRO-01, BOOK-03

---

## 1. Troubleshooting Chapter — Reconciled Honest Content

### Source documents read

- `.planning/STATE.md` — Phase 2 environment decisions and accumulated Phase 3 learnings  
- `.planning/phases/03-capture-the-openhands-run/03-02-RUN-NOTES-attempt1.md` — Attempt 1 failure analysis  
- `.planning/phases/03-capture-the-openhands-run/03-02-RUN-NOTES.md` — Attempt 2 run notes  
- `.planning/phases/03-capture-the-openhands-run/captured/CAPTURE-MANIFEST.md` — Requirement-to-artifact map  
- `.planning/REQUIREMENTS.md` — Original TROUBLE-01 anticipated list  
- `.planning/ROADMAP.md` — Phase 5 success criteria  

---

### 1.1 Real Failure Modes (what actually happened — document ALL of these)

#### REAL-01: Colima instead of Docker Desktop — DOCKER_HOST required

**What happened:**  
The machine uses Colima (not Docker Desktop). The Docker daemon socket lives at `/Users/ohama/.colima/default/docker.sock`; `/var/run/docker.sock` does NOT exist. OpenHands needs `DOCKER_HOST=unix:///Users/ohama/.colima/default/docker.sock` to find the daemon.

**Symptom without fix:** OpenHands fails to start or cannot pull agent-server images because it cannot connect to the Docker socket.

**Fix:** Set `DOCKER_HOST=unix:///Users/ohama/.colima/default/docker.sock` before running OpenHands (either export or inline env var). Start Colima first: `colima start --cpu 4 --memory 8 --disk 60`.

**Note for readers:** Docker Desktop users do NOT need this; they have `/var/run/docker.sock` automatically. Colima users must set DOCKER_HOST. On Linux, the socket path may differ — check `docker context inspect` or `docker info`.

---

#### REAL-02: --override-with-envs is REQUIRED — LLM_* env vars silently ignored without it

**What happened:**  
Without `--override-with-envs`, OpenHands ignores `LLM_MODEL`, `LLM_BASE_URL`, and `LLM_API_KEY` environment variables silently. The agent starts but routes to a default (often broken or cloud) endpoint.

**Symptom:** OpenHands appears to start but LLM calls fail with authentication errors or connection refused, even though env vars are set correctly.

**Fix:** Always include `--override-with-envs` in the headless invocation:
```bash
LLM_MODEL="openai/qwen-local" LLM_BASE_URL="http://127.0.0.1:4000/v1" LLM_API_KEY="dummy" \
openhands --headless --json --yolo --override-with-envs -t "..."
```

**Why it matters:** This is a silent failure — no error message indicates the env vars were ignored.

---

#### REAL-03: FsLex out-of-distribution for 35B model — attempt 1 failed entirely on FsLex

**What happened (Attempt 1):**  
The Qwen2.5-35B model is unfamiliar with FsLex (`.fsl`) syntax. FsLex does NOT use `%%` section separators — that is FsYacc syntax. Every agent invocation in attempt 1 added `%%` to Lexer.fsl, which breaks the build with:
```
Lexer.fsl(8): error : Unexpected character '%'
```
Three separate agent invocations (94 + 27 + 16 TerminalActions = 137 total) all failed to produce a valid Lexer.fsl. Other sub-issues:
- `lexeme lexbuf` does not exist; correct is `LexBuffer<_>.LexemeString lexbuf`
- FsLex header braces `{ open Parser }` on one line causes 2-space indentation in generated `.fs`, breaking F# light-mode compilation

**Fix used (attempt 2):** Provide the verbatim Lexer.fsl content in the task prompt (Deviation Rule 3). This is documented honestly in transcript.md and CAPTURE-MANIFEST.md — the agent's real engineering work in attempt 2 was Parser.fsy and Program.fs.

**Lesson for readers:** FsLex syntax is genuinely unusual and poorly represented in LLM training data. If your model cannot write a valid `.fsl` file, provide the lexer verbatim in the task prompt and let the agent focus on the parser.

---

#### REAL-04: file_editor tool validation error — security_risk field missing

**What happened (Attempt 1, Task 4):**  
Every `file_editor` / `str_replace` tool call by qwen-local fails with:
```
Error validating tool 'file_editor': Failed to provide security_risk field in tool 'file_editor'.
```
This happened twice (task4-evaluator.jsonl, task4-evaluator-retry1.jsonl) with zero retries producing a different result.

**Fix:** Add this instruction to EVERY task prompt:
```
IMPORTANT: Create and edit ALL files using ONLY bash shell commands (printf, tee, or
`cat > FILE <<'EOF' ... EOF` with a quoted heredoc). Do NOT use the file_editor /
str_replace tool — it errors in this setup (it requires a security_risk field that
fails validation).
```
This was added to all task prompts in attempt 2 and resulted in zero file_editor errors.

**Why it happens:** The qwen-local model's tool call schema for `file_editor` omits the `security_risk` field that OpenHands requires. This is a model-specific behavior.

---

#### REAL-05: .NET 10 + FsLexYacc 11.3.0 line-directive incompatibility — FixLineDirectives required

**What happened:**  
`fsyacc` and `fslex` generate `# 0 ""` line directives in their output `.fs` files. The F# 10 compiler (shipped with .NET SDK 10.0.203) rejects these with `FS0010: unexpected ...`. This is a known incompatibility.

**Symptom:** Build fails even with a correct `.fsy`/`.fsl` when using .NET 10, even though the same grammar compiles on .NET 8.

**Fix:** The `FixLineDirectives` MSBuild target in `calc.fsproj` strips the offending directives via `sed`:
```xml
<Target Name="FixLineDirectives" BeforeTargets="CoreCompile" DependsOnTargets="CallFsYacc;CallFsLex">
  <Exec Command="sed -i '' '/^# 0/d' Parser.fs" Condition="Exists('Parser.fs')" />
  <Exec Command="sed -i '' '/^# 0/d' Lexer.fs"  Condition="Exists('Lexer.fs')"  />
</Target>
```
This was provided verbatim in task1-scaffold.txt to prevent a non-instructive blocker.

**Note:** On Linux, the sed syntax is `sed -i '/^# 0/d'` (no argument after `-i`). The workflow file runs on `ubuntu-latest` and does NOT build the F# project — only the mdbook — so this is only a local-dev concern.

---

#### REAL-06: FsYacc %start / %type syntax errors — the genuine error-and-fix cycle

**What happened (Attempt 2, Task 3, events 9–30):**  
The agent wrote Parser.fsy with four sequential build failures before succeeding:

| Attempt | Error | Cause |
|---------|-------|-------|
| 1 | `FSY000: at least one %start declaration is required` | Agent wrote `%type <int> start` but omitted `%start` |
| 2 | `Parser.fsy(16,7): error parse error` | Agent used `%start <int> start` (invalid — fsyacc takes only the symbol) |
| 3 | Same parse error | Another attempt at same wrong syntax |
| 4 | `FS0039: 'LexBuffer<_>' does not define 'FromText'` | Correct `%start` syntax at last; but `LexBuffer.FromText` doesn't exist |

**Fix (event 27–30):** Agent correctly separated into `%start start` (separate line) + `%type <int> start` (separate line), and changed `LexBuffer.FromText` to `LexBuffer<char>.FromString`. Build succeeded: `calc net10.0 성공 (0.7초)`.

**This is the genuine error-and-fix cycle (RUN-03) narrated in 4부.** It is documented here for the troubleshooting chapter to reference.

---

### 1.2 Anticipated TROUBLE-01 Failures — Honest Reconciliation

The REQUIREMENTS.md TROUBLE-01 listed these anticipated failure modes. Here is the honest status of each:

| Anticipated Failure | Status | Reality |
|--------------------|--------|---------|
| `host.docker.internal` vs `127.0.0.1` | **DID NOT APPLY** | With LocalWorkspace (host PTY, not Docker), OpenHands calls the LLM from the HOST process. `127.0.0.1:4000` reaches litellm directly. `host.docker.internal` is only needed when running OpenHands inside Docker and the LLM is on the host. Document honestly: not needed in this setup. |
| `openai/` prefix requirement | **APPLIES** | The litellm proxy is configured with model alias `qwen-local`. In the OpenHands invocation `LLM_MODEL="openai/qwen-local"` — the `openai/` prefix is required. Without it, LiteLLM does not know which provider adapter to use. This DID apply and is worth documenting. |
| Timeout / retry storm | **DID NOT APPLY** | Measured ~14–32 s per tool-call cycle. The STACK.md "240 s estimate" was wrong (unmeasured). No timeout errors occurred in either attempt. Document honestly: "anticipated but didn't occur; real timings were 14–32 s in this run." |
| Missing .NET in sandbox | **DID NOT APPLY** | LocalWorkspace = host PTY; `dotnet 10.0.203` is on the host PATH and is directly available to the agent. No custom Docker image or sandbox setup was needed. Document honestly. |
| FsYacc `%left` precedence | **PARTIALLY APPLIES** | The `%left` declarations (`%left PLUS MINUS`, `%left STAR SLASH`) ARE required for correct operator precedence and associativity. However, in attempt 2 the agent wrote them correctly from the start — no precedence bug emerged. The anticipated "bug you have to fix" scenario did NOT occur. The `%left` topic still belongs in the troubleshooting chapter as a "watch for this if your grammar gives wrong results," but should be noted as "did not occur in our run." |

---

### 1.3 File Mapping for TROUBLE-01

The current SUMMARY.md draft (5부 entries):
```
# 5부: 정리와 심화
- [개념 되짚기]()
- [다음 단계]()
---
[부록 A: 자주 묻는 질문]()
[부록 B: 트러블슈팅]()
```

**TROUBLE-01 → 부록 B: 트러블슈팅**

Recommended file path: `src/appendix-b-troubleshooting.md`

The chapter should be structured as:
1. **환경 문제** (environment issues): REAL-01 (Colima/DOCKER_HOST), REAL-02 (--override-with-envs), REAL-05 (.NET 10 line-directive)
2. **에이전트 동작 문제** (agent behavior issues): REAL-03 (FsLex OOD), REAL-04 (file_editor security_risk)
3. **빌드 오류** (build errors): REAL-06 (%start/%type + LexBuffer API)
4. **예상했지만 발생하지 않은 문제** (anticipated but didn't occur): honest reconciliation of host.docker.internal, timeouts, missing .NET, %left precedence bug

**5부 narrative chapters** (개념 되짚기, 다음 단계):
- `src/ch05-wrap-up/review.md` for 개념 되짚기
- `src/ch05-wrap-up/next-steps.md` for 다음 단계

**부록 A: 자주 묻는 질문** → `src/appendix-a-faq.md` (see Section 2 below — reproducibility content may overlap with FAQ or become appendix B-prime)

---

## 2. Reproducibility Appendix — Exact Content

### 2.1 What REPRO-01 requires

"Exact task strings, Docker/run commands, config values, and expected outputs so a reader can reproduce the run."

### 2.2 Prerequisites (exact — reader must have all of these)

| Component | Version | Notes |
|-----------|---------|-------|
| macOS (Apple Silicon) | Any recent | The run was on a headless SSH Mac; adapts to Intel or Linux with minor changes |
| Colima OR Docker Desktop | Colima latest | `colima start --cpu 4 --memory 8 --disk 60` before running OpenHands. Docker Desktop users omit DOCKER_HOST. |
| uv | Any recent | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| OpenHands CLI | v1.16.0 (SDK v1.21.0) | `uv tool install openhands --python 3.12`; PATH via `~/.local/bin` |
| .NET SDK | 10.0.203+ | `dotnet --version` must show 10.x; agent uses host PATH directly (LocalWorkspace) |
| litellm proxy | Running at `127.0.0.1:4000` | `litellm --config /path/to/config.yaml`; must expose model alias `qwen-local` |
| Qwen2.5-35B or larger | Via MLX or vLLM | Must support tool calling (`finish_reason: "tool_calls"`); proxy routes via `openai/qwen-local` |
| FsLexYacc 11.3.0 | In NuGet cache | `~/.nuget/packages/fslexyacc/11.3.0/` should be pre-populated; dotnet restore pulls from cache without network |

**Verify the stack before running:**
```bash
# Docker daemon
docker run hello-world

# OpenHands version
openhands --version                  # SDK v1.21.0 / CLI 1.16.0

# litellm proxy + model alias
curl -s http://127.0.0.1:4000/v1/models | python3 -m json.tool | grep '"id"'
# Should show: "id": "qwen-local"

# LLM tool calling (basic check)
curl -s http://127.0.0.1:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-local","messages":[{"role":"user","content":"Say hello"}]}' \
  | python3 -m json.tool | grep '"content"'

# .NET SDK
dotnet --version                     # 10.0.203 or later
```

### 2.3 Exact environment variable invocation

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
LLM_MODEL="openai/qwen-local" \
LLM_BASE_URL="http://127.0.0.1:4000/v1" \
LLM_API_KEY="dummy" \
OPENHANDS_WORK_DIR="/path/to/your/oh-workdir" \
openhands --headless --json --yolo --override-with-envs \
  -t "$(cat task1-scaffold.txt)" \
  2>task1-scaffold.stderr.log | tee task1-scaffold.jsonl
```

Repeat for each task, substituting the prompt file and log name. Colima users add:
```bash
DOCKER_HOST="unix:///Users/$(whoami)/.colima/default/docker.sock" \
```
at the top of the env block.

### 2.4 Exact task prompts (verbatim sources)

The canonical task prompts are committed at:
```
.planning/phases/03-capture-the-openhands-run/task-prompts/
  00-INVOCATION.md        ← invocation pattern + per-task log filenames
  task1-scaffold.txt      ← dotnet new + exact calc.fsproj content (FixLineDirectives)
  task2-lexer.txt         ← verbatim Lexer.fsl content (provided, not agent-written)
  task3-parser.txt        ← FsYacc grammar spec (behavioral outcomes, no %left hint)
  task4-evaluator.txt     ← Program.fs CLI wiring spec
  task5-buildtest.txt     ← build + 3-case test verification
```

**Key design choices in the prompts:**

- `task1-scaffold.txt`: Provides verbatim `calc.fsproj` with `FixLineDirectives` target. This bypasses the .NET 10 line-directive bug before the agent encounters it.
- `task2-lexer.txt`: Provides verbatim Lexer.fsl content. Rationale: FsLex syntax is out-of-distribution for 35B models (attempt 1 proved this with 137 failed TerminalActions across 3 invocations).
- `task3-parser.txt`: Specifies behavioral outcomes (`10-3-2 = 5`, `2+3*4 = 14`) without revealing `%left`. The agent must discover the correct precedence declarations independently.
- All prompts include: `IMPORTANT: Create and edit ALL files using ONLY bash shell commands ... Do NOT use the file_editor / str_replace tool.`

### 2.5 Expected outputs (verbatim from captured/test-output.txt)

```
=== Calculator Correctness Test ===

Build:
  복원할 프로젝트를 확인하는 중...
  복원할 모든 프로젝트가 최신 상태입니다.
  calc -> .../calc/bin/Debug/net10.0/calc.dll

빌드했습니다.
    경고 0개
    오류 0개

경과 시간: 00:00:00.95

Test cases:
2+3*4 = 14
(2+3)*4 = 20
10-3-2 = 5
```

**Run summary:**
- 5 tasks, 0 retries in attempt 2
- Total events: 146 (across 5 JSONL logs)
- Total TerminalActions: 67
- Timing: task1=3m6s, task2=16s, task3=1m17s, task4=45s, task5=32s → ~6 min total

**Error-and-fix cycle (task3-parser.jsonl events 9–30):**
```
Attempt 1: FSY000 at least one %start declaration is required
Attempt 2: Parser.fsy(16,7): error parse error   [%start <int> start is invalid]
Attempt 3: Parser.fsy(16,7): error parse error   [same error]
Attempt 4: FS0039 LexBuffer<_> does not define 'FromText'
Attempt 5: Build succeeded — calc net10.0 성공 (0.7초)
```

### 2.6 File mapping for REPRO-01

**REPRO-01 → 부록 A: 자주 묻는 질문** (or rename to a dedicated reproducibility appendix)

The SUMMARY.md currently labels this "부록 A: 자주 묻는 질문" (FAQ). Recommendation:
- Either rename to `부록 A: 재현 가이드` (Reproducibility Guide) and put exact commands there, OR
- Keep as FAQ and fold reproducibility steps into it under a "직접 실행해보기" (Run It Yourself) section.

**Recommend:** Rename 부록 A to `부록 A: 재현 가이드` (Reproducibility Guide) for clarity. File path: `src/appendix-a-repro.md`.

---

## 3. GitHub Pages Deployment — Exact Workflow

### 3.1 Current state (verified)

- **Local-only repo**: `main` branch, no remote, no `.github/` directory
- **gh CLI**: logged in as `ohama` (account confirmed via `gh auth status`)
- **Token scopes**: `repo`, `workflow`, `gist`, `read:org` — all required scopes are present
- **book.toml**: `site-url = "/OpenHandsTests/"` — correct for a project page at `github.com/ohama/OpenHandsTests`
- **mdbook build**: passes clean (confirmed 2026-05-28: `INFO HTML book written to .../book`)

### 3.2 GitHub Actions workflow YAML

Create at `.github/workflows/deploy.yml`:

```yaml
name: Deploy mdBook to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install mdBook
        run: |
          tag=$(curl -s 'https://api.github.com/repos/rust-lang/mdBook/releases/latest' \
            | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')
          curl -sSL \
            "https://github.com/rust-lang/mdBook/releases/download/${tag}/mdbook-${tag}-x86_64-unknown-linux-gnu.tar.gz" \
            | tar -xz --directory="$HOME/.cargo/bin"

      - name: Build book
        run: mdbook build

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: book

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**Action versions as of 2026-05-28 (from STACK.md research, HIGH confidence):**
- `actions/checkout@v4` — stable
- `actions/configure-pages@v4` — stable
- `actions/upload-pages-artifact@v3` — stable
- `actions/deploy-pages@v4` — stable

### 3.3 Required GitHub repo settings

Once the repo is created and pushed, enable GitHub Pages:

1. Go to repo → Settings → Pages
2. **Source**: Select "GitHub Actions" (NOT "Deploy from a branch")
3. No branch or folder selection needed — the workflow handles artifact upload

The `permissions: pages: write` + `id-token: write` in the YAML give the workflow the OIDC token it needs. No additional secrets need to be configured.

### 3.4 book.toml additions (optional but recommended)

Current `book.toml` is minimal. Consider adding:

```toml
[output.html]
site-url = "/OpenHandsTests/"      # already present
default-theme = "light"            # already present
preferred-dark-theme = "navy"      # already present
git-repository-url = "https://github.com/ohama/OpenHandsTests"   # add: enables "edit on GitHub" links
edit-url-template = "https://github.com/ohama/OpenHandsTests/edit/main/{path}"  # add: exact edit URL
```

These are optional enhancements — the deploy works without them.

### 3.5 User-gated checkpoint: repo create / push / enable Pages

**CRITICAL: The following steps require user authorization before the agent runs them.**

The `gh` CLI is logged in as `ohama` with `repo` + `workflow` scopes. No remote exists yet. Creating a PUBLIC GitHub repo and pushing is a publishing action. The planner MUST include a checkpoint:

```
USER CHECKPOINT — before the agent runs these commands, confirm:
1. Repo name: OpenHandsTests (must match site-url "/OpenHandsTests/")
2. Visibility: public (GitHub Pages requires public for free accounts) or private + GitHub Pro
3. Confirm it's OK to create the repo and push main branch
```

**Exact commands (run ONLY after user confirms):**

```bash
# 1. Create the remote repo (public, no template, no README — we have our own)
gh repo create OpenHandsTests \
  --public \
  --description "에이전틱 AI 튜토리얼: OpenHands로 배우는 AI 에이전트" \
  --source . \
  --remote origin \
  --push

# 2. Enable GitHub Pages (source = GitHub Actions)
gh api repos/ohama/OpenHandsTests/pages \
  --method POST \
  -f build_type=workflow

# 3. Verify Pages is enabled
gh api repos/ohama/OpenHandsTests/pages | python3 -m json.tool | grep '"status"'
```

After the workflow runs (triggered by the push in step 1), the live URL will be:  
`https://ohama.github.io/OpenHandsTests/`

**Alternative: The user can do steps 2 and 3 manually** in the GitHub web UI (Settings → Pages → Source = "GitHub Actions").

---

## 4. File Mapping for 5부 Chapters

### 4.1 Current SUMMARY.md draft (5부 / appendix)

```markdown
# 5부: 정리와 심화

- [개념 되짚기]()
- [다음 단계]()

---

[부록 A: 자주 묻는 질문]()
[부록 B: 트러블슈팅]()
```

### 4.2 Recommended file paths

| SUMMARY entry | Recommended file | Content |
|--------------|-----------------|---------|
| 개념 되짚기 | `src/ch05-wrap-up/review.md` | Brief review of the 4 key agentic concepts as demonstrated in the real run |
| 다음 단계 | `src/ch05-wrap-up/next-steps.md` | Where to go from here: more OpenHands experiments, larger models, other languages |
| 부록 A: 자주 묻는 질문 | `src/appendix-a-repro.md` | Rename to reproducibility guide (REPRO-01) — or keep as FAQ and embed repro steps |
| 부록 B: 트러블슈팅 | `src/appendix-b-troubleshooting.md` | Troubleshooting chapter (TROUBLE-01) |

**Note on renaming 부록 A:** If the planner wants to keep the title "자주 묻는 질문" (FAQ), the reproducibility content can be structured as Q&A (e.g., "Q: How do I reproduce the exact run? A: ..."). Either approach works.

### 4.3 Directory structure to create

```
src/
  ch05-wrap-up/
    review.md
    next-steps.md
  appendix-a-repro.md         (or appendix-a-faq.md with REPRO content embedded)
  appendix-b-troubleshooting.md
```

The `ch05-wrap-up/` directory needs to be created. The appendix files go directly under `src/`.

### 4.4 SUMMARY.md wiring (exact replacements)

Replace draft `()` entries:

```markdown
# 5부: 정리와 심화

- [개념 되짚기](ch05-wrap-up/review.md)
- [다음 단계](ch05-wrap-up/next-steps.md)

---

[부록 A: 재현 가이드](appendix-a-repro.md)
[부록 B: 트러블슈팅](appendix-b-troubleshooting.md)
```

(Or keep 부록 A title as `자주 묻는 질문` if the planner prefers.)

---

## 5. Flags for User Confirmation

1. **Repo visibility**: The plan assumes PUBLIC (free GitHub Pages). If the user's GitHub account is on Pro/Team, a private repo also works. Confirm before running `gh repo create`.

2. **Repo name**: Must be exactly `OpenHandsTests` to match `site-url = "/OpenHandsTests/"` in `book.toml`. If the name changes, book.toml must also be updated.

3. **Whether to actually publish**: Creating+pushing a public repo is irreversible in the sense that it becomes publicly visible. The planner should treat the actual `gh repo create --push` as a user-gated checkpoint, not autonomous execution.

4. **부록 A title**: `자주 묻는 질문` (FAQ) vs `재현 가이드` (Reproducibility Guide) — either works structurally; the planner should pick based on which framing serves the reader better.

---

## 6. Plan Shape for Phase 5

Based on this research, the planner should create these plans:

| Plan | Content | Requirements |
|------|---------|-------------|
| 05-01-PLAN.md | Write 부록 B (troubleshooting) + 5부 narrative chapters (review + next-steps) | TROUBLE-01 |
| 05-02-PLAN.md | Write 부록 A (reproducibility guide) | REPRO-01 |
| 05-03-PLAN.md | Final mdbook build check (wire all 5부/appendix SUMMARY entries, build green, verify navigation) | BOOK-01 (final gate) |
| 05-04-PLAN.md | Create .github/workflows/deploy.yml; USER CHECKPOINT for gh repo create + push + Pages enable; verify live URL | BOOK-03 |

**Alternative**: Merge 05-01 and 05-02 if the planner prefers fewer plans (both are writing tasks with no dependency between them).

---

## 7. Quick Reference: Key Facts for the Planner

| Fact | Value |
|------|-------|
| mdbook version | 0.5.3 at `/opt/homebrew/bin/mdbook` |
| Current build status | CLEAN (confirmed 2026-05-28) |
| git remote | NONE — local only on `main` |
| gh CLI | Logged in as `ohama`; scopes: repo, workflow |
| book.toml site-url | `/OpenHandsTests/` (project page URL) |
| Expected live URL | `https://ohama.github.io/OpenHandsTests/` |
| DOCKER_HOST (Colima) | `unix:///Users/ohama/.colima/default/docker.sock` |
| litellm proxy | `127.0.0.1:4000`, model alias `qwen-local` |
| OpenHands version | SDK v1.21.0 / CLI v1.16.0 |
| Test results | 14 / 20 / 5 (all PASS) |
| Attempt 1 | FAILED — FsLex OOD; 137 TerminalActions; Lexer.fsl never produced |
| Attempt 2 | SUCCESS — 5 tasks, 0 retries; genuine error-and-fix in task3 (4 failures → self-corrected) |
| 5부 draft entries | 4 entries total: 2 narrative + 2 appendix (all `()`) |
| Appendix files to create | appendix-a-repro.md, appendix-b-troubleshooting.md |
| 5부 chapter files to create | ch05-wrap-up/review.md, ch05-wrap-up/next-steps.md |
