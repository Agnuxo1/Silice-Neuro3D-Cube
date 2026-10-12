"""Blind analysis of cutback measurements with a hidden slope offset (kit v2).

Roles: a custodian (a person, or an agent that does not analyse) creates a
secret offset and publishes only its SHA-256 commitment in the protocol.
The custodian blinds the raw CSV; analysts develop the whole analysis on
blinded data and record a freeze that names the blinded report hash; only
then is the secret revealed. Multiplying each output power by
10**(-offset*L_cm/10) adds exactly `offset` dB/cm to every fitted slope and
leaves residuals, intercepts and interval widths unchanged.

Two leaks are handled explicitly:
- Quantization: blinded powers are rounded to the declared number of
  significant digits of the instrument record, so the hidden factor cannot
  be recovered by snapping values back onto the original grid. The rounding
  perturbs unblinded results at that resolution only.
- Tails: any bounded offset uniform in [-s, s] reveals the verdict with
  probability at most |mu - U| / (2 s) (mu true slope, U threshold). Choose
  s much larger than the decision range; negative blinded slopes (apparent
  gain) are expected and are not anomalies.
See Klein and Roodman, Annu. Rev. Nucl. Part. Sci. 55, 141 (2005).
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import secrets
import subprocess

from agentkit.evidence import canonical, sha256_file, utc_now, write_new_json


def create_secret(path: Path, scale_db_per_cm: float) -> dict:
    """Draw an unpredictable offset in [-scale, scale] and return its commitment."""
    if not math.isfinite(scale_db_per_cm) or scale_db_per_cm <= 0:
        raise ValueError("Blinding scale must be positive")
    generator = secrets.SystemRandom()
    record = {"kind": "additive_slope_offset", "units": "dB/cm",
              "offset_db_per_cm": generator.uniform(-scale_db_per_cm, scale_db_per_cm),
              "salt": secrets.token_hex(16), "created_utc": utc_now()}
    data = canonical(record) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return {"commitment_sha256": hashlib.sha256(data).hexdigest(),
            "scale_db_per_cm": scale_db_per_cm, "kind": record["kind"],
            "tail_leak_bound": "P(verdict revealed) <= |mu - U| / (2 * scale)"}


def _load_secret(path: Path, commitment: str) -> float:
    if sha256_file(path) != commitment:
        raise ValueError("Secret does not match the published commitment")
    return float(json.loads(path.read_text(encoding="utf-8"))["offset_db_per_cm"])


def _round_significant(value: float, digits: int) -> float:
    return float(f"{value:.{digits - 1}e}")


def blind_rows(rows: list[dict], offset_db_per_cm: float, significant_digits: int) -> list[dict]:
    """Return blinded copies of cutback rows (custodian only)."""
    if type(significant_digits) is not int or not 2 <= significant_digits <= 17:
        raise ValueError("Declare the instrument resolution as 2 to 17 significant digits")
    out = []
    for row in rows:
        length_cm = 100 * float(row["length_m"])
        value = float(row["output_power_w"]) * 10 ** (-offset_db_per_cm * length_cm / 10)
        blinded = dict(row)
        blinded["output_power_w"] = repr(_round_significant(value, significant_digits))
        out.append(blinded)
    return out


def freeze_analysis(report_path: Path, sources: list[Path], out: Path) -> dict:
    """Record the blinded report and analysis sources before unblinding."""
    record = {"kind": "blind_analysis_freeze", "created_utc": utc_now(),
              "blinded_report_sha256": sha256_file(report_path),
              "analysis_sources": {str(p): sha256_file(p) for p in sources}}
    write_new_json(out, record)
    return record


def _is_committed(path: Path) -> bool:
    folder = path.resolve().parent
    run = lambda *a: subprocess.run(["git", "-C", str(folder), *a], capture_output=True,
                                    text=True, encoding="utf-8")
    tracked = run("ls-files", "--error-unmatch", "--", path.name).returncode == 0
    clean = run("diff", "--quiet", "HEAD", "--", path.name).returncode == 0
    return tracked and clean


def unblind_report(report: dict, offset_db_per_cm: float) -> dict:
    """Subtract the offset from every slope-valued field of a fit_cutback report."""
    result = copy.deepcopy(report)
    result["mean_loss_db_per_cm"] -= offset_db_per_cm
    result["ci95"] = [value - offset_db_per_cm for value in result["ci95"]]
    for guide in result["guides"]:
        guide["loss_db_per_cm"] -= offset_db_per_cm
    result["unblinded"] = True
    return result


def main() -> None:
    """init and blind (custodian), freeze (analyst), unblind (after a committed freeze)."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--secret", type=Path, required=True)
    init.add_argument("--scale-db-per-cm", type=float, required=True)
    init.add_argument("--commitment-out", type=Path, required=True)
    blind = commands.add_parser("blind")
    blind.add_argument("--input", type=Path, required=True)
    blind.add_argument("--secret", type=Path, required=True)
    blind.add_argument("--commitment", required=True)
    blind.add_argument("--significant-digits", type=int, required=True)
    blind.add_argument("--out", type=Path, required=True)
    freeze = commands.add_parser("freeze")
    freeze.add_argument("--report", type=Path, required=True)
    freeze.add_argument("--sources", type=Path, nargs="+", required=True)
    freeze.add_argument("--out", type=Path, required=True)
    reveal = commands.add_parser("unblind")
    reveal.add_argument("--report", type=Path, required=True)
    reveal.add_argument("--secret", type=Path, required=True)
    reveal.add_argument("--commitment", required=True)
    reveal.add_argument("--analysis-freeze", type=Path, required=True)
    reveal.add_argument("--allow-uncommitted-freeze", action="store_true")
    reveal.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "init":
        record = create_secret(args.secret, args.scale_db_per_cm)
        write_new_json(args.commitment_out, record)
        print(json.dumps({"commitment_sha256": record["commitment_sha256"]}))
    elif args.command == "blind":
        offset = _load_secret(args.secret, args.commitment)
        with args.input.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        blinded = blind_rows(rows, offset, args.significant_digits)
        with args.out.open("x", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(blinded)
        print(json.dumps({"blinded_rows": len(blinded), "input_sha256": sha256_file(args.input),
                          "significant_digits": args.significant_digits}))
    elif args.command == "freeze":
        record = freeze_analysis(args.report, args.sources, args.out)
        print(json.dumps({"blinded_report_sha256": record["blinded_report_sha256"]}))
    else:
        freeze_record = json.loads(args.analysis_freeze.read_text(encoding="utf-8"))
        if (freeze_record.get("kind") != "blind_analysis_freeze"
                or freeze_record.get("blinded_report_sha256") != sha256_file(args.report)):
            raise ValueError("The freeze record does not name this blinded report")
        committed = _is_committed(args.analysis_freeze)
        if not committed and not args.allow_uncommitted_freeze:
            raise ValueError("Commit the freeze record before unblinding")
        offset = _load_secret(args.secret, args.commitment)
        report = json.loads(args.report.read_text(encoding="utf-8"))
        result = unblind_report(report, offset)
        result.update({"analysis_freeze_sha256": sha256_file(args.analysis_freeze),
                       "analysis_freeze_committed": committed,
                       "blinded_report_sha256": sha256_file(args.report)})
        write_new_json(args.out, result)
        print(json.dumps({"mean_loss_db_per_cm": result["mean_loss_db_per_cm"], "ci95": result["ci95"]}))


if __name__ == "__main__":
    main()
