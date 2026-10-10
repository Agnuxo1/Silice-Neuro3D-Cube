"""TAREA G, G3 y G4: propagacion BPM de un modo de un nucleo en la guia doble.

Propaga el modo de un nucleo (solver2d, un disco en -d/2) con experimentos/bpm_claude/bpm.py
y mide el primer maximo de P2(z) = |<psi_R|A(z)>|^2 / (<psi_R|psi_R><A0|A0>).
Compara z_max con L_c = pi/(2 kappa_FD), con kappa_FD tomado de resultados_g1_g2.json (G1).
Modelo numerico escalar. Un hilo, CPU. Contrato: CONTRATO-acoplador.md (secciones 3 y 7).
Salida: resultados_g3_bpm.json y curvas npz (sin pickle) en esta carpeta.
"""
import datetime
import hashlib
import json
import pathlib
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
EXP = HERE.parent
for sub in ("solver2d_claude", "bpm_claude"):
    sys.path.insert(0, str(EXP / sub))
import solver2d as S2   # noqa: E402  (experimentos/solver2d_claude/solver2d.py)
import bpm as BPM       # noqa: E402  (experimentos/bpm_claude/bpm.py)

LAM, A, N1, N2 = 1.55, 6.0, 1.444, 1.439
H = 0.2          # malla BPM
L = 40.4         # semilado de la ventana: N = 405 (enmienda E-1)
N_REF = N1       # referencia del BPM (CONTRATO-bpm: n_ref = n1)
TOL_LC, P2_MIN, LOSS_MAX, TOL_DZ, P2_FLOOR = 0.10, 0.90, 1e-3, 0.01, 0.05
Z_FACTOR = 1.25  # propagar hasta 1,25 L_c para ver el maximo y la bajada


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def two_core(d):
    return [
        {"kind": "disk", "x0": -d / 2.0, "y0": 0.0, "r": A, "n": N1},
        {"kind": "disk", "x0": +d / 2.0, "y0": 0.0, "r": A, "n": N1},
    ]


def single(x0):
    return [{"kind": "disk", "x0": float(x0), "y0": 0.0, "r": A, "n": N1}]


def ip(a, b):
    """Producto interno con h^2 (campos en la convencion BPM [ix, iy])."""
    return H * H * np.sum(np.conj(a) * b)


def first_local_max(z, p2, floor):
    for k in range(1, len(p2) - 1):
        if p2[k] > floor and p2[k] >= p2[k - 1] and p2[k] > p2[k + 1]:
            return k
    return None


def run_one(d, dz, kappa_fd, tag):
    t0 = time.time()
    geo = S2.solve(two_core(d), N2, LAM, L, H, n_modes=1, s_sub=8)
    n_xy = np.sqrt(geo["cell_n2"]).T                       # BPM: [ix, iy]
    sL = S2.solve(single(-d / 2.0), N2, LAM, L, H, n_modes=1, s_sub=8)
    sR = S2.solve(single(+d / 2.0), N2, LAM, L, H, n_modes=1, s_sub=8)
    E0 = sL["psi"][0].T.astype(complex)
    psiR = sR["psi"][0].T.astype(complex)
    n0 = ip(E0, E0).real
    nR = ip(psiR, psiR).real
    P0 = n0

    lc = np.pi / (2.0 * kappa_fd)                           # um
    z_end = Z_FACTOR * lc
    z_end = float(np.ceil(z_end / dz) * dz)

    zs, p2, ptot = [], [], []

    def observe(z, Aa):
        ov = ip(psiR, Aa)
        zs.append(float(z))
        p2.append(float(abs(ov) ** 2 / (nR * n0)))
        ptot.append(float(ip(Aa, Aa).real / P0))

    BPM.propagate(n_xy, E0, LAM, H, dz, [z_end], N_REF, cap=True, observe=observe)
    zs = np.asarray(zs)
    p2 = np.asarray(p2)
    ptot = np.asarray(ptot)
    np.savez(HERE / f"curva_g3_{tag}.npz", z_um=zs, P2=p2, P_total=ptot)

    k = first_local_max(zs, p2, P2_FLOOR)
    if k is None:
        z_max, p2_max, loss = None, None, None
        rel_dev = None
    else:
        z_max = float(zs[k])
        p2_max = float(p2[k])
        loss = float(1.0 - ptot[k])
        rel_dev = abs(z_max - lc) / lc
    i10 = int(np.argmin(np.abs(zs - 10000.0)))
    gmax = int(np.argmax(p2))
    return {
        "tag": tag, "d_um": d, "dz_um": dz, "h_um": H, "L_um": L, "N": int(geo["N"]),
        "kappa_FD_per_um": kappa_fd, "Lc_FD_um": lc, "z_end_um": z_end,
        "z_max_um": z_max, "P2_at_z_max": p2_max, "loss_total_at_z_max": loss,
        "rel_dev_zmax_vs_Lc": rel_dev,
        "P2_global_max": float(p2[gmax]), "z_global_max_um": float(zs[gmax]),
        "P2_at_10mm": float(p2[i10]), "z_at_10mm_sampled_um": float(zs[i10]),
        "P_total_end": float(ptot[-1]),
        "overlap_launch_R": float(abs(ip(psiR, E0)) ** 2 / (nR * n0)),
        "steps": int(round(z_end / dz)), "time_s": round(time.time() - t0, 1),
        "curve_file": f"curva_g3_{tag}.npz",
    }


