# Architecture Research — v1.4 Planning Comparison Harness

**Domain:** A/B comparison harness for task-planning regimes on the local 35B, integrated with the existing OpenHands headless capture pipeline
**Researched:** 2026-06-01
**Confidence:** HIGH (grounded in real captured JSONL artifacts from v1.2/v1.3; real schema confirmed by inspection; pipeline pattern confirmed across 4 prior milestones)

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          v1.4 HARNESS LAYER                             │
│                                                                         │
│  ┌────────────────────────────┐  ┌────────────────────────────────────┐ │
│  │      ARM A                 │  │      ARM B                         │ │
│  │  Claude task plan          │  │  Single-goal prompt                │ │
│  │  → converted to OH prompt  │  │  → OpenHands self-plans+executes   │ │
│  │  → OH executes             │  │                                    │ │
│  └────────────┬───────────────┘  └──────────────┬─────────────────────┘ │
│               │                                 │                       │
│               └──────────────┬──────────────────┘                       │
│                              ▼                                          │
│            OpenHands headless invocation (REUSED FROM v1.2/v1.3)       │
│            OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL="openai/qwen-35b"     │
│            openhands --headless --json --yolo --override-with-envs      │
│            -t "$(cat prompt.txt)"  | tee <arm>-<example>.jsonl          │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                      CAPTURE LAYER (REUSED)                             │
│                                                                         │
│   per-example, per-arm JSONL tee'd to oh-workdir-planning/<arm>/        │
│   → honesty gate (source=agent on every ActionEvent)                    │
│   → metrics extractor (python3, extended from v1.3 extractor)           │
│   → captured-planning/<example>/<arm>/ committed artifact tree          │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                      ANALYSIS LAYER                                     │
│                                                                         │
│   per_arm_metrics.json  ─→  comparison_table.json  ─→  부록 D chapter  │
│   (per example, per arm)    (example × arm × metric)  (verbatim from   │
│                                                          captured data) │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|---------------|----------------|
| Arm A prompt builder | Turn a Claude task decomposition into a single OpenHands-consumable prompt | Plain text file: Claude's numbered task plan + context, formatted as a single `-t` string |
| Arm B prompt builder | A single-goal prompt giving OpenHands the full goal with no pre-decomposition | Plain text file: "Build X. Plan and execute all steps yourself." |
| Headless invocation | Run the 35B on a single prompt, capture JSONL | Reused verbatim from v1.2/v1.3 (same env vars, `--headless --json --yolo --override-with-envs`) |
| JSONL tee pipeline | Capture JSONL to disk in real time | `| tee oh-workdir-planning/<arm>-<example>.jsonl` |
| Honesty gate | Assert source=agent on every ActionEvent before commit | Reused verbatim from v1.3 10-03-PLAN.md Task 1 |
| Metrics extractor | Parse JSONL → per-arm metrics record | python3 script (extended from existing poll/status pattern) |
| Comparison table builder | Combine per-arm records across all examples → one renderable table | python3 or jq, output as JSON/Markdown |
| captured-planning/ layout | Committed artifact tree for the whole study | New directory parallel to captured-rust/, captured-scala/ |
| 부록 D chapter | Korean Markdown written verbatim from the captured data | mdBook source file, wired into src/SUMMARY.md after 부록 C |

---

## Artifact Layout: `captured-planning/`

This tree is the v1.4 analog of `captured-rust/` and `captured-scala/`. It is committed once the capture gate closes (parallel to how 10-03 commits `captured-scala/`).

