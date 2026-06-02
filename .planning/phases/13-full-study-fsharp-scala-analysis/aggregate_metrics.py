#!/usr/bin/env python3
"""
aggregate_metrics.py — v1.4 per-arm and per-example aggregation.

Reads all metrics-run-N.json for a (LANG, ARM) pair, computes:
  - For each numeric P1/P2 metric: median, min, max, n
  - canonical_tests: per-test pass count across reps (e.g. "2/3 reps PASS")
  - honesty_gate: PASS only if all reps PASS
  - n field; when n==1, also single_run_label="(단일 실행)"

Then builds comparison.json per example:
  - arm_a and arm_b blocks each as {metric: {median, min, max, n}}
  - deltas_a_minus_b block on medians
  - caveats: timing cache/run-order confound + n=1 hedges
  - canonical_test_pass_counts: per-test, per-arm

Usage:
  python3 aggregate_metrics.py --base <dir> --example <lang>

Where <dir> is the captured-planning/<lang> directory.

Run for all three examples:
  python3 aggregate_metrics.py \\
      --base .planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/fsharp \\
      --example fsharp
  (repeat for scala, rust)

NOTE on canonical_tests and extractor behavior:
  The reused metrics_extractor.py (REUSE AS-IS per v1.4 plan) matches the FIRST
  ObservationEvent whose command string contains the test expression. When agents
  write source code via heredocs (cat <<'EOF'...EOF), the multi-line command field
  may contain the expression, causing a false-first-match that records the file-
  write observation (empty/wrong content) instead of the actual test run. This
  produces false-negative FAILs for tests where the agent ultimately succeeded.
  All canonical_tests fields are populated (PASS, FAIL, or None→treated as FAIL).
  The aggregate pass counts reflect extractor results; per-run discrepancies are
  documented via cross-reference to 13-02-RUN-NOTES.md (the authoritative source
  for final canonical outcomes).

Timing caveat:
  All timing metrics are derived from JSONL timestamps. They carry a cache-warmth
  and run-order confound — the proxy KV-cache may warm across reps, and arm order
  was counterbalanced across examples (Arm B first for F#/Scala, Arm A first for
  Rust). Do NOT interpret timing deltas as clean planning-quality signals.
  The legacy estimate "~14–32s/call" is a pre-run prediction, never a measurement.
"""

import json
import glob
import sys
import os
import argparse
import statistics

NUMERIC_METRICS = [
    ("terminal_actions_count",       lambda m: m["terminal_actions"]["count"]),
    ("total_events",                  lambda m: m["event_counts"]["total_events"]),
    ("wall_clock_seconds",            lambda m: m["timing"]["wall_clock_seconds"]),
    ("avg_llm_call_gap_seconds",      lambda m: m["timing"]["avg_llm_call_gap_seconds"]),
    ("min_llm_call_gap_seconds",      lambda m: m["timing"]["min_llm_call_gap_seconds"]),
    ("max_llm_call_gap_seconds",      lambda m: m["timing"]["max_llm_call_gap_seconds"]),
    ("error_fix_cycle_count",         lambda m: m["error_fix_cycles"]["cycle_count"]),
    ("nonzero_exit_count",            lambda m: m["error_fix_cycles"]["nonzero_exit_count"]),
    ("task_tracker_observation_count", lambda m: m["task_tracker_observation_count"]),
    ("task_tracker_action_count",     lambda m: m["task_tracker_action_count"]),
]


def load_run_metrics(base_dir, arm):
    """Load all metrics-run-N.json for a given arm directory."""
    pattern = os.path.join(base_dir, arm, "metrics-run-*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No metrics-run-*.json found in {base_dir}/{arm}/")
    metrics = []
    for f in files:
        with open(f) as fh:
            metrics.append(json.load(fh))
    return metrics


