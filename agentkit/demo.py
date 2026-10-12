"""Generate bounded manufactured controls; no data are physical measurements."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.linalg import expm

from agentkit.evidence import canonical, write_new_json
from agentkit.mesh import compile_passive
from agentkit.metrology import fit_cutback, system_energy
from agentkit.numerics import (coherent_decomposition, exact_discrete_transport,
                               generalized_modes, optical_error_budget,
                               splitting_control, spatial_forecast, spatial_holdout)
from agentkit.paraxial import grid, disk_area_weights


def run_demo(directory: Path) -> dict:
    """Create explicit control inputs and reports in a fresh directory."""
    if directory.exists():
        raise FileExistsError("Manufactured-control directory must be new")
    directory.mkdir(parents=True)
    (x, y), dx = grid(32, 64e-6)
    field = np.exp(-(x*x+y*y)/(6e-6)**2).astype(np.complex128)
    field /= np.sqrt(np.sum(abs(field)**2)*dx*dx)
    radius = np.hypot(x, y)
    profile = np.where((radius >= 6e-6) & (radius < 12e-6), -0.005, 0.0)
    with (directory/"paraxial_input.npz").open("xb") as output:
        np.savez_compressed(output, field=field, delta_n=profile)
    write_new_json(directory/"paraxial_config.json",
                   {"width_m": 64e-6, "wavelength_m": 1550e-9,
                    "n_reference": 1.444, "length_m": 100e-6, "steps": 32})
    a = 1j*np.array([[0.2, 0.5], [0.5, -0.3]])
    b = 1j*np.diag([0.7, -0.2])
    split = [splitting_control(a, b, np.array([1, 1j])/np.sqrt(2), 1.0, n)
             for n in (4, 8, 16)]
    operator = np.array([[1, 4], [0, 2]], dtype=complex)
    modes = generalized_modes(operator, np.ones(2))
    decomposition = coherent_decomposition(np.array([0.3, 0.7j]),
                                           modes["right"][:, :1], np.ones(2),
                                           modes["left"][:, :1])
    target = expm(1j*np.array([[0.2, 0.4], [0.4, -0.1]])) @ np.diag([0.8, 0.5])
    with (directory/"target.npz").open("xb") as output:
        np.savez_compressed(output, target=target)
    compiled = compile_passive(target)
    source = np.array([[0, 0], [1, 0], [0, 1], [1, 1]], dtype=float)
    transport = exact_discrete_transport(source, np.full(4, 0.25),
                                         source+np.array([0.1, 0.0]), np.full(4, 0.25))
    h = np.array([1, 0.8, 0.64, 0.512])
    powers = 0.333 + 0.002*h**2
    forecast = spatial_forecast(powers[:3], np.full(3, 1e-10))
    holdout = spatial_holdout(powers[:3], np.full(3, 1e-10), powers[3],
                             1e-10, 1e-10, 1e-10)
    rows = []
    for chip, slope in enumerate((0.09, 0.10, 0.11)):
        for length_cm in (1, 2, 3, 4):
            loss_db = 0.4 + slope*length_cm
            rows.append({"chip_id": str(chip), "guide_id": "manufactured",
                         "length_m": length_cm/100, "wavelength_m": 1550e-9,
                         "polarization": "x", "input_power_w": 1e-3,
                         "output_power_w": 1e-3*10**(-loss_db/10), "sigma_loss_db": 0.005})
    with (directory/"manufactured_cutback.csv").open("x", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    energy_rows = [{"time_s": i, "completed_inferences": i*1000,
                    "source_w": 1, "modulation_w": 0.2, "detection_w": 0.1,
                    "control_w": 0.3, "cooling_w": 0.4} for i in range(3)]
    summary = {"scope": "manufactured_controls_only",
               "splitting_errors": [s["relative_field_error"] for s in split],
               "coherent_balance_error": decomposition["balance_error"],
               "coherent_cross_power": decomposition["cross_power"],
               "compiler_error": compiled["reconstruction_error"],
               "transport_wasserstein2": transport["wasserstein2"],
               "forecast": forecast, "holdout": holdout,
               "optical_path_budget": optical_error_budget(1.444, 0.01, 1550e-9, 1e-6, 1e-9),
               "detector_area_m2": float(disk_area_weights(32, 64e-6, 6e-6, 16).sum()),
               "manufactured_cutback": fit_cutback(rows),
               "manufactured_energy": system_energy(energy_rows)}
    write_new_json(directory/"summary.json", summary)
    write_new_json(directory/"S16_manufactured.json",
                   {"observables": {"quadratic_field": {
                       "powers": powers[:3].tolist(), "temporal_errors": [1e-10]*3},
                       "linear_intensity": {"powers": powers[:3].tolist(),
                                            "temporal_errors": [1e-10]*3}}})
    protocol = {"experiment_id": "manufactured_controls_v1", "task_id": "T01",
                "scope": "manufactured_control", "model": "analytic_fixture",
                "units": {"length": "m", "power": "relative_to_input"},
                "criteria": [{"id": "holdout_passed", "operator": "eq", "threshold": True}],
                "resource_limits": {"cpu_threads": 1, "seconds": 40, "gpu": False},
                "heldout_policy": "Known analytic law; never used as a T96 result"}
    write_new_json(directory/"protocol.json", protocol)
    protocol_hash = hashlib.sha256(canonical(protocol)).hexdigest()
    result = {"experiment_id": protocol["experiment_id"], "scope": protocol["scope"],
              "protocol_sha256": protocol_hash, "status": "completed",
              "artifacts": ["summary.json"],
              "metrics": {"holdout_passed": bool(holdout["passed"])}}
    # This result is an explicit schema fixture, not a prospective research receipt.
    write_new_json(directory/"result_schema_fixture.json", result)
    return summary


def main() -> None:
    """Run the manufactured demonstration without importing any GPU library."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    summary = run_demo(args.directory)
    print(json.dumps({"scope": summary["scope"], "compiler_error": summary["compiler_error"],
                      "holdout_passed": summary["holdout"]["passed"]}))


if __name__ == "__main__":
    main()
