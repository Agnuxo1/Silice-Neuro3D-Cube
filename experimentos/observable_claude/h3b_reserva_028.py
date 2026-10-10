"""H3 (extension a la malla reservada dx=0,28 um de T96/Q4): sin propagar de nuevo. Lee el campo final
de 009d (out/state_T96d_dx3.npy, generado por 009d, NO reproducido aqui) y calcula P16 (convencion 009d),
P64 (cobertura de H1) y Pc (original). Compara con resultados_q4_reserva_028.json (P=0,3329871268545929).
Criterios de CONTRATO-Q4-RESERVA-028 sin cambios: Q5 (dispersion rel. < 0,5 %), P-R1 (banda fija),
P-R2 (|P(0,28)-P(0,4)| <= 4,4e-4). Q4 historico no se reevalua aqui.
"""
import os, sys, json, hashlib
os.environ["OMP_NUM_THREADS"] = "1"
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import observable_cobertura as oc

dx = 0.28e-6; N = 457
A = np.load(os.path.join(HERE, "..", "glass009d_claude", "out", "state_T96d_dx3.npy"))
assert A.shape == (N, N), A.shape
w16 = oc.disk_coverage_uniform(N, dx, ss=16)
w64 = oc.disk_coverage(N, dx, ss=64)
P28 = dict(P16=oc.obs_cov(A, w16, dx), P64=oc.obs_cov(A, w64, dx), Pc=oc.obs_center(A, dx))
ref = json.load(open(os.path.join(HERE, "..", "glass009d_claude", "resultados_q4_reserva_028.json")))
# P(0,5) y P(0,4) de esta tarea (campos re-propagados en h3_run_009d.py)
def hp(dxtag, ch=None):
    n = f"h3_T96d_dx{dxtag}" + (f"_c{ch}" if ch is not None else "") + ".json"
    return json.load(open(os.path.join(HERE, "out", n)))
P05 = {"P16": hp(5)["P16_009d_convention"], "P64": hp(5)["P64_cobertura_H1"], "Pc": hp(5)["Pc_centro_original"]}
P04 = {"P16": hp(4, 1)["P16_009d_convention"], "P64": hp(4, 1)["P64_cobertura_H1"], "Pc": hp(4, 1)["Pc_centro_original"]}
band = ref["P_R1_band"]
res = {}
for lab in ["P16", "P64", "Pc"]:
    vals = [P05[lab], P04[lab], P28[lab]]
    spread = (max(vals) - min(vals)) / np.mean(vals)
    res[lab] = dict(P28=P28[lab], P05=P05[lab], P04=P04[lab],
                    Q5_spread_rel=float(spread), Q5_pass=bool(spread < 0.005),
                    PR1_in_band=bool(band[0] <= P28[lab] <= band[1]),
                    PR2_abs_diff_28_04=float(abs(P28[lab] - P04[lab])), PR2_pass=bool(abs(P28[lab] - P04[lab]) <= 4.4e-4))
out = dict(
    tarea="H3b", nota="campo 009d leido, no reproducido en esta tarea; P16 debe igualar la cifra de 009d",
    P16_minus_009d_reserve=float(P28["P16"] - ref["P"]["0.28"]),
    state_sha256=hashlib.sha256(open(os.path.join(HERE, "..", "glass009d_claude", "out", "state_T96d_dx3.npy"), "rb").read()).hexdigest(),
    resultados=res,
)
json.dump(out, open(os.path.join(HERE, "out", "h3b_reserva_028.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