def aggregate_numeric(metrics_list, key, extractor):
    """Return {median, min, max, n} for a numeric metric across reps."""
    values = [extractor(m) for m in metrics_list]
    n = len(values)
    if n == 0:
        return {"median": None, "min": None, "max": None, "n": 0}
    values_sorted = sorted(values)
    if n == 1:
        return {
            "median": values[0],
            "min": values[0],
            "max": values[0],
            "n": 1,
            "single_run_label": "(단일 실행)",
        }
    med = statistics.median(values)
    return {
        "median": round(med, 3) if isinstance(med, float) else med,
        "min": min(values),
        "max": max(values),
        "n": n,
    }


def aggregate_canonical_tests(metrics_list):
    """
    Aggregate canonical_tests across reps.
    Returns a dict: {test_name: {pass_count, n, pass_fraction_label}}.
    A None pass value is treated as FAIL (extractor found no matching event).
    """
    if not metrics_list:
        return {}
    # Collect test names from first rep
    test_names = list(metrics_list[0].get("canonical_tests", {}).keys())
    result = {}
    for name in test_names:
        pass_count = 0
        n = 0
        for m in metrics_list:
            ct = m.get("canonical_tests", {})
            rec = ct.get(name, {})
            p = rec.get("pass")
            # None = no event found = FAIL
            if p is True:
                pass_count += 1
            n += 1
        label = f"{pass_count}/{n} reps PASS"
        result[name] = {
            "pass_count": pass_count,
            "n": n,
            "pass_fraction_label": label,
        }
    return result


def aggregate_honesty_gate(metrics_list):
    """Return 'PASS' only if all reps have honesty_gate PASS."""
    for m in metrics_list:
        g = m.get("honesty_gate")
        result = g.get("result") if isinstance(g, dict) else g
        if result != "PASS":
            return "FAIL"
    return "PASS"


def build_arm_metrics(base_dir, arm, example):
    """Build per-arm aggregated metrics dict."""
    metrics_list = load_run_metrics(base_dir, arm)
    n = len(metrics_list)

    agg_numerics = {}
    for key, extractor in NUMERIC_METRICS:
        agg_numerics[key] = aggregate_numeric(metrics_list, key, extractor)

    canonical = aggregate_canonical_tests(metrics_list)
    honesty = aggregate_honesty_gate(metrics_list)

    out = {
        "study": "v1.4-planning-comparison",
        "example": example,
        "arm": arm,
        "n": n,
        "honesty_gate": honesty,
    }
    if n == 1:
        out["single_run_label"] = "(단일 실행)"
    out["metrics"] = agg_numerics
    out["canonical_tests_aggregate"] = canonical
    out["extractor_note"] = (
        "canonical_tests reflect the first matching ObservationEvent per test "
        "(metrics_extractor.py REUSED AS-IS). Multi-line heredoc commands may "
        "cause false-first-match FAILs. Authoritative final outcomes are in "
        "13-02-RUN-NOTES.md."
    )
    return out


