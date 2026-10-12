"""Planar layered layouts of the radix-2 butterfly (no repo imports).
Wires carry labels 0..N-1; coupler stage s pairs labels differing in bit s (DIT order s = 0..n-1).
Between consecutive orderings, crossings = inversions; a wire's crossings = number of wires it inverts with.
Worst path: light may switch to the partner at every coupler."""
import itertools, math, sys, numpy as np

def per_wire_inv(a, b):
    """a, b: arrays of labels in position order. Returns per-label crossing count going from a to b."""
    n = len(a); pos_b = np.empty(n, int); pos_b[b] = np.arange(n)
    pb = pos_b[a]                                   # position in b of the wire at position i in a
    i, j = np.triu_indices(n, 1)
    inv = pb[i] > pb[j]
    cnt = np.zeros(n, int); np.add.at(cnt, a[i[inv]], 1); np.add.at(cnt, a[j[inv]], 1)
    return cnt

def worst_path(N, orders, inp=None, out=None):
    """orders[s] = wire order at coupler stage s. inp/out: fixed input/output orders (None = free)."""
    n = len(orders)
    best = per_wire_inv(inp, orders[0]).astype(int) if inp is not None else np.zeros(N, int)
    total = int(best.sum() // 2)
    for s in range(n):
        new = np.empty(N, int)
        for w in range(N):
            new[w] = max(best[w], best[w ^ (1 << s)])   # after the coupler the light may be on either wire
        best = new
        nxt = orders[s + 1] if s + 1 < n else out
        if nxt is not None:
            c = per_wire_inv(orders[s], nxt); best = best + c; total += int(c.sum() // 2)
    return total, int(best.max())

def repo_layout(N):
    """Adjacent-swap interleave (i, i+d) before each stage and inverse swaps after (as in T25)."""
    n = int(math.log2(N)); ident = np.arange(N); tot = wp = 0
    best = np.zeros(N, int); total = 0
    for s in range(n):
        d = 1 << s; order = []
        for start in range(0, N, 2 * d):
            for j in range(d): order += [start + j, start + d + j]
        order = np.array(order)
        c = per_wire_inv(ident, order); total += 2 * int(c.sum() // 2)
        b2 = best + c
        new = np.array([max(b2[w], b2[w ^ d]) for w in range(N)])
        best = new + c                                 # inverse swaps: same per-wire count on the exit wire
    return total, int(best.max())

def key_order(N, bitorder, mask=0):
    """Sort labels by key: bits listed in bitorder (most significant first) of (label xor mask)."""
    labels = np.arange(N)
    keys = np.zeros(N, int)
    for b in bitorder: keys = keys * 2 + (((labels ^ mask) >> b) & 1)
    return labels[np.argsort(keys, kind="stable")]

def candidates(N, s, masks):
    n = int(math.log2(N)); others = [b for b in range(n) if b != s]
    for perm in itertools.permutations(others):
        for m in masks: yield key_order(N, list(perm) + [s], m)

def search(N, fix_in, fix_out, masks=(0,), objective="worst"):
    n = int(math.log2(N)); ident = np.arange(N)
    C = [list(candidates(N, s, masks)) for s in range(n)]
    best = None
    sizes = [len(c) for c in C]
    if math.prod(sizes) > 3e5:  # beam search on (worst, total)
        beams = [((0, 0), [o]) for o in C[0]]
        for s in range(1, n):
            ext = []
            for _, seq in beams:
                for o in C[s]:
                    t, w = worst_path(N, seq + [o], ident if fix_in else None, None)
                    ext.append(((w, t) if objective == "worst" else (t, w), seq + [o]))
            ext.sort(key=lambda x: x[0]); beams = ext[:400]
        seqs = [seq for _, seq in beams]
    else:
        seqs = (list(x) for x in itertools.product(*C))
    for seq in seqs:
        t, w = worst_path(N, seq, ident if fix_in else None, ident if fix_out else None)
        sc = (w, t) if objective == "worst" else (t, w)
        if best is None or sc < best[0]: best = (sc, t, w)
    return best[1], best[2]

print("N | repo total, worst | closed form | composite (fixed I/O) | best bit-perm layouts: fixed I/O ; free output ; free I/O  (total, worst)")
for k in range(2, 7):
    N = 1 << k
    rt, rw = repo_layout(N)
    # composite: same interleave orders, no restore between stages, identity at both ends
    orders = []
    for s in range(k):
        d = 1 << s; o = []
        for start in range(0, N, 2 * d):
            for j in range(d): o += [start + j, start + d + j]
        orders.append(np.array(o))
    ct, cw = worst_path(N, orders, np.arange(N), np.arange(N))
    masks = range(N) if N <= 16 else (0,)
    r1 = search(N, True, True, masks); r2 = search(N, True, False, masks); r3 = search(N, False, False, masks)
    r3t = search(N, False, False, masks, objective="total")
    print(f"{N:3d} | {rt:5d}, {rw:3d} | {N*(N-1-k)//2:5d} | {ct:5d}, {cw:3d} | {r1} ; {r2} ; {r3} | min-total free I/O {r3t}")
    sys.stdout.flush()
