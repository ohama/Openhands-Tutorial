# Stack Research

**Domain:** Korean-language mdBook tutorial teaching Agentic AI via OpenHands (local Qwen LLM), worked example = F# FsLex/FsYacc calculator
**Researched:** 2026-05-27
**Confidence:** MEDIUM-HIGH overall (details per layer below)

---

## Layer 1: Tutorial Authoring & Publishing (mdBook + GitHub Pages)

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| mdBook | 0.5.3 | Static site generator — turns Markdown chapters into a navigable HTML book | The project-standard tool; author has the `mdbook` skill configured. Rust-native, zero JS framework overhead, excellent GitHub Pages story. |
| GitHub Actions | N/A (cloud) | CI: build mdBook and deploy to Pages on every push | Free for public repos; tight integration with Pages; fully declarative via workflow YAML. |
| GitHub Pages | N/A (hosted) | Hosting for the published tutorial | Free static hosting; pairs perfectly with Actions-based mdBook deploys. |

### Installation on macOS (Apple Silicon)

```bash
# Option A — Homebrew (simplest, no Rust required)
brew install mdbook          # installs 0.5.3 as of May 2026

# Option B — Cargo (always gets latest)
cargo install mdbook         # requires Rust >= 1.88 (rustup install stable)
```

Homebrew is recommended for local authoring because it requires no Rust toolchain; Cargo is useful if you need a cutting-edge pre-release.

### Essential Commands

```bash
mdbook init my-book          # scaffold: book.toml + src/SUMMARY.md + src/chapter_1.md
mdbook serve                 # live-reload dev server at http://localhost:3000
mdbook build                 # produce book/ directory for deployment
```

### GitHub Pages Deployment (GitHub Actions)

Use the modern "GitHub Actions" Pages deploy method (Settings → Pages → Source = "GitHub Actions"), NOT the legacy `gh-pages` branch approach.

Create `.github/workflows/deploy.yml`:

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

**Configuration tip:** Set `output.html.site-url` in `book.toml` to your GitHub Pages URL so relative links work correctly.

### What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `gh-pages` branch approach | Deprecated in favour of Actions-native deploy; requires extra push permissions and manual worktree management | `actions/deploy-pages@v4` (direct artifact deploy) |
| `peaceiris/actions-mdbook` third-party action | Adds an unmaintained dependency for something the install-from-release-URL pattern does cleanly | Direct binary download in workflow |
| Netlify / Vercel | Adds unnecessary account dependency when GitHub Pages is free and native | GitHub Pages |

**Confidence: HIGH** — Official mdBook docs, GitHub wiki, and Homebrew formula all consistent.

---

## Layer 2: OpenHands (Agentic AI Runtime)

### Current Version

**OpenHands 1.7** (released 2026-05-01). Docker image: `docker.openhands.dev/openhands/openhands:1.7`. Agent-server image: `ghcr.io/openhands/agent-server:1.19.1-python`.

### Recommended Install Method on macOS (Apple Silicon)

**Use `uv tool install` + `openhands serve` (GUI mode). This is the recommended non-Docker path, but Docker Desktop must still be running in the background** because OpenHands spawns agent sandboxes as containers.

```bash
# 1. Install uv (if not already present)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install OpenHands (Python 3.12 required)
uv tool install openhands --python 3.12

# 3. Launch GUI on http://localhost:3000
openhands serve
```

**Why `uv` over raw Docker:** The `openhands serve` path is documented as the "easiest way to start" and avoids writing/maintaining the full `docker run` invocation manually. Docker Desktop must still be running; OpenHands will pull agent-server images automatically.

**macOS Docker Desktop prerequisite:** Enable `Settings > Advanced > Allow the default Docker socket to be used` — required so OpenHands can spawn sandbox containers.

**Alternative — raw Docker (useful for scripting or CI):**

```bash
docker run -it --rm --pull=always \
  -e AGENT_SERVER_IMAGE_REPOSITORY=ghcr.io/openhands/agent-server \
  -e AGENT_SERVER_IMAGE_TAG=1.19.1-python \
  -e LOG_ALL_EVENTS=true \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands:/.openhands \
  -p 3000:3000 \
  --add-host host.docker.internal:host-gateway \
  --name openhands-app \
  docker.openhands.dev/openhands/openhands:1.7
```

### Connecting OpenHands to the Local Qwen Endpoint

OpenHands uses **LiteLLM** under the hood for all LLM calls. LiteLLM determines the provider and routing from the model string prefix.

#### Critical: `host.docker.internal` for Docker ↔ Host Communication

