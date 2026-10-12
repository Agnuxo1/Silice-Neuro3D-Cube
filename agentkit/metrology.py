"""Cutback regression and whole-system energy calculations with explicit units."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import t

from agentkit.evidence import sha256_file, write_new_json


def fit_cutback(rows: list[dict]) -> dict:
    """Fit each cutback guide and use independent chip means for uncertainty.

    Fields: chip_id, guide_id, length_m, wavelength_m, polarization,
    input_power_w, output_power_w, sigma_loss_db. One invocation must
    represent one wavelength and one polarization.
    """
    if not rows:
        raise ValueError("No measurement rows")
    settings = {(float(r["wavelength_m"]), r["polarization"]) for r in rows}
    if len(settings) != 1:
        raise ValueError("Separate wavelengths and polarizations before fitting")
    wavelength, polarization = next(iter(settings))
    if not math.isfinite(wavelength) or wavelength <= 0 or not polarization:
        raise ValueError("Measurement settings are invalid")
    groups = {}
    for row in rows:
        key = (row["chip_id"], row["guide_id"])
        if not all(key):
            raise ValueError("Chip and guide identifiers are required")
        values = [float(row[k]) for k in ("length_m", "input_power_w",
                                          "output_power_w", "sigma_loss_db")]
        if not all(math.isfinite(v) and v > 0 for v in values):
            raise ValueError("Lengths, powers and loss uncertainties must be positive")
        groups.setdefault(key, []).append(values)
    guides, chip_slopes = [], {}
    for (chip, guide), data in sorted(groups.items()):
        values = np.asarray(data)
        lengths_cm = 100 * values[:, 0]
        if len(np.unique(lengths_cm)) < 4:
            raise ValueError("Each guide requires at least four distinct cutback lengths")
        loss = 10 * np.log10(values[:, 1] / values[:, 2])
        sigma = values[:, 3]
        design = np.column_stack([np.ones(len(data)), lengths_cm])
        weighted_design = design / sigma[:, None]
        weighted_loss = loss / sigma
        parameters, _, rank, _ = np.linalg.lstsq(weighted_design, weighted_loss, rcond=None)
        if rank != 2:
            raise ValueError("Cutback regression is rank deficient")
        residual = loss - design @ parameters
        dof = len(data) - 2
        reduced_chi2 = float(np.sum((residual / sigma)**2) / dof)
        covariance = np.linalg.inv(weighted_design.T @ weighted_design) * max(1.0, reduced_chi2)
        record = {"chip_id": chip, "guide_id": guide,
                  "loss_db_per_cm": float(parameters[1]),
                  "intercept_db": float(parameters[0]),
                  "slope_standard_error": float(np.sqrt(covariance[1, 1])),
                  "reduced_chi2": reduced_chi2,
                  "max_abs_residual_db": float(np.max(abs(residual))),
                  "lengths_cm": lengths_cm.tolist()}
        guides.append(record)
        chip_slopes.setdefault(chip, []).append(record)
    if len(chip_slopes) < 3:
        raise ValueError("At least three independent chips are required")
    chip_means = np.array([np.mean([r["loss_db_per_cm"] for r in records])
                           for records in chip_slopes.values()])
    between_chip_se = float(chip_means.std(ddof=1) / np.sqrt(len(chip_means)))
    measurement_se = float(np.sqrt(sum(
        sum(r["slope_standard_error"]**2 for r in records) / len(records)**2
        for records in chip_slopes.values())) / len(chip_slopes))
    # Conservative diagnostic: retain whichever uncertainty component is larger.
    standard_error = max(between_chip_se, measurement_se)
    mean = float(chip_means.mean())
    margin = float(t.ppf(0.975, len(chip_means)-1) * standard_error)
    return {"wavelength_m": wavelength, "polarization": polarization,
            "independent_chips": len(chip_means),
            "mean_loss_db_per_cm": mean, "ci95": [mean-margin, mean+margin],
            "between_chip_standard_error": between_chip_se,
            "measurement_standard_error": measurement_se,
            "guides": guides,
            "assumptions": "Independent chips, approximately normal chip means, linear cutback loss; systematic calibration uncertainty must be added separately."}


def system_energy(rows: list[dict]) -> dict:
    """Integrate synchronized electrical measurements and all accepted inferences."""
    if len(rows) < 2:
        raise ValueError("At least two synchronized electrical samples are required")
    time_s = np.array([float(r["time_s"]) for r in rows])
    count = np.array([float(r["completed_inferences"]) for r in rows])
    names = ("source_w", "modulation_w", "detection_w", "control_w", "cooling_w")
    powers = np.array([[float(r[name]) for name in names] for r in rows])
    if not all(np.all(np.isfinite(a)) for a in (time_s, count, powers)):
        raise ValueError("Measurements must be finite")
    if np.any(np.diff(time_s) <= 0) or np.any(np.diff(count) < 0) or powers.min() < 0:
        raise ValueError("Time/count ordering and nonnegative powers are required")
    if np.any(count != np.floor(count)):
        raise ValueError("Inference counters must be integers")
    completed = int(count[-1]-count[0])
    if completed <= 0:
        raise ValueError("No complete inferences were measured")
    energies = np.sum((powers[1:] + powers[:-1]) * np.diff(time_s)[:, None] / 2, axis=0)
    total = float(energies.sum())
    return {"duration_s": float(time_s[-1]-time_s[0]),
            "completed_inferences": completed,
            "component_energy_j": dict(zip(names, map(float, energies))),
            "total_energy_j": total, "joules_per_inference": total/completed,
            "inferences_per_second": completed/float(time_s[-1]-time_s[0]),
            "scope": "full_system_electrical_measurement",
            "note": "Include idle/active intervals and calibration uncertainty in the experimental report; zero power must be physically documented."}


def main() -> None:
    """Read calibrated CSV data and write a new analysis report."""
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("cutback", "energy"))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    result = fit_cutback(rows) if args.kind == "cutback" else system_energy(rows)
    result["input_sha256"] = sha256_file(args.input)
    write_new_json(args.out, result)
    print(json.dumps({key: value for key, value in result.items() if key != "guides"}))


if __name__ == "__main__":
    main()
