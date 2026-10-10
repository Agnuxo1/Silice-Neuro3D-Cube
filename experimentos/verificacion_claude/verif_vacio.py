"""VERIFICACION V3, parte D (frontera 009c en vacio). Solvers INDEPENDIENTES del ADI de 009c.

Modos:
  dst  : Laplaciano FD de 2.o orden con pared de Dirichlet (la misma discretizacion espacial que adi2d), pero
         integrado EXACTO en z por diagonalizacion con DST-I (Strang con el absorbente). Aisla el error del ADI en z.
  fft  : espectral periodico (precision espectral en el espacio). Es la solucion 'casi continua'. Solo valida si el haz
         no vuelve por el borde periodico (theta <= 0,02 en 2 mm).
  adi  : adi2d.py de 009c (importado, solo lectura) con otra malla.
Uso: python -B verif_vacio.py MODO THETA DOM_um DX_um [DZ_um=2.5] [FRAC=0.2] [P=4] [SMAX=4e4]
Salida: tabla por z y JSON en verif_vacio_out/.
"""
import os, sys, json, math, time
os.environ["OMP_NUM_THREADS"] = "1"; os.environ["OPENBLAS_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
import numpy as np
from scipy.fft import dstn, idstn, fft2, ifft2, fftfreq

HERE = os.path.dirname(os.path.abspath(__file__))
lam = 1550e-9; n0 = 1.444; k0 = 2 * math.pi / lam; b0 = k0 * n0     # constantes fisicas (enunciado)

def run(mode, theta, dom, dx, dz=2.5e-6, frac=0.2, p=4.0, smax=4e4, total_z=2.0e-3, every=40, w0=6e-6, RU=40e-6):
    N = int(round(dom / dx)); d2 = dx * dx
    ax = (np.arange(N) - N // 2) * dx
    x, y = np.meshgrid(ax, ax, indexing="xy")
    kt = b0 * theta; zR = b0 * w0 ** 2 / 2
    f = np.exp(-(x * x + y * y) / w0 ** 2) * np.exp(1j * kt * x)
    A0 = f / math.sqrt((np.abs(f) ** 2).sum() * d2)
    N0 = A0[N // 2, N // 2].real
    P0 = float((np.abs(A0) ** 2).sum() * d2)
    e = np.maximum(np.abs(x), np.abs(y)) / (N * dx / 2)
    band = e > (1 - frac)
    sig = smax * np.maximum((e - (1 - frac)) / frac, 0) ** p
    useful = np.hypot(x, y) < RU

    def analytic(z):
        zeta = z / zR; xs = kt * z / b0
        return N0 / (1 + 1j * zeta) * np.exp(-(((x - xs) ** 2 + y * y) / (w0 ** 2 * (1 + 1j * zeta)))) \
            * np.exp(1j * kt * x) * np.exp(-1j * kt ** 2 * z / (2 * b0))

    steps = int(round(total_z / dz))
    if mode == "dst":
        m = np.arange(1, N + 1)
        lm = -(4 / dx ** 2) * np.sin(np.pi * m / (2 * (N + 1))) ** 2
        Lk = lm[:, None] + lm[None, :]
        prop = np.exp(1j * Lk * dz / (2 * b0))
        ah = np.exp(-sig * dz / 2)
        def step(A):
            A = A * ah
            A = idstn(prop * dstn(A, type=1, norm="ortho"), type=1, norm="ortho")
            return A * ah
    elif mode == "fft":
        kx = 2 * np.pi * fftfreq(N, dx)
        K2 = kx[:, None] ** 2 + kx[None, :] ** 2
        prop = np.exp(-1j * K2 * dz / (2 * b0))
        ah = np.exp(-sig * dz / 2)
        def step(A):
            A = A * ah
            A = ifft2(prop * fft2(A))
            return A * ah
    elif mode == "adi":
        sys.path.insert(0, os.path.join(HERE, "..", "glass009_claude"))
        import adi2d as S
        st = S.Stepper(np.zeros((N, N)), sig, dx, dz)
        step = st.step
    else:
        raise SystemExit("modo")

    rows = []
    def rec(s, A):
        z = s * dz; Aa = analytic(z)
        rows.append(dict(z=z, Pu_num=float((np.abs(A[useful]) ** 2).sum() * d2), Pu_an=float((np.abs(Aa[useful]) ** 2).sum() * d2),
                         Pt=float((np.abs(A) ** 2).sum() * d2), Pband_an=float((np.abs(Aa[band]) ** 2).sum() * d2),
                         E=float(np.linalg.norm((A - Aa)[useful]) / np.linalg.norm(Aa[useful]))))
    A = A0.astype(complex); rec(0, A)
    for s in range(1, steps + 1):
        A = step(A)
        if s % every == 0:
            rec(s, A)
    zarr = min([r["z"] for r in rows if r["Pband_an"] > 1e-4 * P0] or [float("nan")])
    for r in rows:
        r["dP"] = (r["Pu_num"] - r["Pu_an"]) / P0
    W = [r for r in rows if r["z"] >= zarr - 1e-12]
    mx = max(W, key=lambda r: abs(r["dP"]))
    return dict(mode=mode, theta=theta, dom_um=dom * 1e6, dx_um=dx * 1e6, dz_um=dz * 1e6, N=N, frac=frac, p=p, smax=smax,
                P0=P0, z_arr_mm=zarr * 1e3, max_dP_over_P0=abs(mx["dP"]), z_max_mm=mx["z"] * 1e3, rows=rows)

if __name__ == "__main__":
    mode = sys.argv[1]; theta = float(sys.argv[2]); dom = float(sys.argv[3]) * 1e-6; dx = float(sys.argv[4]) * 1e-6
    dz = float(sys.argv[5]) * 1e-6 if len(sys.argv) > 5 else 2.5e-6
    frac = float(sys.argv[6]) if len(sys.argv) > 6 else 0.2
    pp = float(sys.argv[7]) if len(sys.argv) > 7 else 4.0
    smax = float(sys.argv[8]) if len(sys.argv) > 8 else 4e4
    t0 = time.time()
    r = run(mode, theta, dom, dx, dz, frac, pp, smax)
    od = os.path.join(HERE, "verif_vacio_out"); os.makedirs(od, exist_ok=True)
    tag = f"{mode}_th{theta}_dom{dom*1e6:.0f}_dx{dx*1e6:.3f}_dz{dz*1e6:.2f}_f{frac}_p{pp:g}_s{smax:g}"
    json.dump(r, open(os.path.join(od, tag + ".json"), "w"), indent=1)
    print(tag, "z_arr=%.2f mm" % r["z_arr_mm"], "max|dP|/P0=%.4e @ z=%.2f mm" % (r["max_dP_over_P0"], r["z_max_mm"]),
          "Ptot(end)=%.6f" % r["rows"][-1]["Pt"], "t=%.1fs" % (time.time() - t0), flush=True)
