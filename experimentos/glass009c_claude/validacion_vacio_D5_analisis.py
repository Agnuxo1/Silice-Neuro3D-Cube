# -*- coding: utf-8 -*-
"""GLASS-009c D5: validacion de vacio con haces de cola espectral controlada (cambio de protocolo de haz).

Contrato: CONTRATO-HAZ-COLA-D5-r5.md (fijado antes de este calculo).
Lee D5_out/*.json (corridas nuevas) y D3_out/*.json (referencias ya calculadas, mismas condiciones).
No lanza simulaciones. Solo numpy, scipy y adi2d.py (solver de 009c; solo para malla y energia inicial).
Escribe resultados009c_D5.json.
"""
import hashlib
import json
import os
import sys

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True

import numpy as np
from scipy import special

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "glass009_claude"))
import adi2d as S  # solver de 009c (sin cambios)

D3DIR = os.path.join(HERE, "D3_out")
D5DIR = os.path.join(HERE, "D5_out")
OUTJSON = os.path.join(HERE, "resultados009c_D5.json")

# Umbrales fijados en CONTRATO-HAZ-COLA-D5-r5.md
K1_THR = 1e-4
W0_MM = 0.2          # inicio de la ventana comun (de D4)
Z1_MM = 2.0          # fin de la ventana comun
FRAC = 0.2           # absorbente base
ZMAX = 2.0e-3        # fin de la ventana para la banda cinematica
L = 256e-6           # dominio
DX = 0.5e-6
K0A_TOL = 1e-9
K0B_TOL = 1e-12
K0C_TOL = 1e-9
K0D_TOL = 1e-9
K0E_TOL = 1e-12
K2A_TOL = 1e-6
K2B_TOL = 0.02
K2C_TOL = 1e-10
K4_TOL = 0.10

