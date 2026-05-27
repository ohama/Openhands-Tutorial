# Pitfalls Research

**Domain:** Korean mdBook tutorial — Agentic AI via OpenHands + local Qwen 35B MLX + F# FsLex/FsYacc calculator
**Researched:** 2026-05-27
**Confidence:** HIGH for OpenHands/LLM pitfalls (backed by GitHub issues); HIGH for FsLexYacc specifics (backed by official docs/community); MEDIUM for MLX-specific behavior (limited direct docs)

---

## Critical Pitfalls

### Pitfall 1: `127.0.0.1` vs `host.docker.internal` — OpenHands Cannot Reach the Local MLX Server

**What goes wrong:**
OpenHands runs its agent-server inside a Docker container. When `LLM_BASE_URL` is set to `http://127.0.0.1:8000/v1`, Docker interprets `127.0.0.1` as the *container's own* loopback — not the host Mac's loopback. The MLX server is on the host. Every LLM call silently fails with a connection-refused error, and the agent never starts.

**Why it happens:**
Docker networking on macOS has no direct bridge to the host at `127.0.0.1`. The only standard escape hatch is `host.docker.internal`, which Docker Desktop resolves to the host's IP. Users familiar with running CLIs natively copy the same URL they used to test the endpoint from their terminal — it works there, breaks inside Docker.

**How to avoid:**
- Set `LLM_BASE_URL=http://host.docker.internal:8000/v1` in every `docker run` invocation (not `localhost` or `127.0.0.1`).
- The official OpenHands `docker run` template already includes `--add-host host.docker.internal:host-gateway` — do not remove this flag.
- Verify with `curl http://host.docker.internal:8000/health` *from inside* a throwaway container before running OpenHands.
- In the tutorial's setup chapter: show the full verified `docker run` command with the `--add-host` flag and the `host.docker.internal` URL, not `127.0.0.1`.

**Warning signs:**
- The OpenHands UI shows the agent initializing but never produces any first action.
- The terminal log shows `litellm.exceptions.APIConnectionError` or `ConnectionRefusedError` for `127.0.0.1`.
- Repeated retries with no clear timeout or model error message.

**Phase to address:** Setup/Installation chapter (Phase: OpenHands + local LLM 설정)

---

### Pitfall 2: Wrong Model Name Format — liteLLM Does Not Route to the Local Endpoint

**What goes wrong:**
OpenHands uses liteLLM under the hood. liteLLM routes requests based on the model name *prefix*. If you set `LLM_MODEL` to the raw path like `/Users/ohama/llm-system/models/qwen36-35b` or just `qwen36-35b`, liteLLM will not recognise it as an OpenAI-compatible endpoint and will either refuse the request or try to route it to a cloud provider. The result is an authentication error or silent misconfiguration.

**Why it happens:**
liteLLM identifies providers by a string prefix (`openai/`, `ollama/`, `anthropic/`, etc.). For custom OpenAI-compatible endpoints (vLLM, SGLang, MLX), the required prefix is `openai/` followed by the model name *the server advertises*, not a local file path. The local MLX server may advertise the model ID as the full filesystem path — that becomes the value after `openai/`.

**How to avoid:**
- Query the server's model list first: `curl http://127.0.0.1:8000/v1/models | jq '.data[].id'`. Use whatever ID the server returns.
- Set `LLM_MODEL=openai/<id-from-server>`. Example: if the server returns `/Users/ohama/llm-system/models/qwen36-35b`, set `LLM_MODEL=openai//Users/ohama/llm-system/models/qwen36-35b`.
- Set `LLM_API_KEY=local` (any non-empty placeholder — liteLLM requires a non-empty key for OpenAI-compatible routes; the MLX server ignores it).
- Set `LLM_BASE_URL=http://host.docker.internal:8000/v1`.
- If the server ID is an ugly path, configure the MLX server to expose a shorter alias, or set `LLM_DROP_PARAMS=true` to suppress any unsupported parameters liteLLM might inject.
- In the tutorial: show an exact verified working `docker run` with all four env vars; note that the model name must match `curl /v1/models` output.

**Warning signs:**
- `litellm.exceptions.AuthenticationError` even though you know there is no auth needed.
- `LiteLLM.BadRequestError: model not found`.
- OpenHands UI model validation fails at startup.

