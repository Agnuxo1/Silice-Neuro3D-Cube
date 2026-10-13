"""300-dpi report figures from the frozen benchmark (no recomputation of results).

python -B make_figures.py --results-dir resultados/agent/neurocubo_20261013 --traj-dir D:/PROJECTS/.cognition/neurocubo/real/trajectories
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"
SERIES = {"optical": "#2a78d6", "logistic": "#eb6834", "mlp": "#1baf7a", "real_matched": "#eda100",
          "majority": "#8a8984"}
LABEL = {"optical": "Neuro-cube (optical)", "logistic": "Logistic regression", "mlp": "MLP (free gain)",
         "real_matched": "Real net, matched gain", "majority": "Majority class"}
SIZE_COLOR = {4: "#eb6834", 8: "#2a78d6"}
BLUES = LinearSegmentedColormap.from_list("seq", ["#f3f6fb", "#2a78d6", "#0d2f5c"])
DIGITS = {"dev03": [0, 1, 2, 3], "res47": [4, 5, 6, 7], "syn": [0, 1, 2, 3]}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.titlecolor": INK, "axes.titlesize": 9, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                     "legend.frameon": False})


def save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig_training(res: Path, traj: Path, out: Path, tasks) -> None:
    keys = [(t, n) for t in tasks for n in (4, 8)]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.6), sharey=False)
    for ax, (task, n) in zip(axes.flat, keys):
        cand = json.loads((res / "training" / ("candidates_%s_N%d.json" % (task, n))).read_text())
        g = cand["chosen_gain"]
        for start in next(p for p in cand["per_gain"] if p["gain"] == g)["starts"]:
            path = traj / ("%s_N%d_G%g_seed%d.npz" % (task, n, g, start["seed"]))
            if not path.exists():
                continue
            with np.load(path) as d:
                loss = d["loss"]
            chosen = start["seed"] == cand["chosen_seed"]
            ax.plot(np.arange(1, len(loss) + 1), loss, color=SERIES["optical"] if chosen else MUTED,
                    lw=2 if chosen else 0.8, alpha=1 if chosen else 0.6, zorder=3 if chosen else 2)
        ax.set_xscale("log")
        ax.set_title("%s, N = %d  (G = %g, seed %d%s)" % (task, n, g, cand["chosen_seed"],
                                                          "" if cand["chosen_converged"] else ", NOT converged"))
        ax.set_xlabel("L-BFGS iteration (one full-batch epoch)")
        ax.set_ylabel("training cross-entropy")
    fig.suptitle("Training inside Blender: every start at the chosen readout gain (blue = selected)",
                 color=INK, fontsize=10)
    fig.tight_layout()
    save(fig, out)


def fig_responses(report: dict, out: Path) -> None:
    resp = report["responses"]
    digits = DIGITS[resp["task"]]
    examples = resp["examples"][:12]
    fig = plt.figure(figsize=(7.2, 6.4))
    grid = fig.add_gridspec(4, 6, wspace=0.35, hspace=0.75)
    for i, ex in enumerate(examples):
        r, c = divmod(i, 3)
        ax_img = fig.add_subplot(grid[r, 2 * c])
        ax_img.imshow(np.asarray(ex["image_8x8"]), cmap="Greys", vmin=0, vmax=16)
        ax_img.set_xticks([]), ax_img.set_yticks([])
        ax_img.grid(False)
        ax_img.set_title("true %d" % digits[ex["true"]], fontsize=7, color=INK2)
        ax = fig.add_subplot(grid[r, 2 * c + 1])
        inten = np.asarray(ex["output_intensities"])
        ports = np.arange(len(inten))
        colors = [SERIES["optical"] if p < len(digits) else GRID for p in ports]
        ax.grid(axis="x", visible=False)
        ax.bar(ports, inten, color=colors, width=0.7)
        ax.bar([ex["predicted"]], [inten[ex["predicted"]]], color="#0d2f5c" if ex["correct"] else "#e34948",
               width=0.7)
        ax.set_xticks(ports)
        ax.set_xticklabels([str(digits[p]) if p < len(digits) else "" for p in ports], fontsize=6)
        ax.tick_params(axis="y", labelsize=6)
        ax.set_title("pred %d %s" % (digits[ex["predicted"]], "ok" if ex["correct"] else "WRONG"), fontsize=7,
                     color=INK if ex["correct"] else "#e34948")
    n_fail = len(resp["failures"])
    fig.suptitle("Neuro-cube responses on the reserved test set (%s, N = %d): input image and detected output "
                 "intensities\n(read ports labelled by digit; dark bar = predicted; %d test failures in total)"
                 % (resp["task"], resp["n"], n_fail), color=INK, fontsize=9)
    save(fig, out)


def fig_robustness(report: dict, out: Path, tasks) -> None:
    fig, axes = plt.subplots(1, len(tasks) + 1, figsize=(7.2, 2.8))
    for ax, task in zip(axes, tasks):
        for n in (4, 8):
            rob = report["tasks"][task]["results"]["N%d" % n]["robustness"]
            sig = [r["sigma"] for r in rob]
            base = rob[0]["accuracy"]
            nore = [base] + [r["without_recalibration"]["mean"] for r in rob[1:]]
            reca = [base] + [r["with_recalibration"]["mean"] for r in rob[1:]]
            lo = [base] + [r["without_recalibration"]["p05"] for r in rob[1:]]
            ax.plot(sig, reca, "-o", color=SIZE_COLOR[n], lw=2, ms=4, label="N=%d recalibrated" % n)
            ax.plot(sig, nore, "--s", color=SIZE_COLOR[n], lw=1.5, ms=4, label="N=%d frozen" % n)
            ax.fill_between(sig, lo, nore, color=SIZE_COLOR[n], alpha=0.12, lw=0)
        ax.set_title(task)
        ax.set_xlabel("coupler error sigma (rad), corr. 0.8")
        ax.set_ylabel("test accuracy (mean; band to p05)")
    axes[0].legend(fontsize=6, loc="lower left")
    ax = axes[-1]
    for n in (4, 8):
        for task, style in zip(tasks, ("--", "-")):
            res = report["tasks"][task]["results"]["N%d" % n]
            bits = [d["bits"] for d in res["dac"]]
            ax.plot(bits, [d["accuracy"] for d in res["dac"]], style, marker="o", ms=4, color=SIZE_COLOR[n],
                    label="%s N=%d" % (task, n))
            ax.axhline(res["models"]["optical"]["accuracy"], color=SIZE_COLOR[n], lw=0.6, ls=":")
    ax.set_title("phase DAC resolution")
    ax.set_xlabel("bits over 2 pi")
    ax.set_xticks([8, 10, 12])
    ax.legend(fontsize=6)
    fig.tight_layout()
    save(fig, out)


def fig_comparison(report: dict, out: Path, tasks, show_task: str) -> None:
    models = ["optical", "real_matched", "logistic", "mlp", "majority"]
    fig = plt.figure(figsize=(7.2, 5.6))
    grid = fig.add_gridspec(2, 5, height_ratios=[1.1, 1], hspace=0.55, wspace=0.45)
    ax = fig.add_subplot(grid[0, :])
    configs = [(t, n) for t in tasks for n in (4, 8)]
    for j, m in enumerate(models):
        for i, (t, n) in enumerate(configs):
            block = report["tasks"][t]["results"]["N%d" % n]["models"][m]
            x = i + (j - 2) * 0.14
            lo, hi = block["accuracy_ci95_clopper_pearson"]
            ax.plot([x, x], [lo, hi], color=SERIES[m], lw=2, solid_capstyle="round")
            ax.plot(x, block["accuracy"], "o", ms=5, color=SERIES[m], mec=SURFACE, mew=1,
                    label=LABEL[m] if i == 0 else None)
    ax.set_xticks(range(len(configs)))
    ax.set_xticklabels(["%s N=%d" % c for c in configs])
    ax.set_ylabel("test accuracy (Clopper-Pearson 95 %)")
    ax.legend(ncol=5, fontsize=6, loc="upper center", bbox_to_anchor=(0.5, 1.18))
    for k, m in enumerate(models[:4]):
        for r, n in enumerate([8]):
            axc = fig.add_subplot(grid[1, k])
            cm = np.asarray(report["tasks"][show_task]["results"]["N%d" % n]["models"][m]["confusion_matrix_rows_true"])
            axc.imshow(cm, cmap=BLUES)
            axc.grid(False)
            for (a, b), v in np.ndenumerate(cm):
                axc.text(b, a, str(v), ha="center", va="center", fontsize=6,
                         color="#ffffff" if v > cm.max() / 2 else INK)
            d = DIGITS[show_task]
            axc.set_xticks(range(len(d)), [str(v) for v in d])
            axc.set_yticks(range(len(d)), [str(v) for v in d])
            axc.set_xlabel("predicted")
            if k == 0:
                axc.set_ylabel("true")
            axc.set_title("%s\n%s N=%d" % (LABEL[m], show_task, n), fontsize=7)
    save(fig, out)


def fig_phases(res: Path, report: dict, out: Path, show_task: str) -> None:
    with np.load(res / "training" / ("trajectory_selected_%s_N8.npz" % show_task)) as d:
        phases, loss = d["phases"].astype(float), d["loss"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={"width_ratios": [1.6, 1]})
    ax = axes[0]
    it = np.arange(1, len(phases) + 1)
    unwrapped = np.unwrap(phases, axis=0)
    rel = unwrapped - unwrapped[0]
    for k in range(rel.shape[1]):
        ax.plot(it, rel[:, k], color=MUTED, lw=0.4, alpha=0.6)
    ax.plot(it, np.sqrt(np.mean(rel ** 2, axis=1)), color=SERIES["optical"], lw=2, label="RMS change")
    ax.set_xscale("log")
    ax.set_xlabel("iteration")
    ax.set_ylabel("heater phase change (rad)")
    ax.set_title("All 128 heater phases during training (%s, N = 8)" % show_task)
    ax.legend(fontsize=6)
    ax = axes[1]
    n = 8
    final = np.mod(phases[-1], 2 * np.pi)
    img = np.full((2 * n, n + 1), np.nan)
    from neurocubo_core import mesh_template
    tmpl = mesh_template(n)
    for li in range(2):
        q = final[li * n * n:(li + 1) * n * n]
        for k, (m, col) in enumerate(tmpl):
            img[li * n + m, col - 1] = q[2 * k]
        img[li * n:(li + 1) * n, n] = q[2 * len(tmpl):]
    im = ax.imshow(img, cmap="twilight", vmin=0, vmax=2 * np.pi, aspect="auto")
    ax.grid(False)
    ax.axhline(n - 0.5, color=INK, lw=1)
    ax.set_xlabel("column (last = output phases)")
    ax.set_ylabel("layer 1 modes | layer 2 modes")
    ax.set_title("final internal phases theta (rad)")
    fig.colorbar(im, ax=ax, fraction=0.05)
    fig.tight_layout()
    save(fig, out)


def main() -> None:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--traj-dir", type=Path, required=True)
    parser.add_argument("--tasks", nargs="+", default=["dev03", "res47"])
    parser.add_argument("--show-task", default="res47")
    args = parser.parse_args()
    res = args.results_dir
    report = json.loads((res / "benchmark" / "benchmark.json").read_text())
    figs = res / "figures"
    fig_training(res, args.traj_dir, figs / "fig1_training.png", args.tasks)
    fig_responses(report, figs / ("fig2_responses_%s_N8.png" % args.show_task))
    fig_robustness(report, figs / "fig3_robustness.png", args.tasks)
    fig_comparison(report, figs / "fig4_confusion.png", args.tasks, args.show_task)
    fig_phases(res, report, figs / "fig5_phases.png", args.show_task)
    print("figures written to", figs)


if __name__ == "__main__":
    main()
