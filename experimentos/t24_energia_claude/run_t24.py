"""T24 energy kill test: optoelectronic dense layer versus cited digital references.

Reads parameter files whose every value carries a provenance string, then
evaluates agentkit.limits.layer_budget at the preregistered primary point
(N = M = 64, 8 bits, 1 GS/s) and on a declared sensitivity grid. Outputs are
parametric budgets, never measurements. See PROTOCOL-T24.json.

Usage (from the repository root):
  python -B experimentos/t24_energia_claude/run_t24.py --out resultados/agent/t24_energy_20261012/budget.json
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agentkit.evidence import sha256_file, write_new_json  # noqa: E402
from agentkit.limits import layer_budget, max_depth  # noqa: E402

HERE = Path(__file__).resolve().parent
LAYER_KEYS = ("wavelength_m", "quantum_efficiency", "optical_transmission",
              "laser_wall_plug_efficiency", "modulator_energy_j", "dac_energy_j",
              "adc_energy_j", "static_power_w", "current_noise_a_rthz")
PRIMARY = {"n": 64, "bits": 8, "rate": 1e9}
GRID = {"n": (16, 64, 256), "bits": (4, 6, 8), "rate": (1e9, 1e10)}


def load(name: str) -> dict:
    path = HERE / name
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path), "data": data}


def sourced(params: dict) -> list[str]:
    """Names of parameters without a nonempty provenance string."""
    provenance = params.get("provenance", {})
    names = [*params["layer"], *params.get("depth", {}), *params.get("programmable", {})]
    return [k for k in names if not str(provenance.get(k, "")).strip()]


def budget(layer: dict, n: int, bits: int, rate: float, reference: float, static_w: float) -> dict:
    kwargs = {k: layer[k] for k in LAYER_KEYS}
    kwargs["static_power_w"] = static_w
    result = layer_budget(n_inputs=n, n_outputs=n, bits=bits, sample_rate_hz=rate,
                          digital_reference_j_per_mac=reference, **kwargs)
    return {"n": n, "bits": bits, "sample_rate_hz": rate, "static_power_w": static_w,
            "joules_per_mac": result["joules_per_mac"],
            "components_per_frame_j": result["components_per_frame_j"],
            "dominant_component": result["dominant_component"],
            "advantage_factor": result["advantage_factor"],
            "detector_photons": result["detector"]["photons"],
            "thermal_sigma_electrons": result["detector"]["thermal_sigma_electrons"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Output path must be new")
    sets = {"nominal": load("params_nominal.json"), "optimistic": load("params_optimistic.json")}
    references = load("digital_references.json")
    refs = {k: float(v["j_per_mac"]) for k, v in references["data"]["references"].items()}
    missing = {name: sourced(item["data"]) for name, item in sets.items()}
    report = {"scope": "parametric_budget_not_measurement",
              "inputs": {name: {"path": item["path"], "sha256": item["sha256"]}
                         for name, item in {**sets, "references": references}.items()},
              "primary_point": PRIMARY, "references_j_per_mac": refs,
              "unsourced_parameters": missing, "primary": {}, "programmable_variant": {},
              "max_depth": {}, "sweep": []}
    for name, item in sets.items():
        params = item["data"]
        layer = params["layer"]
        report["primary"][name] = {ref: budget(layer, PRIMARY["n"], PRIMARY["bits"], PRIMARY["rate"],
                                               value, layer["static_power_w"])
                                   for ref, value in refs.items()}
        prog = params["programmable"]
        n = PRIMARY["n"]
        shifters = n * (n - 1)  # two per MZI in a Clements mesh of N(N-1)/2 MZIs
        static_prog = shifters * prog["mean_heater_power_w_per_shifter"] + layer["static_power_w"]
        report["programmable_variant"][name] = {
            "shifters": shifters, "static_power_w": static_prog,
            **{ref: budget(layer, n, PRIMARY["bits"], PRIMARY["rate"], value, static_prog)
               for ref, value in refs.items()}}
        depth = params["depth"]
        detector_j = report["primary"][name][next(iter(refs))]["detector_photons"] * \
            6.62607015e-34 * 299792458.0 / layer["wavelength_m"]
        report["max_depth"][name] = {
            "available_laser_optical_w": depth["available_laser_optical_w"],
            "fixed_loss_db": depth["fixed_loss_db"], "loss_per_stage_db": depth["loss_per_stage_db"],
            "max_stages": max_depth(depth["available_laser_optical_w"], PRIMARY["rate"], n,
                                    detector_j, depth["fixed_loss_db"], depth["loss_per_stage_db"]),
            "stages_needed_clements_two_meshes": 2 * n + 1}
        for size, bits, rate in itertools.product(GRID["n"], GRID["bits"], GRID["rate"]):
            row = budget(layer, size, bits, rate, refs["modern"], layer["static_power_w"])
            row["parameter_set"] = name
            row["advantage_vs_old"] = refs["old"] / row["joules_per_mac"]
            report["sweep"].append(row)
    primary = report["primary"]
    metrics = {
        "all_parameters_sourced": not any(missing.values()),
        "optimistic_advantage_vs_modern": primary["optimistic"]["modern"]["advantage_factor"],
        "optimistic_advantage_vs_old": primary["optimistic"]["old"]["advantage_factor"],
        "nominal_advantage_vs_modern": primary["nominal"]["modern"]["advantage_factor"],
        "nominal_advantage_vs_old": primary["nominal"]["old"]["advantage_factor"]}
    adv = metrics["optimistic_advantage_vs_modern"]
    if metrics["optimistic_advantage_vs_old"] <= 1:
        verdict = "H-A discarded: the optimistic case does not beat even the lenient reference."
    elif adv < 1:
        verdict = "H-A withdrawn as headline: the optimistic case does not beat the modern reference."
    elif metrics["nominal_advantage_vs_modern"] < 1:
        verdict = "H-A conditional: only the optimistic parameter set beats the modern reference."
    else:
        verdict = "H-A survives as a candidate: both parameter sets beat the modern reference."
    report["metrics"] = metrics
    report["verdict_by_registered_rule"] = verdict
    write_new_json(args.out, report)
    print(json.dumps({"metrics": metrics, "verdict": verdict}, indent=1))


if __name__ == "__main__":
    main()
