"""Create user-facing results from completed evidence; never run propagation."""
import argparse
import csv
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fmt(x):return 'no disponible' if x is None else f'{x:.9g}'

def export(out,visible):
    assert not out.exists();out.mkdir(parents=True)
    epath=ROOT/'resultados/codex/point03_analytic_20261007T004526617696Z';gpath=ROOT/'resultados/codex/point03_reconstructed_20261007_G2';hpath=ROOT/'resultados/codex/point03_exponential_20261007_H2'
    h=read(hpath/'assessment.json');he=read(hpath/'execution.json');ha=read(hpath/'integrity_audit.json');g=read(gpath/'assessment.json');e=read(epath/'assessment.json')
    assert he['status']=='completed' and ha['integrity_pass'] and sha(hpath/'assessment.json')==he['assessment_sha256']
    kpredpath=ROOT/'resultados/codex/point03_linear_prediction_20261007.json';kpath=ROOT/'resultados/codex/point03_linear_K640_20261007.json';jpath=ROOT/'resultados/codex/point03_scatter_diagnostic_20261007.json'
    k=read(kpath) if kpath.exists() else None;kp=read(kpredpath);j=read(jpath) if jpath.exists() else None
    current='CERRADO: convergencia local de potencia aceptada por H2' if h['point03_closed'] else 'ABIERTO: convergencia local aún no aceptada'
    lines=['# Evaluación T96/Q4 — 7 de octubre de 2026','',f'**Punto 3: {current}.**', '', 'El ensayo E se recuperó completo, sin relanzarlo: ocho simulaciones, 144 checkpoints y 28 800 pasos. Su evaluación científica es negativa. Los archivos originales y los fallos históricos se conservaron.', '', '## Contrastes realizados', '', '| Estudio | Resultado | Evidencia principal |','|---|---|---|', '| E original | FAIL | Discrepancia de órdenes 42,956%; predicción N500 fuera de tolerancia; control longitudinal N400 fuera del intervalo registrado |', '| F, reconstrucción del detector | Diagnóstico favorable, sin cierre | Predicciones espaciales pasan; el control longitudinal N400 sigue fallando |', '| G2, refinamiento ADI | FAIL | Control longitudinal N400/N500 y predicción N640 incumplen; integridad de 233 chunks válida |', f"| H2, referencia exponencial | {'PASS local' if h['scientific_pass'] else 'FAIL'} | {ha['checkpoints_checked']} checkpoints auditados; referencias temporales y nueva predicción N640 contrastadas |", '', 'H1 y G1 sufrieron fallos operativos conservados. Sus recuperaciones G2/H2 reutilizaron resultados válidos y repitieron sólo el trabajo necesario, con contratos y límites fijados previamente. H2 reutiliza 48 checkpoints de H1 y añade 28, con particiones de 11/17 tramos en N640.', '', '## Referencia H2: resultados y criterios', '', '| N | dx (µm) | Potencia núcleo / entrada, campo reconstruido | Partición fina |','|---:|---:|---:|---:|']
    for r in h['rows']:lines.append(f"| {r['N']} | {128/r['N']:.6g} | {r['methods'][str(r['fine_segments'])]['field']['P_core']:.12f} | {r['fine_segments']} |")
    lines += ['', '| Criterio H2 | Campo | Intensidad |','|---|---:|---:|']
    for label,key in [('Orden observado','orders'),('Discrepancia relativa de órdenes','order_disagreement')]:
        vals=[h['spatial'][m][key] for m in ('field','intensity')];lines.append('| '+label+' | '+' | '.join('/'.join(fmt(v) for v in x) if isinstance(x,list) else fmt(x) for x in vals)+' |')
    for label,key in [('Predicción N640','prediction'),('Potencia N640','actual'),('Residual N640','residual'),('Límite previo N640','limit'),('Predicción aceptada','pass_')]:lines.append('| '+label+' | '+' | '.join(str(h['holdout'][m][key]) if key=='pass_' else fmt(h['holdout'][m][key]) for m in ('field','intensity'))+' |')
    lines += ['', f"Consistencia de referencias: {h['reference_consistency_pass']}; contraste temporal directo ADI: {h['temporal_direct_pass']}; cuadratura: {h['quadrature_pass']}; controles gaussianos: {h['gaussian_pass']}.", '', 'Los indicadores de incertidumbre son condicionales: no son cotas rigurosas ni intervalos con una cobertura probabilística acreditada. Se limitó el exponente del indicador espacial a 2; los órdenes altos del observable no demuestran ese orden para el campo.']
    if j:
        lines += ['', '## Diagnóstico de dispersión J', '', 'Se aplicó a las cinco referencias completas y consistentes. No cambia el dictamen de E/G/H2. La adaptación retuvo un control sintético fallido del indicador seleccionado y añadió una envolvente distinta; sus controles favorables no prueban cobertura universal.']
        for m,v in j['models'].items():lines.append(f"- {m}: indicador seleccionado en N640 {fmt(v['intervals'][-1]['uncertainty'])}; envolvente {fmt(v['envelope_intervals'][-1]['uncertainty'])}.")
    if k:
        lines += ['', '## Contraste de detector K', '', 'Los detectores bilineales se verificaron con momentos exactos, 16 celdas de referencia independientes y Gaussianas con fases conocidas. Sus cuatro mallas iniciales pasan. Se congelaron predicciones N640/N626 antes de medir los nuevos funcionales; K640 reutiliza una trayectoria y no constituye una nueva simulación independiente.', '', '| Detector | N640 medido | Residual | Límite previo | Pasa todos los criterios K640 |','|---|---:|---:|---:|---|']
        for m,v in k['gates'].items():lines.append(f"| {m} | {fmt(v['actual'])} | {fmt(v['residual'])} | {fmt(v['limit'])} | {all(v[q] for q in ('holdout_pass','uncertainty_pass','temporal_pass','reference_pass','quadrature_pass'))} |")
        lines += ['', f"Resultado K640: {k['K640_pass']}. Una aceptación por K requiere además el nuevo ensayo prospectivo N626; este informe no atribuye ese resultado si no existe evidencia separada."]
    lines += ['', '## Alcance y continuidad', '', 'Modelo escalar paraxial ideal: longitud 2 mm, dominio 128 µm, núcleo de radio 6 µm, longitud de onda 1550 nm. Se comparó potencia fraccional del núcleo, sin renormalizar salidas ni alinear fases. La referencia exponencial resuelve el operador espacial discretizado, no el continuo exacto ni Maxwell.', '', 'Las particiones de un mismo algoritmo exponencial son controles de consistencia. Particiones relacionadas pueden compartir incrementos internos; no se presentan como dos algoritmos independientes. Campo complejo, fase, frontera, perfiles medidos y fabricación quedan sujetos a los puntos posteriores.', '', 'El checkout principal se preservó. La copia aislada retiene fuentes, contratos, predicciones, arrays completos y fallos. El paquete adjunto contiene informes y hashes, no todos los arrays. JEV: fallback local identificado; el bloqueo de seguridad remoto heredado se conservó, sin recomendación remota válida.', '', '## Fuentes primarias consultadas', '', '- [NASA: convergencia espacial](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html).', '- [SciPy 1.15.1: acción de la exponencial](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.sparse.linalg.expm_multiply.html).', '- [Eça–Hoekstra 2014: estimación con dispersión](https://doi.org/10.1016/j.jcp.2014.01.006). Adaptación diagnóstica explícita, sin importar una garantía de cobertura.', '- [Vassallo 1997: interfaces y discretización óptica](https://opg.optica.org/josaa/abstract.cfm?uri=josaa-14-12-3273). Sólo resumen del editor.', '- [Henning–Peterseim 2017: potenciales abruptos](https://arxiv.org/html/1608.02267). Formulación e hipótesis examinadas; método distinto, sin transferencia automática del teorema.', '']
    report=out/'evaluacion_T96_Q4.md';report.write_text('\n'.join(lines),encoding='utf-8')
    files=[epath/'assessment.json',gpath/'assessment.json',gpath/'execution.json',gpath/'integrity_audit.json',hpath/'assessment.json',hpath/'execution.json',hpath/'integrity_audit.json',hpath/'manifest.json',ROOT/'resultados/codex/point03_exponential_20261007_H1/execution.json',ROOT/'resultados/codex/point03_exponential_20261007_H1/prediction.json',kpredpath]
    files += [p for p in (kpath,jpath) if p.exists()]
    files += [ROOT/'resultados/codex/point03_exponential_partition_diagnostic_20261007.json']
    files += [ROOT/'Docs'/name for name in ('POINT-03-ANALYTIC-PROPAGATION-RESULTS.md','POINT-03-G-RESULTS.md','POINT-03-EXPONENTIAL-REFERENCE-CONTRACT.md','POINT-03-H-RECOVERY-CONTRACT.md','POINT-03-LINEAR-DETECTOR-CONTRACT.md','POINT-03-SCATTER-DIAGNOSTIC-CONTRACT.md','POINT-03-INTERFACE-LITERATURE.md','POINT-03-EXPONENTIAL-CODE-REVIEW.md','POINT-03-EXPONENTIAL-PARTITION-RESULTS.md')]
    manifest={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in files};(out/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    archive=out/'evidencias_T96_Q4.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,str(p.relative_to(ROOT)).replace('\\','/'))
        z.write(out/'SHA256.json','SHA256.json')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name,d in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==d
    visible.mkdir(parents=True,exist_ok=True)
    for p in (report,archive):
        target=visible/p.name;assert not target.exists();shutil.copyfile(p,target);assert sha(target)==sha(p)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),point03_closed=h['point03_closed'],files={str(visible/p.name):sha(p) for p in (report,archive)},archive_reports=len(files),zip_crc_and_sha_verified=True)
    (out/'export.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result));return result

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--visible',type=Path,required=True);args=p.parse_args();export(args.out,args.visible)
if __name__=='__main__':main()