**Phase to address:** Setup/Installation chapter (Phase: OpenHands LLM 설정 섹션)

---

### Pitfall 3: LLM Timeouts at ~240s — OpenHands Disconnects and Enters a Retry Storm

**What goes wrong:**
The MLX server on local hardware takes ~240 seconds for a complex tool-calling request. OpenHands/liteLLM has a default timeout (`LLM_TIMEOUT`) of 0 (unlimited in theory), but in practice the retry logic fires every `LLM_RETRY_MIN_WAIT` (default 15s) with exponential backoff up to 120s, and up to 8 retries (`LLM_NUM_RETRIES=8`). A legitimately slow response may be interrupted and retried, producing 8 × 240s = ~32 minutes of retries before giving up. Worse, prior to OpenHands fixing issue #8768, the error message was opaque — the user could not tell if it was a timeout or a real error.

**Why it happens:**
OpenHands was designed for cloud LLMs that respond in <5s. The retry parameters are hardcoded for that world. With a 240s model, the first "retry min wait" (15s) fires before the model has finished streaming. Each retry resets the context — the model starts over, potentially causing an infinite reattempt loop.

**How to avoid:**
- Set `LLM_TIMEOUT=600` (or higher) via environment variable when running the Docker container.
- Set `LLM_NUM_RETRIES=2` and `LLM_RETRY_MIN_WAIT=300` to prevent premature retries.
- In `config.toml` under `[llm]`: `timeout = 600`, `num_retries = 2`, `retry_min_wait = 300`.
- Monitor the MLX server's stdout to confirm it is actively generating (not hung) during long waits.
- For the tutorial: frame the 240s wait explicitly — show a "patience" callout. Tell readers the agent is computing, not hung, and how to tell the difference (MLX server logs should show token generation). Document the exact `LLM_TIMEOUT` setting to use.

**Warning signs:**
- `litellm.Timeout: APITimeoutError` in logs.
- The agent restarts a task from scratch repeatedly.
- MLX server logs show a request arriving multiple times.

**Phase to address:** Setup chapter (LLM 설정) AND the "live run" chapter where readers follow along with the actual run.

---

### Pitfall 4: OpenHands Agent Stuck in a Loop — `AgentStuckInLoopError` with No Recovery

**What goes wrong:**
OpenHands's stuck detector fires when the agent repeats the same action/observation pattern 6+ times, or produces 3+ consecutive monologue messages without tool use. With a slow 35B model, the agent may legitimately need long think-loops (e.g., waiting for a `dotnet build` that takes 30s inside the container), triggering false-positive stuck detection. Once triggered, the default behaviour (pre-fix #5480) halts the agent and prevents the user from sending further messages.

**Why it happens:**
- Slow LLM inference causes long pauses between tool calls that look like loops.
- The F# build cycle (restore → generate → compile) can be multi-step and slow inside the sandbox, leading the agent to re-check intermediate states repeatedly.
- A model that cannot parse a compiler error (e.g., confusing FsYacc-generated code line numbers with source lines) may emit the same "read file" action repeatedly.

**How to avoid:**
- Task scope: give OpenHands one small, concrete step at a time rather than the entire "build a calculator from scratch" ask. Break the task into: (1) scaffold .fsproj + dependencies, (2) write Lexer.fsl, (3) write Parser.fsy with precedence, (4) write Evaluator.fs, (5) wire Program.fs. Restart the agent for each phase if needed.
- For long build commands, add a timeout to the bash tool invocation: `dotnet build 2>&1 | head -50` instead of open-ended commands.
- Keep the conversation fresh: if the agent starts looping on a compiler error it cannot fix, send a user message with the exact error text and ask it to fix only *that* error.
- In the tutorial: be honest that local models sometimes get stuck; show readers what the stuck state looks like and how to intervene (send a clarifying message, or restart with a narrower task). This is a teaching moment about agentic AI limitations.

**Warning signs:**
- The OpenHands UI shows the same file being read multiple times without any writes in between.
- The agent produces text-only messages with no tool calls for 3+ turns.
- `AgentStuckInLoopError` appears in the backend log.

**Phase to address:** The conceptual "agentic loop" chapter (framing failure modes honestly) AND the live-run chapter (task decomposition strategy).

---

### Pitfall 5: .NET SDK / FsLexYacc Not Available in OpenHands Runtime Sandbox

