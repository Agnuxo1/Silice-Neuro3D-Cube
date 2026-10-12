"""Build the T24 parameter files from the raw literature search under the frozen rules.

Input: experimentos/t24_energia_claude/raw_parameter_search_20261013.json (values,
sources and notes gathered by a search agent after the T24 commitment).
Output (new files): params_nominal.json, params_optimistic.json,
digital_references.json and sources.json (records for verify_refs.py).

Choices that apply PROTOCOL-T24.json literally, each stated in the provenance:
- Optical transmission = 2 facets + 2 cm access propagation + modulator
  insertion loss + mesh. The dense passive N x N layer is the agentkit SVD
  realization (two Clements meshes, 2N MZI layers); mesh loss = 2N x the
  cited all-inclusive loss per MZI stage. Primary point N = 64.
- Static power (passive): nominal = cited measured TEC power of a photonic
  module; optimistic = 0 W, ASSUMPTION (athermal passive operation).
- Laser wall-plug efficiency and available power: the quantity is that of a
  SINGLE-MODE 1550 nm laser, because a coherent waveguide mesh needs one;
  multimode broad-area values from the search are recorded but not used.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw_parameter_search_20261013.json"
N_PRIMARY = 64
ACCESS_CM = 2.0


def src(entry: dict) -> str:
    parts = [entry.get("title", "").strip(), str(entry.get("year", ""))]
    if entry.get("doi"):
        parts.append("DOI " + entry["doi"])
    if entry.get("url"):
        parts.append(entry["url"])
    parts.append("where: " + str(entry.get("where", "")))
    return "; ".join(p for p in parts if p)


def clean_title(title: str) -> str:
    """Drop an appended '(Authors et al., venue ...)' note that the search added to some titles."""
    cut = title.rfind(" (")
    tail = title[cut:]
    if cut > 0 and any(k in tail for k in ("et al", "IEEE", "ISSCC", "VLSI", "JSSC", ", 20", " 20")):
        title = title[:cut]
    return title.strip()


def db_to_t(db: float) -> float:
    return 10 ** (-db / 10)


def main() -> None:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    p = raw["parameters"]
    out = {}
    for case in ("nominal", "optimistic"):
        s = case + "_source"
        facet = p["fs_coupling_loss_db_per_facet"][case]
        prop = p["fs_propagation_loss_db_per_cm"][case]
        mod_il = p["modulator_insertion_loss_db"][case]
        stage = p["loss_per_stage_db"][case]
        mesh_db = 2 * N_PRIMARY * stage
        total_db = 2 * facet + ACCESS_CM * prop + mod_il + mesh_db
        if case == "nominal":
            wpe = p["laser_wall_plug_efficiency"]["nominal"]
            wpe_src = src(p["laser_wall_plug_efficiency"]["nominal_source"])
            power = p["available_laser_optical_w"]["nominal"]
            power_src = src(p["available_laser_optical_w"]["nominal_source"])
            static = p["static_power_w"]["nominal"]
            static_src = "Measured module-level TEC power. " + src(p["static_power_w"]["nominal_source"])
        else:
            wpe = 0.30
            wpe_src = ("Single-mode 1550 nm laser: 'peak efficiencies over 30%', Labrecque et al., ISLC 2024, "
                       "DOI 10.1109/ISLC57752.2024.10717351 (abstract, read by a search sub-agent); cross-check 28.49 % "
                       "PCE, Liu et al., Opt. Lett. 50, 3018 (2025), DOI 10.1364/OL.561530 (abstract). The search's 0.50 "
                       "(Garrod et al., Appl. Phys. Lett. 2014, DOI 10.1063/1.4893576) is a multimode broad-area laser and "
                       "is not usable for a single-mode coherent mesh.")
            power = 2.0
            power_src = ("Single-mode: '>2 W single spatial/spectral mode' monolithic DFB-tapered laser, Labrecque et al., "
                         "ISLC 2024, DOI 10.1109/ISLC57752.2024.10717351 (abstract, read by a search sub-agent). The 4.9 W "
                         "multimode value (Kanold et al., SPIE 2024, DOI 10.1117/12.3001390) is not used.")
            static = 0.0
            static_src = "ASSUMPTION: athermal passive operation (protocol rule for the optimistic static power)."
        layer = {"wavelength_m": 1.55e-6,
                 "quantum_efficiency": p["quantum_efficiency"][case],
                 "optical_transmission": db_to_t(total_db),
                 "laser_wall_plug_efficiency": wpe,
                 "modulator_energy_j": p["modulator_energy_j"][case],
                 "dac_energy_j": p["dac_energy_j"][case],
                 "adc_energy_j": p["adc_energy_j"][case],
                 "static_power_w": static,
                 "current_noise_a_rthz": p["current_noise_a_rthz"][case]}
        depth = {"available_laser_optical_w": power,
                 "fixed_loss_db": 2 * facet + mod_il,
                 "loss_per_stage_db": stage}
        programmable = {"mean_heater_power_w_per_shifter": p["heater_mean_power_w"][case]}
        provenance = {
            "wavelength_m": "Project operating wavelength (design choice), 1550 nm.",
            "quantum_efficiency": src(p["quantum_efficiency"][s]),
            "optical_transmission": (
                "Computed: 2 facets x %.3f dB [%s] + %.1f cm x %.3f dB/cm access propagation [%s] + modulator "
                "insertion loss %.3f dB [%s] + mesh 2N x %.2f dB = %.2f dB for N = %d (SVD realization, two Clements "
                "meshes; per-stage loss already includes the MZI propagation length) [%s]. Total %.3f dB, "
                "transmission %.3e." % (facet, src(p["fs_coupling_loss_db_per_facet"][s]), ACCESS_CM, prop,
                                       src(p["fs_propagation_loss_db_per_cm"][s]), mod_il,
                                       src(p["modulator_insertion_loss_db"][s]), stage, mesh_db, N_PRIMARY,
                                       src(p["loss_per_stage_db"][s]), total_db, db_to_t(total_db))),
            "laser_wall_plug_efficiency": wpe_src,
            "modulator_energy_j": "Driver included. " + src(p["modulator_energy_j"][s]),
            "dac_energy_j": "Power / sample rate. " + src(p["dac_energy_j"][s]),
            "adc_energy_j": "Power / sample rate. " + src(p["adc_energy_j"][s]),
            "static_power_w": static_src,
            "current_noise_a_rthz": src(p["current_noise_a_rthz"][s]),
            "available_laser_optical_w": power_src,
            "fixed_loss_db": "Computed: 2 x facet loss + modulator insertion loss (sources as in optical_transmission).",
            "loss_per_stage_db": src(p["loss_per_stage_db"][s]),
            "mean_heater_power_w_per_shifter": "Mean = P_2pi / 2. " + src(p["heater_mean_power_w"][s])}
        out[case] = {"case": case, "primary_n": N_PRIMARY, "transmission_db": total_db,
                     "layer": layer, "depth": depth, "programmable": programmable, "provenance": provenance}
    for case, data in out.items():
        path = HERE / ("params_%s.json" % case)
        if path.exists():
            raise FileExistsError(path.name)
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    refs = raw["digital_references"]
    digital = {"references": {
        "old": {"j_per_mac": 2.3e-13, "source": "Horowitz, ISSCC 2014, DOI 10.1109/ISSCC.2014.6757323, Fig. 1.1.9: "
                "8-bit add 0.03 pJ + 8-bit multiply 0.2 pJ, 45 nm, 0.9 V; arithmetic only.", "node": "45 nm", "year": 2014},
        "modern": {"j_per_mac": refs["modern"]["j_per_mac"], "tops_per_w": refs["modern"].get("tops_per_w"),
                   "node": refs["modern"].get("node"), "year": refs["modern"].get("year"),
                   "source": src(refs["modern"]), "conditions": refs["modern"].get("conditions", ""),
                   "conversion": "J/MAC = 2 / (TOPS/W) x 1e-12 (1 MAC = 2 operations)"}}}
    path = HERE / "digital_references.json"
    if path.exists():
        raise FileExistsError(path.name)
    path.write_text(json.dumps(digital, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    records, seen = [], set()

    def add(entry: dict, key: str) -> None:
        doi = (entry or {}).get("doi")
        if doi and doi.lower() not in seen:
            seen.add(doi.lower())
            records.append({"id": key, "doi": doi, "title": clean_title(entry.get("title", "")),
                            "year": entry.get("year")})
    for name, value in p.items():
        for case in ("nominal", "optimistic"):
            add(value.get(case + "_source"), "%s_%s" % (name, case))
    add(refs["modern"], "digital_modern")
    for extra_doi, title, year in (
            ("10.1109/ISSCC.2014.6757323", "1.1 Computing's energy problem (and what we can do about it)", 2014),
            ("10.1109/ISLC57752.2024.10717351", "Watt-Class High Brightness Tapered Laser with Integrated Distributed Feedback Grating at 1550 nm", 2024),
            ("10.1364/OL.561530", "High-efficiency 1.55-um DFB laser with a 600-um short cavity and sub-20-kHz linewidth", 2025)):
        if extra_doi.lower() not in seen:
            seen.add(extra_doi.lower())
            records.append({"id": "extra_" + extra_doi, "doi": extra_doi, "title": title, "year": year})
    path = HERE / "sources.json"
    if path.exists():
        raise FileExistsError(path.name)
    path.write_text(json.dumps({"records": records}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({c: {"transmission_db": round(d["transmission_db"], 3)} for c, d in out.items()}), len(records))


if __name__ == "__main__":
    main()
