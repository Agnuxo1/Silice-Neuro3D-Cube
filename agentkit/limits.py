"""Parametric energy and precision budget for an optoelectronic linear layer (kit v2).

This is a kill test, not a measurement. It asks whether, with stated
parameters, a passive optical layer could beat a digital reference energy
per multiply-accumulate (MAC) at a stated output precision. Every input is
explicit; nothing is looked up. Digital reference energies must come from a
cited source or a measurement, with technology node and year.

Noise model at each detector over one sample period T (electrons):
  variance = N_e (shot) + sigma_th**2, sigma_th = i_n * sqrt(B) * T / q.
Requirement: k * sqrt(variance) <= N_e / (2 L), L = 2**bits levels.
Optical amortization over fan-in follows the photoelectric multiplication
argument of Hamerly et al., Phys. Rev. X 9, 021032 (2019).
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from agentkit.evidence import write_new_json

PLANCK_J_S = 6.62607015e-34
LIGHT_M_S = 299792458.0
ELEMENTARY_C = 1.602176634e-19


def _positive(**values: float) -> None:
    for name, value in values.items():
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(name + " must be finite and positive")


def photon_energy_j(wavelength_m: float) -> float:
    """Return h c / lambda in joules."""
    _positive(wavelength_m=wavelength_m)
    return PLANCK_J_S * LIGHT_M_S / wavelength_m


def required_electrons(bits: int, sigma_multiple: float = 1.0,
                       thermal_sigma_electrons: float = 0.0) -> float:
    """Full-scale photoelectrons resolving 2**bits levels at k sigma."""
    if type(bits) is not int or not 1 <= bits <= 24:
        raise ValueError("bits must be an integer from 1 to 24")
    _positive(sigma_multiple=sigma_multiple)
    if not math.isfinite(thermal_sigma_electrons) or thermal_sigma_electrons < 0:
        raise ValueError("thermal noise must be finite and nonnegative")
    a = 1.0 / (4.0 * sigma_multiple**2 * (2.0**bits)**2)
    return (1.0 + math.sqrt(1.0 + 4.0 * a * thermal_sigma_electrons**2)) / (2.0 * a)


def detection_energy_j(bits: int, wavelength_m: float, quantum_efficiency: float,
                       sample_rate_hz: float, current_noise_a_rthz: float = 0.0,
                       bandwidth_hz: float | None = None, sigma_multiple: float = 1.0) -> dict:
    """Optical energy that must reach one detector per sample."""
    _positive(wavelength_m=wavelength_m, sample_rate_hz=sample_rate_hz)
    if not 0 < quantum_efficiency <= 1:
        raise ValueError("quantum efficiency must lie in (0, 1]")
    if not math.isfinite(current_noise_a_rthz) or current_noise_a_rthz < 0:
        raise ValueError("current noise must be finite and nonnegative")
    bandwidth = sample_rate_hz / 2 if bandwidth_hz is None else bandwidth_hz
    _positive(bandwidth_hz=bandwidth)
    period = 1.0 / sample_rate_hz
    sigma_th = current_noise_a_rthz * math.sqrt(bandwidth) * period / ELEMENTARY_C
    electrons = required_electrons(bits, sigma_multiple, sigma_th)
    photons = electrons / quantum_efficiency
    return {"electrons": electrons, "photons": photons,
            "thermal_sigma_electrons": sigma_th,
            "optical_energy_j": photons * photon_energy_j(wavelength_m)}


def layer_budget(n_inputs: int, n_outputs: int, bits: int, wavelength_m: float,
                 quantum_efficiency: float, sample_rate_hz: float,
                 optical_transmission: float, laser_wall_plug_efficiency: float,
                 modulator_energy_j: float, dac_energy_j: float, adc_energy_j: float,
                 static_power_w: float = 0.0, current_noise_a_rthz: float = 0.0,
                 sigma_multiple: float = 1.0,
                 digital_reference_j_per_mac: float | None = None) -> dict:
    """Energy per frame and per MAC for a dense passive N-by-M layer.

    Assumes the laser energy is shared without excess loss beyond
    `optical_transmission` (all coupling, propagation, splitting excess and
    crossing loss, as a fraction). Electrical energies are per sample.
    """
    if type(n_inputs) is not int or type(n_outputs) is not int or min(n_inputs, n_outputs) < 1:
        raise ValueError("Layer dimensions must be positive integers")
    if not 0 < optical_transmission <= 1 or not 0 < laser_wall_plug_efficiency <= 1:
        raise ValueError("Transmission and wall-plug efficiency must lie in (0, 1]")
    for name, value in (("modulator", modulator_energy_j), ("dac", dac_energy_j),
                        ("adc", adc_energy_j), ("static", static_power_w)):
        if not math.isfinite(value) or value < 0:
            raise ValueError(name + " energy must be finite and nonnegative")
    detector = detection_energy_j(bits, wavelength_m, quantum_efficiency, sample_rate_hz,
                                  current_noise_a_rthz, None, sigma_multiple)
    laser_optical = n_outputs * detector["optical_energy_j"] / optical_transmission
    components = {"laser_electrical_j": laser_optical / laser_wall_plug_efficiency,
                  "modulators_j": n_inputs * modulator_energy_j,
                  "dacs_j": n_inputs * dac_energy_j,
                  "adcs_j": n_outputs * adc_energy_j,
                  "static_j": static_power_w / sample_rate_hz}
    total = sum(components.values())
    macs = n_inputs * n_outputs
    result = {"scope": "parametric_budget_not_measurement",
              "components_per_frame_j": components, "total_per_frame_j": total,
              "macs_per_frame": macs, "joules_per_mac": total / macs,
              "detector": detector, "dominant_component": max(components, key=components.get)}
    if digital_reference_j_per_mac is not None:
        _positive(digital_reference_j_per_mac=digital_reference_j_per_mac)
        result["advantage_factor"] = digital_reference_j_per_mac / result["joules_per_mac"]
    return result


def max_depth(available_laser_optical_w: float, sample_rate_hz: float, n_outputs: int,
              detector_energy_j: float, fixed_loss_db: float, loss_per_stage_db: float) -> int | None:
    """Deepest cascade whose loss still leaves enough photons at every detector."""
    _positive(available_laser_optical_w=available_laser_optical_w,
              sample_rate_hz=sample_rate_hz, detector_energy_j=detector_energy_j,
              loss_per_stage_db=loss_per_stage_db)
    if type(n_outputs) is not int or n_outputs < 1 or not math.isfinite(fixed_loss_db) or fixed_loss_db < 0:
        raise ValueError("Invalid outputs or fixed loss")
    headroom_db = 10 * math.log10(available_laser_optical_w /
                                  (sample_rate_hz * n_outputs * detector_energy_j)) - fixed_loss_db
    if headroom_db < 0:
        return None
    return int(math.floor(headroom_db / loss_per_stage_db + 1e-12))


def main() -> None:
    """Evaluate a JSON parameter file with layer_budget and keep the result."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    params = json.loads(args.params.read_text(encoding="utf-8"))
    provenance = params.pop("provenance", None)
    if not isinstance(provenance, dict):
        raise ValueError("provenance must map every parameter to its source")
    missing = [k for k in params if not str(provenance.get(k, "")).strip()]
    if missing:
        raise ValueError("Missing provenance for: " + ", ".join(sorted(missing)))
    result = layer_budget(**params)
    result["parameters"] = params
    result["provenance"] = provenance
    write_new_json(args.out, result)
    print(json.dumps({"joules_per_mac": result["joules_per_mac"],
                      "dominant_component": result["dominant_component"],
                      "advantage_factor": result.get("advantage_factor")}))


if __name__ == "__main__":
    main()
