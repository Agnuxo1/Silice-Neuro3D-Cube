"""Verificacion de bpm.py segun CONTRATO-bpm.md (umbrales fijados antes de calcular).

Solo CPU, numpy/scipy. Ejecutar con: python -B verificar_bpm.py
"""
import json
import time
import datetime
import numpy as np
from scipy import special as sp
from scipy.optimize import brentq

import bpm

LAM = 1.55            # um
A_CORE = 6.0          # um
N1 = 1.444
N2 = 1.439
NREF = N1
K0 = 2.0 * np.pi / LAM
VNUM = K0 * A_CORE * np.sqrt(N1 ** 2 - N2 ** 2)
NEFF_GIVEN = 1.4421922   # referencia del enunciado (se verifica, no se usa como entrada)

# Umbrales (fijados en CONTRATO-bpm.md)
THR_V0 = 1e-9
THR_C0 = 1e-6
THR_C1 = 0.999
THR_C2 = 1e-5
THR_C3 = 1e-6
THR_C4 = 1e-5
THR_C5 = 1e-5

H_BASE = 0.2
H_FINE = 0.1
N_BASE = 401   # M = 200, ventana +-40 um
N_FINE = 801   # M = 400
DZ_BASE = 1.0
DZ_HALF = 0.5
Z_B1 = 1000.0  # 1 mm
Z_B4 = 10000.0 # 10 mm (solo informa)


def lp01_solve():
    """Ecuacion caracteristica de la fibra de salto (escalar, exacta)."""
    def f(u):
        w = np.sqrt(VNUM ** 2 - u ** 2)
        return u * sp.j1(u) / sp.j0(u) - w * sp.k1(w) / sp.k0(w)
    u = brentq(f, 1e-6, 2.404825)
    w = np.sqrt(VNUM ** 2 - u ** 2)
    neff = np.sqrt(N1 ** 2 - (u / (K0 * A_CORE)) ** 2)
    return float(u), float(w), float(neff)


def lp01_field(x, xc, u, w):
    """LP01 analitico centrado en (xc, 0), E(0) = 1, muestreado en nodos."""
    X, Y = np.meshgrid(x, x, indexing="ij")
    r = np.hypot(X - xc, Y)
    rin = np.minimum(r, A_CORE)
    rout = np.maximum(r, A_CORE)
    with np.errstate(all="ignore"):
        inside = sp.j0(u * rin / A_CORE) / sp.j0(u)
        outside = sp.k0(w * rout / A_CORE) / sp.k0(w)
    return np.where(r <= A_CORE, inside, outside).astype(complex)


def n_xy_cell(x, h, centers, sub=16):
    """Indice sqrt(<n^2>) promediado por celda (subcuadricula sub x sub)."""
    N = len(x)
    X0, Y0 = np.meshgrid(x, x, indexing="ij")
    offs = (np.arange(sub) + 0.5) / sub - 0.5
    acc = np.zeros((N, N))
    for ox in offs:
        for oy in offs:
            X = X0 + ox * h
            Y = Y0 + oy * h
            inside = np.zeros((N, N), dtype=bool)
            for xc in centers:
                inside |= np.hypot(X - xc, Y) <= A_CORE
            acc += np.where(inside, N1 ** 2, N2 ** 2)
    return np.sqrt(acc / (sub * sub))


def n_xy_nodal(x, centers):
    """Indice muestreado en nodos (sensibilidad, no criterio principal)."""
    X0, Y0 = np.meshgrid(x, x, indexing="ij")
    inside = np.zeros(X0.shape, dtype=bool)
    for xc in centers:
        inside |= np.hypot(X0 - xc, Y0) <= A_CORE
    return np.where(inside, N1, N2)


def mask_disk(x, xc):
    X0, Y0 = np.meshgrid(x, x, indexing="ij")
    return np.hypot(X0 - xc, Y0) <= A_CORE


