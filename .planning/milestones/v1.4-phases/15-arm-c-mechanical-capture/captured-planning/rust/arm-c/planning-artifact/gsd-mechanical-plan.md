# Arm C (mechanical) — code-free conversion of the GSD plan

> The mechanical, **code-free** strip of the GSD-generated plan
> (`../01-PLAN.md` + `../RESEARCH.md`) into a single-session OH prompt that respects the
> study's *unaided discipline* (the 35B writes all source itself).
> Analogous to Arm A's `claude-plan.md`. Created 2026-06-04.

---

## 0. Status (honesty label)

**Candidate study arm — NOT yet captured.** This is a planning artifact only. It has not
been run on the 35B; there are no execution metrics here. If promoted to a real arm it
would move into a `captured-planning/.../arm-c/` tree and be run under the same conditions
as Arm A/B.

---

## 1. What this is and why it exists

The original GSD plan (`../01-PLAN.md`, Task 2) **embeds the full ~25-line Rust reference
implementation**. Fed to the 35B verbatim, that would let the model copy-paste the answer —
which **invalidates the study** (the independent variable is whether an expert *plan* helps
the 35B *write/execute*, not whether it can copy code). See `../../planning-process-comparison.md` §3.

This artifact converts that GSD plan into a form usable as a real study arm:
**all source code and copy-pasteable answers removed, but GSD's research-derived failure-mode
guidance kept as prose.** That makes Arm C a distinct, informative condition:

```
Arm A         = expert plan, structure only          (minimal; no pitfalls)
Arm C (mech)  = expert plan + pitfall/protocol guidance, still code-free   ← THIS
Arm B         = 35B self-plan                         (no expert plan)
Arm C (orig)  = expert plan + full source             (study-invalid: spoon-feeds answer)
```

Arm C (mech) tests: **does telling the 35B about the known failure modes — without giving
it code — help it write correct Rust itself?**

---

## 2. Conversion rules (mechanical strip)

### REMOVED (would break the unaided discipline)
- ❌ The entire Rust reference implementation (Task 2 code block).
- ❌ The literal "exact response bytes" answer string
  (`HTTP/1.1 200 OK\r\nContent-Length: 6\r\n...`) — that is the answer in non-Rust form.
- ❌ Rust API names that hand over the solution: `TcpListener::bind`, `listener.incoming()`,
  `BufReader`, `read_line`, `write_all`, `format!`, etc. The 35B must choose these itself.
- ❌ The literal `Content-Length: 6` — replaced with "a Content-Length matching the body's
  byte length" so the model must count the bytes itself.
- ❌ GSD-executor machinery (frontmatter, `must_haves`, `key_links`, grep-pattern verifies).

### KEPT (this is what distinguishes Arm C-mech from Arm A)
- ✅ GSD's 3-task structure: scaffold / write-server / build-test.
- ✅ The **scope insight** ("respond to ANY request identically → do NOT build parsing,
  routing, threading"). Expressed as guidance, not code.
- ✅ All 5 research pitfalls, rephrased as **HTTP-protocol requirements and failure-mode
  warnings** (curl-hang framing, EOF-deadlock read, CRLF in headers, bind-once, loop must
  survive a bad connection) — protocol facts, not Rust source.
- ✅ The "honest failure > fabricated success" discipline (already in the control block).

### TRANSFORMED (code → behavioral requirement)
| GSD plan (with code) | Arm C-mech (code-free) |
|---|---|
| `write_all("HTTP/1.1 200 OK\r\n…")` | "well-formed HTTP/1.1: status line, headers, blank line, body; header lines end with CRLF" |
| `Content-Length: {}, body.len()` | "a Content-Length header whose value equals the body's byte length" |
| `read_line` / "don't `read_to_end`" | "do not read the request to EOF — it deadlocks; read only enough to proceed" |
| `for stream in listener.incoming()` | "bind once before the loop; the accept loop must never exit on its own" |
| `if let Err(e) = … eprintln!` | "must survive a single bad connection (one IO error must not kill the server)" |

---

## 3. GSD task → Arm C-mech step mapping

| GSD `01-PLAN.md` task | Arm C-mech step | Code stripped? |
|---|---|---|
| Task 1 — Scaffold (`cargo init`, empty deps) | Step 1 — Scaffold | n/a (no code) |
| Task 2 — Implement (full reference impl) | Step 2 — Write server | ✅ all code → requirements/warnings |
| Task 3 — Acceptance test (scripted curl) | Step 3 — Build and test | kept the shell test (it's the canonical test, allowed) |

Note Step 3 keeps the curl/build shell commands: those are the **acceptance test**, which is
shared by all arms (it lives in the control block too). The test is not "the answer" — it's
how every arm is judged.

---

## 4. How it differs from Arm A (the research point)

| | Arm A | Arm C (mech) |
|---|---|---|
| Origin | mechanical port of v1.2 decomposition | mechanical strip of GSD research+plan |
| Pitfall guidance | none (structure only) | **5 failure modes stated as requirements** |
| Scope-skip hint | implicit | explicit ("don't build parsing/routing/threading") |
| Source code | none | none |
| Control block | study canonical | **byte-identical** (proven, see `PROMPT-DIFF.txt`) |

→ Arm A vs Arm C-mech isolates a clean sub-variable: **the value of failure-mode foresight**
in an expert plan, holding "code-free" constant. (Original Arm A pilot showed the 35B
self-correcting on a multi-command rejection; Arm C-mech would pre-warn some such frictions
without handing over code.)

---

## 5. Artifacts

| File | What |
|---|---|
| `oh-prompt.txt` | the single-session OH prompt (control block + code-free steps) — the runnable artifact |
| `PROMPT-DIFF.txt` | symmetry evidence: control block byte-identical to study canonical → `CONTROL-BLOCK SYMMETRY: PASS` |
| `gsd-mechanical-plan.md` | this conversion record |
| `../01-PLAN.md`, `../RESEARCH.md` | the GSD source this was stripped from |

---

## 6. One sentence

> Arm C (mech) is the GSD plan with **the answer removed but the expertise kept**: no Rust
> source, no literal response bytes, no API names — only the research-derived failure modes
> restated as HTTP requirements the 35B must satisfy by writing its own code, over a control
> block proven byte-identical to Arm A/B.