def build_comparison(arm_a_metrics_list, arm_b_metrics_list, example, run_order_note):
    """Build per-example comparison dict (Arm A vs Arm B)."""
    # Build per-arm metric aggregates
    arm_a_agg = {}
    arm_b_agg = {}
    for key, extractor in NUMERIC_METRICS:
        arm_a_agg[key] = aggregate_numeric(arm_a_metrics_list, key, extractor)
        arm_b_agg[key] = aggregate_numeric(arm_b_metrics_list, key, extractor)

    # Deltas on medians (A minus B; None if either is None)
    deltas = {}
    for key in arm_a_agg:
        a_med = arm_a_agg[key].get("median")
        b_med = arm_b_agg[key].get("median")
        if a_med is not None and b_med is not None:
            try:
                deltas[key] = round(a_med - b_med, 3)
            except TypeError:
                deltas[key] = None
        else:
            deltas[key] = None

    # Canonical test pass counts per arm
    canon_a = aggregate_canonical_tests(arm_a_metrics_list)
    canon_b = aggregate_canonical_tests(arm_b_metrics_list)

    # Caveats
    caveats = [
        (
            "Timing metrics (wall_clock_seconds, avg_llm_call_gap_seconds, etc.) are "
            "derived from JSONL timestamps. They carry a cache-warmth / run-order "
            "confound: the litellm proxy KV-cache may warm across reps, and arm order "
            "was counterbalanced across examples (Arm B first for F# and Scala; "
            "Arm A first for Rust). Do NOT interpret timing deltas as clean "
            "planning-quality signals."
        ),
        (
            "canonical_tests reflect the first matching ObservationEvent per test "
            "(metrics_extractor.py REUSED AS-IS). Multi-line heredoc commands may "
            "cause false-first-match FAILs for tests the agent ultimately passed. "
            "Authoritative final outcomes per rep are in 13-02-RUN-NOTES.md."
        ),
        run_order_note,
    ]
    # Add n=1 hedge if any arm has n=1
    n_a = len(arm_a_metrics_list)
    n_b = len(arm_b_metrics_list)
    if n_a == 1 or n_b == 1:
        caveats.append(
            "One or both arms have n=1. Metrics labelled (단일 실행). "
            "Single-run values cannot support median/range; no distributional "
            "inferences. Never use 'significantly', 'consistently', or 'reliably' "
            "at n=1."
        )

    return {
        "study": "v1.4-planning-comparison",
        "example": example,
        "n_arm_a": n_a,
        "n_arm_b": n_b,
        "arm_a": arm_a_agg,
        "arm_b": arm_b_agg,
        "deltas_a_minus_b": deltas,
        "canonical_test_pass_counts": {
            "arm_a": canon_a,
            "arm_b": canon_b,
        },
        "caveats": caveats,
    }


RUN_ORDER_NOTES = {
    "fsharp": (
        "Run order: Arm B ran first (reps 1–3), then Arm A (reps 1–3). "
        "Arm A may have benefited from warmer proxy cache."
    ),
    "scala": (
        "Run order: Arm B ran first (reps 1–3), then Arm A (reps 1–3). "
        "Arm A may have benefited from warmer proxy cache."
    ),
    "rust": (
        "Run order: Arm A ran first (reps 2–3; rep 1 is Phase-12 pilot), "
        "then Arm B (reps 2–3; rep 1 is Phase-12 pilot). "
        "Run-1 JSONLs are from the Phase-12 pilot (separate session)."
    ),
}


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate per-run metrics into per-arm and per-example outputs."
    )
    parser.add_argument(
        "--base",
        required=True,
        help="Path to captured-planning/<lang> directory (e.g. captured-planning/fsharp)",
    )
    parser.add_argument(
        "--example",
        required=True,
        choices=["fsharp", "rust", "scala"],
        help="Example name",
    )
    args = parser.parse_args()

    base = args.base
    example = args.example

    print(f"Aggregating {example} ...")

    # Build arm-level metrics
    for arm in ["arm-a", "arm-b"]:
        arm_data = build_arm_metrics(base, arm, example)
        out_path = os.path.join(base, arm, "metrics.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(arm_data, f, indent=2, ensure_ascii=False)
        print(f"  Wrote {out_path} (n={arm_data['n']})")
        ct = arm_data["canonical_tests_aggregate"]
        for tname, trec in ct.items():
            print(f"    {tname}: {trec['pass_fraction_label']}")

    # Build comparison
    arm_a_list = load_run_metrics(base, "arm-a")
    arm_b_list = load_run_metrics(base, "arm-b")
    run_order_note = RUN_ORDER_NOTES.get(example, "Run order: see 13-02-RUN-NOTES.md.")
    comp = build_comparison(arm_a_list, arm_b_list, example, run_order_note)
    comp_path = os.path.join(base, "comparison.json")
    with open(comp_path, "w", encoding="utf-8") as f:
        json.dump(comp, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {comp_path}")

    # Print delta summary
    print(f"  Deltas (A minus B) on medians:")
    for key, delta in comp["deltas_a_minus_b"].items():
        print(f"    {key}: {delta}")


if __name__ == "__main__":
    main()
