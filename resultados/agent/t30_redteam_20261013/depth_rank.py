"""Rank of the Jacobian of (params -> U) for layered meshes of general two-mode elements.
Mesh: phase screen (N) then D x [beam-splitter layer R(theta) on disjoint pairs, phase screen (N)].
This is the most general layered mesh of U(2) elements. Rank = local image dimension (max N^2)."""
import numpy as np
rng = np.random.default_rng(1)

def pairs_for(N, layer, cyl):
    if layer % 2 == 0: return [(i, i + 1) for i in range(0, N - 1, 2)]
    p = [(i, i + 1) for i in range(1, N - 1, 2)]
    if cyl and N % 2 == 0: p.append((N - 1, 0))          # wrap-around pair: needs 3D (cylinder) or a crossing
    return p

def build(params, N, D, cyl):
    k = 0; U = np.diag(np.exp(1j * params[k:k + N])); k += N
    for l in range(D):
        L = np.eye(N, dtype=complex)
        for (a, b) in pairs_for(N, l, cyl):
            t = params[k]; k += 1
            L[[a, a, b, b], [a, b, a, b]] = [np.cos(t), -np.sin(t), np.sin(t), np.cos(t)]
        U = np.diag(np.exp(1j * params[k:k + N])) @ L @ U; k += N
    return U

def nparams(N, D, cyl): return N + sum(len(pairs_for(N, l, cyl)) + N for l in range(D))

def rank(N, D, cyl):
    P = nparams(N, D, cyl); x = rng.uniform(0, 2 * np.pi, P); h = 1e-6
    J = []
    for i in range(P):
        e = np.zeros(P); e[i] = h
        dU = (build(x + e, N, D, cyl) - build(x - e, N, D, cyl)) / (2 * h)
        J.append(np.concatenate([dU.real.ravel(), dU.imag.ravel()]))
    s = np.linalg.svd(np.array(J), compute_uv=False)
    return int((s > 1e-6 * s[0]).sum()), sum(len(pairs_for(N, l, cyl)) for l in range(D))

for N in (4, 5, 6, 8):
    for D in (N - 2, N - 1, N):
        rp, mp = rank(N, D, False); rc, mc = rank(N, D, True)
        print(f"N={N} D={D}: planar rank {rp}/{N*N} ({mp} elements) | cylindrical rank {rc}/{N*N} ({mc} elements)")