class Recorder:
    """Registra overlap con psi0, potencia, y opcionalmente P2 modal y de disco."""

    def __init__(self, psi0, h, psi2=None, mask2=None):
        self.psi0 = psi0
        self.h2 = h * h
        self.n0 = float(np.sum(np.abs(psi0) ** 2) * self.h2)
        self.psi2 = psi2
        self.n2 = float(np.sum(np.abs(psi2) ** 2) * self.h2) if psi2 is not None else None
        self.mask2 = mask2
        self.z = []
        self.ip = []
        self.P = []
        self.P2m = []
        self.P2d = []

    def __call__(self, z, A):
        self.z.append(float(z))
        self.ip.append(complex(np.sum(np.conj(self.psi0) * A) * self.h2))
        self.P.append(float(np.sum(np.abs(A) ** 2) * self.h2))
        if self.psi2 is not None:
            ip2 = np.sum(np.conj(self.psi2) * A) * self.h2
            self.P2m.append(float(abs(ip2) ** 2 / (self.n2 * self.n0)))
        if self.mask2 is not None:
            self.P2d.append(float(np.sum(np.abs(A[self.mask2]) ** 2) * self.h2 / self.n0))

    def phase(self):
        return np.unwrap(np.angle(np.array(self.ip)))

    def n_impl_at(self, z):
        zs = np.array(self.z)
        ph = self.phase()
        k = int(np.argmin(np.abs(zs - z)))
        return float(NREF - ph[k] / (K0 * zs[k])), float(zs[k])

    def overlap2_at(self, z):
        zs = np.array(self.z)
        k = int(np.argmin(np.abs(zs - z)))
        return float(abs(self.ip[k]) ** 2 / (self.n0 * self.P[k])), float(zs[k])

    def loss_at(self, z):
        zs = np.array(self.z)
        k = int(np.argmin(np.abs(zs - z)))
        return float(1.0 - self.P[k] / self.P[0]), float(zs[k])


def first_local_max(z, y, start=5):
    for k in range(start, len(y) - 1):
        if y[k] > y[k - 1] and y[k] >= y[k + 1]:
            yl, y0, yr = y[k - 1], y[k], y[k + 1]
            den = yl - 2.0 * y0 + yr
            off = 0.5 * (yl - yr) / den if den != 0 else 0.0
            dzs = z[k + 1] - z[k]
            return {"z_um": float(z[k] + off * dzs),
                    "value": float(y0 - 0.25 * (yl - yr) * off),
                    "index_step": int(k)}
    return None


