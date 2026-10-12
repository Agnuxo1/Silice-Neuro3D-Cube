"""Export publication figures from explicit CSV data with fixed scientific labels."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from agentkit.evidence import sha256_file, write_new_json


def plot_convergence(input_path: Path, output_prefix: Path, scope: str) -> dict:
    """Plot every retained mesh sample and numerical error indicator.

    Required CSV columns: mesh_um, power_fraction, error_indicator.
    Error bars are indicators, not statistical confidence intervals.
    """
    with input_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    values = np.array([[float(row[key]) for key in
                        ("mesh_um", "power_fraction", "error_indicator")] for row in rows])
    if values.ndim != 2 or values.shape[1] != 3 or len(values) < 3:
        raise ValueError("At least three complete convergence rows are required")
    if (not np.all(np.isfinite(values)) or np.any(values[:, 0] <= 0)
            or np.any(values[:, 1:] < 0)):
        raise ValueError("Convergence values must be finite and nonnegative")
    if len(np.unique(values[:, 0])) != len(values):
        raise ValueError("Duplicate meshes need a separately declared aggregation protocol")
    if scope not in ("numerical_model", "manufactured_control"):
        raise ValueError("This figure is for a numerical model or manufactured control")
    order = np.argsort(values[:, 0])
    values = values[order]
    outputs = [output_prefix.with_suffix(suffix) for suffix in (".png", ".pdf", ".json")]
    if any(path.exists() for path in outputs):
        raise FileExistsError("Figure output paths must be new")
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "savefig.facecolor": "white"}):
        fig, ax = plt.subplots(figsize=(6.8, 4.4), layout="constrained")
        ax.errorbar(values[:, 0], values[:, 1], yerr=values[:, 2],
                    marker="o", capsize=4, color="#146C94", label="All retained samples")
        ax.set_xlabel("Nominal mesh spacing (µm)")
        ax.set_ylabel("Core power / input power")
        ax.set_title("Spatial refinement")
        ax.grid(alpha=0.2)
        ax.legend()
        fig.supxlabel("Error bars: numerical indicators, not 95% confidence intervals. " +
                      scope.replace("_", " ") + "; no physical measurement.", fontsize=8)
        fig.savefig(outputs[0], dpi=300)
        fig.savefig(outputs[1])
        plt.close(fig)
    manifest = {"input_sha256": sha256_file(input_path), "scope": scope,
                "selection": "all retained CSV rows, sorted only by mesh spacing",
                "rows": len(values), "error_bar_type": "numerical_indicator",
                "outputs": {p.name: sha256_file(p) for p in outputs[:2]}}
    write_new_json(outputs[2], manifest)
    return manifest


def main() -> None:
    """Create static PNG/PDF figures and an input/output hash manifest."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    parser.add_argument("--scope", choices=("numerical_model", "manufactured_control"),
                        required=True)
    args = parser.parse_args()
    result = plot_convergence(args.input, args.output_prefix, args.scope)
    print("Exported", result["rows"], "rows with explicit numerical scope.")


if __name__ == "__main__":
    main()