```
.planning/milestones/v1.4-phases/
└── 12-planning-comparison-harness/
    ├── captured-planning/
    │   ├── CAPTURE-MANIFEST.md          # top-level manifest: study design, both arms, all 3 examples
    │   │
    │   ├── fsharp/                      # F# calculator example
    │   │   ├── arm-a/
    │   │   │   ├── logs/
    │   │   │   │   └── run.jsonl        # the one OH invocation for Arm A (or multiple if multi-task)
    │   │   │   ├── planning-artifact/
    │   │   │   │   ├── claude-plan.md   # Claude's task decomposition (the input)
    │   │   │   │   └── oh-prompt.txt    # the converted prompt fed to OH
    │   │   │   ├── final-source/        # agent-written source files
    │   │   │   ├── test-output.txt      # fresh host canonical test re-run
    │   │   │   └── metrics.json         # per-arm metrics record (see schema below)
    │   │   ├── arm-b/
    │   │   │   ├── logs/
    │   │   │   │   └── run.jsonl        # OH invocation for Arm B (single prompt)
    │   │   │   ├── planning-artifact/
    │   │   │   │   ├── oh-goal-prompt.txt  # the single-goal prompt fed to OH
    │   │   │   │   └── oh-self-plan.md     # extracted from the JSONL: what OH actually planned
    │   │   │   ├── final-source/
    │   │   │   ├── test-output.txt
    │   │   │   └── metrics.json
    │   │   └── comparison.json          # per-example comparison (arm-a vs arm-b on all metrics)
    │   │
    │   ├── rust/                        # Rust HTTP server example
    │   │   ├── arm-a/ ...               # same structure as fsharp/arm-a/
    │   │   ├── arm-b/ ...
    │   │   └── comparison.json
    │   │
    │   └── scala/                       # Scala calculator example
    │       ├── arm-a/ ...
    │       ├── arm-b/ ...
    │       └── comparison.json
    │
    ├── task-prompts/
    │   ├── arm-a/
    │   │   ├── fsharp-oh-prompt.txt     # converted Claude plan → OH prompt
    │   │   ├── rust-oh-prompt.txt
    │   │   └── scala-oh-prompt.txt
    │   └── arm-b/
    │       ├── fsharp-goal-prompt.txt   # single-goal "plan and execute" prompts
    │       ├── rust-goal-prompt.txt
    │       └── scala-goal-prompt.txt
    │
    └── 12-01-PLAN.md / 12-02-PLAN.md / 12-03-PLAN.md
        (planning phase plans)
```

### oh-workdir-planning/ (gitignored scratch)

```
oh-workdir-planning/         # gitignored; ephemeral captures
├── arm-a/
│   ├── fsharp-run.jsonl
│   ├── fsharp-run.stderr.log
│   ├── rust-run.jsonl
│   ├── rust-run.stderr.log
│   ├── scala-run.jsonl
│   └── scala-run.stderr.log
└── arm-b/
    ├── fsharp-run.jsonl
    ├── fsharp-run.stderr.log
    ├── rust-run.jsonl
    ├── rust-run.stderr.log
    ├── scala-run.jsonl
    └── scala-run.stderr.log
```

The `.gitignore` entry `oh-workdir-planning/` is added in Phase 12 preflight, parallel to the `oh-workdir-scala/` entry added in Phase 10 preflight.

---

## The Claude-Plan → OpenHands-Plan Converter (Arm A)

### The core insight

OpenHands has no native "plan file" format. The headless CLI accepts a single task string via `-t`. There is no built-in planning artifact format, no "task list" input, no multi-step orchestration beyond the agent's own reasoning within a single session. This was confirmed by inspecting the existing invocation pattern (all five prior milestones use one `-t` string per OpenHands invocation) and the real JSONL schema (a single MessageEvent with `source=user` at the start of every task capture).

**Conclusion for Arm A:** "Convert a Claude plan into an OpenHands plan" means: take Claude's numbered task decomposition and reformat it as a single comprehensive task string that instructs the agent to carry out all the steps, with the full context embedded. The agent then self-sequences within one session. This is the fairest interpretation because:
- It respects OpenHands' actual architecture (one session = one prompt)
- It preserves what Claude planned while letting OpenHands execute
- Arm B differs only in that OpenHands sees only the goal, not the pre-decomposition

### Conversion pipeline

```
Claude task plan (claude-plan.md)
    │
    ▼
Converter (manual transform; ~10 min per example)
    │   Rules:
    │   1. Preserve all task names and their success criteria verbatim
    │   2. Write as imperative instructions: "First, scaffold the project..."
    │   3. Include the IMPORTANT: bash-only constraint (same as existing task prompts)
    │   4. Include the working directory and toolchain version context
    │   5. Include the canonical test inputs/expected outputs
    │   6. Do NOT include scaffolded source code (that would violate the unaided discipline)
    │
    ▼
oh-prompt.txt (the Arm A input to OpenHands)
    │
    ▼
openhands --headless --json --yolo --override-with-envs -t "$(cat oh-prompt.txt)"
    | tee oh-workdir-planning/arm-a/<example>-run.jsonl
```

### What the Arm A prompt looks like

```
You are working in /path/to/oh-workdir-planning/arm-a/.

IMPORTANT: Use only bash terminal commands (cat >, printf, heredoc) to write files.
Do NOT use the file_editor tool.

Goal: Build a [project description]. Complete the following steps in order:

Step 1 — [task name]: [description and success criteria from Claude's plan]
Step 2 — [task name]: [description and success criteria]
Step 3 — [task name]: [description and success criteria, including canonical tests]

Canonical tests (must pass):
  [test inputs and expected outputs, verbatim from the example's definition]

Run all steps sequentially in this one session. Do not stop until all canonical
tests pass or you have documented why they cannot be fixed.
```

