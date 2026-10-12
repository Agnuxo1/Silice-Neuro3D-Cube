"""Command-line access to independent scalar S16 and coherent-field controls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from agentkit.evidence import sha256_file, write_new_json
from agentkit.numerics import (coherent_decomposition, spatial_forecast,
                               spatial_holdout, transfer_sensitivity)
from agentkit.mesh import complex_pairs


def main() -> None:
    """Analyze explicit JSON or reduced NPZ inputs and preserve new output."""
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("forecast", "holdout", "decomposition", "sensitivity"))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.kind in ("forecast", "holdout"):
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if set(payload["observables"]) != {"quadratic_field", "linear_intensity"}:
            raise ValueError("Both prescribed S16 observables are required")
        if args.kind == "forecast":
            result = {name: spatial_forecast(item["powers"], item["temporal_errors"])
                      for name, item in payload["observables"].items()}
            result = {"observables": result,
                      "eligible": len(result) == 2 and all(v["eligible"] for v in result.values())}
        else:
            result = {name: spatial_holdout(**item)
                      for name, item in payload["observables"].items()}
            result = {"observables": result,
                      "passed": len(result) == 2 and all(v["passed"] for v in result.values())}
    else:
        with np.load(args.input, allow_pickle=False) as data:
            if args.kind == "decomposition":
                values = coherent_decomposition(data["field"], data["basis"], data["mass"],
                                                data["dual"] if "dual" in data else None)
                result = {key: complex_pairs(value) if isinstance(value, np.ndarray) else value
                          for key, value in values.items()}
            else:
                values = transfer_sensitivity(data["generator"], data["perturbation"],
                                              float(data["length_m"].item()))
                result = {key: complex_pairs(value) if isinstance(value, np.ndarray) else value
                          for key, value in values.items()}
    result["input_sha256"] = sha256_file(args.input)
    result["scope"] = "reduced_model_diagnostic"
    write_new_json(args.out, result)
    print(json.dumps({key: value for key, value in result.items()
                      if key in ("eligible", "passed", "scope", "input_sha256")}))


if __name__ == "__main__":
    main()