Because OpenHands sandboxes run inside Docker containers, they cannot reach `localhost` or `127.0.0.1` on the host. Use the Docker-internal hostname `host.docker.internal` to resolve the host machine's IP from within a container.

The local MLX server is at `http://127.0.0.1:8000/v1` on the host. From within Docker this becomes:

```
http://host.docker.internal:8000/v1
```

#### Exact LLM Configuration

Configure via the OpenHands web UI at `http://localhost:3000` → gear icon → LLM tab → Advanced toggle:

| Field | Value | Notes |
|-------|-------|-------|
| **LLM Provider** | (leave as Custom / OpenAI-compatible) | |
| **Custom Model** | `openai/qwen36-35b` | `openai/` prefix tells LiteLLM to use the OpenAI chat-completions format. The part after the slash is the model name as returned by the server's `/v1/models` endpoint — verify with `curl http://127.0.0.1:8000/v1/models`. If the server advertises the full path `/Users/ohama/llm-system/models/qwen36-35b`, use that exact string after `openai/`. |
| **Base URL** | `http://host.docker.internal:8000/v1` | Do NOT use `localhost` or `127.0.0.1` — those resolve inside the Docker container, not to the host. |
| **API Key** | `dummy` (any non-empty string) | The MLX server does not require authentication; LiteLLM still requires a non-empty key field. |

#### Equivalent `agent_settings.json` (config file approach)

Settings are persisted at `~/.openhands/agent_settings.json`. You can pre-populate this file:

```json
{
  "llm": {
    "model": "openai/qwen36-35b",
    "api_key": "dummy",
    "base_url": "http://host.docker.internal:8000/v1"
  }
}
```

#### Equivalent environment-variable override (CLI approach)

```bash
export LLM_MODEL="openai/qwen36-35b"
export LLM_API_KEY="dummy"
export LLM_BASE_URL="http://host.docker.internal:8000/v1"
openhands --override-with-envs
```

Note: `--override-with-envs` applies env vars as a one-time override; they are NOT persisted to the settings file.

#### `config.toml` [llm] section (development / self-hosted mode)

If running from source (`make run`):

```toml
[llm]
model = "openai/qwen36-35b"
api_key = "dummy"
base_url = "http://localhost:8000/v1"   # no Docker; direct host access
timeout = 300
num_retries = 3
retry_min_wait = 10
retry_max_wait = 60
```

### Tool/Function Calling Notes

- The local MLX Qwen server has been verified to return `finish_reason: "tool_calls"` — it is compatible with OpenHands' tool-calling requirements.
- OpenHands relies heavily on tool calling for its agent loop. Models that fall back to text-based tool simulation will break the loop. The Qwen 3.6 35B is confirmed working.
- The 35B model is SLOW on local hardware (~240 s per tool-call round trip). OpenHands has default timeouts that are too short for this. Set `timeout = 300` (5 min) or higher in config.

### Apple Silicon Caveats