### What changes Arm A vs Arm B

Arm B omits Steps 1–3 and instead says: "Plan the implementation yourself, then execute it. Do not ask for confirmation between steps."

The working directory, toolchain, IMPORTANT constraint, and canonical tests are identical between arms. The only difference is whether the task decomposition is pre-supplied (Arm A) or left to the agent (Arm B).

---

## Metrics Extractor

### JSONL Schema (confirmed from real captured files)

The real schema, confirmed by inspection of `task3-buildtest.jsonl` from the v1.3 Scala run:

| Field | Type | Notes |
|-------|------|-------|
| `kind` | str | `"MessageEvent"`, `"ActionEvent"`, `"ObservationEvent"`, `"AgentErrorEvent"`, `"ConversationErrorEvent"` |
| `source` | str | `"user"`, `"agent"`, `"environment"` |
| `timestamp` | str | ISO 8601, e.g. `"2026-06-01T14:52:18.696140"` |
| `tool_name` | str | `"terminal"`, `"file_editor"`, `""` |
| `action` | dict or None | Present on `ActionEvent`; contains `command` (str), `kind` (`"TerminalAction"`, `"FinishAction"`) |
| `observation` | dict or None | Present on `ObservationEvent`; contains `content` (list of `{type,text}` dicts), `exit_code` (int), `command` (str), `kind` (`"TerminalObservation"`) |
| `error` | str | Present on `AgentErrorEvent` |

Note: the existing poll/status-check snippets in plans 10-02/10-03 use the `kind` field at the top level and `action.kind` / `observation.kind` sub-fields, which match the real schema.

### Per-Arm Metrics Record (`metrics.json`)

```json
{
  "study": "v1.4-planning-comparison",
  "example": "fsharp",
  "arm": "arm-a",
  "run_date": "2026-06-01",
  "model": "openai/qwen-35b",
  "prompt_file": "task-prompts/arm-a/fsharp-oh-prompt.txt",

  "event_counts": {
    "total_events": 0,
    "MessageEvent": 0,
    "ActionEvent": 0,
    "ObservationEvent": 0,
    "AgentErrorEvent": 0,
    "ConversationErrorEvent": 0
  },

  "terminal_actions": {
    "count": 0,
    "list": []
  },

  "finish": {
    "has_finish_action": false,
    "has_conversation_error": false,
    "settled_by": "FinishAction | ConversationError | idle-timeout"
  },

  "timing": {
    "first_event_ts": "",
    "last_event_ts": "",
    "wall_clock_seconds": 0.0,
    "llm_call_gaps_seconds": [],
    "avg_llm_call_gap_seconds": 0.0,
    "min_llm_call_gap_seconds": 0.0,
    "max_llm_call_gap_seconds": 0.0
  },

  "error_fix_cycles": {
    "nonzero_exit_count": 0,
    "cycles": [
      {
        "error_event_index": 0,
        "error_exit_code": 0,
        "error_command_excerpt": "",
        "fix_event_index": 0,
        "fix_command_excerpt": ""
      }
    ]
  },

  "canonical_tests": {
    "fsharp": {
      "2+3*4":   {"expected": "14", "actual": null, "pass": null, "event_index": null},
      "(2+3)*4": {"expected": "20", "actual": null, "pass": null, "event_index": null},
      "10-3-2":  {"expected": "5",  "actual": null, "pass": null, "event_index": null}
    },
    "rust": {
      "curl_hello": {"expected": "hello", "actual": null, "pass": null, "event_index": null}
    },
    "scala": {
      "2+3*4":   {"expected": "14", "actual": null, "pass": null, "event_index": null},
      "(2+3)*4": {"expected": "20", "actual": null, "pass": null, "event_index": null},
      "10-3-2":  {"expected": "5",  "actual": null, "pass": null, "event_index": null}
    }
  },

  "honesty_gate": {
    "result": "PASS | FAIL",
    "total_action_events_checked": 0,
    "offending_events": []
  },

  "source_agent_ratio": 1.0
}
```

**LLM-call gap definition:** `ObservationEvent.timestamp → next ActionEvent.timestamp`. This measures pure model thinking time, excluding bash execution. Consistent with the v1.3 manifest definition.