W0_SET = [2, 4, 6, 8, 12]
MAIN = [("W6_d256_base", 6), ("W8_d256_base", 8), ("W12_d256_base", 12)]
REF256 = [("w2_d256_base", 2), ("w4_d256_base", 4)]        # D3_out, misma malla/dz/absorbente/ventana
REPRO = "K0a_repro_w6_d128_base"                           # D5_out, reproduccion de V1
REPRO_REF = "V1_w6_d128_base"                               # D3_out, referencia
DIAG_A = "G12a_w12_d256_dx025"
DIAG_B = "G12b_w12_d256_dz125"
DESC128 = "V1_w6_d128_base"
ALL_NEW = [t for t, _ in MAIN] + [REPRO, DIAG_A, DIAG_B]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def to_py(v):
    if isinstance(v, dict):
        return {k: to_py(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [to_py(x) for x in v]
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        return float(v)
    return v


def load(folder, tag):
    path = os.path.join(folder, tag + ".json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    rows = d["rows"]
    arr = {k: np.array([r[k] for r in rows], dtype=float)
           for k in ["z_m", "Pu_num", "Pu_an", "P_total_num", "P_band_an", "P_band_num", "E"]}
    return {"meta": d, "arr": arr, "P0": float(d["P0"]), "path": path, "tag": tag}


def mwin(arr, p0, z0_mm=W0_MM, z1_mm=Z1_MM):
    """M = max_W |dP_u|/P0 en la ventana [z0, z1] (mm). Retorno y perdida por separado."""
    z = arr["z_m"]
    m = (z >= z0_mm * 1e-3 - 1e-12) & (z <= z1_mm * 1e-3 + 1e-12)
    dp = (arr["Pu_num"] - arr["Pu_an"])[m] / p0
    zz = z[m] * 1e3
    i = int(np.argmax(np.abs(dp)))
    return {"M": float(abs(dp[i])), "z_M_mm": float(zz[i]), "nW": int(m.sum()),
            "rho_max": float(max(0.0, dp.max())), "lam_max": float(max(0.0, -dp.min()))}


def band(q):
    """Bandas heredadas de 009c (K4 de D4)."""
    if 2.5 <= q <= 6.0:
        return "discretizacion (orden ~2)"
    if 0.67 <= q <= 1.5:
        return "independiente de la malla"
    return "indeterminado"


def main():
    missing = []

    def need(folder, tag):
        r = load(folder, tag)
        if r is None:
            missing.append(tag)
        return r

    new = {t: need(D5DIR, t) for t in ALL_NEW}
    refs = {t: need(D3DIR, t) for t, _ in REF256}
    desc128 = need(D3DIR, DESC128)
    ok_all = all(v is not None for v in new.values())

    # ---- celdas principales y referencias (ventana comun) ----
    def cell(run, tag, w0_um, absorbente="base"):
        m = mwin(run["arr"], run["P0"])
        last = -1
        return {
            "tag": tag, "w0_um": float(w0_um), "dominio_um": float(run["meta"]["domain_um"]),
            "dx_um": float(run["meta"]["dx_um"]), "dz_um": float(run["meta"]["dz_um"]),
            "absorbente": absorbente, "M": m["M"], "z_M_mm": m["z_M_mm"], "nW": m["nW"],
            "rho_max": m["rho_max"], "lam_max": m["lam_max"],
            "pass_K1_cell": bool(m["M"] < K1_THR),
            "descriptivo_P_total_fin": float(run["arr"]["P_total_num"][last] / run["P0"]),
            "descriptivo_P_band_an_fin": float(run["arr"]["P_band_an"][last] / run["P0"]),
        }

    cells = []
    for tag, w0 in MAIN:
        if new[tag] is not None:
            cells.append(cell(new[tag], tag, w0))
    cells_ref = []
    for tag, w0 in REF256:
        if refs[tag] is not None:
            cells_ref.append(cell(refs[tag], tag, w0))
    cell_desc128 = cell(desc128, DESC128, 6.0) if desc128 is not None else None
    m_repro = None
    if new[REPRO] is not None:
        m_repro = cell(new[REPRO], REPRO, 6.0)

    # ---- K0 (herramienta) ----
    k0 = {}
    # K0a: reproduccion de V1 (w0=6, 128 um, base)
    if new[REPRO] is not None and desc128 is not None:
        a, b = new[REPRO]["arr"], desc128["arr"]
        same_len = len(a["z_m"]) == len(b["z_m"]) and np.allclose(a["z_m"], b["z_m"], rtol=0, atol=1e-15)
        if same_len:
            d_dp = float(np.max(np.abs((a["Pu_num"] - a["Pu_an"]) - (b["Pu_num"] - b["Pu_an"]))) / new[REPRO]["P0"])
            d_E = float(np.max(np.abs(a["E"] - b["E"])))
            k0["K0a_val"] = {"max_dDP_rel": d_dp, "max_dE": d_E}
            k0["K0a_pass"] = bool(d_dp <= K0A_TOL and d_E <= K0A_TOL)
        else:
            k0["K0a_val"] = {"max_dDP_rel": None, "max_dE": None, "nota": "longitud de filas distinta"}
            k0["K0a_pass"] = False
    else:
        k0["K0a_val"] = None
        k0["K0a_pass"] = False

    # K0b: sigma del runner == adi2d.sigma_map
    sig_diffs = [new[t]["meta"]["K0b_sigma_maxdiff_rel"] for t in ALL_NEW if new[t] is not None]
    k0["K0b_max"] = float(max(sig_diffs)) if sig_diffs else None
    k0["K0b_pass"] = bool(k0["K0b_max"] is not None and k0["K0b_max"] <= K0B_TOL)
    # K0c: analitico en z=0 == A(0)
    c0 = [new[t]["meta"]["K0c_analytic0_rel"] for t in ALL_NEW if new[t] is not None]
    k0["K0c_max"] = float(max(c0)) if c0 else None
    k0["K0c_pass"] = bool(k0["K0c_max"] is not None and k0["K0c_max"] <= K0C_TOL)
    # K0d: P_total no crece entre muestras
    inc = []
    for t in ALL_NEW:
        if new[t] is not None:
            inc.append(float(np.max(np.diff(new[t]["arr"]["P_total_num"])) / new[t]["P0"]))
    k0["K0d_max_increase"] = float(max(inc)) if inc else None
    k0["K0d_pass"] = bool(k0["K0d_max_increase"] is not None and k0["K0d_max_increase"] <= K0D_TOL)
    # K0e: P0 = 1
    p0dev = [abs(new[t]["P0"] - 1.0) for t in ALL_NEW if new[t] is not None]
    k0["K0e_max_P0dev"] = float(max(p0dev)) if p0dev else None
    k0["K0e_pass"] = bool(k0["K0e_max_P0dev"] is not None and k0["K0e_max_P0dev"] <= K0E_TOL)
    # K0f: 19 muestras en la ventana de las principales
    k0["K0f_pass"] = bool(len(cells) == len(MAIN) and all(c["nW"] == 19 for c in cells))
    k0_pass = bool(k0["K0a_pass"] and k0["K0b_pass"] and k0["K0c_pass"] and k0["K0d_pass"]
                   and k0["K0e_pass"] and k0["K0f_pass"] and ok_all)

    # ---- K1 (retorno, principal) ----
    k1_cells = [c["tag"] for c in cells if c["pass_K1_cell"]]
    k1_pass = bool(len(k1_cells) >= 1 and len(cells) == len(MAIN))
    passing_w0 = [c["w0_um"] for c in cells if c["pass_K1_cell"]]

    # ---- K2 (cola espectral: verificacion de la formula y del calculo discreto) ----
    b0 = S.b0
    kc = b0 * (1 - FRAC) * (L / 2) / ZMAX
    N = int(round(L / DX))
    kf = 2 * np.pi * np.fft.fftfreq(N, d=DX)
    KX, KY = np.meshgrid(kf, kf, indexing="xy")
    Kmax = np.maximum(np.abs(KX), np.abs(KY))
    Krad = np.hypot(KX, KY)
    spec = []
    k2a_err = []
    k2b_err = []
    k2c_err = []
    kk = np.linspace(-kc, kc, 400001)
    h = kk[1] - kk[0]
    for w0 in W0_SET:
        w0m = w0 * 1e-6
        A0 = S.gaussian(N, DX, w0m)
        Fk = np.fft.fft2(A0)
        En = np.abs(Fk) ** 2
        tot = float(En.sum())
        p_in = float(np.sum(np.abs(A0) ** 2))
        parseval = float(abs(p_in - tot / (N * N)) / p_in)
        f_sq_fft_out = float(En[Kmax > kc].sum() / tot)
        f_rad_fft_out = float(En[Krad > kc].sum() / tot)
        # forma analitica 1D: fraccion de energia en |k|<=kc = erf(kc*w0/sqrt2)
        a = kc * w0m / np.sqrt(2.0)
        erf_closed = float(special.erf(a))
        p1 = (w0m / np.sqrt(2 * np.pi)) * np.exp(-kk ** 2 * w0m ** 2 / 2)
        erf_num = float(h * (p1.sum() - 0.5 * (p1[0] + p1[-1])))
        k2a_err.append(abs(erf_num - erf_closed) / erf_closed)
        f_sq_an = float(1 - erf_closed ** 2)                    # cuadrado = producto de dos ejes
        f_rad_an = float(np.exp(-(kc * w0m) ** 2 / 2))          # disco 2D
        k2b_err.append(abs(f_sq_fft_out - f_sq_an))
        k2c_err.append(parseval)
        spec.append({
            "w0_um": float(w0), "kc_1_por_m": float(kc),
            "F_fuera_cuadrado_analitico": f_sq_an, "F_fuera_cuadrado_FFT": f_sq_fft_out,
            "F_fuera_radial_analitico": f_rad_an, "F_fuera_radial_FFT": f_rad_fft_out,
            "erf_1D_num_err_rel": float(abs(erf_num - erf_closed) / erf_closed),
            "parseval_err_rel": parseval,
        })
    k2a_pass = bool(max(k2a_err) <= K2A_TOL)
    k2b_pass = bool(max(k2b_err) <= K2B_TOL)
    k2c_pass = bool(max(k2c_err) <= K2C_TOL)
    k2_pass = bool(k2a_pass and k2b_pass and k2c_pass)
    spec_by_w0 = {s["w0_um"]: s for s in spec}

    # ---- K3 (malla, w0 = 12) y K4 (paso temporal, w0 = 12) ----
    m12 = [c for c in cells if c["w0_um"] == 12.0]
    dA = new[DIAG_A]
    dB = new[DIAG_B]
    k3 = {"evaluable": False}
    k4 = {"evaluable": False}
    if m12 and dA is not None:
        M_main12 = m12[0]["M"]
        M_A = mwin(dA["arr"], dA["P0"])["M"]
        q = M_main12 / M_A
        k3 = {"evaluable": True, "M_dx05": M_main12, "M_dx025": M_A, "q": float(q), "clase": band(q)}
        k3["pass"] = bool(band(q) != "indeterminado")
    if m12 and dB is not None:
        M_main12 = m12[0]["M"]
        M_B = mwin(dB["arr"], dB["P0"])["M"]
        rel = abs(M_main12 - M_B) / M_B
        k4 = {"evaluable": True, "M_dz25": M_main12, "M_dz125": M_B, "rel": float(rel)}
        k4["pass"] = bool(rel < K4_TOL)
    k3_pass = bool(k3.get("pass", False))
    k4_pass = bool(k4.get("pass", False))

    # ---- criterios ----
    crit_K0 = {
        "id": "K0",
        "description": ("herramienta: K0a reproduccion de V1 (1e-9); K0b sigma (1e-12); K0c analitico en z=0 (1e-9); "
                        "K0d P_total no crece (1e-9); K0e P0=1 (1e-12); K0f 19 muestras en W"),
        "value": (f"K0a={k0['K0a_val']}; K0b max={k0['K0b_max']}; K0c max={k0['K0c_max']}; "
                  f"K0d max_inc={k0['K0d_max_increase']}; K0e max|P0-1|={k0['K0e_max_P0dev']}; K0f={k0['K0f_pass']}"),
        "pass_": k0_pass,
    }
    if cells:
        m_str = "; ".join(f"w0={c['w0_um']:g} um: M={c['M']:.4e} (z={c['z_M_mm']:.1f} mm)" for c in cells)
    else:
        m_str = "sin celdas"
    crit_K1 = {
        "id": "K1",
        "description": "retorno: alguna corrida principal (w0 in {6,8,12} um, 256 um, base, ventana z>=0,2 mm) con M < 1e-4",
        "value": f"{m_str}; celdas que cumplen: {k1_cells if k1_cells else 'ninguna'}",
        "pass_": k1_pass,
    }
    crit_K2 = {
        "id": "K2",
        "description": ("cola espectral (verificacion): K2a erf 1D frente a integral numerica (1e-6); "
                        "K2b |F_fuera FFT - analitico| <= 0,02 (cuadrado) para w0 in {2,4,6,8,12}; "
                        "K2c Parseval (1e-10)"),
        "value": (f"K2a max_err_rel={max(k2a_err):.2e}; K2b max_abs={max(k2b_err):.3e}; "
                  f"K2c max_parseval={max(k2c_err):.2e}; k_c={kc:.4e} 1/m"),
        "pass_": k2_pass,
    }
    if k3.get("evaluable"):
        k3_val = (f"w0=12: M(dx0,5)={k3['M_dx05']:.4e}, M(dx0,25)={k3['M_dx025']:.4e}, q={k3['q']:.3f} ({k3['clase']})")
    else:
        k3_val = "no evaluable (falta G12a o la principal de w0=12)"
    crit_K3 = {
        "id": "K3",
        "description": "malla (w0=12): q = M(dx0,5)/M(dx0,25) no indeterminado (bandas de 009c)",
        "value": k3_val,
        "pass_": k3_pass,
    }
    if k4.get("evaluable"):
        k4_val = (f"w0=12: M(dz2,5)={k4['M_dz25']:.4e}, M(dz1,25)={k4['M_dz125']:.4e}, rel={k4['rel']:.4f}")
    else:
        k4_val = "no evaluable (falta G12b o la principal de w0=12)"
    crit_K4 = {
        "id": "K4",
        "description": "paso temporal (w0=12): |M(dz2,5)-M(dz1,25)|/M(dz1,25) < 0,10",
        "value": k4_val,
        "pass_": k4_pass,
    }
    criteria = [crit_K0, crit_K1, crit_K2, crit_K3, crit_K4]
    n_pass = sum(1 for c in criteria if c["pass_"])

    # ---- veredicto (reglas del contrato, pasos 3 y 4) ----
    if k1_pass:
        veredicto = ("CAMBIO DE PROTOCOLO DE HAZ: w0 = " + ", ".join(f"{w:g} um" for w in passing_w0)
                     + " cumple K1 con absorbente base y dominio 256 um. No valida el absorbente con el criterio original.")
    else:
        veredicto = ("NINGUN HAZ PROBADO CUMPLE K1 = 1e-4: ni w0 = 2, 4 (D3/D4), ni w0 = 6, 8, 12 um (D5), "
                     "con absorbente base y dominio 256 um. La validacion de vacio con K1 no se cumple con ningun haz probado.")
    if k1_pass and not (k3.get("evaluable") and k4.get("evaluable")):
        veredicto += " Diagnosticos de malla o paso no evaluables: el veredicto no tiene control de malla."
    if k1_pass and k3.get("evaluable") and not k3_pass:
        veredicto += " K3 no supera la malla para w0 = 12: el veredicto depende de la malla."

    # ---- descriptivos (sin pass) ----
    ms = {}
    for c in cells_ref:
        ms[c["w0_um"]] = c["M"]
    for c in cells:
        ms[c["w0_um"]] = c["M"]
    slope = None
    if len(ms) >= 3:
        xs = np.log(np.array(sorted(ms.keys())))
        ys = np.log(np.array([ms[k] for k in sorted(ms.keys())]))
        slope = float(np.polyfit(xs, ys, 1)[0])
    desc = {
        "nota": "NO pre-declarado como criterio; solo lectura, sin pass.",
        "M_256_base_por_w0": {str(k): float(ms[k]) for k in sorted(ms.keys())},
        "pendiente_log_M_vs_log_w0_256_base": slope,
        "F_fuera_por_w0": spec,
        "efecto_dominio_w0_6": (
            {"M_128um": cell_desc128["M"], "M_256um": next((c["M"] for c in cells if c["w0_um"] == 6.0), None)}
            if cell_desc128 is not None else None),
        "K0a_repro": m_repro,
        "celdas_referencia_256_base": cells_ref,
        "diagnosticos_w12": {
            "G12a_dx025": (mwin(dA["arr"], dA["P0"]) if dA is not None else None),
            "G12b_dz125": (mwin(dB["arr"], dB["P0"]) if dB is not None else None),
        },
    }

    # ---- hashes ----
    hashes = {"script": sha256_file(os.path.abspath(__file__)),
              "runner": sha256_file(os.path.join(HERE, "validacion_vacio_D5_run.py")),
              "adi2d.py": sha256_file(os.path.join(HERE, "..", "glass009_claude", "adi2d.py"))}
    for t in ALL_NEW:
        if new[t] is not None:
            hashes[t + ".json"] = sha256_file(new[t]["path"])
    for t, _ in REF256:
        if refs[t] is not None:
            hashes[t + ".json"] = sha256_file(refs[t]["path"])
    if desc128 is not None:
        hashes[DESC128 + ".json"] = sha256_file(desc128["path"])

    status = "done" if (not missing) else "partial"
    result = {
        "task": "GLASS-009c D5: validacion de vacio con haces de cola espectral controlada (cambio de protocolo de haz)",
        "contrato": "CONTRATO-HAZ-COLA-D5-r5.md",
        "status": status,
        "faltan": {"criterios": [],
                   "celdas": missing},
        "protocolo": {
            "ventana_comun_mm": [W0_MM, Z1_MM], "muestras": "cada 0,1 mm (19)",
            "dominio_um": 256, "dx_um": 0.5, "dz_um": 2.5, "pasos": 800, "absorbente": {"f": FRAC, "p": 4},
            "w0_um_nuevos": [6, 8, 12], "K1_umbral": K1_THR,
            "cambio_de_protocolo_haz": bool(k1_pass),
            "cambio_declarado": "w0 en {6,8,12} um en lugar de {2,4} um; ventana D4; K1 sin cambio",
            "banda_fourier_primaria": "cuadrado max(|kx|,|ky|) <= k_c, k_c = b0(1-f)(L/2)/z_max",
            "banda_fourier_sensibilidad": "disco |k| <= k_c (descriptivo)",
            "k_c_1_por_m": float(kc), "b0_1_por_m": float(b0),
        },
        "veredicto": veredicto,
        "haces_que_cumplen_K1": passing_w0,
        "cells": cells,
        "K0": k0,
        "K2_cola_espectral": spec,
        "K3_malla": k3,
        "K4_paso": k4,
        "descriptivo": desc,
        "criteria": criteria,
        "n_pass": int(n_pass),
        "n_criteria": int(len(criteria)),
        "hashes_sha256": hashes,
        "limites": [
            "Solo theta=0, paraxial, delta n=0. Modelo numerico, sin medida ni dispositivo.",
            "Muestreo cada 0,1 mm: el maximo entre muestras no se ve.",
            "K1 vale para el absorbente base (f=0,2, p=4) y dominio 256 um. No se probo f=0,3 ni p distinto de 4 a 256 um en D5.",
            "La banda de Fourier es una definicion cinematica fijada en el contrato, no una medida del absorbente.",
            "La referencia analitica no incluye absorcion: para w0 = 6 y 8 um el haz libre alcanza el borde absorbente en la ventana.",
            "K2b usa tolerancia absoluta 0,02. Para F_fuera pequeno (w0 >= 8 um) es poco exigente.",
            "Diagnosticos de malla y paso solo para w0 = 12 um.",
            "Router JEV: router.py plan (deterministic_tool, effort high) y router.py jev con provenance=jev (band: disco, confianza 0,14; no_extend: 0,77). La banda primaria se mantiene por contrato fijado antes de la consulta.",
        ],
        "scipy_disponible": True,
    }
    # limpieza del campo faltan (sin claves temporales)
    result["faltan"] = {"criterios": [c["id"] for c in criteria if not c["pass_"] and "no evaluable" in c["value"]],
                        "celdas": missing}

    with open(OUTJSON, "w", encoding="utf-8") as f:
        json.dump(to_py(result), f, indent=1, ensure_ascii=False)

    # resumen a consola
    print("kc=%.6e 1/m  b0=%.6e" % (kc, b0))
    for c in cells:
        print("%-16s w0=%4.1f M=%.6e z=%.2f nW=%d K1=%s Pfin=%.4f Pband_an_fin=%.4e" % (
            c["tag"], c["w0_um"], c["M"], c["z_M_mm"], c["nW"], c["pass_K1_cell"],
            c["descriptivo_P_total_fin"], c["descriptivo_P_band_an_fin"]))
    for c in cells_ref:
        print("ref %-14s M=%.6e z=%.2f" % (c["tag"], c["M"], c["z_M_mm"]))
    if cell_desc128 is not None:
        print("ref V1_w6_d128_base M=%.6e" % cell_desc128["M"])
    print("K0", {k: v for k, v in k0.items()})
    for s in spec:
        print("spec w0=%4.1f Fsq_an=%.6e Fsq_fft=%.6e Frad_an=%.6e Frad_fft=%.6e" % (
            s["w0_um"], s["F_fuera_cuadrado_analitico"], s["F_fuera_cuadrado_FFT"],
            s["F_fuera_radial_analitico"], s["F_fuera_radial_FFT"]))
    print("K3", k3)
    print("K4", k4)
    print("pendiente log-log M vs w0:", slope)
    print("veredicto:", veredicto)
    print("status:", status, "faltan:", missing)
    print("n_pass %d / %d" % (n_pass, len(criteria)))
    for c in criteria:
        print(c["id"], c["pass_"], "|", c["value"])


if __name__ == "__main__":
    main()
