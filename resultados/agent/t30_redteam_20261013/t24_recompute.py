"""Independent recomputation of T24 (no repo imports). Reads the frozen parameter files by absolute path."""
import json, numpy as np
R = "D:/PROJECTS/Silice-Neuro3D-Cube-closure-20261012/"
h, c, q = 6.62607015e-34, 2.99792458e8, 1.602176634e-19
refs = json.load(open(R + "experimentos/t24_energia_claude/digital_references.json"))["references"]
modern, old = refs["modern"]["j_per_mac"], refs["old"]["j_per_mac"]
budget = json.load(open(R + "resultados/agent/t24_energy_20261012/budget.json"))

def per_mac(p, N=64, M=64, bits=8, fs=1e9, k=1.0, T_override_db=None):
    L = 2 ** bits
    B, T = fs / 2, 1 / fs
    sth = p["current_noise_a_rthz"] * np.sqrt(B) * T / q          # thermal sigma in electrons
    # k * sqrt(Ne + sth^2) = Ne / (2L)  ->  Ne^2 - 4k^2L^2 Ne - 4k^2L^2 sth^2 = 0
    a = 4 * k**2 * L**2
    Ne = (a + np.sqrt(a**2 + 4 * a * sth**2)) / 2
    hv = h * c / p["wavelength_m"]
    Topt = p["optical_transmission"] if T_override_db is None else 10 ** (-T_override_db / 10)
    laser = M * Ne / p["quantum_efficiency"] * hv / (Topt * p["laser_wall_plug_efficiency"])
    parts = dict(laser=laser, mod=N * p["modulator_energy_j"], dac=N * p["dac_energy_j"],
                 adc=M * p["adc_energy_j"], static=p["static_power_w"] / fs)
    return sum(parts.values()) / (N * M), {k_: v / (N * M) for k_, v in parts.items()}, Ne, sth

for case in ("nominal", "optimistic"):
    P = json.load(open(R + f"experimentos/t24_energia_claude/params_{case}.json"))
    p, dep = P["layer"], P["depth"]
    e, parts, Ne, sth = per_mac(p)
    rep = budget["primary"][case]["modern"]["joules_per_mac"]
    print(f"{case}: E/MAC={e:.4e} J (repo {rep:.4e}, rel.diff {abs(e-rep)/rep:.1e}); sigma_th={sth:.1f} e-, "
          f"photons/det={Ne/p['quantum_efficiency']:.0f}; adv modern={modern/e:.3e}, old={old/e:.3e}")
    print("   parts fJ/MAC:", {k: round(v * 1e15, 2) for k, v in parts.items()})
    fixed = P["transmission_db"] - 2 * 64 * dep["loss_per_stage_db"]       # facets + access + modulator
    e0, parts0, *_ = per_mac(p, T_override_db=fixed)
    print(f"   lossless mesh: {e0*1e15:.1f} fJ/MAC, adv modern {modern/e0:.3f}, old {old/e0:.2f}; "
          f"converters+mod only {sum(v for k,v in parts0.items() if k in ('mod','dac','adc'))*1e15:.1f} fJ/MAC")
    # break-even per-MZI-stage loss (SVD mesh, 128 stages) against each reference
    for name, ref in (("old", old), ("modern", modern)):
        lo, hi = 0.0, 0.35
        if per_mac(p, T_override_db=fixed)[0] > ref:
            print(f"   break-even stage loss vs {name}: none (fails even lossless)"); continue
        for _ in range(60):
            mid = (lo + hi) / 2
            (lo, hi) = (mid, hi) if per_mac(p, T_override_db=fixed + 128 * mid)[0] < ref else (lo, mid)
        print(f"   break-even stage loss vs {name}: {lo:.3f} dB/stage (mesh {128*lo:.1f} dB)")
    # alternative realizations of a 64x64 layer (exploratory): stage loss 0.07 dB (1.2 cm MZI at 0.06 dB/cm)
    for label, mesh_db in (("SVD 128 st @0.07 dB", 128 * 0.07), ("fan-out tree 2x6 st @0.35 dB", 12 * 0.35)):
        ea, *_ = per_mac(p, T_override_db=fixed + mesh_db)
        print(f"   {label}: {ea*1e15:.0f} fJ/MAC, adv modern {modern/ea:.3f}, old {old/ea:.2f}")
    # max stages from laser power
    Ne_ph = Ne / p["quantum_efficiency"]
    head = 10 * np.log10(dep["available_laser_optical_w"] / (1e9 * 64 * Ne_ph * h * c / p["wavelength_m"])) - dep["fixed_loss_db"]
    print(f"   max stages = {int(np.floor(head / dep['loss_per_stage_db']))} (repo {budget['max_depth'][case]['max_stages']})")
# lossless break-even N (optimistic)
P = json.load(open(R + "experimentos/t24_energia_claude/params_optimistic.json"))["layer"]
fixed = 46.34 - 44.8
for N in (64, 128, 256, 286, 300, 320):
    print("N", N, "lossless optimistic E/MAC fJ", round(per_mac(P, N=N, M=N, T_override_db=fixed)[0] * 1e15, 2))