def main():
    t0 = time.time()
    out = {"fecha_utc": datetime.datetime.utcnow().isoformat() + "Z", "bloques": {}}
    log = []

    def say(msg):
        print(msg, flush=True)
        log.append(msg)

    u, w, neff_an = lp01_solve()
    n_par_pred = NREF + (neff_an ** 2 - NREF ** 2) / (2.0 * NREF)
    out["analitico"] = {"V": VNUM, "u": u, "w": w, "neff_analitico": neff_an,
                        "neff_dado_enunciado": NEFF_GIVEN,
                        "neff_paraxial_prediccion": n_par_pred,
                        "k0_um^-1": K0, "n_ref": NREF}
    say(f"[ref] V={VNUM:.6f} u={u:.6f} w={w:.6f} neff_analitico={neff_an:.10f} "
        f"neff_par_pred={n_par_pred:.10f}")

    # ---- C0: referencia analitica
    c0_val = abs(neff_an - NEFF_GIVEN)
    say(f"[C0] |neff_analitico - 1.4421922| = {c0_val:.3e}  (umbral {THR_C0:.0e})")

    # ---- Malla base y LP01 de un nucleo
    x = bpm.axis_coords(N_BASE, H_BASE)
    E0 = lp01_field(x, 0.0, u, w)
    n_cell = n_xy_cell(x, H_BASE, [0.0])

    # ---- V0: unitariedad sin CAP (200 um)
    rec_v0 = Recorder(E0, H_BASE)
    bpm.propagate(n_cell, E0, LAM, H_BASE, DZ_BASE, [200.0], NREF, cap=False, observe=rec_v0)
    v0_dev = float(np.max(np.abs(np.array(rec_v0.P) / rec_v0.P[0] - 1.0)))
    say(f"[V0] sin CAP, 200 um: max|P/P0-1| = {v0_dev:.3e}  (umbral {THR_V0:.0e})")

    # ---- B1: LP01 propagado 1 mm (h=0.2, dz=1), CAP activo
    t1 = time.time()
    rec_b1 = Recorder(E0, H_BASE)
    bpm.propagate(n_cell, E0, LAM, H_BASE, DZ_BASE, [Z_B1], NREF, cap=True, observe=rec_b1)
    ov2_1mm, zc = rec_b1.overlap2_at(Z_B1)
    neff_b1, _ = rec_b1.n_impl_at(Z_B1)
    loss_b1, _ = rec_b1.loss_at(Z_B1)
    curve = {}
    for zq in [100.0, 200.0, 400.0, 600.0, 800.0, 1000.0]:
        nq, _ = rec_b1.n_impl_at(zq)
        oq, _ = rec_b1.overlap2_at(zq)
        curve[str(int(zq))] = {"neff_impl": nq, "overlap2": oq}
    say(f"[B1] h=0.2 dz=1: overlap2(1mm)={ov2_1mm:.10f}  neff_impl(1mm)={neff_b1:.10f}  "
        f"perdida(1mm)={loss_b1:.3e}  ({time.time() - t1:.1f} s)")
    out["bloques"]["B1"] = {"h_um": H_BASE, "N": N_BASE, "dz_um": DZ_BASE, "z_um": Z_B1,
                            "overlap2_1mm": ov2_1mm, "neff_impl_1mm": neff_b1,
                            "delta_neff_vs_analitico": neff_b1 - neff_an,
                            "perdida_1mm": loss_b1, "curva": curve}

    # ---- I1: sensibilidad con muestreo nodal (sin umbral)
    n_nod = n_xy_nodal(x, [0.0])
    rec_nod = Recorder(E0, H_BASE)
    bpm.propagate(n_nod, E0, LAM, H_BASE, DZ_BASE, [Z_B1], NREF, cap=True, observe=rec_nod)
    neff_nod, _ = rec_nod.n_impl_at(Z_B1)
    ov_nod, _ = rec_nod.overlap2_at(Z_B1)
    say(f"[I1] muestreo nodal: neff_impl(1mm)={neff_nod:.10f} "
        f"(dif vs analitico {neff_nod - neff_an:+.3e}), overlap2={ov_nod:.8f}")
    out["bloques"]["I1_nodal"] = {"neff_impl_1mm": neff_nod,
                                  "delta_vs_analitico": neff_nod - neff_an,
                                  "overlap2_1mm": ov_nod}

    # ---- B2a: convergencia en dz (dz/2), h = 0.2
    t2 = time.time()
    rec_dzh = Recorder(E0, H_BASE)
    bpm.propagate(n_cell, E0, LAM, H_BASE, DZ_HALF, [Z_B1], NREF, cap=True, observe=rec_dzh)
    neff_dzh, _ = rec_dzh.n_impl_at(Z_B1)
    ov_dzh, _ = rec_dzh.overlap2_at(Z_B1)
    d_dz = neff_dzh - neff_b1
    say(f"[B2a] dz=0.5: neff_impl(1mm)={neff_dzh:.10f}  cambio vs dz=1: {d_dz:+.3e}  "
        f"overlap2={ov_dzh:.10f} ({time.time() - t2:.1f} s)")
    out["bloques"]["B2_dz"] = {"neff_dz1": neff_b1, "neff_dz05": neff_dzh,
                               "cambio": d_dz, "overlap2_dz05": ov_dzh}

    # ---- B2b: convergencia en h (h/2 = 0.1), dz = 1
    t3 = time.time()
    xf = bpm.axis_coords(N_FINE, H_FINE)
    E0f = lp01_field(xf, 0.0, u, w)
    n_cell_f = n_xy_cell(xf, H_FINE, [0.0])
    rec_hf = Recorder(E0f, H_FINE)
    bpm.propagate(n_cell_f, E0f, LAM, H_FINE, DZ_BASE, [Z_B1], NREF, cap=True, observe=rec_hf)
    neff_hf, _ = rec_hf.n_impl_at(Z_B1)
    ov_hf, _ = rec_hf.overlap2_at(Z_B1)
    loss_hf, _ = rec_hf.loss_at(Z_B1)
    d_h = neff_hf - neff_b1
    say(f"[B2b] h=0.1: neff_impl(1mm)={neff_hf:.10f}  cambio vs h=0.2: {d_h:+.3e}  "
        f"overlap2={ov_hf:.10f} perdida={loss_hf:.3e} ({time.time() - t3:.1f} s)")
    out["bloques"]["B2_h"] = {"neff_h02": neff_b1, "neff_h01": neff_hf, "cambio": d_h,
                              "overlap2_h01": ov_hf, "perdida_h01": loss_hf,
                              "delta_h01_vs_analitico": neff_hf - neff_an}

    # ---- B3: perdida del modo guiado (del propio B1)
    say(f"[B3] perdida del modo guiado (1 mm, h=0.2): {loss_b1:.3e}  (umbral {THR_C5:.0e})")
    out["bloques"]["B3"] = {"perdida_1mm_h02": loss_b1, "perdida_1mm_h01": loss_hf}

    # ---- B4: dos nucleos a +-8 um, E0 = modo de un nucleo (en x=-8), solo informa
    t4 = time.time()
    xc1, xc2 = -8.0, +8.0
    psi_a = lp01_field(x, xc1, u, w)   # entrada: nucleo 1 en x=-8
    psi_b = lp01_field(x, xc2, u, w)   # proyeccion: nucleo 2 en x=+8
    n_two = n_xy_cell(x, H_BASE, [xc1, xc2])
    mask_b = mask_disk(x, xc2)
    rec_b4 = Recorder(psi_a, H_BASE, psi2=psi_b, mask2=mask_b)
    bpm.propagate(n_two, psi_a, LAM, H_BASE, DZ_BASE, [Z_B4], NREF, cap=True, observe=rec_b4)
    z_arr = np.array(rec_b4.z)
    fm = first_local_max(z_arr, np.array(rec_b4.P2m))
    fm_disk = first_local_max(z_arr, np.array(rec_b4.P2d))
    P2m_end = rec_b4.P2m[-1]
    say(f"[B4] P2m primer maximo: {fm} ; P2 disco primer maximo: {fm_disk} ; "
        f"P2m final={P2m_end:.4e} ({time.time() - t4:.1f} s)")
    out["bloques"]["B4"] = {"separacion_um": 16.0, "z_max_propagado_um": Z_B4,
                            "primer_max_P2m": fm, "primer_max_P2_disco": fm_disk,
                            "P2m_inicial": rec_b4.P2m[0], "P2m_final": P2m_end,
                            "perdida_final": rec_b4.loss_at(Z_B4)[0]}

    # ---- Criterios
    crit = []

    def add(cid, desc, value, thr, passed):
        crit.append({"id": cid, "description": desc, "value": value,
                     "threshold": thr, "pass": bool(passed)})

    add("V0", "Unitariedad sin CAP (200 um): max|P/P0-1| <= 1e-9",
        f"{v0_dev:.3e}", "1e-9", v0_dev <= THR_V0)
    add("C0", "n_eff analitico propio vs 1.4421922: |dif| <= 1e-6",
        f"{c0_val:.3e} (n_eff={neff_an:.10f})", "1e-6", c0_val <= THR_C0)
    add("C1", "B1 overlap2 a 1 mm >= 0.999 (h=0.2, dz=1)",
        f"{ov2_1mm:.10f}", ">=0.999", ov2_1mm >= THR_C1)
    dn_b1 = abs(neff_b1 - neff_an)
    add("C2", "B1 |neff_impl(1mm) - neff_analitico| <= 1e-5",
        f"{dn_b1:.3e} (neff_impl={neff_b1:.10f})", "1e-5", dn_b1 <= THR_C2)
    add("C3", "B2 |neff(dz=0.5) - neff(dz=1)| <= 1e-6 (h=0.2)",
        f"{abs(d_dz):.3e}", "1e-6", abs(d_dz) <= THR_C3)
    add("C4", "B2 |neff(h=0.1) - neff(h=0.2)| <= 1e-5 (dz=1)",
        f"{abs(d_h):.3e}", "1e-5", abs(d_h) <= THR_C4)
    add("C5", "B3 perdida del modo guiado a 1 mm (con CAP) <= 1e-5",
        f"{loss_b1:.3e}", "1e-5", loss_b1 <= THR_C5)
    add("C6", "B4 primer maximo de P2m hallado en 0<z<=10 mm (solo informa)",
        (f"z={fm['z_um']:.2f} um, P2m={fm['value']:.6f}" if fm else "no hallado"),
        "informativo", fm is not None)
    add("I1", "Sensibilidad: muestreo nodal vs celda (informativo)",
        f"nodal neff={neff_nod:.10f}, dif analitico={neff_nod - neff_an:+.3e}",
        "sin umbral", True)

    out["criterios"] = crit
    out["tiempo_total_s"] = time.time() - t0
    say("")
    for c in crit:
        say(f"{c['id']:>3} | pass={c['pass']} | {c['value']} | umbral {c['threshold']}")
    say(f"tiempo total: {time.time() - t0:.1f} s")

    with open("resultados_bpm.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=float)
    with open("log_bpm.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")


if __name__ == "__main__":
    main()
