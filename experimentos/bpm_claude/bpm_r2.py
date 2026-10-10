"""BPM escalar paraxial parametrico (ronda 2, CONTRATO-bpm-r2.md). Modelo numerico. Solo CPU.

Ecuacion: 2 i k0 n_ref dA/dz = lap A + k0^2 (n^2 - n_ref^2) A - i Gamma A.
Split-step de Strang: A <- P ifft[D fft(P A)], P = exp(-i dz V/(4 k0 n_ref)),
D = exp(+i dz K^2/(2 k0 n_ref)), V = k0^2 (n^2 - n_ref^2) - i Gamma.
Gamma = 2 k0 n_ref R0 t^2, t = clip((s - s0)/w, 0, 1), s = max(|x|, |y|).
R0 (um^-1) es la tasa de atenuacion de amplitud en el borde de la ventana.
Malla: x_i = (i - M) h, N = 2M + 1, indices [ix, iy] (meshgrid 'ij').
Implementacion propia; no importa src/silice/.
"""
import numpy as np
import scipy.fft as sfft
from scipy.sparse.linalg import LinearOperator, eigsh

LAM = 1.55
A_CORE = 6.0
N1 = 1.444
N2 = 1.439
NREF = N1
K0 = 2.0 * np.pi / LAM
SUB = 16


def axis(W, h):
    M = int(round(W / h))
    N = 2 * M + 1
    return (np.arange(N) - M) * h


def cell_n2(x, h, centers, sub=SUB, nbg=N2):
    """<n^2> promediado por celda (sub x sub subceldas). Nucleos disco de radio A_CORE en centers."""
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
            acc += np.where(inside, N1 ** 2, nbg ** 2)
    return acc / (sub * sub)


def gamma_cap(x, s0, w, R0):
    X, Y = np.meshgrid(x, x, indexing="ij")
    s = np.maximum(np.abs(X), np.abs(Y))
    t = np.clip((s - s0) / w, 0.0, 1.0)
    return 2.0 * K0 * NREF * R0 * t * t


def lp01_analytic(x, xc, u, w):
    """LP01 analitico muestreado (E(0)=1), centrado en (xc, 0)."""
    from scipy import special as sp
    X, Y = np.meshgrid(x, x, indexing="ij")
    r = np.hypot(X - xc, Y)
    rin = np.minimum(r, A_CORE)
    rout = np.maximum(r, A_CORE)
    with np.errstate(all="ignore"):
        inside = sp.j0(u * rin / A_CORE) / sp.j0(u)
        outside = sp.k0(w * rout / A_CORE) / sp.k0(w)
    return np.where(r <= A_CORE, inside, outside).astype(complex)


class Rec:
    """Registra P(z) y los solapes <f|A(z)> h^2 con los campos de 'projs'."""

    def __init__(self, h, projs):
        self.h2 = h * h
        self.z = []
        self.P = []
        self.projs = projs
        self.norms = {k: float(np.sum(np.abs(v) ** 2) * self.h2) for k, v in projs.items()}
        self.ip = {k: [] for k in projs}

    def __call__(self, z, A):
        self.z.append(float(z))
        self.P.append(float(np.sum(np.abs(A) ** 2) * self.h2))
        for k, v in self.projs.items():
            self.ip[k].append(complex(np.sum(np.conj(v) * A) * self.h2))

    def idx(self, z):
        return int(np.argmin(np.abs(np.array(self.z) - z)))

    def loss_at(self, z):
        k = self.idx(z)
        return 1.0 - self.P[k] / self.P[0]

    def ov2_at(self, key, z):
        k = self.idx(z)
        return abs(self.ip[key][k]) ** 2 / (self.norms[key] * self.P[k])

    def neff_impl_at(self, key, z):
        k = self.idx(z)
        ph = np.unwrap(np.angle(np.array(self.ip[key])))
        zk = self.z[k]
        if zk == 0.0:
            return float("nan")
        return float(NREF - ph[k] / (K0 * zk))


def propagate(n2, E0, h, dz, z_end, W_unused, s0, w, R0, projs, cap=True, cb=None):
    """Propaga E0 hasta z_end (um). projs: dict nombre -> campo de proyeccion. cb(z, A) opcional."""
    N = E0.shape[0]
    x = (np.arange(N) - (N - 1) // 2) * h
    V = K0 * K0 * (n2 - NREF * NREF).astype(complex)
    if cap and R0 > 0.0:
        V = V - 1j * gamma_cap(x, s0, w, R0)
    kx = 2.0 * np.pi * np.fft.fftfreq(N, d=h)
    K2 = kx[:, None] ** 2 + kx[None, :] ** 2
    D = np.exp(1j * dz * K2 / (2.0 * K0 * NREF))
    P = np.exp(-1j * dz * V / (4.0 * K0 * NREF))
    nsteps = int(round(z_end / dz))
    A = E0.astype(complex).copy()
    rec = Rec(h, projs)
    rec(0.0, A)
    if cb is not None:
        cb(0.0, A)
    for k in range(1, nsteps + 1):
        A = P * A
        A = sfft.ifft2(D * sfft.fft2(A, workers=1), workers=1)
        A = P * A
        rec(k * dz, A)
        if cb is not None:
            cb(k * dz, A)
    return rec, A


def discrete_ground_state(n2, h, v0):
    """Autoestado guiado del operador -(lap + V_real) (periodico, espectral) en la malla de n2.

    Devuelve (psi real normalizada con sum psi^2 h^2 = 1, n_eff discreto).
    """
    N = n2.shape[0]
    kx = 2.0 * np.pi * np.fft.fftfreq(N, d=h)
    K2 = kx[:, None] ** 2 + kx[None, :] ** 2
    Vr = K0 * K0 * (n2 - NREF * NREF)

    def mv(v):
        u = np.asarray(v).reshape(N, N)
        out = np.real(sfft.ifft2(K2 * sfft.fft2(u, workers=1), workers=1)) - Vr * u
        return out.ravel()

    Hop = LinearOperator((N * N, N * N), matvec=mv, dtype=float)
    vals, vecs = eigsh(Hop, k=1, which="SA", v0=v0.ravel().real, tol=1e-10, maxiter=20000)
    E = float(vals[0])
    psi = vecs[:, 0].reshape(N, N)
    psi = psi / np.sqrt(np.sum(psi * psi) * h * h)
    imax = np.unravel_index(int(np.argmax(np.abs(psi))), psi.shape)
    if psi[imax] < 0:
        psi = -psi
    neff = NREF - E / (2.0 * K0 * K0 * NREF)
    return psi, float(neff)
