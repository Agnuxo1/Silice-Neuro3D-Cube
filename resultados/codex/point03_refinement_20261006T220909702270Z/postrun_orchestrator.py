"""Retain the Stage B assessment and independently audit checkpoint chains."""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
import sys
import time

ROOT=Path(r"D:\PROJECTS\Silice-Neuro3D-Cube-work-20261006")
OUT=ROOT/"resultados/codex/point03_refinement_20261006T220909702270Z"
START=time.monotonic()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path,data):
    with path.open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(data,handle,indent=2,allow_nan=False)
        handle.write("\n")


report={"schema":"silice.point03-postrun.v1","status":"running"}
try:
    executions=list(OUT.glob("execution_*.json"))
    assert len(executions)==1, "Expected one complete execution, not a silently selected attempt."
    execution_path=executions[0]
    execution=read(execution_path)
    assert execution["status"]=="completed" and execution["operational_pass"]
    assessment_path=OUT/"assessment.json"
    command=[sys.executable,"-B","-u",str(ROOT/"scripts/assess_point03_refinement.py"),
             "--execution",str(execution_path),"--out",str(assessment_path)]
    result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=40)
    for label,raw in (("stdout",result.stdout),("stderr",result.stderr)):
        with (OUT/("assessment."+label+".log")).open("xb") as handle:
            handle.write(raw)
    report["assessor_returncode"]=result.returncode
    assert result.returncode in (0,2), "Assessment found invalid evidence; inspect its report."
    assessment=read(assessment_path)
    assert assessment["integrity_pass"] and assessment["operational_pass"]
    chains=[]
    for reference in execution["case_reports"]:
        case=read(reference["path"])
        assert sha(reference["path"])==reference["sha256"]
        current=Path(case["last_checkpoint_path"])
        expected=case["last_checkpoint_sha256"]
        end=case["steps_target"]
        seen=set()
        chain=[]
        while current:
            assert current not in seen and current.parent==Path(reference["path"]).parent
            seen.add(current)
            assert sha(current)==expected
            checkpoint=read(current)
            assert checkpoint["status"]=="checkpoint_completed"
            assert checkpoint["case_id"]==case["case_id"]
            assert checkpoint["manifest_sha256"]==execution["manifest_sha256"]
            assert checkpoint["input_npz_sha256"]==case["input_npz_sha256"]
            assert checkpoint["steps_done"]==end and 1<=end-checkpoint["steps_start"]<=200
            assert checkpoint["elapsed_s"]<=35 and checkpoint["numeric_valid"]
            field=Path(checkpoint["final_npz_path"])
            assert field.parent==current.parent and sha(field)==checkpoint["final_npz_sha256"]
            chain.append({"report_path":str(current),"report_sha256":expected,
                          "field_path":str(field),"field_sha256":checkpoint["final_npz_sha256"],
                          "steps_start":checkpoint["steps_start"],"steps_done":end})
            end=checkpoint["steps_start"]
            previous=checkpoint["previous_checkpoint_path"]
            expected=checkpoint["previous_checkpoint_sha256"]
            if previous is None:
                assert expected is None and end==0
                current=None
            else:
                assert end>0 and expected
                current=Path(previous)
        completed_files={p for p in Path(reference["path"]).parent.glob("chunk_*.json")
                         if read(p).get("status")=="checkpoint_completed"}
        assert completed_files==seen, "Unused or disconnected completed checkpoints."
        chains.append({"case_id":case["case_id"],"checkpoints":list(reversed(chain)),"chain_pass":True})
    assert all(child["returncode"]==0 and child["elapsed_s"]<=40 for child in execution["children"])
    report.update(status="passed",execution_path=str(execution_path),execution_sha256=sha(execution_path),
                  assessment_path=str(assessment_path),assessment_sha256=sha(assessment_path),chains=chains,
                  checkpoint_count=sum(len(c["checkpoints"]) for c in chains),
                  tracked_inputs_unchanged=execution["tracked_inputs_unchanged"],
                  tracked_file_count=len(execution["tracked_sha256_before"]))
    compact={key:assessment[key] for key in ("status","scientific_pass","operational_pass","integrity_pass",
        "primary_grids","primary_core_powers","signed_differences","candidate_observed_orders",
        "relative_order_disagreement","holdout","auxiliary","auxiliary_sum_both_grids","auxiliary_maximum_sum",
        "gates","accepted_gci","historical_Q4_replaced")}
    compact["cases"]=[{k:row[k] for k in ("case_id","N","profile_samples","dz_m","steps_completed","P0","P_final","P_core","maximum_metric_absolute_error")} for row in assessment["cases"]]
    compact.update(execution_elapsed_s=execution["elapsed_s"],child_count=len(execution["children"]),
                   maximum_child_elapsed_s=max(c["elapsed_s"] for c in execution["children"]),
                   tracked_file_count=report["tracked_file_count"],checkpoint_count=report["checkpoint_count"],
                   assessment_elapsed_s=assessment["elapsed_s"],assessment_sha256=report["assessment_sha256"])
    save(OUT/"compact_result.json",compact)
    with (OUT/"cases.csv").open("x",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=list(compact["cases"][0]))
        writer.writeheader()
        writer.writerows(compact["cases"])
    print(json.dumps(compact))
except Exception as error:
    report.update(status="failed",error_type=type(error).__name__,error=str(error))
report["elapsed_s"]=time.monotonic()-START
save(OUT/"checkpoint_audit.json",report)
with (OUT/"postrun_orchestrator.py").open("xb") as handle:
    handle.write(Path(__file__).read_bytes())
print(json.dumps({"postrun_status":report["status"],"error":report.get("error"),"elapsed_s":report["elapsed_s"]}))
raise SystemExit(0 if report["status"]=="passed" else 1)
