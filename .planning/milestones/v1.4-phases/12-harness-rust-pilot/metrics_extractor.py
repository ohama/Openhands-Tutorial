#!/usr/bin/env python3
"""
metrics_extractor.py — v1.4 per-arm metrics extractor.

Parses an OpenHands headless JSONL capture and emits a metrics.json record
per the ARCHITECTURE.md schema for the v1.4 Planning Comparison study.

Usage:
  python3 metrics_extractor.py \
      --jsonl oh-workdir-planning/arm-a/rust-run.jsonl \
      --example rust \
      --arm arm-a \
      --prompt-file task-prompts/CONTROL-BLOCK-rust.txt \
      --out captured-planning/rust/arm-a/metrics.json

Event numbering: 1-BASED throughout (event #1 = first JSONL line).
The ARCHITECTURE.md reference snippet uses 0-based events.index(); all
indices emitted by this extractor are converted to 1-based (Pitfall 8/11).
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
    """Parse JSONL file; skip blank lines and non-JSON lines."""
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


def _find_usage(events):
    """
    Scan all events for a 'usage' field.
    Returns (usage_present: bool, usage_sample: dict|None).
    Resolves open unknown #2 (Phase 12-02 will confirm if P3 token metrics are feasible).
    """
    for e in events:
        # Top-level usage key
        if "usage" in e and isinstance(e["usage"], dict):
            return True, e["usage"]
        # Nested under observation
        obs = e.get("observation") or {}
        if "usage" in obs and isinstance(obs["usage"], dict):
            return True, obs["usage"]
        # Nested under llm_response or metadata sub-key
        for subkey in ("llm_response", "metadata"):
            sub = e.get(subkey) or {}
            if "usage" in sub and isinstance(sub["usage"], dict):
                return True, sub["usage"]
    return False, None


def _count_task_tracker(events):
    """
    Count TaskTracker-related events.
    Resolves open unknown #1 (Phase 12-02 will confirm if Arm B emits these).

    task_tracker_observation_count: ObservationEvents where observation.kind
        contains "TaskTracker" or tool_name/any field mentions task_tracker.
    task_tracker_action_count: ActionEvents with similar markers.
    """
    obs_count = 0
    act_count = 0
    for e in events:
        kind = e.get("kind", "")
        tool = (e.get("tool_name") or "").lower()

        if kind == "ObservationEvent":
            obs = e.get("observation") or {}
            obs_kind = (obs.get("kind") or "").lower()
            if "tasktracker" in obs_kind or "task_tracker" in obs_kind or \
               "task_tracker" in tool or "tasktracker" in tool:
                obs_count += 1

        elif kind == "ActionEvent":
            act = e.get("action") or {}
            act_kind = (act.get("kind") or "").lower()
            if "tasktracker" in act_kind or "task_tracker" in act_kind or \
               "task_tracker" in tool or "tasktracker" in tool:
                act_count += 1

    return obs_count, act_count


def _extract_canonical_tests(events, example):
    """
    Scan ObservationEvents for canonical test outputs.
    Returns a dict keyed by test name with {expected, actual, pass, event_index}.
    event_index is 1-BASED (event #1 = first JSONL line).
    """
    if example in ("fsharp", "scala"):
        tests = {
            "2+3*4":   {"expected": "14",  "actual": None, "pass": None, "event_index": None},
            "(2+3)*4": {"expected": "20",  "actual": None, "pass": None, "event_index": None},
            "10-3-2":  {"expected": "5",   "actual": None, "pass": None, "event_index": None},
        }
        for idx, e in enumerate(events, start=1):  # 1-based
            if e.get("kind") != "ObservationEvent":
                continue
            obs = e.get("observation") or {}
            cmd = obs.get("command", "")
            content = extract_text(obs.get("content", "")).strip()
            exit_code = obs.get("exit_code", -1)
            for expr, rec in tests.items():
                if rec["actual"] is not None:
                    continue
                if expr in cmd or expr.replace("*", r"\*") in cmd:
                    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
                    actual = lines[-1] if lines else ""
                    rec["actual"] = actual
                    rec["pass"] = (exit_code == 0 and actual == rec["expected"])
                    rec["event_index"] = idx  # 1-based
        return tests

    elif example == "rust":
        tests = {
            "curl_hello": {
                "expected": "hello",
                "actual": None,
                "pass": None,
                "event_index": None,
            },
        }
        for idx, e in enumerate(events, start=1):  # 1-based
            if e.get("kind") != "ObservationEvent":
                continue
            obs = e.get("observation") or {}
            cmd = obs.get("command", "")
            content = extract_text(obs.get("content", "")).strip()
            exit_code = obs.get("exit_code", -1)
            # Skip rejected multi-command observations (exit_code is None = runtime
            # rejected the command before execution; "Cannot execute multiple commands"
            # pattern also indicates the curl never actually ran — Pitfall: first curl
            # ObservationEvent may be a rejection, not a real result).
            if exit_code is None:
                continue
            if "curl" in cmd and tests["curl_hello"]["actual"] is None:
                actual = "hello" if "hello" in content else content[:40]
                tests["curl_hello"]["actual"] = actual
                tests["curl_hello"]["pass"] = ("hello" in content and exit_code == 0)
                tests["curl_hello"]["event_index"] = idx  # 1-based
        return tests

    return {}


def compute_metrics(events, example, arm, prompt_file):
    """
    Compute all metrics from a loaded event list.
    All emitted event indices are 1-BASED.
    """
    kind_counts = collections.Counter(e.get("kind") for e in events)

    # --- Terminal actions: ActionEvent, source=agent, tool_name=terminal ---
    terminal_actions = [
        e for e in events
        if e.get("kind") == "ActionEvent"
        and e.get("source") == "agent"
        and e.get("tool_name") == "terminal"
    ]

    # --- Finish and error signals ---
    has_finish = any(
        (e.get("action") or {}).get("kind") == "FinishAction"
        for e in events
    )
    has_conv_error = any(e.get("kind") == "ConversationErrorEvent" for e in events)

    # --- Timing ---
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

    # --- LLM call gaps: ObservationEvent.ts -> next ActionEvent.ts ---
    gaps = []
    for i, e in enumerate(events):
        if e.get("kind") == "ObservationEvent" and i + 1 < len(events):
            nxt = events[i + 1]
            if (nxt.get("kind") == "ActionEvent"
                    and nxt.get("timestamp")
                    and e.get("timestamp")):
                t_obs = datetime.datetime.fromisoformat(e["timestamp"])
                t_act = datetime.datetime.fromisoformat(nxt["timestamp"])
                gaps.append((t_act - t_obs).total_seconds())

    # --- Error-fix cycles: nonzero-exit ObservationEvent -> next agent ActionEvent ---
    # Indices stored as 1-based.
    cycles = []
    nonzero_count = 0
    for i, e in enumerate(events):
        if e.get("kind") != "ObservationEvent":
            continue
        obs = e.get("observation") or {}
        exit_code = obs.get("exit_code")
        if exit_code is None or exit_code == 0:
            continue
        nonzero_count += 1
        err_event_index = i + 1  # convert to 1-based
        # Find next agent ActionEvent
        for j in range(i + 1, len(events)):
            nxt = events[j]
            if nxt.get("kind") == "ActionEvent" and nxt.get("source") == "agent":
                act = nxt.get("action") or {}
                cycles.append({
                    "error_event_index": err_event_index,         # 1-based
                    "error_exit_code": exit_code,
                    "error_command_excerpt": extract_text(obs.get("content", ""))[:120],
                    "fix_event_index": j + 1,                     # 1-based
                    "fix_command_excerpt": str(act.get("command", ""))[:120],
                })
                break

    # --- Honesty gate: every ActionEvent must have source=agent ---
    # MessageEvent source=user is NOT an ActionEvent — correctly not flagged (Pitfall 13).
    bad = []
    total_action_events = 0
    for idx, e in enumerate(events, start=1):  # 1-based
        if e.get("kind") != "ActionEvent":
            continue
        total_action_events += 1
        if e.get("source") != "agent":
            bad.append({
                "event_index": idx,   # 1-based
                "source": e.get("source"),
                "command": str((e.get("action") or {}).get("command", ""))[:80],
            })
    gate_result = "PASS" if not bad else "FAIL"

    # --- Canonical tests ---
    canonical_tests = _extract_canonical_tests(events, example)

    # --- Usage detection (resolves open unknown #2) ---
    usage_present, usage_sample = _find_usage(events)

    # --- Task tracker detection (resolves open unknown #1) ---
    tt_obs_count, tt_act_count = _count_task_tracker(events)

    # --- Source-agent ratio ---
    agent_action_count = sum(
        1 for e in events
        if e.get("kind") == "ActionEvent" and e.get("source") == "agent"
    )
    source_agent_ratio = agent_action_count / max(1, total_action_events)

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
            "commands": [
                str((e.get("action") or {}).get("command", ""))[:120]
                for e in terminal_actions
            ],
        },

        "finish": {
            "has_finish_action": has_finish,
            "has_conversation_error": has_conv_error,
            "settled_by": (
                "FinishAction" if has_finish
                else ("ConversationError" if has_conv_error else "idle-timeout")
            ),
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
            "nonzero_exit_count": nonzero_count,
            "cycle_count": len(cycles),
            "cycles": cycles,
        },

        "canonical_tests": canonical_tests,

        "honesty_gate": {
            "result": gate_result,
            "total_action_events_checked": total_action_events,
            "offending_events": bad,
        },

        "source_agent_ratio": round(source_agent_ratio, 4),

        # --- Open unknowns resolved in Phase 12-02 pilot ---
        "usage_present": usage_present,
        "usage_sample": usage_sample,
        "task_tracker_observation_count": tt_obs_count,
        "task_tracker_action_count": tt_act_count,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract per-arm metrics from an OpenHands headless JSONL capture."
    )
    parser.add_argument("--jsonl", required=True, help="Path to the JSONL capture file")
    parser.add_argument(
        "--example",
        required=True,
        choices=["fsharp", "rust", "scala"],
        help="Example name (determines canonical test set)",
    )
    parser.add_argument(
        "--arm",
        required=True,
        choices=["arm-a", "arm-b"],
        help="Study arm identifier",
    )
    parser.add_argument("--prompt-file", required=True, help="Path to the prompt file used")
    parser.add_argument("--out", required=True, help="Output path for metrics.json")
    args = parser.parse_args()

    events = load_events(args.jsonl)
    metrics = compute_metrics(events, args.example, args.arm, args.prompt_file)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"Metrics written to: {args.out}")
    print(f"  Total events:       {metrics['event_counts']['total_events']}")
    print(f"  TerminalActions:    {metrics['terminal_actions']['count']}")
    print(f"  Wall clock:         {metrics['timing']['wall_clock_seconds']}s")
    print(f"  LLM avg gap:        {metrics['timing']['avg_llm_call_gap_seconds']}s")
    print(f"  Error-fix cycles:   {metrics['error_fix_cycles']['cycle_count']}")
    print(f"  Honesty gate:       {metrics['honesty_gate']['result']}")
    print(f"  usage_present:      {metrics['usage_present']}")
    print(f"  task_tracker_obs:   {metrics['task_tracker_observation_count']}")
    print(f"  task_tracker_act:   {metrics['task_tracker_action_count']}")

    ct = metrics["canonical_tests"]
    if args.example == "rust":
        ch = ct.get("curl_hello", {})
        status = "PASS" if ch.get("pass") else "FAIL"
        print(
            f"  curl_hello:         {ch.get('actual')!r} "
            f"(expected {ch.get('expected')!r}) → {status} "
            f"[event #{ch.get('event_index')}]"
        )
    elif args.example in ("fsharp", "scala"):
        for expr, rec in ct.items():
            status = "PASS" if rec.get("pass") else "FAIL"
            print(
                f"  {expr}: {rec.get('actual')!r} "
                f"(expected {rec.get('expected')!r}) → {status} "
                f"[event #{rec.get('event_index')}]"
            )


# ---------------------------------------------------------------------------
# Self-validation fixture (run with --self-test to execute)
# ---------------------------------------------------------------------------

def _run_self_validation():
    """
    Self-validate on a synthetic fixture.
    Clean fixture  → honesty_gate PASS, curl_hello PASS, event indices 1-based.
    Dirty fixture  → honesty_gate FAIL (ActionEvent source=user injected).
    Raises AssertionError on any discrepancy.
    """
    import tempfile, os

    # Build a clean fixture JSONL
    clean_lines = [
        # Event 1: MessageEvent source=user (initial task prompt — NOT an ActionEvent, must NOT be flagged)
        json.dumps({
            "kind": "MessageEvent",
            "source": "user",
            "timestamp": "2026-06-02T00:00:00.000000",
            "tool_name": "",
            "action": None,
            "observation": None,
        }),
        # Event 2: ActionEvent source=agent TerminalAction cargo build
        json.dumps({
            "kind": "ActionEvent",
            "source": "agent",
            "timestamp": "2026-06-02T00:00:01.000000",
            "tool_name": "terminal",
            "action": {"kind": "TerminalAction", "command": "cargo build 2>&1"},
            "observation": None,
        }),
        # Event 3: ObservationEvent exit_code=0 (build success)
        json.dumps({
            "kind": "ObservationEvent",
            "source": "environment",
            "timestamp": "2026-06-02T00:00:04.500000",
            "tool_name": "",
            "action": None,
            "observation": {
                "kind": "TerminalObservation",
                "command": "cargo build 2>&1",
                "exit_code": 0,
                "content": [{"type": "text", "text": "   Compiling rust-server v0.1.0\n    Finished dev target"}],
            },
        }),
        # Event 4: ActionEvent source=agent curl test
        json.dumps({
            "kind": "ActionEvent",
            "source": "agent",
            "timestamp": "2026-06-02T00:00:05.000000",
            "tool_name": "terminal",
            "action": {"kind": "TerminalAction", "command": "curl -s http://localhost:8080/"},
            "observation": None,
        }),
        # Event 5: ObservationEvent curl -> hello (canonical test pass)
        json.dumps({
            "kind": "ObservationEvent",
            "source": "environment",
            "timestamp": "2026-06-02T00:00:07.200000",
            "tool_name": "",
            "action": None,
            "observation": {
                "kind": "TerminalObservation",
                "command": "curl -s http://localhost:8080/",
                "exit_code": 0,
                "content": [{"type": "text", "text": "hello\n"}],
            },
        }),
        # Event 6: ActionEvent source=agent FinishAction
        json.dumps({
            "kind": "ActionEvent",
            "source": "agent",
            "timestamp": "2026-06-02T00:00:08.000000",
            "tool_name": "",
            "action": {"kind": "FinishAction", "command": ""},
            "observation": None,
        }),
    ]

    # Build a dirty fixture: same as clean but event 2 has source=user
    dirty_lines = list(clean_lines)
    dirty_event2 = json.loads(dirty_lines[1])
    dirty_event2["source"] = "user"
    dirty_lines[1] = json.dumps(dirty_event2)

    results = {}

    for label, lines in [("clean", clean_lines), ("dirty", dirty_lines)]:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as f:
            f.write("\n".join(lines) + "\n")
            tmp_path = f.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            out_path = f.name

        try:
            events = load_events(tmp_path)
            metrics = compute_metrics(events, "rust", "arm-a", "dummy.txt")
            with open(out_path, "w") as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            results[label] = metrics
            print(f"\n--- Fixture '{label}' metrics.json ---")
            print(json.dumps(metrics, indent=2, ensure_ascii=False))
        finally:
            os.unlink(tmp_path)
            os.unlink(out_path)

    # --- Assertions on clean fixture ---
    c = results["clean"]
    assert c["honesty_gate"]["result"] == "PASS", \
        f"Clean fixture should have PASS gate, got: {c['honesty_gate']['result']}"
    ct_clean = c["canonical_tests"]["curl_hello"]
    assert ct_clean["pass"] is True, \
        f"Clean fixture curl_hello should pass, got: {ct_clean}"
    assert isinstance(ct_clean["event_index"], int) and ct_clean["event_index"] >= 1, \
        f"curl_hello event_index must be 1-based integer, got: {ct_clean['event_index']}"
    # The curl ObservationEvent is line 5 (1-based) in clean fixture
    assert ct_clean["event_index"] == 5, \
        f"Expected event_index=5 (1-based), got {ct_clean['event_index']}"
    assert c["usage_present"] is False, \
        f"No usage in clean fixture, got: {c['usage_present']}"
    assert c["task_tracker_observation_count"] == 0, \
        f"No task_tracker in clean fixture, got: {c['task_tracker_observation_count']}"

    # MessageEvent source=user must NOT appear in offending_events (Pitfall 13)
    offending_sources = [ev["source"] for ev in c["honesty_gate"]["offending_events"]]
    assert offending_sources == [], \
        f"No offending events expected in clean fixture, got: {offending_sources}"

    # --- Assertions on dirty fixture ---
    d = results["dirty"]
    assert d["honesty_gate"]["result"] == "FAIL", \
        f"Dirty fixture should have FAIL gate, got: {d['honesty_gate']['result']}"
    assert len(d["honesty_gate"]["offending_events"]) == 1, \
        f"Expected 1 offending event, got: {d['honesty_gate']['offending_events']}"
    offending_idx = d["honesty_gate"]["offending_events"][0]["event_index"]
    assert offending_idx == 2, \
        f"Offending event should be 1-based index 2 (event #2), got: {offending_idx}"

    print("\n=== SELF-VALIDATION RESULT ===")
    print("  Clean fixture → honesty_gate: PASS (OK)")
    print(f"  Clean fixture → curl_hello.pass: {ct_clean['pass']} (OK)")
    print(f"  Clean fixture → curl_hello.event_index: {ct_clean['event_index']} (1-based, OK)")
    print(f"  Clean fixture → usage_present: {c['usage_present']} (OK)")
    print(f"  Clean fixture → task_tracker_observation_count: {c['task_tracker_observation_count']} (OK)")
    print(f"  Dirty fixture → honesty_gate: FAIL (OK)")
    print(f"  Dirty fixture → offending_events[0].event_index: {offending_idx} (1-based, OK)")
    print("SELF-VALIDATION: PASS")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        _run_self_validation()
        sys.exit(0)
    main()
