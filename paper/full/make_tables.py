"""Render the supplementary tables of the full paper from committed records.

Inputs (read-only):
  Docs/CIERRE-20261012/CLAIMS-LEDGER-20261013-final.json   (claims ledger)
  resultados/agent/prereg/*_commitment.json, *_audit.json   (preregistration)
  resultados/agent/prereg/T25_attempt1_status.json          (retained failure)

Outputs: paper/full/tables/tab_claims.tex and tab_protocols.tex. The text of
each claim is reproduced as recorded; nothing is reworded or upgraded.

  python -B paper/full/make_tables.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "tables"

# Order matters: braces are escaped before any replacement that inserts braces.
REPLACE = [("\\", r"\textbackslash"), ("{", r"\{"), ("}", r"\}"), ("&", r"\&"), ("%", r"\%"),
           ("$", r"\$"), ("#", r"\#"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
           (r"\textbackslash", r"\textbackslash{}"), ("_", r"\_\allowbreak{}")]


def tex(text: str) -> str:
    """Escape LaTeX specials, then typeset a few plain-text math tokens."""
    out = str(text)
    for a, b in REPLACE:
        out = out.replace(a, b)
    for a, b in ((" <= ", r" $\le$ "), (" >= ", r" $\ge$ "), ("<=", r"$\le$"), (">=", r"$\ge$"),
                 (" < ", r" $<$ "), (" > ", r" $>$ "), ("+/-", r"$\pm$"), (" deg", r"$^\circ$")):
        out = out.replace(a, b)
    out = out.replace("/", r"/\allowbreak{}")
    return out


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def claims_table() -> str:
    ledger = load(ROOT / "Docs/CIERRE-20261012/CLAIMS-LEDGER-20261013-final.json")
    lines = [r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{2.35cm}>{\raggedright\arraybackslash}p{13.2cm}@{}}",
             r"\caption{Full claims ledger after the adversarial review (%d claims; stage \texttt{%s}). "
             r"Statements, falsifiers and limitations are reproduced as recorded in "
             r"\texttt{Docs/CIERRE-20261012/CLAIMS-LEDGER-20261013-final.json}; evidence items carry SHA-256 "
             r"hashes in that file.}\label{tab:claims}\\" % (len(ledger["claims"]), ledger["stage"]),
             r"\toprule Claim, scope, status & Statement, falsifier, evidence, limitations and next action \\ \midrule \endfirsthead",
             r"\toprule Claim, scope, status & Statement, falsifier, evidence, limitations and next action \\ \midrule \endhead",
             r"\bottomrule \endfoot"]
    for claim in ledger["claims"]:
        evidence = "; ".join("%s: \\texttt{%s}" % (tex(e["kind"]), tex(e["path"])) for e in claim.get("evidence", []))
        parts = [r"\textbf{Statement.} " + tex(claim["statement"]),
                 r"\textbf{Falsifier.} " + tex(claim["falsifier"]),
                 r"\textbf{Evidence.} " + (evidence or "none")]
        if claim.get("limitations"):
            parts.append(r"\textbf{Limitations.} " + tex(claim["limitations"]))
        if claim.get("withdrawal_reason"):
            parts.append(r"\textbf{Withdrawal reason.} " + tex(claim["withdrawal_reason"]))
        if claim.get("depends_on"):
            parts.append(r"\textbf{Depends on.} " + tex(", ".join(claim["depends_on"])))
        if claim.get("next_action"):
            parts.append(r"\textbf{Next action.} " + tex(claim["next_action"]))
        head = r"\textbf{%s}\newline \texttt{%s}\newline %s" % (tex(claim["id"]), tex(claim["scope"]), tex(claim["status"]))
        lines.append(head + " & " + r" \newline ".join(parts) + r" \\ \addlinespace[2pt]")
    lines.append(r"\end{longtable}")
    return "\n".join(lines) + "\n"


def protocols_table() -> str:
    prereg = ROOT / "resultados/agent/prereg"
    order = [("T25", "T25_commitment.json", None), ("T25r2", "T25r2_commitment.json", "T25r2_audit.json"),
             ("T24", "T24_commitment.json", "T24_audit.json"), ("T26", "T26_commitment.json", "T26_audit.json"),
             ("T27", "T27_commitment.json", "T27_audit.json"), ("T20D", "T20D_commitment.json", "T20D_audit.json")]
    rows = []
    for label, commit_file, audit_file in order:
        record = load(prereg / commit_file)
        protocol = load(ROOT / record["protocol_path"])
        if audit_file:
            audit = load(prereg / audit_file)
            n_ok = sum(1 for c in audit["checks"] if c["passed"])
            verdict = "%s (%d/%d criteria; integrity checks %s)" % (
                "PASS" if audit["passed"] else "FAIL", n_ok, len(audit["checks"]),
                "clean" if not any(audit[k] for k in ("artifacts_present_at_commitment", "unplanned_artifacts",
                                                       "artifacts_added_outside_commitment_descendants",
                                                       "other_protocol_versions_same_experiment")) else "flagged")
        else:
            status = load(prereg / "T25_attempt1_status.json")
            verdict = "attempt 1 %s; superseded by r2" % status["status"].replace("_", " ")
        sha = record["protocol_sha256"]
        rows.append(r"%s & \texttt{%s} & \texttt{%s} & %s & \texttt{%s} & %s & %s \\" % (
            label, tex(protocol["experiment_id"]), record["commit"][:7], tex(record["commit_time_iso"].replace("T", " ")),
            r"\allowbreak ".join(sha[i:i + 16] for i in range(0, 64, 16)),
            "yes (server)" if record["published_at_commitment"] and record["published_check"] == "server" else "no",
            tex(verdict)))
    head = [r"\begin{table}[htbp]\centering\scriptsize",
            r"\caption{Preregistered protocols, commitment records and audits. Commit: abbreviated git commit "
            r"that contains the protocol; time: commit time (self-recorded, UTC+02:00); SHA-256: hash of the "
            r"canonical protocol JSON; published: whether \texttt{git ls-remote} showed the commit on the "
            r"server branch \texttt{origin/agent/scientific-closure-20261012} before any result. Source: "
            r"\texttt{resultados/agent/prereg/}.}\label{tab:protocols}",
            r"\setlength{\tabcolsep}{3pt}",
            r"\begin{tabular}{@{}l>{\raggedright\arraybackslash}p{2.7cm}l>{\raggedright\arraybackslash}p{1.95cm}"
            r">{\raggedright\arraybackslash}p{2.45cm}>{\raggedright\arraybackslash}p{1.3cm}"
            r">{\raggedright\arraybackslash}p{2.75cm}@{}}",
            r"\toprule Test & Experiment id & Commit & Time & Protocol SHA-256 & Published & Audit \\ \midrule"]
    return "\n".join(head + rows + [r"\bottomrule\end{tabular}\end{table}"]) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tab_claims.tex").write_text(claims_table(), encoding="utf-8")
    (OUT / "tab_protocols.tex").write_text(protocols_table(), encoding="utf-8")
    print(sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