**What goes wrong:**
OpenHands's default sandbox image is `nikolaik/python-nodejs:python3.12-nodejs22`. It contains Python and Node.js — not the .NET SDK. Running `dotnet` inside the sandbox will fail with "command not found". FsLex and FsYacc are .NET tools installed via `dotnet tool install`. Without .NET, the entire example project cannot compile.

**Why it happens:**
OpenHands ships a generic sandbox optimised for Python/JS workloads. Niche runtimes like .NET must be added explicitly via a custom sandbox image or `runtime_extra_deps` in `config.toml`.

**How to avoid:**
- **Option A — `runtime_extra_deps`**: Add to `config.toml` under `[sandbox]`:
  ```toml
  runtime_extra_deps = """
  apt-get update && apt-get install -y wget &&
  wget https://dot.net/v1/dotnet-install.sh &&
  chmod +x dotnet-install.sh &&
  ./dotnet-install.sh --channel 9.0 --install-dir /usr/local/share/dotnet &&
  ln -s /usr/local/share/dotnet/dotnet /usr/local/bin/dotnet
  """
  ```
  Verify with `runtime_startup_env_vars = {DOTNET_ROOT = "/usr/local/share/dotnet"}`.
- **Option B — Custom sandbox Dockerfile** (preferred for reproducibility):
  ```dockerfile
  FROM nikolaik/python-nodejs:python3.12-nodejs22
  RUN wget https://dot.net/v1/dotnet-install.sh && \
      bash dotnet-install.sh --channel 9.0 --install-dir /usr/local/share/dotnet && \
      ln -s /usr/local/share/dotnet/dotnet /usr/local/bin/dotnet
  ENV DOTNET_ROOT=/usr/local/share/dotnet
  ENV PATH=$PATH:/usr/local/share/dotnet
  ```
  Build: `docker build -t openhands-dotnet .`
  Run OpenHands with: `SANDBOX_BASE_CONTAINER_IMAGE=openhands-dotnet`.
- Test before the tutorial run: open an OpenHands bash session and run `dotnet --version` to confirm.
- For the tutorial: provide the exact verified Dockerfile/config snippet; readers should not have to figure this out themselves.

**Warning signs:**
- Agent's first `dotnet new` or `dotnet build` command fails with "command not found" or "bash: dotnet: not found".
- The agent tries to install dotnet via `apt-get install dotnet` — the package name and channel in Debian repos differ and may install outdated versions.

**Phase to address:** Setup chapter (샌드박스 환경 준비), verified before the live run.

---

### Pitfall 6: FsLexYacc — Operator Precedence Absent or Wrong → `2+3*4` Returns 20 Instead of 14

**What goes wrong:**
The target output `2+3*4 → 14` requires correct operator precedence (multiplication before addition). Without explicit `%left` / `%right` declarations in the `.fsy` grammar, fsyacc's LALR parser resolves the shift-reduce conflict arbitrarily (or right-to-left by default), producing `2+(3*4) = 14` by accident — or `(2+3)*4 = 20` depending on rule ordering. An AI agent without FsYacc expertise is likely to write a grammar that looks correct but lacks precedence declarations entirely.