def main():
    t_start = utc()
    g1 = json.loads((HERE / "resultados_g1_g2.json").read_text(encoding="utf-8"))
    kappa = {float(k): v["kappa_FD_per_um"] for k, v in g1["G1_main_h0125"].items()}
    out = {
        "task": "G3 BPM P2 primer maximo frente a L_c = pi/(2 kappa_FD) ; G4 lectura",
        "started_utc": t_start,
        "files_sha256": {
            "bpm.py": sha256(EXP / "bpm_claude" / "bpm.py"),
            "solver2d.py": sha256(EXP / "solver2d_claude" / "solver2d.py"),
            "resultados_g1_g2.json": sha256(HERE / "resultados_g1_g2.json"),
        },
        "params": {"lam_um": LAM, "a_um": A, "n1": N1, "n2": N2, "h_um": H, "L_um": L,
                   "n_ref": N_REF, "P2_floor": P2_FLOOR, "tol_Lc": TOL_LC,
                   "P2_min": P2_MIN, "loss_max": LOSS_MAX, "tol_dz": TOL_DZ},
        "runs": {},
    }

    plan = [(14.0, 1.0, "d14_dz1"), (16.0, 1.0, "d16_dz1"),
            (14.0, 0.5, "d14_dz0p5"), (20.0, 1.0, "d20_dz1")]
    for d, dz, tag in plan:
        print(f"[{utc()}] inicio {tag}", flush=True)
        r = run_one(d, dz, kappa[d], tag)
        out["runs"][tag] = r
        print(tag, {k: r[k] for k in ("z_max_um", "Lc_FD_um", "rel_dev_zmax_vs_Lc",
                                      "P2_at_z_max", "loss_total_at_z_max", "P2_at_10mm",
                                      "time_s")}, flush=True)
        # escribir tras cada corrida para conservar resultados parciales
        out["finished_partial_utc"] = utc()
        (HERE / "resultados_g3_bpm.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                     encoding="utf-8", newline="\n")

    # criterios G3 evaluados por el codigo
    crit = {}
    for tag in ("d14_dz1", "d16_dz1", "d20_dz1"):
        if tag not in out["runs"]:
            crit[tag] = {"evaluated": False}
            continue
        r = out["runs"][tag]
        if r["z_max_um"] is None:
            crit[tag] = {"evaluated": True, "pass_G3_1": False, "reason": "sin maximo"}
            continue
        crit[tag] = {
            "evaluated": True,
            "G3_1_rel_dev": r["rel_dev_zmax_vs_Lc"], "G3_1_pass": bool(r["rel_dev_zmax_vs_Lc"] <= TOL_LC),
            "G3_2_P2_at_zmax": r["P2_at_z_max"], "G3_2_pass": bool(r["P2_at_z_max"] >= P2_MIN),
            "G3_3_loss": r["loss_total_at_z_max"], "G3_3_pass": bool(r["loss_total_at_z_max"] <= LOSS_MAX),
        }
    if "d14_dz0p5" in out["runs"] and out["runs"]["d14_dz1"]["z_max_um"] is not None \
            and out["runs"]["d14_dz0p5"]["z_max_um"] is not None:
        a = out["runs"]["d14_dz1"]["z_max_um"]
        b = out["runs"]["d14_dz0p5"]["z_max_um"]
        dev = abs(b - a) / a
        crit["G3_4_dz_sensitivity_d14"] = {"z_dz1": a, "z_dz0p5": b, "rel_dev": dev,
                                           "pass": bool(dev <= TOL_DZ)}
    else:
        crit["G3_4_dz_sensitivity_d14"] = {"evaluated": False}
    out["criteria"] = crit

    # G4: lectura del H-T8-1 con kappa_FD (d = 20) y BPM a 10 mm
    k20 = kappa[20.0]
    p2_fd_10mm = float(np.sin(k20 * 10000.0) ** 2)
    g4 = {"P2_FD_at_20um_10mm": p2_fd_10mm, "H_T8_1_threshold": 0.10,
          "H_T8_1_pass_with_FD": bool(p2_fd_10mm <= 0.10)}
    if "d20_dz1" in out["runs"]:
        g4["P2_BPM_at_20um_10mm"] = out["runs"]["d20_dz1"]["P2_at_10mm"]
        g4["H_T8_1_pass_with_BPM"] = bool(out["runs"]["d20_dz1"]["P2_at_10mm"] <= 0.10)
    out["G4"] = g4
    out["finished_utc"] = utc()
    (HERE / "resultados_g3_bpm.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                 encoding="utf-8", newline="\n")
    print("G4", g4, flush=True)
    print("escrito resultados_g3_bpm.json", flush=True)


if __name__ == "__main__":
    main()