**Error-fix cycle definition:** A cycle is a pair of (ObservationEvent with nonzero exit_code) immediately followed by a corrective ActionEvent (another TerminalAction, usually a file rewrite or sed). Cycles are extracted by scanning adjacent pairs.

### Python3 Metrics Extractor

```python
#!/usr/bin/env python3
"""
metrics_extractor.py — v1.4 per-arm metrics extractor.

Usage:
  python3 metrics_extractor.py \
      --jsonl oh-workdir-planning/arm-a/fsharp-run.jsonl \
      --example fsharp \
      --arm arm-a \
      --prompt-file task-prompts/arm-a/fsharp-oh-prompt.txt \
      --out captured-planning/fsharp/arm-a/metrics.json
"""

import json
import sys
import argparse
import datetime
import collections

def extract_text(content):
    """Extract text from a content field that may be a list of {type,text} dicts."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in content
        )
    return str(content)


def load_events(path):
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"):
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return events


def compute_metrics(events, example, arm, prompt_file):
    kind_counts = collections.Counter(e.get("kind") for e in events)

    # Terminal actions (source=agent, tool_name=terminal)
    terminal_actions = [
        e for e in events
        if e.get("kind") == "ActionEvent"
        and e.get("source") == "agent"
        and e.get("tool_name") == "terminal"
    ]

    # Finish + error signals
    has_finish = any(
        (e.get("action") or {}).get("kind") == "FinishAction"
        for e in events
    )
    has_conv_error = any(e.get("kind") == "ConversationErrorEvent" for e in events)

    # Timing
    timestamps = [e["timestamp"] for e in events if e.get("timestamp")]
    if timestamps:
        first_ts = timestamps[0]
        last_ts = timestamps[-1]
        t0 = datetime.datetime.fromisoformat(first_ts)
        t1 = datetime.datetime.fromisoformat(last_ts)
        wall = (t1 - t0).total_seconds()
    else:
        first_ts = last_ts = ""
        wall = 0.0

    # LLM call gaps: ObservationEvent → next ActionEvent
    gaps = []
    for i, e in enumerate(events):
        if e.get("kind") == "ObservationEvent" and i + 1 < len(events):
            nxt = events[i + 1]
            if nxt.get("kind") == "ActionEvent" and nxt.get("timestamp") and e.get("timestamp"):
                t_obs = datetime.datetime.fromisoformat(e["timestamp"])
                t_act = datetime.datetime.fromisoformat(nxt["timestamp"])
                gaps.append((t_act - t_obs).total_seconds())

    # Error-fix cycles: nonzero-exit ObservationEvent → next agent ActionEvent
    observation_events = [e for e in events if e.get("kind") == "ObservationEvent"]
    nonzero_exits = [
        e for e in observation_events
        if (e.get("observation") or {}).get("exit_code", 0) != 0
    ]

    cycles = []
    for err_e in nonzero_exits:
        err_idx = events.index(err_e)
        obs = err_e.get("observation") or {}
        # Look for the next agent ActionEvent after this
        for j in range(err_idx + 1, len(events)):
            nxt = events[j]
            if nxt.get("kind") == "ActionEvent" and nxt.get("source") == "agent":
                act = nxt.get("action") or {}
                cycles.append({
                    "error_event_index": err_idx,
                    "error_exit_code": obs.get("exit_code"),
                    "error_command_excerpt": extract_text(obs.get("content", ""))[:120],
                    "fix_event_index": j,
                    "fix_command_excerpt": str(act.get("command", ""))[:120],
                })
                break

    # Honesty gate: every ActionEvent must have source=agent
    bad = [
        {"event_index": i, "source": e.get("source"), "command": str((e.get("action") or {}).get("command", ""))[:80]}
        for i, e in enumerate(events)
        if e.get("kind") == "ActionEvent" and e.get("source") != "agent"
    ]
    gate_result = "PASS" if not bad else "FAIL"

    # Canonical test extraction — scan ObservationEvents for known test commands/outputs
    # (example-specific; caller passes example name for lookup)
    canonical_tests = _extract_canonical_tests(events, example)

    return {
        "study": "v1.4-planning-comparison",
        "example": example,
        "arm": arm,
        "run_date": datetime.date.today().isoformat(),
        "model": "openai/qwen-35b",
        "prompt_file": prompt_file,
        "event_counts": {
            "total_events": len(events),
            **{k: v for k, v in kind_counts.items()},
        },
        "terminal_actions": {
            "count": len(terminal_actions),
            "commands": [str((e.get("action") or {}).get("command", ""))[:120] for e in terminal_actions],
        },
        "finish": {
            "has_finish_action": has_finish,
            "has_conversation_error": has_conv_error,
            "settled_by": "FinishAction" if has_finish else ("ConversationError" if has_conv_error else "idle-timeout"),
        },
        "timing": {
            "first_event_ts": first_ts,
            "last_event_ts": last_ts,
            "wall_clock_seconds": round(wall, 2),
            "llm_call_gaps_seconds": [round(g, 3) for g in gaps],
            "avg_llm_call_gap_seconds": round(sum(gaps) / len(gaps), 2) if gaps else 0.0,
            "min_llm_call_gap_seconds": round(min(gaps), 2) if gaps else 0.0,
            "max_llm_call_gap_seconds": round(max(gaps), 2) if gaps else 0.0,
        },
        "error_fix_cycles": {
            "nonzero_exit_count": len(nonzero_exits),
            "cycle_count": len(cycles),
            "cycles": cycles,
        },
        "canonical_tests": canonical_tests,
        "honesty_gate": {
            "result": gate_result,
            "total_action_events_checked": sum(1 for e in events if e.get("kind") == "ActionEvent"),
            "offending_events": bad,
        },
        "source_agent_ratio": (
            sum(1 for e in events if e.get("kind") == "ActionEvent" and e.get("source") == "agent")
            / max(1, sum(1 for e in events if e.get("kind") == "ActionEvent"))
        ),
    }


def _extract_canonical_tests(events, example):
    """
    Scan ObservationEvents for canonical test outputs.
    Returns a dict of {test_key: {expected, actual, pass, event_index}}.
    """
    if example in ("fsharp", "scala"):
        tests = {
            "2+3*4":   {"expected": "14", "actual": None, "pass": None, "event_index": None},
            "(2+3)*4": {"expected": "20", "actual": None, "pass": None, "event_index": None},
            "10-3-2":  {"expected": "5",  "actual": None, "pass": None, "event_index": None},
        }
        for i, e in enumerate(events):
            if e.get("kind") != "ObservationEvent":
                continue
            obs = e.get("observation") or {}
            cmd = obs.get("command", "")
            content = extract_text(obs.get("content", "")).strip()
            exit_code = obs.get("exit_code", -1)
            for expr, rec in tests.items():
                if rec["actual"] is not None:
                    continue
                # Check if this observation corresponds to running this expression
                if expr in cmd or expr.replace("*", r"\*") in cmd:
                    # Extract the last non-empty line as the program output
                    lines = [l.strip() for l in content.splitlines() if l.strip()]
                    actual = lines[-1] if lines else ""
                    rec["actual"] = actual
                    rec["pass"] = (exit_code == 0 and actual == rec["expected"])
                    rec["event_index"] = i
        return tests
    elif example == "rust":
        tests = {
            "curl_hello": {"expected": "hello", "actual": None, "pass": None, "event_index": None},
        }
        for i, e in enumerate(events):
            if e.get("kind") != "ObservationEvent":
                continue
            obs = e.get("observation") or {}
            cmd = obs.get("command", "")
            content = extract_text(obs.get("content", "")).strip()
            exit_code = obs.get("exit_code", -1)
            if "curl" in cmd and tests["curl_hello"]["actual"] is None:
                actual = "hello" if "hello" in content else content[:40]
                tests["curl_hello"]["actual"] = actual
                tests["curl_hello"]["pass"] = "hello" in content and exit_code == 0
                tests["curl_hello"]["event_index"] = i
        return tests
    return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", required=True)
    parser.add_argument("--example", required=True, choices=["fsharp", "rust", "scala"])
    parser.add_argument("--arm", required=True, choices=["arm-a", "arm-b"])
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    events = load_events(args.jsonl)
    metrics = compute_metrics(events, args.example, args.arm, args.prompt_file)

    with open(args.out, "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"Metrics written to {args.out}")
    print(f"  TerminalActions: {metrics['terminal_actions']['count']}")
    print(f"  Wall clock: {metrics['timing']['wall_clock_seconds']}s")
    print(f"  LLM avg gap: {metrics['timing']['avg_llm_call_gap_seconds']}s")
    print(f"  Error-fix cycles: {metrics['error_fix_cycles']['cycle_count']}")
    print(f"  Honesty gate: {metrics['honesty_gate']['result']}")
    if args.example in ("fsharp", "scala"):
        for expr, rec in metrics["canonical_tests"].items():
            print(f"  {expr}: {rec['actual']!r} (expected {rec['expected']!r}) → {'PASS' if rec['pass'] else 'FAIL'}")


if __name__ == "__main__":
    main()
```

