"""Record factual milestone without altering frozen study data."""
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_point03_exponential import ROOT,sha,write

timing=ROOT/'resultados/codex/point03_fdst_manufactured_timing_20261007.json'
d=json.loads(timing.read_text(encoding='utf-8'))
assert d['pass_'] and d['no_T96_propagation'] and d['source_sha256']=='run_point03_exponential'
write(ROOT/'resultados/codex/point03_fdst_manufactured_timing_metadata_audit_20261007.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),timing_path=str(timing),timing_sha256=sha(timing),metadata_correction_only=True,original_source_sha256_is_module_name=True,kernel_path=str(ROOT/'scripts/point03_fdst.py'),kernel_sha256=sha(ROOT/'scripts/point03_fdst.py'),h_helper_sha256=sha(ROOT/'scripts/run_point03_exponential.py'),manufactured_control_pass=d['pass_'],field_relative_error=d['field_relative_error'],seconds_per_step=d['seconds_per_step'],no_optical_propagation=True,raw_report_unchanged=True))
p=ROOT/'coordinacion/CHECKPOINT.md';old=p.read_text(encoding='utf-8')
text='''## K626 negativo; kernel FDST contrastado — {utc}

K626 completo3371,950s/28CP, integridad independientePASS48celdas/hash.
FAIL ambas predicciones: campo1,45058e-5>1,12504e-5; intensidad
1,41303e-5>7,61571e-6. Referencia cruda5,87269e-10<=1e-9, pero ambas
potenciasR11/R17~3,906e-10>1e-10: FAIL. Fuentes46f3567 intactas.
Diagnóstico cúbico N6260,3329668172481241>N6400,3329597828900894:
dispersión no monótona; no causa demostrada. Mantener E/G/H/K FAIL.
Nuevo kernelFDST fuente fb9cf4f: operador FD original, DST-I ortho,
Yoshida4; controles densos/senos/norma/ordenPASS3,9994/4,0009.
Coste fabricado626/100pasos18,2423s/error2,541e-13PASS, SINperfilT96.
Metadato hash de salida fue nombre de módulo: auditoría separada lo
identifica y añade hash real sin tocar el dato original.
Piloto ópticoFDST registrado antes de propagar: N626 entradaK intacta,
dz0,625/0,3125/0,15625um (3200/6400/12800pasos),56chunks400pasos,
7200s/hijos360/corte370/CPU1. Campo fino<=1e-4/Pambas<=1e-6,
órdenes[3,5;4,5]. Fuentes/contrato se congelan antes del primer paso.
Sólo contraste temporal, NOcierre espacial aunquePASS. Punto3ABIERTO,
no barrido modal ni posteriores. Principal preservado; JEVfallback
local/bloqueo heredado, sinGPU/instalaciones/push/subagentes.

'''.format(utc=datetime.now(timezone.utc).isoformat())
p.write_text(text+old,encoding='utf-8')
p=ROOT/'Docs/PROJECT-STATUS-20261007.md';old=p.read_text(encoding='utf-8')
old=old.replace('K640 favorable, nueva prueba N626 en curso','K640 favorable; K626 completo y negativo; contraste FDST registrado')
old=old.replace('la intensidad queda próxima a su límite. La prueba N626 es nueva y\nmantiene las predicciones originales y todos los umbrales. El estado\nde convergencia seguirá abierto hasta finalizar/auditar/evaluar esa prueba.','la intensidad queda próxima a su límite. K626 terminó con integridad\nPASS y resultados negativos en ambas predicciones y ambas concordancias\nde potencia. Punto3 abierto. El nuevo kernelFDST pasa controles conocidos;\nsu piloto temporal está registrado y no permite cerrar convergencia espacial.')
p.write_text(old,encoding='utf-8')
print('Checkpoint factual y estado fechados actualizados; datos congelados intactos.')
