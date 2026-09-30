"""Read-only evidence audit: lineage, budgets and gates, not a second solver."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]


def audit(report):
    if report.get("status")!="completed_two_bounded_jobs":raise ValueError("incomplete report")
    parent_path=(ROOT/report["parent_report"]).resolve()
    if not parent_path.is_relative_to(ROOT/"resultados/codex"):raise ValueError("parent outside results")
    if hashlib.sha256(parent_path.read_bytes()).hexdigest()!=report["parent_sha256"]:
        raise ValueError("parent hash mismatch")
    parent=json.loads(parent_path.read_text(encoding="utf-8"))
    if report["cases"][:len(parent["cases"])]!=parent["cases"]:raise ValueError("reused cases altered")
    if len(report["cases"])!=10 or len({c["name"] for c in report["cases"]})!=10:
        raise ValueError("case count/uniqueness")
    for rel,sha in report["hashes_before"].items():
        path=(ROOT/rel).resolve()
        if not path.is_relative_to(ROOT) or hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise ValueError("source hash mismatch")
    for c in report["cases"]:
        balance=abs(c["input_power"]-c["output_power"]-c["material_removed"]-c["boundary_removed"])/c["input_power"]
        if balance>=1e-10:raise ValueError("power balance")
        core=c["core_fraction_remaining"]*c["output_power"]/c["input_power"]
        if abs(core-c["core_power_fraction_input"])>1e-12:raise ValueError("core normalization")
        if not 0<=core<=1 or c["material_removed"]<0 or c["boundary_removed"]<0:
            raise ValueError("passive bounds")
        if not c["core_untouched"] or not c["outside_untouched"]:raise ValueError("profile bounds")
    cases={c["name"]:c for c in report["cases"]}
    for gate in report["gates"]:
        ref=cases[gate["reference"]]["core_power_fraction_input"]
        candidate=cases[gate["candidate"]]["core_power_fraction_input"]
        absolute=abs(candidate-ref);relative=absolute/abs(ref) if ref else None
        flag=ref>=1e-6 and absolute<0.005 and relative<0.1
        if gate["gate"]!=flag or abs(gate["absolute"]-absolute)>1e-12:
            raise ValueError("gate recomputation")
    return dict(cases=10,gates=4,partial_case_lineage=True,
                complete_sha256_sources=True,power_normalization=True,
                scope="report invariants only, NOT independent wave solver")


def main():
    parser=argparse.ArgumentParser();parser.add_argument("report",type=Path)
    args=parser.parse_args();path=args.report.resolve()
    if not path.is_relative_to(ROOT/"resultados/codex"):parser.error("report under own results only")
    result=audit(json.loads(path.read_text(encoding="utf-8")))
    result["report_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps(result));return 0


if __name__=="__main__":sys.exit(main())
