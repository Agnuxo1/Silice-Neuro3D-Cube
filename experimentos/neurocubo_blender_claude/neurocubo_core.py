"""Neuro-cube numerical core: geometry -> transfer, two-mesh optoelectronic network, exact gradients.

NUMERICAL MODEL. Blender supplies geometry, runs the training loop and draws the
result; the physics below comes from validated repository models and stated
assumptions. Nothing here is a device measurement or a render-engine physics
calculation (R1/R2/P1 failed on accuracy; R3 only validates representation).

Conventions
-----------
* MZI blocks reuse agentkit.mzi: MZI = B(eps2) P(theta) B(eps1) P(phi), upper-arm
  heaters, coupler angle a = pi/4 + eps, Clements ordering (Optica 3, 1460, 2016).
* Coupler angle from geometry: a = kappa(g) * L_c. kappa(g) is interpolated
  (log-linear) between finite-difference supermode values at g = 14, 16, 20 um
  (experimentos/acoplador_claude, G2: FD vs coupled-mode theory within 0.08 % at
  14 um). Model-to-model validation only; no measurement. Outside 14-20 um the
  function refuses to extrapolate.
* g is the centre-to-centre separation of the two cores of the step-index analogue
  (core radius 6 um, i.e. 12 um diameter; V = 2.92, so the analogue is not strictly
  single-mode: LP11 cut-off is V = 2.405). At g = 14 um the core edges are 2 um apart.
* Phase of an arm: 2 pi n_eff L / lambda plus the heater phase. Arms and idle
  guides are ASSUMED path-length matched (the drawn S-bends are about 0.24 um longer
  than a straight idle guide, about 5.5 rad per column, which a real layout must
  compensate), so only heater phases differ and the remaining propagation phase is
  common (global) to the whole layer.
* Coupling inside the S-bend access regions is NOT modelled (estimated about
  0.06 rad per S-bend, 0.12 rad per coupler, systematic); couplers are nominal
  (eps = 0) unless errors are drawn explicitly.
* Loss per stage (MZI column): 0.35 dB nominal (Ceccarelli et al. 2020, cited in
  T24), applied to every mode of every column (balanced design).
* Network: amplitude-encoded signed real input x (phase-referenced carrier) ->
  mesh 1 -> detection + signed-field push-pull MZM re-emission a = cos(0.5 (pi I/V_pi + bias))
  (agentkit.learning_v2 convention) -> mesh 2 -> intensities -> logits = G * I[ports] -> softmax.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field

import numpy as np
from scipy.linalg import expm, expm_frechet
from scipy.optimize import minimize
from scipy.special import logsumexp

from agentkit import mzi as akm

SCOPE = "numerical_neural_model"
WAVELENGTH_M = 1.55e-6
N0 = 1.444
N_CLADDING_MODEL = 1.439
N_EFF = 1.4421921654570125          # analytic LP01, experimentos/acoplador_claude G1.5
KAPPA_FD_TABLE = ((14e-6, 471.6394183216887),   # 1/m, acoplador_claude resultados_g1_g2.json
                  (16e-6, 203.05398235231223),
                  (20e-6, 38.51257119356343))
NOMINAL_GAP_M = 14e-6
LOSS_DB_PER_STAGE = 0.35
TWO_PI = 2 * math.pi


# ----------------------------------------------------------------------------- physics
def kappa_of_gap(gap_m: float) -> float:
    """Coupling constant (1/m) inside the cross-validated range 14-20 um."""
    gaps = [g for g, _ in KAPPA_FD_TABLE]
    if not math.isfinite(gap_m) or not gaps[0] - 1e-12 <= gap_m <= gaps[-1] + 1e-12:
        raise ValueError("gap outside the cross-validated kappa(g) range 14-20 um")
    for g, k in KAPPA_FD_TABLE:
        if abs(gap_m - g) <= 1e-15:
            return k
    logs = [math.log(k) for _, k in KAPPA_FD_TABLE]
    return float(math.exp(np.interp(gap_m, gaps, logs)))


def coupler_angle(gap_m: float, length_m: float) -> float:
    """Coupled-mode coupler angle a = kappa(g) L (a = pi/4 is 50:50)."""
    return kappa_of_gap(gap_m) * length_m


def balanced_coupler_length(gap_m: float = NOMINAL_GAP_M) -> float:
    """Length giving a = pi/4 at the stated gap."""
    return math.pi / (4 * kappa_of_gap(gap_m))


def propagation_phase(length_m: float, n_eff: float = N_EFF,
                      wavelength_m: float = WAVELENGTH_M) -> float:
    """2 pi n_eff L / lambda reduced modulo 2 pi."""
    return math.fmod(TWO_PI * n_eff * length_m / wavelength_m, TWO_PI)


def stage_amplitude(loss_db_per_stage: float, stages: int) -> float:
    """Field amplitude transmission of `stages` lossy stages."""
    return 10 ** (-loss_db_per_stage * stages / 20)


def haar_unitary(n: int, rng: np.random.Generator) -> np.ndarray:
    z = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / math.sqrt(2)
    q, r = np.linalg.qr(z)
    d = np.diag(r)
    return q * (d / abs(d))


# ----------------------------------------------------------------------------- mesh
def mesh_template(n: int) -> list[tuple[int, int]]:
    """(upper mode, column) of each MZI in Clements propagation order (structure only)."""
    structures = []
    for seed in (0, 1):
        dec = akm.clements_decompose(haar_unitary(n, np.random.default_rng(seed)))
        structures.append([(op["modes"][0], op["layer"]) for op in dec["mzis"]])
    if structures[0] != structures[1]:
        raise RuntimeError("Clements structure depends on the target; template undefined")
    return structures[0]


@dataclass
class MeshSpec:
    """Fixed (non-trainable) part of one mesh layer, derived from geometry."""
    n: int
    template: list
    eps: np.ndarray            # (K, 2) coupler-angle errors (eps_in, eps_out)
    eta: float                 # field amplitude transmission of the layer
    common_phase: float        # global propagation phase of the layer (rad)
    stages: int = 0

    @property
    def n_mzi(self) -> int:
        return len(self.template)

    @property
    def n_params(self) -> int:
        return 2 * self.n_mzi + self.n


def ideal_mesh_spec(n: int, loss_db_per_stage: float = LOSS_DB_PER_STAGE,
                    common_phase: float = 0.0) -> MeshSpec:
    template = mesh_template(n)
    stages = max(c for _, c in template)
    return MeshSpec(n, template, np.zeros((len(template), 2)),
                    stage_amplitude(loss_db_per_stage, stages), common_phase, stages)


def _dblocks(theta: float, phi: float, e1: float, e2: float):
    b1, b2 = akm.coupler(e1), akm.coupler(e2)
    pt = np.diag([np.exp(1j * theta), 1.0])
    pp = np.diag([np.exp(1j * phi), 1.0])
    dt = np.diag([1j * np.exp(1j * theta), 0.0])
    dp = np.diag([1j * np.exp(1j * phi), 0.0])
    return b2 @ dt @ b1 @ pp, b2 @ pt @ b1 @ dp


def mesh_transfer(params, spec: MeshSpec, derivatives: bool = False):
    """Transfer T = eta e^{i Phi} D(psi) M_K ... M_1 and dT/dp in parameter order.

    Parameter order: theta_1, phi_1, ..., theta_K, phi_K, psi_1..psi_n.
    """
    p = np.asarray(params, dtype=float)
    n, k_count = spec.n, spec.n_mzi
    if p.shape != (spec.n_params,) or not np.all(np.isfinite(p)):
        raise ValueError("Wrong or non-finite mesh parameters")
    blocks = []
    prefix = [np.eye(n, dtype=complex)]
    for k, (m, _) in enumerate(spec.template):
        block = akm.mzi(p[2 * k], p[2 * k + 1], float(spec.eps[k, 0]), float(spec.eps[k, 1]))
        blocks.append(block)
        nxt = prefix[-1].copy()
        nxt[m:m + 2, :] = block @ prefix[-1][m:m + 2, :]
        prefix.append(nxt)
    scale = spec.eta * np.exp(1j * spec.common_phase)
    out = np.exp(1j * p[2 * k_count:])
    transfer = scale * out[:, None] * prefix[-1]
    if not derivatives:
        return transfer, None
    d = [None] * spec.n_params
    left = scale * np.diag(out)
    for k in range(k_count - 1, -1, -1):
        m = spec.template[k][0]
        d_theta, d_phi = _dblocks(p[2 * k], p[2 * k + 1], float(spec.eps[k, 0]), float(spec.eps[k, 1]))
        right = prefix[k][m:m + 2, :]
        d[2 * k] = left[:, m:m + 2] @ (d_theta @ right)
        d[2 * k + 1] = left[:, m:m + 2] @ (d_phi @ right)
        new_left = left.copy()
        new_left[:, m:m + 2] = left[:, m:m + 2] @ blocks[k]
        left = new_left
    for j in range(n):
        dj = np.zeros((n, n), dtype=complex)
        dj[j, :] = scale * 1j * out[j] * prefix[-1][j, :]
        d[2 * k_count + j] = dj
    return transfer, np.asarray(d)


def params_from_decomposition(dec: dict) -> np.ndarray:
    values = []
    for op in dec["mzis"]:
        values.extend([op["theta_rad"], op["phi_rad"]])
    values.extend(dec["output_phases_rad"])
    return np.asarray(values, dtype=float)


def decomposition_from_params(params, spec: MeshSpec) -> dict:
    """agentkit.mzi decomposition dict (for clements_reconstruct) from mesh parameters."""
    p = np.asarray(params, dtype=float)
    k_count = spec.n_mzi
    mzis = [{"modes": [m, m + 1], "theta_rad": float(p[2 * k]), "phi_rad": float(p[2 * k + 1]),
             "layer": int(c)} for k, (m, c) in enumerate(spec.template)]
    return {"dimension": spec.n, "mzis": mzis,
            "output_phases_rad": [float(v) for v in p[2 * k_count:]]}


# ----------------------------------------------------------------------------- real gain-matched layer
def skew_basis(n: int) -> np.ndarray:
    basis = []
    for i in range(n):
        for j in range(i + 1, n):
            e = np.zeros((n, n))
            e[i, j], e[j, i] = 1.0, -1.0
            basis.append(e)
    return np.asarray(basis)


def real_matched_transfer(params, n: int, eta: float, derivatives: bool = False):
    """W = eta Q1 diag(cos t) Q2^T: real weights with spectral norm <= eta (passive gain)."""
    p = np.asarray(params, dtype=float)
    m = n * (n - 1) // 2
    if p.shape != (n * n,) or not np.all(np.isfinite(p)):
        raise ValueError("Wrong or non-finite real-layer parameters")
    basis = skew_basis(n)
    s1, s2 = np.einsum("k,kij->ij", p[:m], basis), np.einsum("k,kij->ij", p[m + n:], basis)
    q1, q2 = expm(s1), expm(s2)
    c = np.cos(p[m:m + n])
    w = eta * (q1 * c) @ q2.T
    if not derivatives:
        return w, None
    d = []
    for e in basis:
        d.append(eta * (expm_frechet(s1, e, compute_expm=False) * c) @ q2.T)
    sn = -np.sin(p[m:m + n])
    for j in range(n):
        d.append(eta * sn[j] * np.outer(q1[:, j], q2[:, j]))
    left = q1 * c
    for e in basis:
        d.append(eta * left @ expm_frechet(s2, e, compute_expm=False).T)
    return w, np.asarray(d)


# ----------------------------------------------------------------------------- network
@dataclass
class NetConfig:
    kind: str                  # "optical" or "real_matched"
    n: int
    gain: float
    ports: tuple
    v_pi: float = 1.0
    bias: float = 0.0
    specs: tuple = field(default_factory=tuple)   # (MeshSpec, MeshSpec) for optical
    etas: tuple = (1.0, 1.0)                        # for real_matched

    @property
    def layer_params(self) -> int:
        return self.n * self.n

    @property
    def n_params(self) -> int:
        return 2 * self.n * self.n


def optical_config(n: int, gain: float, ports, specs=None, v_pi: float = 1.0,
                   bias: float = 0.0) -> NetConfig:
    specs = specs or (ideal_mesh_spec(n), ideal_mesh_spec(n))
    return NetConfig("optical", n, float(gain), tuple(int(p) for p in ports), v_pi, bias, tuple(specs),
                     (specs[0].eta, specs[1].eta))


def real_matched_config(n: int, gain: float, ports, loss_db_per_stage: float = LOSS_DB_PER_STAGE,
                        v_pi: float = 1.0, bias: float = 0.0) -> NetConfig:
    stages = max(c for _, c in mesh_template(n))
    eta = stage_amplitude(loss_db_per_stage, stages)
    return NetConfig("real_matched", n, float(gain), tuple(int(p) for p in ports), v_pi, bias,
                     tuple(), (eta, eta))


def _layer(p, cfg: NetConfig, index: int, derivatives: bool):
    if cfg.kind == "optical":
        return mesh_transfer(p, cfg.specs[index], derivatives)
    if cfg.kind == "real_matched":
        return real_matched_transfer(p, cfg.n, cfg.etas[index], derivatives)
    raise ValueError("Unknown network kind")


def forward(params, x, cfg: NetConfig, derivatives: bool = False):
    """Logits G*I[ports], all output intensities and optional exact parameter directions."""
    x = np.asarray(x, dtype=float)
    p = np.asarray(params, dtype=float)
    n = cfg.n
    if x.ndim != 2 or x.shape[1] != n or not np.all(np.isfinite(x)):
        raise ValueError("Inputs must be finite rows with n features")
    if p.shape != (cfg.n_params,):
        raise ValueError("Wrong parameter count")
    if not (math.isfinite(cfg.v_pi) and cfg.v_pi > 0 and math.isfinite(cfg.bias)):
        raise ValueError("V_pi must be positive and bias finite")
    t1, d1 = _layer(p[:n * n], cfg, 0, derivatives)
    t2, d2 = _layer(p[n * n:], cfg, 1, derivatives)
    z1 = x @ t1.T
    i1 = abs(z1) ** 2
    angle = 0.5 * (math.pi * i1 / cfg.v_pi + cfg.bias)
    amplitude = np.cos(angle)
    slope = -0.5 * math.pi / cfg.v_pi * np.sin(angle)
    z2 = amplitude @ t2.T
    intensity = abs(z2) ** 2
    ports = list(cfg.ports)
    logits = cfg.gain * intensity[:, ports]
    if not derivatives:
        return logits, intensity, None
    directions = []
    for direction in d1:
        di1 = 2 * np.real(np.conj(z1) * (x @ direction.T))
        dz2 = (slope * di1) @ t2.T
        directions.append(cfg.gain * 2 * np.real(np.conj(z2) * dz2)[:, ports])
    for direction in d2:
        dz2 = amplitude @ direction.T
        directions.append(cfg.gain * 2 * np.real(np.conj(z2) * dz2)[:, ports])
    return logits, intensity, np.asarray(directions)


def objective(params, x, y, cfg: NetConfig):
    """Mean cross-entropy on G-scaled intensity logits and its exact gradient."""
    logits, _, directions = forward(params, x, cfg, True)
    y = np.asarray(y)
    if y.shape != (len(x),) or y.dtype.kind not in "iu" or y.min() < 0 or y.max() >= logits.shape[1]:
        raise ValueError("Labels must index the read-out ports")
    normalizer = logsumexp(logits, axis=1)
    loss = float(np.mean(normalizer - logits[np.arange(len(y)), y]))
    weights = np.exp(logits - normalizer[:, None])
    weights[np.arange(len(y)), y] -= 1
    weights /= len(y)
    return loss, np.einsum("nc,knc->k", weights, directions)


def cross_entropy(params, x, y, cfg: NetConfig) -> float:
    logits, _, _ = forward(params, x, cfg)
    return float(np.mean(logsumexp(logits, axis=1) - logits[np.arange(len(y)), y]))


def predict(params, x, cfg: NetConfig) -> np.ndarray:
    return forward(params, x, cfg)[0].argmax(axis=1)


def init_params(cfg: NetConfig, seed: int) -> np.ndarray:
    """Optical: all phases U(0, 2 pi). Real: generators 0.5 N(0,1), singular angles U(0, 2 pi)."""
    rng = np.random.default_rng(seed)
    if cfg.kind == "optical":
        return rng.uniform(0, TWO_PI, cfg.n_params)
    n, m = cfg.n, cfg.n * (cfg.n - 1) // 2
    layers = []
    for _ in range(2):
        layers.extend([0.5 * rng.standard_normal(m), rng.uniform(0, TWO_PI, n),
                       0.5 * rng.standard_normal(m)])
    return np.concatenate(layers)


class _Cache:
    """Remember recent objective evaluations so the per-iteration callback does not recompute."""

    def __init__(self, x, y, cfg):
        self.x, self.y, self.cfg, self.store, self.evaluations = x, y, cfg, {}, 0

    def __call__(self, p):
        key = np.asarray(p, dtype=float).tobytes()
        if key not in self.store:
            if len(self.store) > 32:
                self.store.clear()
            self.store[key] = objective(p, self.x, self.y, self.cfg)
            self.evaluations += 1
        loss, grad = self.store[key]
        return loss, grad.copy()


def fit_start(x, y, cfg: NetConfig, start, maxiter: int, gradient_threshold: float = 1e-5,
              on_iteration=None) -> dict:
    """One L-BFGS-B start (learning_v2 options) with a per-iteration hook and full trajectory."""
    cache = _Cache(np.asarray(x, float), np.asarray(y), cfg)
    loss0, grad0 = cache(start)
    trajectory = [np.asarray(start, float).copy()]
    losses, gnorms = [loss0], [float(np.max(abs(grad0)))]
    if on_iteration is not None:
        on_iteration(0, trajectory[0], loss0, gnorms[0])

    def callback(xk):
        loss, grad = cache(xk)
        trajectory.append(np.asarray(xk, float).copy())
        losses.append(loss)
        gnorms.append(float(np.max(abs(grad))))
        if on_iteration is not None:
            on_iteration(len(losses) - 1, trajectory[-1], loss, gnorms[-1])

    result = minimize(cache, np.asarray(start, float), jac=True, method="L-BFGS-B", callback=callback,
                      options={"maxiter": maxiter, "gtol": 1e-8, "ftol": 1e-12})
    loss, gradient = objective(result.x, x, y, cfg)
    norm = float(np.max(abs(gradient)))
    if not np.array_equal(result.x, trajectory[-1]):
        trajectory.append(np.asarray(result.x, float).copy())
        losses.append(loss)
        gnorms.append(norm)
    return {"parameters": result.x.tolist(), "training_loss": loss, "gradient_infinity_norm": norm,
            "optimizer_success": bool(result.success), "optimizer_message": str(result.message),
            "iterations": int(result.nit), "function_evaluations": cache.evaluations,
            "converged": bool(result.success and norm <= gradient_threshold),
            "trajectory": np.asarray(trajectory), "loss_history": np.asarray(losses),
            "gradient_history": np.asarray(gnorms)}


def accuracy(params, x, y, cfg) -> float:
    return float(np.mean(predict(params, x, cfg) == np.asarray(y)))


# ----------------------------------------------------------------------------- geometry
def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def geometry_hash(geometry: dict) -> str:
    """SHA-256 of the canonical geometry without its own hash field."""
    body = {k: v for k, v in geometry.items() if k != "sha256"}
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def design_layout(n: int, gain: float, ports, depths_m=(3.0e-3, 6.0e-3), mode_pitch_m: float = 50e-6,
                  heater_length_m: float = 1.0e-3, sbend_length_m: float = 0.85e-3,
                  gap_m: float = NOMINAL_GAP_M, loss_db_per_stage: float = LOSS_DB_PER_STAGE,
                  v_pi: float = 1.0, bias: float = 0.0, layer_params=None) -> dict:
    """Parametric neuro-cube design (SI units) that the Blender builder instantiates.

    Each MZI column: phi heater | S-in | coupler | S-out | theta heater | S-in | coupler | S-out.
    Layer 1 runs +x at depth z1; layer 2 runs -x at depth z2 (folded at the
    optoelectronic face). Path lengths are ASSUMED matched; S-bend coupling and
    bend loss are not modelled (minimum S-bend radius about 8 mm for 0.85 mm length).
    """
    template = mesh_template(n)
    stages = max(c for _, c in template)
    lc = balanced_coupler_length(gap_m)
    column_len = 2 * heater_length_m + 4 * sbend_length_m + 2 * lc
    out_len = heater_length_m
    layer_len = stages * column_len + out_len
    margin = 2.0e-3
    side = layer_len + 2 * margin
    layers = []
    for li in range(2):
        p = (np.zeros(n * n) if layer_params is None else np.asarray(layer_params[li], float))
        mzis = []
        for k, (m, col) in enumerate(template):
            x0 = margin + (col - 1) * column_len
            mzis.append({
                "index": k, "modes": [m, m + 1], "column": col, "x_start_m": x0,
                "coupler_in": {"gap_m": gap_m, "length_m": lc,
                               "x_m": x0 + heater_length_m + sbend_length_m},
                "coupler_out": {"gap_m": gap_m, "length_m": lc,
                                "x_m": x0 + 2 * heater_length_m + 3 * sbend_length_m + lc},
                "heater_phi": {"phi": float(p[2 * k + 1]), "length_m": heater_length_m, "x_m": x0},
                "heater_theta": {"phi": float(p[2 * k]), "length_m": heater_length_m,
                                 "x_m": x0 + heater_length_m + 2 * sbend_length_m + lc},
                "arm_path_m": {"outer": [heater_length_m, heater_length_m],
                               "inner": [heater_length_m, heater_length_m]}})
        outs = [{"mode": j, "phi": float(p[2 * len(template) + j]), "length_m": out_len,
                 "x_m": margin + stages * column_len} for j in range(n)]
        layers.append({"name": "L%d" % (li + 1), "n": n, "depth_m": depths_m[li],
                       "direction": 1 if li == 0 else -1, "stages": stages,
                       "loss_db_per_stage": loss_db_per_stage, "mode_pitch_m": mode_pitch_m,
                       "column_path_m": [column_len] * stages, "output_section_path_m": out_len,
                       "mzis": mzis, "output_heaters": outs})
    return {"schema": "neurocubo-geometry/1", "scope": SCOPE, "units": "SI (m, rad)",
            "material": {"n0": N0, "n_cladding_model": N_CLADDING_MODEL, "n_eff": N_EFF,
                         "wavelength_m": WAVELENGTH_M,
                         "n_eff_source": "analytic LP01 of the step-index analogue (acoplador_claude G1.5)"},
            "coupler_model": {"kappa_table_per_m": [[g, k] for g, k in KAPPA_FD_TABLE],
                              "gap_definition": "centre-to-centre separation; step-index analogue with core radius 6 um (12 um diameter), V = 2.92 (not strictly single-mode)",
                              "validation": "FD supermodes vs coupled-mode theory, within 0.08 % at 14 um "
                                            "(acoplador_claude G2); model-to-model, not measured",
                              "nominal_gap_m": gap_m, "balanced_length_m": lc},
            "loss_source": "0.35 dB per stage nominal (Ceccarelli et al. 2020, cited in T24)",
            "cube": {"side_m": side, "margin_m": margin, "layer_length_m": layer_len},
            "layers": layers,
            "optoelectronic_stage": {"type": "detect_and_reemit_signed_push_pull_MZM",
                                     "v_pi": v_pi, "bias": bias,
                                     "note": "external optoelectronics at the folding face; "
                                             "phase-referenced carrier assumed (T12 point 7)"},
            "readout": {"gain": float(gain), "ports": [int(q) for q in ports],
                        "note": "logits = gain * detected intensity; gain is an electronic resource"},
            "input_encoding": "signed real amplitudes on n input modes (phase-referenced carrier)"}


def spec_from_geometry_layer(layer: dict) -> tuple[MeshSpec, np.ndarray]:
    """MeshSpec (fixed part) and heater parameters of one geometry layer."""
    n = int(layer["n"])
    template = mesh_template(n)
    mzis = sorted(layer["mzis"], key=lambda item: item["index"])
    if [(m["modes"][0], m["column"]) for m in mzis] != [tuple(t) for t in template]:
        raise ValueError("Geometry MZI order differs from the Clements template")
    k_wave = TWO_PI * N_EFF / WAVELENGTH_M
    eps = np.zeros((len(mzis), 2))
    params = np.zeros(n * n)
    for k, item in enumerate(mzis):
        eps[k, 0] = coupler_angle(item["coupler_in"]["gap_m"], item["coupler_in"]["length_m"]) - math.pi / 4
        eps[k, 1] = coupler_angle(item["coupler_out"]["gap_m"], item["coupler_out"]["length_m"]) - math.pi / 4
        outer, inner = item["arm_path_m"]["outer"], item["arm_path_m"]["inner"]
        params[2 * k] = item["heater_theta"]["phi"] + k_wave * (inner[0] - inner[1])
        params[2 * k + 1] = item["heater_phi"]["phi"] + k_wave * (outer[0] - outer[1])
    outs = sorted(layer["output_heaters"], key=lambda item: item["mode"])
    for j, item in enumerate(outs):
        params[2 * len(mzis) + j] = item["phi"]
    stages = int(layer["stages"])
    common = propagation_phase(sum(layer["column_path_m"]) + layer["output_section_path_m"])
    eta = stage_amplitude(layer["loss_db_per_stage"], stages)
    return MeshSpec(n, template, eps, eta, common, stages), params


def config_from_geometry(geometry: dict) -> tuple[NetConfig, np.ndarray]:
    """Network configuration and full parameter vector from a geometry record."""
    specs, params = [], []
    for layer in geometry["layers"]:
        spec, p = spec_from_geometry_layer(layer)
        specs.append(spec)
        params.append(p)
    oe, ro = geometry["optoelectronic_stage"], geometry["readout"]
    cfg = optical_config(specs[0].n, ro["gain"], ro["ports"], specs, oe["v_pi"], oe["bias"])
    return cfg, np.concatenate(params)


def set_layer_params(geometry: dict, params) -> dict:
    """Copy of the geometry with heater phases replaced (mesh order)."""
    geometry = json.loads(json.dumps(geometry))
    p = np.asarray(params, float)
    for li, layer in enumerate(geometry["layers"]):
        n = layer["n"]
        q = p[li * n * n:(li + 1) * n * n]
        k_count = len(layer["mzis"])
        for item in layer["mzis"]:
            k = item["index"]
            item["heater_theta"]["phi"] = float(q[2 * k])
            item["heater_phi"]["phi"] = float(q[2 * k + 1])
        for item in layer["output_heaters"]:
            item["phi"] = float(q[2 * k_count + item["mode"]])
    geometry.pop("sha256", None)
    return geometry


# ----------------------------------------------------------------------------- errors and DAC
def draw_splitter_errors(cfg: NetConfig, sigma: float, correlation: float, rng) -> list[np.ndarray]:
    """Shared (whole device) plus local Gaussian coupler-angle errors, as in T27."""
    shared = rng.normal(0, sigma * math.sqrt(correlation))
    return [shared + rng.normal(0, sigma * math.sqrt(1 - correlation), size=(s.n_mzi, 2))
            for s in cfg.specs]


def with_errors(cfg: NetConfig, errors) -> NetConfig:
    specs = tuple(MeshSpec(s.n, s.template, s.eps + e, s.eta, s.common_phase, s.stages)
                  for s, e in zip(cfg.specs, errors))
    return optical_config(cfg.n, cfg.gain, cfg.ports, specs, cfg.v_pi, cfg.bias)


def quantize_phases(params, bits: int) -> np.ndarray:
    """Heater phases on a uniform DAC grid of 2**bits levels over [0, 2 pi)."""
    levels = 2 ** bits
    wrapped = np.mod(np.asarray(params, float), TWO_PI)
    return np.mod(np.round(wrapped / TWO_PI * levels), levels) * TWO_PI / levels


# ----------------------------------------------------------------------------- field map for rendering
def layer_mode_powers(params_layer, spec: MeshSpec, field_in) -> np.ndarray:
    """|field|^2 per mode after each column (row 0 = input), for drawing light in the guides."""
    p = np.asarray(params_layer, float)
    f = np.asarray(field_in, complex).copy()
    rows = [abs(f) ** 2]
    by_column = {}
    for k, (m, c) in enumerate(spec.template):
        by_column.setdefault(c, []).append((k, m))
    per_stage = 10 ** (-LOSS_DB_PER_STAGE / 20) if spec.stages == 0 else spec.eta ** (1 / spec.stages)
    for c in sorted(by_column):
        for k, m in by_column[c]:
            f[m:m + 2] = akm.mzi(p[2 * k], p[2 * k + 1], float(spec.eps[k, 0]), float(spec.eps[k, 1])) @ f[m:m + 2]
        f = f * per_stage
        rows.append(abs(f) ** 2)
    return np.asarray(rows)
