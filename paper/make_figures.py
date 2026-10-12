"""Draw manuscript figures from committed results (no new computation).

Inputs are the hashed JSON results under resultados/agent/. Outputs go to
paper/figures/ and are regenerated deterministically; they carry no data
that is not in their inputs.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
STYLE = {"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False,
         "savefig.facecolor": "white", "axes.titlesize": 9, "legend.fontsize": 7.5}
BLUE, RED, GREEN, GREY, PURPLE, ORANGE = "#146C94", "#C0392B", "#2E8B57", "0.45", "#7A3E9D", "#B5651D"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def fig_t27() -> None:
    d = load("resultados/agent/t27_calibration_20261012/results.json")
    rows = d["primary"]["rows"]
    floor = 1e-16
    series = [("A: ideal programming", "before", GREY), ("B: in situ", "after", BLUE),
              ("B: 8-bit DAC", "after_8bit", PURPLE), ("C: model-based", "after_model_estimated_errors", GREEN)]
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), layout="constrained")
        for label, key, color in series:
            v = np.sort(np.maximum([r[key] for r in rows], floor))
            axes[0].step(v, np.arange(1, len(v) + 1) / len(v), where="post", color=color, label=label)
        axes[0].axvline(1e-3, color=RED, ls="--", lw=0.9)
        axes[0].text(1.2e-3, 0.08, "registered\nthreshold", color=RED, fontsize=7)
        axes[0].set_xscale("log")
        axes[0].set_xlabel("Infidelity 1 - |Tr(U$^\\dagger$V)|/N")
        axes[0].set_ylabel("Fraction of realizations")
        axes[0].set_title("(a) N = 8, $\\sigma$ = 0.02 rad, shared fraction 0.8")
        axes[0].legend(frameon=False, loc="upper left")
        labels, before, after = [], [], []
        for s in [d["primary"]] + d["secondary"]:
            if s is not d["primary"] and (s["n"], s["sigma_rad"], s["correlation"]) == (8, 0.02, 0.8):
                continue
            labels.append("N=%d\n%.2f\n%.1f" % (s["n"], s["sigma_rad"], s["correlation"]))
            before.append(s["summary"]["before"]["wilks_95_95_upper"])
            after.append(max(s["summary"]["after"]["wilks_95_95_upper"], floor))
        x = np.arange(len(labels))
        axes[1].bar(x - 0.2, before, 0.4, color=GREY, label="A: ideal programming")
        axes[1].bar(x + 0.2, after, 0.4, color=BLUE, label="B: in situ")
        axes[1].axhline(1e-3, color=RED, ls="--", lw=0.9)
        axes[1].set_yscale("log")
        axes[1].set_xticks(x, labels, fontsize=6.5)
        axes[1].set_ylabel("95/95 upper bound of infidelity")
        axes[1].set_title("(b) N, $\\sigma$ (rad), shared fraction")
        axes[1].set_ylim(1e-15, 30)
        axes[1].legend(frameon=False, fontsize=7, ncol=2, loc="upper center")
        fig.supxlabel("Model study T27 (60 Haar targets per setting); no fabricated device.", fontsize=7)
        fig.savefig(OUT / "fig_t27_calibration.pdf")
        fig.savefig(OUT / "fig_t27_calibration.png", dpi=300)
        plt.close(fig)


def fig_t24() -> None:
    path = ROOT / "resultados/agent/t24_energy_20261012/budget.json"
    if not path.exists():
        return
    d = json.loads(path.read_text(encoding="utf-8"))
    refs = d["references_j_per_mac"]
    names = ["laser_electrical_j", "modulators_j", "dacs_j", "adcs_j", "static_j"]
    nice = ["Laser", "Modulators", "DACs", "ADCs", "Static"]
    colors = [ORANGE, PURPLE, GREEN, BLUE, GREY]
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), layout="constrained")
        floor = 1e-6  # pJ; zero components are drawn at the axis floor and labeled
        for i, name in enumerate(("nominal", "optimistic")):
            p = d["primary"][name]["modern"]
            macs = p["n"] * p["n"]
            for j, (comp, label, color) in enumerate(zip(names, nice, colors)):
                value = p["components_per_frame_j"][comp] / macs * 1e12
                y = i + (j - 2) * 0.12
                axes[0].plot(max(value, floor), y, "o", color=color, label=label if i == 0 else None)
            axes[0].plot(p["joules_per_mac"] * 1e12, i + 0.36, "D", color="black",
                         label="Total" if i == 0 else None)
        for key, ls, label in (("modern", "-", "Digital INT8, 3 nm (2026)"), ("old", ":", "Digital 8-bit, 45 nm (2014)")):
            axes[0].axvline(refs[key] * 1e12, color=RED, ls=ls, lw=1, label=label)
        axes[0].set_yticks([0, 1], ["Nominal", "Optimistic"])
        axes[0].set_ylim(-1.3, 1.6)
        axes[0].set_xscale("log")
        axes[0].set_xlim(floor * 0.5, 5e3)
        axes[0].set_xlabel("Energy per MAC (pJ), N = 64, 8 bits, 1 GS/s")
        axes[0].set_title("(a) Components at the registered point")
        axes[0].annotate("static = 0 W (assumption)", (floor, 1 + 0.24), xytext=(4e-6, 1.45), fontsize=6,
                         arrowprops={"arrowstyle": "-", "lw": 0.5, "color": GREY})
        axes[0].legend(frameon=False, fontsize=6, loc="lower left", ncol=2)
        for name, color in (("nominal", GREY), ("optimistic", BLUE)):
            for bits, marker in ((4, "o"), (8, "s")):
                rows = [r for r in d["sweep"] if r["parameter_set"] == name and r["bits"] == bits and r["sample_rate_hz"] == 1e9]
                axes[1].plot([r["n"] for r in rows], [r["advantage_factor"] for r in rows], marker=marker,
                             color=color, label="%s, %d bits" % (name, bits))
        # Exploratory (not registered): optimistic set without mesh loss, 8 bits.
        import sys
        sys.path.insert(0, str(ROOT))
        from agentkit.limits import layer_budget
        layer = json.loads((ROOT / "experimentos/t24_energia_claude/params_optimistic.json").read_text(encoding="utf-8"))["layer"]
        layer = dict(layer, optical_transmission=10 ** (-(2 * 0.2 + 2 * 0.07 + 1.0) / 10))
        ns = [16, 32, 64, 128, 256, 512, 1024]
        adv = [layer_budget(n_inputs=n, n_outputs=n, bits=8, sample_rate_hz=1e9,
                            digital_reference_j_per_mac=refs["modern"], **layer)["advantage_factor"] for n in ns]
        axes[1].plot(ns, adv, "s--", color=GREEN, mfc="white", label="optimistic, 8 bits,\nno mesh loss (exploratory)")
        axes[1].axhline(1, color=RED, ls="--", lw=0.9)
        axes[1].set_xscale("log", base=2)
        axes[1].set_yscale("log")
        axes[1].set_xlabel("Fan-in N = M")
        axes[1].set_ylabel("Advantage vs modern INT8 reference")
        axes[1].set_title("(b) Fan-in sensitivity, 1 GS/s")
        axes[1].legend(frameon=False, fontsize=6, loc="lower right")
        fig.supxlabel("Parametric budget T24 from cited values; not a measurement. Registered sweep keeps the N = 64 mesh transmission.", fontsize=7)
        fig.savefig(OUT / "fig_t24_energy.pdf")
        fig.savefig(OUT / "fig_t24_energy.png", dpi=300)
        plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("fig_t25_scaling.pdf", "fig_t25_scaling.png"):
        shutil.copyfile(ROOT / "resultados/agent/t25_scaling_20261012" / name, OUT / name)
    fig_t27()
    fig_t24()
    print(sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