**Why it happens:**
- The agent's training data includes YACC/Bison examples that may not show `%left` syntax for fsyacc specifically.
- fsyacc's `%left` declarations are order-sensitive: operators declared on *later* lines have *higher* precedence. Agents often get this backwards.
- fsyacc has a known bug (issue #39): `%nonassoc` handling is broken; `%left`/`%right` must be used instead.

**How to avoid:**
The minimal correct precedence block for a `+` `-` `*` `/` calculator:
```fsharp
%left PLUS MINUS        (* lower precedence — declared first *)
%left TIMES DIVIDE      (* higher precedence — declared second *)
```
Unary minus needs a named precedence level:
```fsharp
%nonassoc UMINUS        (* if fsyacc #39 is fixed; otherwise use %right *)
```
and the rule must use `%prec UMINUS`:
```fsharp
| MINUS expr %prec UMINUS { Neg $2 }
```
- Give the agent the exact precedence block in the initial prompt, or review the generated `.fsy` file before running `dotnet build`.
- Verify with a test: `2+3*4` must return 14, `2*3+4` must return 10. Add these as explicit `printf` checks in Program.fs.
- In the tutorial: explain why the `%left` order matters — this is a teachable grammar concept that supports the tutorial's didactic goal.

**Warning signs:**
- `dotnet build` succeeds but `2+3*4` gives 20.
- fsyacc emits "shift/reduce conflict" warnings to stdout during build without explanation of which tokens are conflicting.
- Agent's grammar has all operators on the same `%left` line or no precedence declarations at all.

**Phase to address:** F# FsLexYacc 소개 chapter (explain grammar + precendence) AND during live-run review of agent output.

---

### Pitfall 7: FsLexYacc — Generated Files Not in `.fsproj` / Wrong Compile Order

**What goes wrong:**
FsLex and FsYacc generate F# source files (`Lexer.fs`, `Parser.fs`, `Parser.fsi`) at build time from `.fsl`/`.fsy` sources. If these generated files are not declared correctly in the `.fsproj`, the build silently skips generation or fails with a "file not found" error. The compile order also matters: `Parser.fsi` and `Parser.fs` must appear before `Lexer.fs` in the `<Compile>` item list (because `Lexer.fs` does `open Parser`), and the `FsYacc` and `FsLex` `<ItemGroup>` must appear *before* the `<Compile>` group.

**Why it happens:**
- The `.fsproj` format for FsLexYacc requires both the `<PackageReference>` to `FsLexYacc` and a `<Import>` of the build targets — agents often omit the targets import.
- F# compilation is strictly ordered top-to-bottom in `.fsproj`; violating this order with generated files causes confusing errors that look like missing files even when the files exist.
- The agent cannot see the generated files until after the first successful build, creating a chicken-and-egg confusion.

**How to avoid:**
Provide the agent with a template `.fsproj` snippet that includes the exact correct structure:
```xml
<ItemGroup>
  <PackageReference Include="FsLexYacc" Version="10.*" />
</ItemGroup>
<ItemGroup>
  <FsYacc Include="Parser.fsy">
    <OtherFlags>--module Parser</OtherFlags>
  </FsYacc>
  <FsLex Include="Lexer.fsl">
    <OtherFlags>--unicode</OtherFlags>
  </FsLex>
</ItemGroup>
<ItemGroup>
  <Compile Include="Parser.fsi" />
  <Compile Include="Parser.fs" />
  <Compile Include="Lexer.fs" />
  <Compile Include="Evaluator.fs" />
  <Compile Include="Program.fs" />
</ItemGroup>
```
- The `FsLexYacc.targets` import is included automatically when using the NuGet package in SDK-style projects — verify this is not accidentally overridden.
- Run `dotnet restore` before the first `dotnet build` so the MSBuild tasks are available.

**Warning signs:**
- `FS0039: The value or constructor 'token' is not defined` in Lexer.fs — indicates `Parser.fsi` is not compiled first.
- `error MSB3073: The command "fslex.exe Lexer.fsl" exited with code 1` — FsLex task not found, missing package restore.
- `FileNotFoundException: Parser.fs` at compile time — build targets ran in wrong order.

**Phase to address:** F# FsLexYacc 소개 chapter; the agent prompt should include the template `.fsproj`.

---

### Pitfall 8: MLX Server Tool-Call Format Issues — Agent Gets Malformed Tool Responses

**What goes wrong:**
The MLX-LM server's OpenAI-compatible endpoint may return malformed or empty `tool_calls` arrays in certain edge cases, or fail to stop generation at the function-call boundary (the model continues emitting text after the tool call JSON). liteLLM parses the response and may return `None` for tool calls, causing the OpenHands agent to treat the response as a plain-text message and not execute any action — the agent effectively goes mute for a turn.

**Why it happens:**
- MLX-LM's tool-call parser depends on a per-model "chat template" that includes function-call stop tokens. If the model's tokenizer config does not have the correct template, generation does not stop at the right point.
- Issue #613 in ml-explore/mlx-lm confirms this for some models: "inference engine does not stop at the token to call the tool."
- The Qwen 3.6 35B model officially supports tool calling, but the MLX quantised version may have a different chat template than the original weights.

**How to avoid:**
- Verify tool calling *before* running the full OpenHands session: send a single tool-call request via `curl` to the MLX server and confirm `finish_reason: "tool_calls"` (the project context confirms this was already verified — document this test in the tutorial so readers can repeat it).
- Set `LLM_DROP_PARAMS=true` if the server rejects unrecognised parameters.
- If tool calls start failing mid-run, check the MLX server's stdout for generation stopping prematurely or running on past the expected end token.
- Pin the `mlx-lm` version that was tested; updates may change template handling.
- In the tutorial: note that the tool-call verification test is a prerequisite to running OpenHands, not optional.

**Warning signs:**
- OpenHands agent produces only text (thoughts) for 2+ turns with no tool calls.
- `finish_reason: "stop"` instead of `"tool_calls"` in the raw server response.
- liteLLM log shows `tool_calls: None` or `tool_calls: []`.

**Phase to address:** Setup chapter (MLX 서버 검증 단계) — tool-call smoke test required before any agent run.

---

### Pitfall 9: Context Window Overflow — Long Agent Transcript Fills Qwen's Window

**What goes wrong:**
OpenHands accumulates a growing conversation transcript (all previous actions, observations, tool results, and system prompts). For a complex F# build session with many `dotnet build` outputs (which can be verbose), the transcript can exceed the model's practical context window. OpenHands will silently condense/truncate the context. The condensed summary may lose critical state (e.g., which files have already been written), causing the agent to redo work or make contradictory edits.

**Why it happens:**
- `dotnet build` with FsLexYacc emits verbose MSBuild output; `dotnet restore` similarly. Each observation gets appended to the context.
- The Qwen 35B model on MLX may be loaded with a limited KV cache (e.g., 8K or 16K tokens) to fit in available unified memory.
- OpenHands's context condenser (introduced Nov 2025) summarises old turns, but the summary encoding for an agentic coding task may lose file content details.

**How to avoid:**
- Set `LLM_MAX_MESSAGE_CHARS=10000` (default 30000) to truncate verbose command outputs to the first 10K characters. Add `| head -100` to all `dotnet build` commands in the agent's bash invocations.
- Set the MLX server's context length explicitly (via `--max-tokens` or equivalent flag at server startup) to match what OpenHands expects.
- Keep the task scope small per session (see Pitfall 4) — shorter sessions mean shorter transcripts.
- Verify the MLX server's advertised context length: `curl http://127.0.0.1:8000/v1/models | jq '.data[].context_length'`. OpenHands uses this to set `LLM_MAX_INPUT_TOKENS`.
- For the tutorial: note that long sessions with verbose build output can cause context issues; recommend the `head` pattern.

**Warning signs:**
- OpenHands log shows `[Trimming prompt to meet context window limitations]`.
- The agent starts rewriting files it already wrote correctly earlier.
- Sudden style change in agent responses (the condenser kicked in and the agent lost its earlier working plan).

**Phase to address:** OpenHands 아키텍처 chapter (context window explanation) AND live-run chapter (practical mitigation tips).

---

### Pitfall 10: Tutorial Transcript Authenticity — Fabricated or Selectively Edited Output Destroys Trust

**What goes wrong:**
The tutorial's stated value is "real captured OpenHands runs." If the author edits agent output for brevity or clarity (fixes typos in agent thoughts, shortens verbose tool outputs, invents a cleaner sequence of events), readers who follow the same steps will see different behaviour — undermining trust. Worse, if the tutorial shows a run that "just works" in N steps, readers whose local run takes 3× as long or requires an intervention will think they are doing something wrong.

**Why it happens:**
- Real runs with a 240s/call model and a local 35B are messy: the agent may backtrack, make a mistake, fix it. Authors feel pressure to present the "ideal" run.
- Long runs are hard to capture fully — there is a temptation to summarise or reconstruct rather than quote verbatim.

**How to avoid:**
- Capture full runs with timestamps before writing. Use the OpenHands UI's session export, or pipe terminal output to a log file: `docker run ... 2>&1 | tee openhands-run.log`.
- When quoting agent output in the tutorial, mark it clearly as a verbatim excerpt (use a distinct callout box style) vs. a paraphrase/summary.
- Explicitly acknowledge failure modes in the tutorial: "In our test run, the agent initially produced a grammar without precedence declarations. Here is what happened next." This is more honest and more educational.
- Include a "your run may differ" note: local LLMs are non-deterministic; the sequence of steps may vary.
- Do not re-run for cleanliness — if the real run had a 3-step mistake-and-fix, include it. That is the most valuable part of an agentic AI tutorial.
- Version-pin everything (OpenHands version, mlx-lm version, model file) so the run is repeatable.

**Warning signs:**
- Author finds themselves "lightly editing" a tool-call argument for readability.
- The tutorial narrative says "the agent then correctly wrote Parser.fsy" without showing the actual content the agent wrote.
- The final tutorial run shows no backtracking, no errors, no interventions — this is statistically implausible for a local 35B on a complex task.

**Phase to address:** Tutorial writing chapter guidance (transcript capture and citation standards).

---

### Pitfall 11: mdBook GitHub Pages — `site-url` Not Set, Assets 404 on Project Site

**What goes wrong:**
GitHub Pages project sites (as opposed to user/org sites) are served at `https://username.github.io/repo-name/`. If `book.toml` does not set `[output.html] site-url = "/repo-name/"`, mdBook generates absolute `/` paths for CSS, JS, and the 404 page. On the project subpath, these resolve to `https://username.github.io/book.css` (which 404s) instead of `https://username.github.io/repo-name/book.css`. The book's navigation works on the index page but CSS/JS fails to load.

**Why it happens:**
mdBook defaults `site-url` to `/`. This is correct for user/org sites but wrong for project sites.

**How to avoid:**
- Set in `book.toml`:
  ```toml
  [output.html]
  site-url = "/repo-name/"
  ```
  Replace `repo-name` with the actual GitHub repository name.
- Use document-relative links for all images and assets in the Markdown source (do not prefix with `/`).
- Include a `.nojekyll` file at the root of the `gh-pages` branch to prevent GitHub's Jekyll from interfering with folders starting with `_`.
- Test locally: `mdbook build && mdbook serve` at `http://localhost:3000` doesn't expose the subpath issue (it serves at root). Actually deploy to Pages to verify, or use `--dest-dir /tmp/test` and check the generated HTML for absolute paths.

**Warning signs:**
- mdBook renders correctly with `mdbook serve` locally but has broken CSS/JS after deployment.
- Browser DevTools shows 404 for `book.css` or `elasticlunr.min.js`.
- The 404 page falls back to GitHub's default 404 (not mdBook's).

