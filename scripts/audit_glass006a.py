"""Read-only peer audit; recompute gates, not eigenvalues or historical provenance."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = {"nom": (500, 150.0), "A": (800, 150.0), "B": (700, 200.0)}


def effective_radius(radius_um, count, extent_um):
    """Face bounding the center-sampled core of the retained FD operator."""
    h = extent_um / count
    return sum((j + 0.5) * h < radius_um for j in range(count)) * h


def audit(peer, own):
    rows = []
    for case in peer["cases"]:
        configs = list(case["configs"].values())
        modes = [c for c in configs if "gamma_im" in c]
        if not modes:
            rows.append(dict(a_um=case["a_um"], t_um=case["t_um"], dn=case["dn"],
                             selected_mode=False))
            continue
        if len(modes) != 3:
            raise ValueError("incomplete matched-mode configurations")
        loss = [c["loss_dB_per_cm"] for c in modes]
        reals = [c["gamma_re"] for c in modes]
        if not all(math.isfinite(v) for v in loss + reals):
            raise ValueError("non-finite mode")
        for c in modes:
            if not math.isclose(c["loss_dB_per_cm"], 2 * c["gamma_im"] * 4.343e-2,
                                rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError("signed loss conversion")
        absolute = max(loss) - min(loss)
        relative = absolute / max(abs(sum(loss) / 3), 1e-12)
        re_delta = max(reals) - min(reals)
        re_relative = re_delta / abs(sum(reals) / 3)
        sign = all(c["gamma_im"] >= 0 for c in modes)
        gate = (relative < 0.10 or absolute < 0.005) and re_relative < 0.01
        if sign != case["G1_sign"] or gate != case["G2_conv"]:
            raise ValueError("reported gate differs from strict sign/convergence")
        rows.append(dict(a_um=case["a_um"], t_um=case["t_um"], dn=case["dn"],
                         selected_mode=True, signed_decay=sign, G2=gate,
                         re_relative=re_relative, loss_relative=relative,
                         re_delta_per_m=re_delta,
                         phase_spread_at_2mm_rad=re_delta * .002,
                         min_reported_unweighted_overlap=min(c["overlap"] for c in modes)))
    tunnel = []
    for g in peer["G3_tunnel"]:
        cases = [next(c for c in peer["cases"] if c["a_um"] == g["a_um"]
                      and c["dn"] == g["dn"] and c["t_um"] == t)
                 for t in (g["t1"], g["t2"])]
        if not all(c["G2_conv"] for c in cases):
            raise ValueError("tunnel uses non-converged case")
        first, second = [c["configs"]["nom"] for c in cases]
        k0 = 2 * math.pi / 1550e-9
        kappa = math.sqrt(2 * k0 * 1.444 * (first["gamma_re"] - k0 * g["dn"]))
        predicted = math.exp(2 * kappa * (g["t2"] - g["t1"]) * 1e-6)
        observed = first["loss_dB_per_cm"] / second["loss_dB_per_cm"]
        if min(first["loss_dB_per_cm"], second["loss_dB_per_cm"]) <= .005:
            raise ValueError("tunnel below preregistered loss floor")
        passed = .5 < observed / predicted < 2
        if not (math.isclose(observed, g["ratio_obs"], rel_tol=1e-12)
                and math.isclose(predicted, g["ratio_pred"], rel_tol=1e-12)
                and passed == g["within_x2"]):
            raise ValueError("tunnel recomputation")
        tunnel.append(dict(**g, recomputed=True))
    baseline = next(c for c in own["cases"] if c["name"] == "continuous")["core_power_fraction_input"]
    g4 = peer["G4"]
    delta = abs(g4["radial"] - baseline)
    if not (math.isclose(baseline, g4["codex_bpm_continuous"], abs_tol=1e-15)
            and math.isclose(delta, g4["abs_diff"], abs_tol=1e-15)
            and (delta < .03) == g4["pass_"]):
        raise ValueError("G4 baseline/gate")
    selected = [r for r in rows if r["selected_mode"]]
    return dict(scope="saved numeric gates only; no new eigenvalue solve or historical execution certification",
                cases=len(rows), selected_modes=len(selected),
                strict_signed_decay_pass=sum(r["signed_decay"] for r in selected),
                convergence_pass=sum(r["G2"] for r in selected), cases_detail=rows,
                tunnel=tunnel, G4=dict(g4, own_baseline_verified=True),
                discrete_core_faces_um={str(a): {name: effective_radius(a, *cfg)
                                                 for name, cfg in CONFIGS.items()}
                                       for a in (6.0, 10.0)},
                interpretation="profile sampling changes physical core faces between configurations; cause hypothesis, not isolated proof")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    target = args.out.resolve()
    if not target.is_relative_to(ROOT / "resultados/codex"):
        parser.error("output must remain under own results")
    start = time.monotonic()
    paths = ["experimentos/glass006a_claude/resultados.json",
             "experimentos/glass006a_claude/resultados_v0_signo_contrato.json",
             "experimentos/glass006a_claude/CONTRACT.md",
             "experimentos/glass006a_claude/ERRATA.md",
             "experimentos/glass006a_claude/run006a.py",
             "experimentos/glass005_claude/radial_ecs.py",
             "resultados/codex/glass007_complete_v1.json"]
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
    peer = json.loads((ROOT / paths[0]).read_text(encoding="utf-8"))
    if peer["contract_sha256"] != hashes[paths[2]] or peer["radial_ecs_sha256"] != hashes[paths[5]]:
        raise ValueError("current input hashes differ from peer report")
    result = audit(peer, json.loads((ROOT / paths[-1]).read_text(encoding="utf-8")))
    result["input_sha256"] = hashes
    result["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["elapsed_s"] = time.monotonic() - start
    if result["elapsed_s"] > 30:
        raise TimeoutError("CPU audit budget")
    for p, sha in hashes.items():
        if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != sha:
            raise ValueError("concurrent input mutation")
    with target.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({k: result[k] for k in ("cases", "selected_modes", "strict_signed_decay_pass",
                                           "convergence_pass", "discrete_core_faces_um", "elapsed_s")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
