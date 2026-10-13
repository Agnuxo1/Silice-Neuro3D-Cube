"""Draw the additional figures of the full paper from committed results only.

Inputs (read-only, committed in the repository):
  resultados/agent/t26_sota_20261012/records.json        (literature, T26)
  resultados/agent/t20_trench_width_20261013/results.json (model, T20D)
  resultados/agent/t25_scaling_20261012/results.json      (model, T25; counts
      used only to check the schematic layout drawn below)
  paper/figures/fig_t2{4,5,7}_*.pdf                       (copied unchanged)

Outputs: paper/full/figures/*.pdf (and .png previews). No new result is
computed: the schematic layout reproduces the T25 construction for N = 8 and
asserts that its crossing counts equal the committed values.

Run from any directory with the project's Python:
  python -B paper/full/make_extra_figures.py
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "figures"
STYLE = {"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False,
         "savefig.facecolor": "white", "axes.titlesize": 9, "legend.fontsize": 7.2,
         "pdf.fonttype": 42}
BLUE, RED, GREEN, GREY, PURPLE, ORANGE = "#146C94", "#C0392B", "#2E8B57", "0.45", "#7A3E9D", "#B5651D"
BAND = "#E8F1F6"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def short_name(record: dict) -> str:
    """First author and year from the record id, e.g. 'ackermann2025_ol' -> 'Ackermann 2025'."""
    head = record["id"].split("_")[0]
    digits = "".join(c for c in head if c.isdigit())
    name = head[: len(head) - len(digits)]
    special = {"rossadams": "Ross-Adams", "dimicco": "Di Micco"}
    return special.get(name, name.capitalize()) + " " + digits


def waveguide_class(record: dict) -> str:
    text = (record.get("waveguide_type") or "").lower()
    if "depressed" in text:
        return "depressed-cladding-like"
    if "multi-core" in text or "slit-beam" in text:
        return "other modified-index"
    return "type I (single or multiscan)"


MARKERS = {"type I (single or multiscan)": "o", "depressed-cladding-like": "D",
           "other modified-index": "^"}


def fig_sota_loss() -> None:
    records = load("resultados/agent/t26_sota_20261012/records.json")["records"]
    rows = [r for r in records if r.get("propagation_loss_db_per_cm") is not None
            and r.get("wavelength_nm") is not None]
    trench = load("resultados/agent/t20_trench_width_20261013/results.json")
    floors = {row["t_um"]: row["leakage_db_per_cm"] for row in trench["rows"]}
    h1, sota = 0.3, trench["s1550_db_per_cm"]
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.15), layout="constrained",
                                 gridspec_kw={"width_ratios": [1.0, 1.05]})
        ax = axes[0]
        ax.axvspan(1530, 1565, color=BAND, zorder=0)
        ax.text(1547, 1.25, "1530-1565 nm", ha="center", va="bottom", fontsize=6.3, color=BLUE)
        for r in rows:
            silica = "fused silica" in r["material"].lower()
            cls = waveguide_class(r)
            upper = "upper bound" in (r.get("loss_method") or "").lower()
            ax.plot(r["wavelength_nm"], r["propagation_loss_db_per_cm"], MARKERS[cls], ms=5.2,
                    mfc=BLUE if silica else "white", mec=BLUE if silica else ORANGE, mew=1.1, zorder=3)
            if upper:
                ax.annotate("", xy=(r["wavelength_nm"], r["propagation_loss_db_per_cm"] * 0.62),
                            xytext=(r["wavelength_nm"], r["propagation_loss_db_per_cm"] * 0.93),
                            arrowprops={"arrowstyle": "-|>", "lw": 0.7, "color": ORANGE})
            if r["id"] in ("skryabin2024_pra", "chen2018_bk7"):
                above = True
                ax.text(r["wavelength_nm"], r["propagation_loss_db_per_cm"] * (1.25 if above else 0.72),
                        short_name(r), fontsize=5.8, ha="center", va="bottom" if above else "top",
                        color="0.25")
        for value, ls, label, factor, va in ((h1, "--", "H1-A threshold 0.3", 1.12, "bottom"),
                                             (sota, "-.", "H1-SOTA threshold 0.06", 0.88, "top")):
            ax.axhline(value, color=RED, ls=ls, lw=0.9)
            ax.text(560, value * factor, label + " dB/cm", color=RED, fontsize=6.3, va=va)
        for t, label in ((12.0, "t = 12 µm"), (16.0, "t = 16 µm")):
            ax.plot(1550, floors[t], "*", ms=8.5, color=GREEN, mec="black", mew=0.4, zorder=4)
            ax.text(1500, floors[t], "model floor\n" + label, fontsize=6.0, color=GREEN,
                    ha="right", va="center")
        ax.set_yscale("log")
        ax.set_xlim(540, 1640)
        ax.set_ylim(1.0e-3, 2.0)
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Propagation loss (dB/cm)")
        ax.set_title("(a) Reported loss versus wavelength")
        handles = [Line2D([], [], ls="", marker=m, mfc="0.6", mec="0.3", label=c) for c, m in MARKERS.items()]
        handles += [Line2D([], [], ls="", marker="o", mfc=BLUE, mec=BLUE, label="fused silica"),
                    Line2D([], [], ls="", marker="o", mfc="white", mec=ORANGE, label="other or unstated glass"),
                    Line2D([], [], ls="", marker="*", ms=8, mfc=GREEN, mec="black", mew=0.4,
                           label="model: ideal HE11 leakage")]
        ax.legend(handles=handles, frameon=False, fontsize=5.9, loc="lower left", handletextpad=0.3,
                  borderaxespad=0.2, ncol=1)
        # (b) records in the telecom band, ranked
        ax = axes[1]
        band = sorted([r for r in rows if 1530 <= r["wavelength_nm"] <= 1565],
                      key=lambda r: r["propagation_loss_db_per_cm"])
        for i, r in enumerate(band):
            silica = "fused silica" in r["material"].lower()
            cls = waveguide_class(r)
            value = r["propagation_loss_db_per_cm"]
            ax.plot(value, i, MARKERS[cls], ms=5.2, mfc=BLUE if silica else "white",
                    mec=BLUE if silica else ORANGE, mew=1.1, zorder=3)
            method = (r.get("loss_method") or "").lower()
            tag = "cut-back" if method.startswith("cut-back") else ""
            ax.text(value * 1.22, i, "%s  %.2f%s" % (short_name(r), value, ("  (" + tag + ")") if tag else ""),
                    va="center", fontsize=6.2)
        n = len(band)
        lines = []
        for value, ls, label in ((h1, "--", "H1-A threshold, 0.3 dB/cm"),
                                 (sota, "-.", "H1-SOTA threshold, 0.06 dB/cm")):
            lines.append(ax.axvline(value, color=RED, ls=ls, lw=0.9, label=label))
        for t, ls in ((12.0, ":"), (16.0, (0, (1, 2.5)))):
            lines.append(ax.axvline(floors[t], color=GREEN, ls=ls, lw=1.1,
                                    label="model floor, t = %g µm: %.4f dB/cm" % (t, floors[t])))
        legend = ax.legend(handles=lines, frameon=True, fontsize=5.9, loc="upper left", handlelength=2.2,
                           borderaxespad=0.1, facecolor="white", edgecolor="none", framealpha=1.0)
        legend.set_zorder(5)
        ax.set_xscale("log")
        ax.set_xlim(1.0e-3, 3.0)
        ax.set_ylim(-0.7, n + 2.6)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.set_xlabel("Propagation loss at 1530-1565 nm (dB/cm)")
        ax.set_title("(b) Telecom-band records, ranked")
        fig.supxlabel("Literature values (T26, %d identifier-verified records with both loss and wavelength); "
                      "green: model prediction (T20D), not a measurement." % len(rows), fontsize=6.6)
        fig.savefig(OUT / "fig_sota_loss.pdf")
        fig.savefig(OUT / "fig_sota_loss.png", dpi=200)
        plt.close(fig)


def fig_trench_leakage() -> None:
    d = load("resultados/agent/t20_trench_width_20261013/results.json")
    t = np.array([r["t_um"] for r in d["rows"]])
    leak = np.array([r["leakage_db_per_cm"] for r in d["rows"]])
    target, sota = d["target_db_per_cm"], d["s1550_db_per_cm"]
    tmin = d["metrics"]["t_min_um_for_10pct_of_sota"]
    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(4.6, 3.0), layout="constrained")
        ax.plot(t, leak, "-", color=BLUE, lw=1.2, zorder=2)
        ax.plot(t, leak, "o", color=BLUE, ms=4.5, zorder=3, label="exact vector solver, HE$_{11}$")
        ax.axhline(sota, color=RED, ls="-.", lw=0.9)
        ax.text(19.9, sota * 1.12, "lowest verified loss, 0.06 dB/cm (literature)", color=RED,
                fontsize=6.3, ha="right", va="bottom")
        ax.axhline(target, color=RED, ls="--", lw=0.9)
        ax.text(19.9, target * 1.12, "design target 0.006 dB/cm (10 % of 0.06)", color=RED,
                fontsize=6.3, ha="right", va="bottom")
        ax.axvline(tmin, color=GREY, ls=":", lw=0.9)
        ax.text(tmin - 0.12, 1.2e-4, "t$_{min}$ = %.1f µm" % tmin, color=GREY, fontsize=6.3,
                ha="right", va="bottom")
        for tt, label, where in ((12.0, "H1-A coupon\nt = 12 µm: %.4f dB/cm", (12.6, 0.11)),
                                 (16.0, "H1-SOTA coupon\nt = 16 µm: %.4f dB/cm", (12.2, 4.0e-4))):
            value = float(leak[t == tt][0])
            ax.plot(tt, value, "s", ms=7.5, mfc="none", mec=ORANGE, mew=1.3, zorder=4)
            ax.annotate(label % value, (tt, value), xytext=where, fontsize=6.3,
                        color=ORANGE, arrowprops={"arrowstyle": "-", "lw": 0.6, "color": ORANGE})
        ax.set_yscale("log")
        ax.set_xlim(11.5, 20.5)
        ax.set_ylim(5e-5, 0.3)
        ax.set_xlabel("Trench width t (µm)")
        ax.set_ylabel("Ideal leakage floor (dB/cm)")
        ax.set_title("HE$_{11}$ leakage of the trench guide at 1550 nm", fontsize=8.6)
        fig.supxlabel("Model (T20D): exact vector leaky-mode solver, ideal step profile, a = 6 µm,\n"
                      "$\\Delta n$ = -0.005; no scattering or absorption. Not a measurement.", fontsize=6.4)
        fig.savefig(OUT / "fig_trench_leakage.pdf")
        fig.savefig(OUT / "fig_trench_leakage.png", dpi=200)
        plt.close(fig)


def _odd_even_layers(current: list[int], target: list[int]) -> list[list[int]]:
    """Layers of disjoint adjacent swaps (odd-even transposition) from current to target order."""
    rank = {v: i for i, v in enumerate(target)}
    order = list(current)
    layers, parity = [], 0
    while order != list(target):
        swaps = [p for p in range(parity, len(order) - 1, 2) if rank[order[p]] > rank[order[p + 1]]]
        if swaps:
            for p in swaps:
                order[p], order[p + 1] = order[p + 1], order[p]
            layers.append(swaps)
        parity ^= 1
    return layers


def butterfly_layout(n: int) -> list[tuple]:
    """Fixed input/output order layout of T25: interleave, couple, restore, per stage."""
    steps, identity = [], list(range(n))
    for s in range(int(np.log2(n))):
        m = 2 ** s
        target = []
        for g in range(0, n, 2 * m):
            for j in range(m):
                target += [g + j, g + j + m]
        for layer in _odd_even_layers(identity, target):
            steps.append(("swap", layer, s))
        steps.append(("couple", m, s))
        for layer in _odd_even_layers(target, identity):
            steps.append(("swap", layer, s))
    return steps


def layout_counts(n: int) -> tuple[int, int]:
    """Total crossings and worst light-path crossings of the drawn layout."""
    order = list(range(n))
    best = {v: 0 for v in order}
    total = 0
    for kind, value, _ in butterfly_layout(n):
        if kind == "swap":
            for p in value:
                best[order[p]] += 1
                best[order[p + 1]] += 1
                order[p], order[p + 1] = order[p + 1], order[p]
                total += 1
        else:
            m = value
            best = {v: max(best[v], best[v ^ m]) for v in best}
    return total, max(best.values())


def fig_layout_schematic() -> None:
    n = 8
    t25 = load("resultados/agent/t25_scaling_20261012/results.json")
    ref = next(r for r in t25["crossings"]["rows"] if r["n"] == n)
    total, worst = layout_counts(n)
    assert (total, worst) == (ref["crossings_total"], ref["worst_path_crossings"]), (total, worst, ref)
    steps = butterfly_layout(n)
    stage_colors = [GREEN, PURPLE, ORANGE]
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.9), layout="constrained")
        for panel, ax in enumerate(axes):
            order = list(range(n))
            x = 0.0
            lifted_any = False
            for kind, value, s in steps:
                if kind == "couple":
                    for p in range(0, n, 2):
                        ax.add_patch(plt.Rectangle((x + 0.15, p - 0.18), 0.7, 1.36, fc=stage_colors[s],
                                                   ec="black", lw=0.5, alpha=0.85, zorder=3))
                    for p in range(n):
                        ax.plot([x, x + 1], [p, p], color="0.15", lw=0.9, zorder=2)
                    x += 1
                    continue
                swapped = set()
                for p in value:
                    swapped.update((p, p + 1))
                for p in range(n):
                    if p not in swapped:
                        ax.plot([x, x + 1], [p, p], color="0.15", lw=0.9, zorder=2)
                for p in value:
                    if panel == 0:
                        ax.plot([x, x + 1], [p, p + 1], color="0.15", lw=0.9, zorder=2)
                        ax.plot([x, x + 1], [p + 1, p], color="0.15", lw=0.9, zorder=2)
                        ax.plot(x + 0.5, p + 0.5, "o", ms=3.4, color=RED, zorder=4)
                    else:
                        # the guide belonging to the moving (upper) block is drawn dashed: second plane
                        a, b = order[p], order[p + 1]
                        m = 2 ** s
                        up = a if (a // m) % 2 == 1 else b
                        for src, dst, label in ((p, p + 1, a), (p + 1, p, b)):
                            style = (0, (2.2, 1.6)) if label == up else "-"
                            ax.plot([x, x + 1], [src, dst], color=BLUE if label == up else "0.15",
                                    lw=1.1 if label == up else 0.9, ls=style, zorder=2)
                        lifted_any = True
                for p in value:
                    order[p], order[p + 1] = order[p + 1], order[p]
                x += 1
            ax.set_xlim(-0.6, x + 0.6)
            ax.set_ylim(n - 0.4, -0.9)
            ax.set_yticks(range(n), ["%d" % i for i in range(n)], fontsize=6.5)
            ax.set_xticks([])
            for side in ("bottom", "left"):
                ax.spines[side].set_visible(False)
            ax.tick_params(left=False)
            if panel == 0:
                ax.set_title("(a) Planar: %d crossings, %d on the worst path" % (total, worst), fontsize=8.2)
                ax.plot([], [], "o", ms=3.4, color=RED, label="waveguide crossing")
            else:
                ax.set_title("(b) Two-plane routing: no crossings", fontsize=8.2)
                ax.plot([], [], color=BLUE, ls=(0, (2.2, 1.6)), lw=1.1, label="guide routed in a second plane")
            for s, c in enumerate(stage_colors):
                ax.add_patch(plt.Rectangle((0, 0), 0, 0, fc=c, ec="black", lw=0.5,
                                           label="couplers, stage %d (span %d)" % (s + 1, 2 ** s)))
            ax.legend(frameon=False, fontsize=6.0, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2,
                      handlelength=1.6, columnspacing=1.0)
        fig.supxlabel("Schematic (N = 8, fixed input and output order; the T25 construction). Crossing counts "
                      "are checked against the committed T25 results.", fontsize=6.4)
        fig.savefig(OUT / "fig_layout_schematic.pdf")
        fig.savefig(OUT / "fig_layout_schematic.png", dpi=200)
        plt.close(fig)


def copy_existing() -> None:
    for name in ("fig_t25_scaling.pdf", "fig_t27_calibration.pdf", "fig_t24_energy.pdf"):
        shutil.copyfile(ROOT / "paper" / "figures" / name, OUT / name)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    copy_existing()
    fig_sota_loss()
    fig_trench_leakage()
    fig_layout_schematic()
    for n in (4, 8, 16, 32):
        print("layout check N=%d: total, worst =" % n, layout_counts(n))
    print(sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
