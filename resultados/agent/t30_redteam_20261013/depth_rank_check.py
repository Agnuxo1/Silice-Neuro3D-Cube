import numpy as np, importlib.util, sys
spec = importlib.util.spec_from_file_location("dr", "D:/PROJECTS/.cognition/silice-closure-20261012/redteam/scratch/depth_rank.py")
src = open(spec.origin).read().split("for N in (4, 5, 6, 8):")[0]
exec(src)
def svals(N, D, cyl, seed):
    r = np.random.default_rng(seed); P = nparams(N, D, cyl); x = r.uniform(0, 2*np.pi, P); h = 1e-6; J = []
    for i in range(P):
        e = np.zeros(P); e[i] = h
        dU = (build(x+e, N, D, cyl) - build(x-e, N, D, cyl)) / (2*h)
        J.append(np.concatenate([dU.real.ravel(), dU.imag.ravel()]))
    return np.linalg.svd(np.array(J), compute_uv=False)
for seed in (2, 3, 4):
    s = svals(8, 8, False, seed); print("planar N=8 D=8 seed", seed, "s[62:66]/s0", (s[62:66]/s[0]).round(8))
    s = svals(8, 7, True, seed); print("cyl    N=8 D=7 seed", seed, "s[62:66]/s0", (s[62:66]/s[0]).round(8))
    s = svals(8, 7, False, seed); print("planar N=8 D=7 seed", seed, "s[56:60]/s0", (s[56:60]/s[0]).round(8))