**Phase to address:** mdBook 출판 chapter (GitHub Pages 배포 설정).

---

### Pitfall 12: GitHub Actions Pages Deployment — Missing Permissions Fail Silently

**What goes wrong:**
The GitHub Actions workflow deploys to Pages using the `GITHUB_TOKEN`. If the workflow does not declare `pages: write` and `id-token: write` permissions, the `actions/deploy-pages` step fails with a cryptic 403 or "resource not accessible" error. This is especially common when copying workflows from older examples that predate the new OIDC-based Pages deployment model.

**Why it happens:**
GitHub changed the Pages deployment model to use OIDC tokens. The `GITHUB_TOKEN` default permissions are read-only for most scopes. Deployment requires explicit opt-in.

**How to avoid:**
Add to the workflow YAML at the job level:
```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```
Also enable Pages in the repository settings under **Settings → Pages → Source → GitHub Actions** before the first deploy.
Use the official `actions/starter-workflows` mdBook workflow as a base — it already includes correct permissions.

**Warning signs:**
- `Error: HttpError: Resource not accessible by integration` in the Actions log.
- The Pages deployment step shows a 403 error.
- The workflow completes "successfully" but no Pages deployment appears in the environment tab.

**Phase to address:** mdBook 출판 chapter (GitHub Actions 워크플로 설정).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Copying raw OpenHands terminal output without timestamps | Faster writing | Reader cannot correlate timing to ~240s claims | Never — always include timing |
| Using `runtime_extra_deps` to install .NET (vs. custom Dockerfile) | No separate build step | Cold-start time added to every sandbox init | MVP only — switch to Dockerfile before final tutorial |
| Giving agent the entire "build the calculator" task at once | Simpler prompt | High loop/stuck probability; hard-to-caption run | Never — always decompose |
| Setting `LLM_TIMEOUT=0` (default) for "simplicity" | No config needed | Random timeouts mid-run derail the session | Never — always set to 600+ |
| Omitting `%left`/`%right` and relying on grammar rule order for precedence | Shorter grammar | Wrong results for `2+3*4`; breaks the demo goal | Never |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| MLX server → OpenHands | `LLM_BASE_URL=http://127.0.0.1:8000/v1` | `LLM_BASE_URL=http://host.docker.internal:8000/v1` |
| liteLLM model routing | `LLM_MODEL=qwen36-35b` or bare path | `LLM_MODEL=openai/<id from /v1/models>` |
| liteLLM API key | Omitting `LLM_API_KEY` entirely | `LLM_API_KEY=local` (any non-empty placeholder) |
| OpenHands sandbox + .NET | Assuming dotnet is pre-installed | Custom Dockerfile extending `nikolaik/python-nodejs` |
| FsLexYacc build targets | Declaring `<Compile>` before `<FsYacc>`/`<FsLex>` items | FsYacc/FsLex ItemGroup must precede Compile ItemGroup |
| mdBook → GitHub Pages project site | Default `site-url = "/"` | `site-url = "/repo-name/"` in `book.toml` |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Agent sends large `dotnet build` output to context | Context fills in 5–10 turns; agent forgets earlier files | `| head -100` on all build commands | After ~5 verbose build turns |
| Unbound retries with 240s model | 8 retries × 240s = 32 min wall time for one failed call | `LLM_NUM_RETRIES=2`, `LLM_RETRY_MIN_WAIT=300` | First timeout event |
| MLX server KV cache too small | Model truncates responses or hallucinates mid-answer | Set `--max-kv-size` or equivalent at MLX server startup | Requests exceeding server's configured cache |
| OpenHands Docker image pull on first run | 10+ min cold start before any agent work | Pre-pull the Docker image before tutorial recording | First run only |