---

## Comparison Table Schema

### Per-Example Comparison (`comparison.json`)

```json
{
  "study": "v1.4-planning-comparison",
  "example": "fsharp",
  "run_date": "2026-06-01",
  "model": "openai/qwen-35b",

  "arm_a": {
    "metrics_file": "arm-a/metrics.json",
    "terminal_actions": 0,
    "wall_clock_seconds": 0.0,
    "avg_llm_call_gap_seconds": 0.0,
    "error_fix_cycle_count": 0,
    "canonical_tests_pass": false,
    "all_tests_pass": false,
    "honesty_gate": "PASS"
  },

  "arm_b": {
    "metrics_file": "arm-b/metrics.json",
    "terminal_actions": 0,
    "wall_clock_seconds": 0.0,
    "avg_llm_call_gap_seconds": 0.0,
    "error_fix_cycle_count": 0,
    "canonical_tests_pass": false,
    "all_tests_pass": false,
    "honesty_gate": "PASS"
  },

  "deltas": {
    "terminal_actions_a_minus_b": 0,
    "wall_clock_seconds_a_minus_b": 0.0,
    "avg_llm_gap_a_minus_b": 0.0,
    "error_fix_cycles_a_minus_b": 0,
    "interpretation": "arm-a faster | arm-b faster | indeterminate"
  }
}
```

