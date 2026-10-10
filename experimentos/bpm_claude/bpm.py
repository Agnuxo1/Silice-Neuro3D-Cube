"""BPM escalar paraxial 2D independiente (split-step de Fourier de Strang).

Ecuacion (convencion del enunciado):
    2 i k0 n_ref dA/dz = lap_perp A + k0^2 (n^2 - n_ref^2) A
Se integra como
    dA/dz = -i/(2 k0 n_ref) [lap_perp A + V A],   V = k0^2 (n^2 - n_ref^2) - i Gamma(x, y)
donde Gamma >= 0 es un potencial absorbente complejo (CAP) en el contorno de la ventana.

Convencion de fase: E = A exp(-i k0 n_ref z). Un modo guiado queda
A(z) ~ psi0 exp(-i k0 (n_eff - n_ref) z), por lo que n_eff,impl = n_ref - phi(z)/(k0 z).

Malla: N x N nodos, indice [i, j] <-> (x_i, y_j), x_i = (i - M) h, N = 2M + 1 (centrada en 0).
Paso (Strang, orden 2 en dz):
    A <- P . IFFT[ D . FFT(P . A) ],   P = exp(-i dz V/(4 k0 n_ref)),   D = exp(+i dz K^2/(2 k0 n_ref))
Sin CAP el paso es unitario (solo fases). La ventana es periodica; el CAP atenua el campo antes del borde.

Interfaz:
    run(n_xy, E0, lam_um, h_um, dz_um, z_save_um, n_ref) -> {z_um: campo 2D complejo}
"""
import numpy as np
import scipy.fft as sfft

CAP_START_UM = 28.0   # s = max(|x|,|y|) donde empieza el CAP
CAP_WIDTH_UM = 12.0   # ancho del CAP (borde de la ventana en s = 40 um)
CAP_RATE_EDGE = 0.5   # um^-1: atenuacion de amplitud por unidad de z en el borde, Gamma/(2 k0 n_ref)


def axis_coords(N, h_um):
    """Coordenadas centradas de los nodos (N impar)."""
    if N % 2 == 0:
        raise ValueError("N debe ser impar para que haya un nodo en el centro")
    M = (N - 1) // 2
    return (np.arange(N) - M) * h_um


def cap_profile(x, k0, n_ref):
    """Gamma(x, y) real y no negativa; se usa como -i Gamma en V."""
    X, Y = np.meshgrid(x, x, indexing="ij")
    s = np.maximum(np.abs(X), np.abs(Y))
    t = np.clip((s - CAP_START_UM) / CAP_WIDTH_UM, 0.0, 1.0)
    G0 = 2.0 * k0 * n_ref * CAP_RATE_EDGE
    return G0 * t * t


def propagate(n_xy, E0, lam_um, h_um, dz_um, z_save_um, n_ref, cap=True, observe=None):
    """Propaga E0 y devuelve {z: campo} para los z de z_save_um.

    observe(z, A): callback opcional llamado en z = 0 y tras cada paso.
    """
    n_xy = np.asarray(n_xy, dtype=float)
    E0 = np.asarray(E0, dtype=complex)
    N = n_xy.shape[0]
    if n_xy.shape != (N, N) or E0.shape != (N, N):
        raise ValueError("n_xy y E0 deben ser matrices cuadradas de la misma forma")
    k0 = 2.0 * np.pi / lam_um
    x = axis_coords(N, h_um)

    V = k0 * k0 * (n_xy * n_xy - n_ref * n_ref).astype(complex)
    if cap:
        V = V - 1j * cap_profile(x, k0, n_ref)

    kx = 2.0 * np.pi * np.fft.fftfreq(N, d=h_um)
    K2 = kx[:, None] ** 2 + kx[None, :] ** 2
    D = np.exp(1j * dz_um * K2 / (2.0 * k0 * n_ref))
    P = np.exp(-1j * dz_um * V / (4.0 * k0 * n_ref))

    zs = sorted(float(z) for z in z_save_um)
    steps_to_save = {}
    for z in zs:
        k = int(round(z / dz_um))
        if abs(k * dz_um - z) > 1e-9 * max(1.0, abs(z)):
            raise ValueError("z_save_um debe ser multiplo de dz_um")
        steps_to_save.setdefault(k, []).append(z)
    nsteps = max(steps_to_save) if steps_to_save else 0

    A = E0.copy()
    saved = {}
    if observe is not None:
        observe(0.0, A)
    for z in steps_to_save.get(0, []):
        saved[z] = A.copy()
    for k in range(1, nsteps + 1):
        A = P * A
        A = sfft.ifft2(D * sfft.fft2(A, workers=1), workers=1)
        A = P * A
        if observe is not None:
            observe(k * dz_um, A)
        for z in steps_to_save.get(k, []):
            saved[z] = A.copy()
    return saved


def run(n_xy, E0, lam_um, h_um, dz_um, z_save_um, n_ref):
    """Interfaz pedida: devuelve {z_um: campo 2D complejo}."""
    return propagate(n_xy, E0, lam_um, h_um, dz_um, z_save_um, n_ref, cap=True, observe=None)