---

## "Looks Done But Isn't" Checklist

- [ ] **MLX server → Docker connectivity:** Verified by running `curl http://host.docker.internal:8000/health` from *inside* a Docker container, not just from the host terminal.
- [ ] **Tool calling:** Verified by sending a test tool-call request and confirming `finish_reason: "tool_calls"` — not just `finish_reason: "stop"`.
- [ ] **Sandbox .NET:** Verified by opening an OpenHands bash session and running `dotnet --version` before the tutorial run starts.
- [ ] **Correct `2+3*4` result:** Verified by actually running `dotnet run` in the completed calculator project and confirming output is `14`, not `20`.
- [ ] **mdBook assets on deployed site:** Verified by loading the GitHub Pages URL in an incognito browser tab and checking DevTools for 404s — not just `mdbook serve` locally.
- [ ] **Tutorial verbatim excerpts:** Every agent output excerpt is traceable to a timestamped run log — no reconstructed dialogue.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong `base_url` (`127.0.0.1`) | LOW | Stop container; re-run with corrected `LLM_BASE_URL` env var |
| Wrong model name/prefix | LOW | Check `/v1/models` output; update `LLM_MODEL` and restart |
| Timeout storm | MEDIUM | Kill container; add `LLM_TIMEOUT`, `LLM_NUM_RETRIES` settings; restart |
| Agent stuck in loop | MEDIUM | Send a clarifying user message; if unresponsive, start a new session with a narrower task |
| No .NET in sandbox | MEDIUM | Build custom Dockerfile; set `SANDBOX_BASE_CONTAINER_IMAGE`; restart OpenHands |
| Wrong operator precedence | LOW | Edit `.fsy` to add `%left` lines in correct order; re-run `dotnet build` |
| Wrong compile order in `.fsproj` | LOW | Reorder `<Compile>` items; `dotnet build` again |
| mdBook 404 after deploy | LOW | Add `site-url` to `book.toml`; push and redeploy |
| GitHub Actions Pages 403 | LOW | Add `permissions` block to workflow YAML; re-run workflow |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| `127.0.0.1` vs `host.docker.internal` | Setup: OpenHands + LLM 설정 | `curl` from inside a Docker container returns HTTP 200 |
| Wrong model name / liteLLM prefix | Setup: LLM 환경변수 설정 | OpenHands UI successfully shows model name without error |
| LLM timeouts | Setup: LLM 환경변수 설정 | `LLM_TIMEOUT=600` in verified `docker run` command |
| Agent stuck in loop | Concepts: 에이전트 루프 소개 + Live run: 태스크 분해 전략 | Tutorial explicitly covers stuck states and interventions |
| No .NET in sandbox | Setup: 샌드박스 준비 | `dotnet --version` from OpenHands bash session |
| Wrong operator precedence | F# 챕터: FsLexYacc 문법 설명 | `2+3*4` returns `14` in final run |
| Wrong `.fsproj` compile order | F# 챕터: .fsproj 설정 템플릿 | `dotnet build` succeeds without FS0039 error |
| MLX tool-call format issues | Setup: MLX 서버 검증 | `finish_reason: "tool_calls"` confirmed before full run |
| Context window overflow | Concepts: 컨텍스트 윈도우 설명 | Monitor token count; `| head -100` applied to build commands |
| Fabricated transcripts | Tutorial writing process: 실행 로그 캡처 | Every excerpt traceable to timestamped `tee` log |
| mdBook site-url missing | 출판: book.toml 설정 | Live GitHub Pages URL loads without CSS 404 |
| GitHub Actions permissions | 출판: workflow.yml 설정 | Actions run shows green Pages deployment |