### Cross-Example Comparison Table (for 부록 D)

The chapter renders this as a Markdown table:

```markdown
| 예제 | 메트릭 | Arm A (Claude 계획) | Arm B (OpenHands 자체 계획) | 차이 |
|------|--------|--------------------|-----------------------------|------|
| F# 계산기 | TerminalAction 수 | N | N | ±N |
| F# 계산기 | 총 실행 시간 (초) | Xs | Xs | ±Xs |
| F# 계산기 | LLM 호출당 평균 시간 | Xs | Xs | ±Xs |
| F# 계산기 | 오류 수정 사이클 수 | N | N | ±N |
| F# 계산기 | 표준 테스트 통과 | PASS/FAIL | PASS/FAIL | — |
| Rust HTTP | ... | ... | ... | ... |
| Scala 계산기 | ... | ... | ... | ... |
```

One row per (example × metric) combination. The comparison generator builds this table from the three `comparison.json` files.

---

## Patterns to Follow

### Pattern 1: Single-Session Single-Prompt (Reuse Established Invocation)

**What:** One OpenHands headless invocation per arm per example. The entire goal (for Arm A: all decomposed steps; for Arm B: just the goal) goes into one `-t` string. The agent's entire session — planning reasoning, file writes, builds, test runs, error-fix cycles — is captured in one JSONL file.

**Why:** This is the proven pattern across v1.2 (Rust, 3 tasks) and v1.3 (Scala, 3 tasks). Each task in prior milestones was a separate invocation because the workdir persisted state between sessions. For v1.4, each arm is ONE invocation, so the agent must plan and execute in one session. This is what distinguishes Arm B from Arm A: Arm B must plan AND execute in one session without hints; Arm A gets the plan embedded in the prompt.

**Implication:** The Arm A prompt must include explicit step transitions ("Now complete Step 2: ...") or rely on the agent to sequence, given the numbered list.

### Pattern 2: Pilot on ONE Example First

**What:** Before running all 3 examples × 2 arms (= 6 invocations), pilot both arms on the SIMPLEST example (Rust HTTP server: one source file, trivial test) to validate the harness and confirm both arms capture cleanly.

**Why:** Piloting catches prompt format issues, missing working-directory setup, and JSONL capture problems before investing in 4 more invocations. The Rust example is the right pilot because it has the fewest moving parts (no grammar files, no `scala-cli` cache, straightforward `curl` test).