- OpenHands Docker images are built for `linux/amd64`. On Apple Silicon, Docker Desktop uses Rosetta 2 emulation. This works for the main `openhands` container but may cause issues with browser automation tasks (Puppeteer/Chrome inside sandbox). For this tutorial (F# file manipulation only, no browser tasks), Rosetta emulation is acceptable.
- The MLX server runs natively on Apple GPU — it is NOT inside Docker, so architecture is not an issue there.
- Known issue (GitHub #3902, closed/stale): Puppeteer fails under Rosetta. Not relevant for this project.

### What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `localhost` / `127.0.0.1` as base_url when using Docker | Resolves inside the container, not the host | `host.docker.internal:8000` |
| Model string without `openai/` prefix | LiteLLM won't know which provider adapter to use; will likely error or fall back to cloud OpenAI | Prefix with `openai/` |
| Default timeout (60 s) | Too short for 35B local inference (~240 s per request) | Set `timeout = 300` or longer |
| Cloud LLM APIs | Out of scope; tutorial is local-only | Local MLX endpoint |

**Confidence: MEDIUM** — Core Docker/uvx install path and LiteLLM `openai/` prefix are well-documented. The exact model ID string (what the MLX server advertises after `openai/`) must be verified at runtime with `curl http://127.0.0.1:8000/v1/models`. The `agent_settings.json` key names are inferred from community sources and CLI help; the official config reference page returned 404 during research.

---

## Layer 3: F# / FsLex / FsYacc (Example Project Stack)

### Current Version Landscape (May 2026)

| Technology | Version | Notes |
|------------|---------|-------|
| .NET SDK | **10.0.300** (LTS, released 2026-05-12) | LTS release (supported until Nov 2028); includes F# 10.0, C# 14. macOS ARM64 (Apple Silicon) installer available. |
| F# | **10.0** | Ships with .NET 10 SDK; no separate install needed. |
| FsLexYacc NuGet | **11.3.0** (released 2024-04-08) | Latest stable; targets .NET Standard 2.0 (compatible with net10.0 projects). |
| FsLexYacc.Runtime | **11.3.0** | Auto-dependency of FsLexYacc; provides runtime support for generated lexers/parsers. |

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| .NET SDK | 10.0.300 | Build host for F# projects; provides `dotnet new`, `dotnet build`, `dotnet run` | LTS = 3-year support; Apple Silicon native ARM64; F# 10 included. |
| FsLexYacc | 11.3.0 | Lexer (`fslex`) + parser (`fsyacc`) generators; produces F# code from `.fsl`/`.fsy` files | The canonical, actively maintained F# lex/yacc toolchain; MSBuild-integrated so `dotnet build` drives everything. |
| FsLexYacc.Runtime | 11.3.0 | Runtime library consumed by generated lexer/parser code | Auto-referenced via FsLexYacc package dependency. |

### Installation on macOS (Apple Silicon)

```bash
# Download and run the .NET 10 installer for macOS ARM64
# https://dotnet.microsoft.com/en-us/download/dotnet/10.0
# or via official script:
curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 10.0
```

Verify:
```bash
dotnet --version   # should print 10.0.300 or later
```

### Minimal F# FsLex/FsYacc Calculator Project Layout

```
Calculator/
├── Calculator.fsproj
├── Lexer.fsl          ← FsLex grammar (tokens: INT, PLUS, MINUS, STAR, SLASH, LPAREN, RPAREN, EOF)
├── Parser.fsy         ← FsYacc grammar (arithmetic expression rules → AST or int)
├── Ast.fs             ← (optional) AST type definitions
└── Program.fs         ← entry point: reads input, calls Lexer → Parser → prints result
```

### .fsproj Wiring

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <!-- FsYacc processes Parser.fsy → Parser.fsi + Parser.fs before compile -->
    <FsYacc Include="Parser.fsy">
      <OtherFlags>--module Parser</OtherFlags>
    </FsYacc>
    <!-- FsLex processes Lexer.fsl → Lexer.fs before compile -->
    <FsLex Include="Lexer.fsl">
      <OtherFlags>--module Lexer --unicode</OtherFlags>
    </FsLex>

    <!-- Compile order: generated interfaces/impls before entry point -->
    <Compile Include="Ast.fs" />
    <Compile Include="Parser.fsi" />   <!-- generated by FsYacc -->
    <Compile Include="Parser.fs" />    <!-- generated by FsYacc -->
    <Compile Include="Lexer.fs" />     <!-- generated by FsLex  -->
    <Compile Include="Program.fs" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="FsLexYacc" Version="11.3.0" />
  </ItemGroup>

</Project>
```

**Important:** The FsLexYacc NuGet package injects MSBuild targets that automatically run `fslex`/`fsyacc` on `.fsl`/`.fsy` files before the F# compiler runs. No separate pre-build step is needed.

### Build & Run Commands

```bash
dotnet new console -lang F# -o Calculator   # scaffold
cd Calculator
dotnet add package FsLexYacc               # adds 11.3.0
dotnet build                               # runs fslex + fsyacc, then fsc
dotnet run                                 # runs the calculator
```

Expected interaction (arithmetic input → integer result):
```
> 2+3*4
14
> (1+2)*-3
-9
```

### Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| FsLexYacc 11.3.0 | FSharp.Core >= 4.6.2 | F# 10 (FSharp.Core 9.x) is compatible |
| FsLexYacc 11.3.0 | .NET Standard 2.0 targets | Works with net10.0 projects via Standard 2.0 shim |
| dotnet SDK 10.0 | macOS ARM64 | Native Apple Silicon support, no Rosetta needed |

### What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `dotnet fsi` (F# Interactive) for the calculator | FsLex/FsYacc produce compiled F# source, not script-friendly; fsi would require manual pre-running the generators | `dotnet build` + `dotnet run` |
| FsLexYacc < 11 | Older versions lack modern .fsproj MSBuild integration; required manual pre-build steps | 11.3.0 |
| FParsec (parser combinator library) | Different paradigm — no lexer/grammar file; not what the tutorial demonstrates | FsLexYacc (grammar-file approach is the tutorial's subject) |
| .NET 8 LTS | Still supported but .NET 10 is now the newer LTS; no reason to use an older version for a greenfield project | .NET 10 (SDK 10.0.300) |

**Confidence: HIGH** — NuGet.org confirms 11.3.0 is current; .NET 10 release confirmed by Microsoft; .fsproj wiring verified against official FsLexYacc docs and community tutorials.

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Tutorial format | mdBook | Docusaurus, MkDocs, VuePress | mdBook is the skill-configured choice; simpler Rust-native build; no Node.js dependency. |
| mdBook deploy | `actions/deploy-pages@v4` (native Pages) | `peaceiris/actions-gh-pages` (gh-pages branch) | Native Pages deploy is the current GitHub recommendation; fewer moving parts. |
| OpenHands install | `uv tool install openhands` + `openhands serve` | Raw `docker run` | `openhands serve` is the officially documented "easiest" path; auto-handles image pulls. |
| LLM endpoint prefix | `openai/` | `hosted_vllm/` | `openai/` is the generic OpenAI-compatible adapter in LiteLLM and confirmed correct for custom base_url endpoints. `hosted_vllm/` is vLLM-specific and would not apply to an MLX server. |
| F# build tool | `dotnet build` (MSBuild via SDK) | `dotnet fsi` / standalone fslex/fsyacc CLIs | MSBuild integration in FsLexYacc 11 makes `dotnet build` drive everything declaratively. |
| F# .NET target | net10.0 | net8.0 | .NET 10 is current LTS; no reason to target older. |

---

## Version Compatibility Matrix

| Component | Version | Requires | Notes |
|-----------|---------|---------|-------|
| mdBook | 0.5.3 | Rust >= 1.88 (only if building from source; brew/binary: none) | |
| OpenHands | 1.7 | Docker Desktop (daemon); Python 3.12 (for uv install) | |
| Agent-server image | 1.19.1-python | Docker | Pulled automatically |
| .NET SDK | 10.0.300 | macOS 13+ on ARM64 | |
| F# | 10.0 | .NET SDK 10 | Bundled |
| FsLexYacc | 11.3.0 | FSharp.Core >= 4.6.2; .NET Standard 2.0 | |

---

## Sources

- **mdBook Homebrew formula** — `https://formulae.brew.sh/formula/mdbook` — version 0.5.3 confirmed (HIGH)
- **mdBook GitHub Releases** — `https://github.com/rust-lang/mdBook/releases/latest` — v0.5.3, released 2026-05-19 (HIGH)
- **mdBook Automated Deployment wiki** — `https://github.com/rust-lang/mdBook/wiki/Automated-Deployment:-GitHub-Actions` — workflow YAML pattern (HIGH)
- **OpenHands GitHub** — `https://github.com/OpenHands/OpenHands` — version 1.7, released 2026-05-01 (HIGH)
- **OpenHands Local Setup docs** — `https://docs.openhands.dev/openhands/usage/run-openhands/local-setup` — Docker command, uvx install, macOS socket setting (HIGH)
- **OpenHands Local LLMs docs** — `https://docs.openhands.dev/openhands/usage/llms/local-llms` — `openai/` prefix, `host.docker.internal`, api_key placeholder (HIGH)
- **OpenHands CLI quickstart (glukhov.org)** — `https://www.glukhov.org/ai-devtools/openhands/` — `agent_settings.json` path, env var names, CLI flags (MEDIUM — community source)
- **LiteLLM OpenAI-compatible providers** — `https://docs.litellm.ai/docs/providers/openai_compatible` — `openai/` prefix confirmed, base_url `/v1` convention (HIGH)
- **NuGet FsLexYacc 11.3.0** — `https://www.nuget.org/packages/FsLexYacc/` — version, release date, dependencies (HIGH)
- **FsLexYacc official docs (fslex)** — `https://fsprojects.github.io/FsLexYacc/content/fslex.html` — .fsproj ItemGroup configuration (HIGH)
- **FsLexYacc official docs (fsyacc)** — `https://github.com/fsprojects/FsLexYacc/blob/master/docs/content/fsyacc.md` — grammar example, .fsy structure (HIGH)
- **thanos.codes FsLexYacc tutorial** — `https://thanos.codes/blog/using-fslexyacc-the-fsharp-lexer-and-parser/` — .fsproj wiring, calculator example (MEDIUM — community)
- **.NET 10 download page** — `https://dotnet.microsoft.com/en-us/download/dotnet/10.0` — SDK 10.0.300 ARM64, released 2026-05-12 (HIGH)

---
*Stack research for: mdBook tutorial + OpenHands local LLM + F# FsLex/FsYacc calculator*
*Researched: 2026-05-27*