---

## Sources

- [OpenHands Local LLMs Docs](https://docs.openhands.dev/openhands/usage/llms/local-llms) — model prefix format, base_url, api_key requirements
- [OpenHands Environment Variables Reference](https://docs.openhands.dev/openhands/usage/environment-variables) — `LLM_TIMEOUT`, `LLM_NUM_RETRIES`, `LLM_BASE_URL`, `LLM_MODEL` full reference
- [OpenHands Custom Sandbox Guide](https://docs.openhands.dev/openhands/usage/advanced/custom-sandbox-guide) — `runtime_extra_deps`, custom Dockerfile approach
- [Issue #8318: LLM Connection Fails — UI overrides `host.docker.internal`](https://github.com/OpenHands/OpenHands/issues/8318)
- [Issue #8768: Improve timeout handling for slow local LLMs](https://github.com/OpenHands/OpenHands/issues/8768)
- [Issue #4995: Allow configuring liteLLM timeout](https://github.com/All-Hands-AI/OpenHands/issues/4995) — confirms `LLM_TIMEOUT` env var is the workaround
- [Issue #7183: AgentStuckInLoopError](https://github.com/OpenHands/OpenHands/issues/7183)
- [Issue #5480 / PR #5500: Cannot recover from AgentStuckInLoop](https://github.com/OpenHands/OpenHands/issues/5480)
- [Issue #10350: Long-running commands trigger stuck detector](https://github.com/OpenHands/OpenHands/issues/10350)
- [OpenHands Stuck Detector docs](https://docs.openhands.dev/sdk/guides/agent-stuck-detector)
- [Issue #9573: OpenHands ignores custom context window for Ollama](https://github.com/OpenHands/OpenHands/issues/9573) — context window config bugs
- [Issue #6634: Trimming prompt message passed to LLM](https://github.com/OpenHands/OpenHands/issues/6634)
- [OpenHands Context Condensation blog post (Nov 2025)](https://www.openhands.dev/blog/openhands-context-condensensation-for-more-efficient-ai-agents)
- [mlx-lm Issue #613: tool calling stops too early](https://github.com/ml-explore/mlx-lm/issues/613)
- [FsLexYacc GitHub — fsprojects/FsLexYacc](https://github.com/fsprojects/FsLexYacc)
- [FsLexYacc Issue #39: %nonassoc not handled correctly](https://github.com/fsprojects/FsLexYacc/issues/39)
- [Using FSLexYacc tutorial — thanos.codes](https://thanos.codes/blog/using-fslexyacc-the-fsharp-lexer-and-parser/) — .fsproj structure, compile order, namespace coupling
- [Fixing Grammar Ambiguities (yacc precedence)](https://journal.stuffwithstuff.com/2008/12/28/fixing-ambiguities-in-yacc/) — %left/%right ordering principle
- [mdBook Renderers docs — site-url](https://rust-lang.github.io/mdBook/format/configuration/renderers.html)
- [GitHub Actions starter workflow for mdBook](https://github.com/actions/starter-workflows/blob/main/pages/mdbook.yml)
- [actions/deploy-pages — id-token: write requirement](https://github.com/actions/deploy-pages)
- [Issue #12229: agent containers cannot resolve host.docker.internal](https://github.com/OpenHands/OpenHands/issues/12229)

---
*Pitfalls research for: Korean mdBook tutorial — OpenHands + local Qwen 35B MLX + F# FsLexYacc calculator*
*Researched: 2026-05-27*
