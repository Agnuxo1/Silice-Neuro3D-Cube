"""Claims ledger: one place where every public statement meets its evidence (kit v2).

A claim cannot be PASS unless evidence of its own scope exists, its bytes
match the recorded hashes, its dependencies pass (without cycles), and the
evidence kind is the one that scope demands: a simulation never closes a
physical claim, and agreement between project AI agents never counts as
external replication. Evidence kinds are declarations; each item must state
who produced it and how, and a human auditor checks those declarations.
The scopes include every scope used in agentkit/tasks.json and tasks_v2.json.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from agentkit.evidence import inside, sha256_file

STATUSES = {"OPEN", "RUNNING", "PARTIAL", "FAIL", "BLOCKED", "PASS",
            "OPEN_OBSERVATION", "WITHDRAWN"}
# scope -> evidence kinds that can close it
REQUIRED_KIND = {
    "software": {"software_test"},
    "manufactured_control": {"software_test", "simulation"},
    "numerical_model": {"simulation"},
    "numerical_wave_model": {"simulation"},
    "numerical_neural_model": {"simulation"},
    "fabricable_design": {"simulation", "design_review"},
    "measured_material": {"measurement"},
    "physical_component": {"measurement"},
    "physical_device": {"measurement"},
    "physical_system": {"measurement"},
    "physical_system_measurement": {"measurement"},
    "independent_evaluation": {"reserved_test"},
    "scientific_claim": {"measurement", "reserved_test"},
    "novelty": {"literature_search"},
    "external_replication": {"external_replication"},
    "observed_impact": {"third_party_record"},
    "decision": {"decision_record"},
    "review": {"review_record"},
}
KINDS = set().union(*REQUIRED_KIND.values())
EXTRA_FIELDS = {"measurement": ("instrument", "operator"),
                "external_replication": ("independent_team", "public_record"),
                "third_party_record": ("public_record",)}


def _cycles(by_id: dict) -> list[str]:
    """Claim ids that lie on a dependency cycle."""
    state, on_cycle = {}, set()

    def visit(node, stack):
        state[node] = 1
        stack.append(node)
        for dep in by_id[node].get("depends_on", []):
            if dep not in by_id:
                continue
            if state.get(dep) == 1:
                on_cycle.update(stack[stack.index(dep):])
            elif dep not in state:
                visit(dep, stack)
        stack.pop()
        state[node] = 2

    for node in by_id:
        if node not in state:
            visit(node, [])
    return sorted(on_cycle)


def validate(ledger: dict, root: Path) -> list[str]:
    """Return every rule violation; an empty list means the ledger is consistent."""
    problems = []
    claims = ledger.get("claims")
    if ledger.get("schema") != 1 or not isinstance(claims, list) or not claims:
        return ["Ledger must have schema 1 and a nonempty claims list"]
    agents = [str(a).strip().lower() for a in ledger.get("project_agents", []) if str(a).strip()]
    by_id = {}
    for claim in claims:
        cid = claim.get("id")
        if not cid or cid in by_id:
            problems.append(f"Missing or duplicate claim id: {cid!r}")
            continue
        by_id[cid] = claim
    for cid in _cycles(by_id):
        problems.append(f"{cid}: dependency cycle")
    for cid, claim in by_id.items():
        status, scope = claim.get("status"), claim.get("scope")
        if status not in STATUSES:
            problems.append(f"{cid}: unknown status {status!r}")
        if scope not in REQUIRED_KIND:
            problems.append(f"{cid}: unknown scope {scope!r}")
            continue
        if not str(claim.get("statement", "")).strip():
            problems.append(f"{cid}: empty statement")
        if not str(claim.get("falsifier", "")).strip():
            problems.append(f"{cid}: a falsifier (what would refute it) is required")
        if status == "WITHDRAWN" and not str(claim.get("withdrawal_reason", "")).strip():
            problems.append(f"{cid}: withdrawn claims keep their reason")
        valid_matching = 0
        for item in claim.get("evidence", []):
            kind, path = item.get("kind"), item.get("path")
            if kind not in KINDS:
                problems.append(f"{cid}: unknown evidence kind {kind!r}")
                continue
            missing = [f for f in ("produced_by", "how", *EXTRA_FIELDS.get(kind, ()))
                       if not str(item.get(f, "")).strip()]
            if missing:
                problems.append(f"{cid}: evidence {path!r} lacks {', '.join(missing)}")
                continue
            if kind in ("external_replication", "third_party_record") and agents:
                named = (str(item.get("independent_team", "")) + " " +
                         str(item.get("produced_by", ""))).lower()
                if any(agent in named for agent in agents):
                    problems.append(f"{cid}: project agents cannot provide {kind}")
                    continue
            try:
                resolved = inside(root, path)
            except (ValueError, TypeError, OSError):
                problems.append(f"{cid}: evidence path missing or unsafe: {path!r}")
                continue
            if not resolved.is_file() or sha256_file(resolved) != item.get("sha256"):
                problems.append(f"{cid}: evidence bytes missing or changed: {path}")
                continue
            if kind in REQUIRED_KIND[scope]:
                valid_matching += 1
        for dep in claim.get("depends_on", []):
            if dep not in by_id:
                problems.append(f"{cid}: unknown dependency {dep}")
            elif status == "PASS" and by_id[dep].get("status") != "PASS":
                problems.append(f"{cid}: PASS requires dependency {dep} to PASS")
        if status == "PASS" and valid_matching == 0:
            needed = ", ".join(sorted(REQUIRED_KIND[scope]))
            problems.append(f"{cid}: PASS requires verified evidence of kind {needed}")
    return problems


def render_table(ledger: dict) -> str:
    """Markdown status table; statements are shown as written, never upgraded."""
    cell = lambda value: " ".join(str(value).split()).replace("|", "/")
    lines = ["| Id | Scope | Status | Statement | Falsifier | Evidence | Limitations | Next action |",
             "|---|---|---|---|---|---|---|---|"]
    for claim in ledger["claims"]:
        evidence = "; ".join(f"{e.get('kind')}: {e.get('path')}" for e in claim.get("evidence", []))
        lines.append("| " + " | ".join(cell(v) for v in (
            claim["id"], claim["scope"], claim["status"], claim.get("statement", ""),
            claim.get("falsifier", ""), evidence or "none", claim.get("limitations", ""),
            claim.get("next_action", ""))) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    """Validate a ledger; write the rendered table only if the ledger is consistent."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--table")
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    problems = validate(ledger, args.root.resolve())
    if args.table and not problems:
        with Path(args.table).open("x", encoding="utf-8") as stream:
            stream.write(render_table(ledger))
    print(json.dumps({"consistent": not problems, "problems": problems,
                      "table_written": bool(args.table and not problems)},
                     ensure_ascii=False, indent=1))
    if problems:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