**Gate:** The pilot is the Phase 12 preflight + execute. Phases 13+ (F# and Scala examples) are blocked until both arms produce non-empty JSONLs with honesty gate PASS.

### Pattern 3: Captured Planning Artifact Extraction (Arm B)

**What:** For Arm B, the "OpenHands self-plan" is not a separate output — it appears within the JSONL as a MessageEvent or AgentThinkAction early in the session. Extract it by scanning the first 5–10 events for the agent's planning text, then save it as `arm-b/<example>/planning-artifact/oh-self-plan.md`.

**Why:** The chapter needs to show what OH's self-plan looked like vs Claude's plan. This is not a file OH writes; it is a transcript artifact that the extractor pulls from the JSONL.

**Extraction:** Look for the first MessageEvent or AgentThinkAction (kind=ActionEvent, source=agent, tool_name="") early in the JSONL and capture its `thought` or `llm_message` field as the planning artifact.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Multiple Invocations Per Arm (Multi-Task Split)

**What:** Splitting Arm A into task1/task2/task3 invocations just like prior milestones.

**Why wrong:** This defeats the study design. Arm A's value is that Claude pre-decomposed the work; if we split it into separate OpenHands sessions, we are doing Claude's decomposition AND OpenHands' sequencing separately — not testing whether the plan format helps within one session. Arm B cannot be split (it has one goal prompt), so Arm A must also be one session for a fair comparison.

**Exception:** If a single-session run fails or times out, fall back to documenting the failure honestly (does Arm A help when the session is long-running? does Arm B get confused without pre-decomposition?). The failure mode is itself data.

### Anti-Pattern 2: Re-using the Prior Task Prompts Verbatim as Arm A

**What:** Using the v1.2 task-prompts-rust/task1-scaffold.txt + task2-server.txt + task3-buildtest.txt as three separate Arm A invocations and calling it "Arm A."

**Why wrong:** Prior task prompts were designed for separate sessions with persistent workdir state. A concatenated single-session version requires explicit state handoff ("the project directory already exists from Step 1") and forward references between steps. Reusing verbatim would produce a malformed single-session prompt that the agent cannot follow.

**Do instead:** Synthesize a new single-session Arm A prompt that preserves Claude's task decomposition as numbered steps with state handoff notes ("After Step 1, the rust-server/ directory will exist...").

### Anti-Pattern 3: Not Piloting Before Full Run

**What:** Running all 6 invocations (3 examples × 2 arms) sequentially before validating the capture pipeline.

**Why wrong:** A prompt format bug in the converter, a missing working-directory init, or an OH version mismatch will silently produce unusable JSONL. With 6 invocations at ~15–40 minutes each (estimated from v1.3 per-task times), an early failure wastes 2–4 hours.

**Do instead:** Pilot on Rust (both arms) first, validate the JSONL schema, confirm both arms capture cleanly, then proceed to F# and Scala.

### Anti-Pattern 4: Comparing Incompatible Workdirs

**What:** Running Arm A and Arm B in the same `oh-workdir-planning/` directory, leaving Arm A's built artifacts in place when Arm B starts.

**Why wrong:** Arm B's agent will discover Arm A's built source and may reuse it, invalidating the comparison (Arm B would be running with pre-built artifacts, not building from scratch).

**Do instead:** Use separate subdirectories: `oh-workdir-planning/arm-a/<example>/` and `oh-workdir-planning/arm-b/<example>/`. Initialize each before the run with only the toolchain (no source files).

---

## Suggested Phase Breakdown (Phases 12+)

### Phase 12: Harness + Pilot (Rust example, both arms)

**Goal:** Establish the harness, write both arm prompts for the Rust example, run both arms, validate that both arms capture cleanly, extract metrics for Rust, close the pilot capture gate.

**Plans:**
- **12-01 Preflight + Harness Setup:** Init `oh-workdir-planning/arm-a/rust/` and `arm-b/rust/`; write the Arm A Rust prompt (Claude plan → single-session OH prompt); write the Arm B Rust goal prompt; add `oh-workdir-planning/` to `.gitignore`; verify the invocation pattern works on Rust (test with `--help` or a trivial echo task if needed).
- **12-02 Execute: Run Both Arms on Rust:** Run Arm A Rust invocation (background, poll JSONL); run Arm B Rust invocation (background, poll JSONL); record run notes. Both arms must produce non-empty JSONL with honesty gate PASS.
- **12-03 Capture Gate: Commit Rust Pilot Artifacts:** Run honesty gate; run metrics extractor for both arms; write `captured-planning/rust/arm-a/metrics.json`, `arm-b/metrics.json`, `rust/comparison.json`; commit pilot artifacts; confirm the pilot capture gate is CLOSED.

**Capture gate condition (pilot):** Both `captured-planning/rust/arm-a/metrics.json` and `captured-planning/rust/arm-b/metrics.json` are committed with `honesty_gate = PASS` AND `canonical_tests.curl_hello.pass` recorded (PASS or FAIL, not null).

### Phase 13: F# and Scala Arms (Full Study Runs)

**Goal:** Run both arms on the two remaining examples (F# calculator and Scala calculator), extract metrics, close the full-study capture gate.

**Plans:**
- **13-01 Execute: F# Both Arms:** Write Arm A F# prompt (Claude's v1 5-task decomposition → single session); write Arm B F# goal prompt; run both arms; poll and settle.
- **13-02 Execute: Scala Both Arms:** Write Arm A Scala prompt (Claude's v1.3 3-task decomposition → single session); write Arm B Scala goal prompt; run both arms; poll and settle.
- **13-03 Capture Gate: Commit Full Study Artifacts:** Run honesty gate on all 6 runs; run metrics extractor on all 6 runs; write all `metrics.json` files; write `fsharp/comparison.json`, `scala/comparison.json`; write `captured-planning/CAPTURE-MANIFEST.md`; commit all artifacts; confirm the full-study capture gate is CLOSED.

**Capture gate condition (full study):** All 6 `metrics.json` files committed with `honesty_gate = PASS` AND all `canonical_tests` populated (not null) — success or failure, but not null.

### Phase 14: 부록 D Chapter + Publish

**Goal:** Write `부록 D "계획 방식 비교: Claude 계획 vs OpenHands 자체 계획"` from the captured comparison data; wire into `src/SUMMARY.md` after 부록 C; build clean; deploy live.

**Plans:**
- **14-01 Write 부록 D:** Write `src/appendix-d-planning-comparison.md` verbatim from the 6 `metrics.json` + 3 `comparison.json` files. Include: the comparison Markdown table (example × metric × arm-a × arm-b × delta); per-arm planning artifact excerpts; qualitative observations (did OH's self-plan resemble Claude's? where did they diverge?); honest interpretation of mixed/inconclusive results. No fabrication.
- **14-02 Wire + Publish:** Add `[부록 D: 계획 방식 비교](appendix-d-planning-comparison.md)` to `src/SUMMARY.md` after 부록 C; `mdbook build` clean; push to main; verify live on GitHub Pages.

---

## Integration Points

### Existing Capture Pipeline (Reused Without Modification)

| Component | Reuse |
|-----------|-------|
| Headless invocation pattern | Verbatim from v1.2/v1.3 `00-INVOCATION.md` |
| JSONL tee (`| tee <arm>-<example>.jsonl`) | Same `tee` pattern |
| Honesty gate python3 snippet | Verbatim from 10-03-PLAN.md Task 1 |
| Poll/status-check pattern | Verbatim from 10-02-PLAN.md jsonl_schema_reference |
| `captured-*/` commit pattern | Same structure; new root `captured-planning/` |

### mdBook SUMMARY.md Integration

The new 부록 D is wired after 부록 C, before any future appendices:

```markdown
[부록 C: 모델 비교 — 35B vs 122B](appendix-c-comparison.md)
[부록 D: 계획 방식 비교: Claude 계획 vs OpenHands 자체 계획](appendix-d-planning-comparison.md)
```

`deploy.yml` is NOT modified. The existing workflow (push to main → mdbook build → GitHub Pages deploy) handles 부록 D automatically.

### Working Directory Isolation

Each arm × example pair gets its own subdirectory inside `oh-workdir-planning/` (gitignored):

```
oh-workdir-planning/
  arm-a/rust/        ← Arm A Rust workspace
  arm-b/rust/        ← Arm B Rust workspace  (separate; no cross-contamination)
  arm-a/fsharp/      ← Arm A F# workspace
  arm-b/fsharp/
  arm-a/scala/
  arm-b/scala/
```

The `-t` prompt for each invocation sets `OPENHANDS_WORK_DIR` to the arm-specific subdirectory.

---

## Sources

- Real JSONL schema confirmed by inspection: `/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1.3-phases/10-capture-the-35b-scala-calculator-run/captured-scala/logs/task3-buildtest.jsonl` (2026-06-01)
- Invocation pattern: `/Users/ohama/projs/OpenHandsTests/.planning/milestones/v1.3-phases/10-capture-the-35b-scala-calculator-run/task-prompts-scala/00-INVOCATION.md`
- Capture pipeline: plans 10-02 and 10-03 (v1.3 Scala capture)
- Capture manifest structure: `captured-rust/CAPTURE-MANIFEST.md` (v1.2) and `captured-scala/CAPTURE-MANIFEST.md` (v1.3)
- SUMMARY.md integration pattern: `src/SUMMARY.md` (current book, showing 부록 A/B/C positioning)
- Project context: `.planning/PROJECT.md`, `.planning/MILESTONES.md`

---

*Architecture research for: v1.4 Planning Comparison Harness — 2-arm × 3-example A/B study on 35B*
*Researched: 2026-06-01*
