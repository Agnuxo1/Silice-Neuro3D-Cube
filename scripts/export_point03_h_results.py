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

def export(out,visible,probe=None,pilot=None,accuracy=None):
    out=out.resolve();visible=visible.resolve()
    probe=probe.resolve() if probe else None
    pilot=pilot.resolve() if pilot else None
    accuracy=accuracy.resolve() if accuracy else None
    assert not out.exists();out.mkdir(parents=True)
    epath=ROOT/'resultados/codex/point03_analytic_20261007T004526617696Z';gpath=ROOT/'resultados/codex/point03_reconstructed_20261007_G2';hpath=ROOT/'resultados/codex/point03_exponential_20261007_H2'
    h=read(hpath/'assessment.json');he=read(hpath/'execution.json');ha=read(hpath/'integrity_audit.json');g=read(gpath/'assessment.json');e=read(epath/'assessment.json')
    assert he['status']=='completed' and ha['integrity_pass'] and sha(hpath/'assessment.json')==he['assessment_sha256']
    kpredpath=ROOT/'resultados/codex/point03_linear_prediction_20261007.json';kpath=ROOT/'resultados/codex/point03_linear_K640_20261007.json';jpath=ROOT/'resultados/codex/point03_scatter_diagnostic_20261007.json'
    k=read(kpath) if kpath.exists() else None;kp=read(kpredpath);j=read(jpath) if jpath.exists() else None
    pa=pe=None
    if probe:
        pe=read(probe/'execution.json');pa=read(probe/'assessment.json');pi=read(probe/'integrity_audit.json')
        assert pe['status']=='completed' and pi['integrity_pass'] and sha(probe/'assessment.json')==pe['assessment_sha256']
        assert k and k['K640_pass']
    la=le=None
    if pilot:
        assert probe is not None
        le=read(pilot/'execution.json');la=read(pilot/'assessment.json');li=read(pilot/'integrity_audit.json')
        assert le['status']=='completed' and li['integrity_pass'] and li['acceptance_recomputed']
        assert sha(pilot/'assessment.json')==le['assessment_sha256'] and not la['point03_closed']
    aa=ae=None
    if accuracy:
        assert pilot is not None
        ae=read(accuracy/'execution.json');aa=read(accuracy/'assessment.json');ai=read(accuracy/'integrity_audit.json')
        assert ae['status']=='completed' and ai['integrity_pass'] and ai['acceptance_recomputed']
        assert sha(accuracy/'assessment.json')==ae['assessment_sha256'] and not aa['point03_closed'] and aa['L1_still_negative']
    closed=h['point03_closed'] or bool(pa and pa['point03_closed'])
    current=('CERRADO: convergencia local de potencia aceptada por '+('H2' if h['point03_closed'] else 'K y la prueba nueva N626')) if closed else 'ABIERTO: convergencia local aún no aceptada'
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
    if pa:
        lines += ['', '## Prueba prospectiva independiente N626', '', 'Geometría nueva con 48 celdas de referencia; 28 checkpoints auditados; predicciones procedentes exclusivamente de N320/400/500. N640 no se utilizó para reajustarlas.', '', '| Detector | Potencia medida | Predicción previa | Residual | Límite | Pasa |','|---|---:|---:|---:|---:|---|']
        for m,v in pa['gates'].items():lines.append(f"| {m} | {fmt(v['actual'])} | {fmt(v['prediction'])} | {fmt(v['residual'])} | {fmt(v['limit'])} | {all(v[q] for q in ('holdout_pass','reference_pass','quadrature_pass'))} |")
        lines += ['',f"Diferencia relativa entre referencias: {fmt(pa['reference_field_difference'])}. Resultado del ensayo nuevo: {pa['scientific_pass']}. E/G/H2 conservan sus resultados propios."]
        for method,v in pa['gates'].items():lines.append(f"- Concordancia de potencia {method}: diferencia {fmt(v['reference_power_difference'])}; límite previo 1e-10; pasa: {v['reference_pass']}.")
        lines += ['', 'También fallan ambas concordancias de potencia entre las particiones 11/17. El diagnóstico cúbico posterior revela potencia N626 superior a N640; no se utiliza como aceptación ni demuestra una causa.']
    if la:
        lines += ['', '## Piloto temporal independiente FDST', '', 'Segundo integrador del mismo operador espacial FD: difracción por transformada seno y composición de cuarto orden. Entradas N626 reutilizadas por hash. Los controles con matriz densa y modos conocidos pasaron antes de T96. Los criterios del piloto se congelaron antes de las tres trayectorias ópticas.', '', '| dz (µm) | Error relativo de campo frente R17 | Diferencia de potencia, campo bilineal | Diferencia de potencia, intensidad bilineal |', '|---:|---:|---:|---:|']
        for row in la['rows']:lines.append(f"| {fmt(row['dz_m']*1e6)} | {fmt(row['errors']['field'])} | {fmt(row['errors']['power_field'])} | {fmt(row['errors']['power_intensity'])} |")
        lines += ['',f"Resultado temporal FDST: {la['pilot_pass']}; 56 checkpoints auditados. Criterios individuales: {la['gates']}.", '', 'Órdenes observados al dividir dz por dos:']
        for quantity,orders in la['observed_orders'].items():lines.append(f"- {quantity}: "+' / '.join(fmt(x) for x in orders)+'.')
        lines += ['', 'Este piloto sólo contrasta el error temporal. Su resultado no cierra la convergencia espacial, no sustituye los fallos anteriores ni valida Maxwell o la fabricación. La referencia Taylor presenta la discrepancia de potencia registrada en K626; no se afirma exactitud ilimitada.']
    lines += ['', '## Alcance y continuidad', '', 'Modelo escalar paraxial ideal: longitud 2 mm, dominio 128 µm, núcleo de radio 6 µm, longitud de onda 1550 nm. Se comparó potencia fraccional del núcleo, sin renormalizar salidas ni alinear fases. La referencia exponencial resuelve el operador espacial discretizado, no el continuo exacto ni Maxwell.', '', 'Las particiones de un mismo algoritmo exponencial son controles de consistencia. Particiones relacionadas pueden compartir incrementos internos; no se presentan como dos algoritmos independientes. Campo complejo, fase, frontera, perfiles medidos y fabricación quedan sujetos a los puntos posteriores.', '', 'El checkout principal se preservó. La copia aislada retiene fuentes, contratos, predicciones, arrays completos y fallos. El paquete adjunto contiene informes y hashes, no todos los arrays. JEV: fallback local identificado; el bloqueo de seguridad remoto heredado se conservó, sin recomendación remota válida.', '', '## Fuentes primarias consultadas', '', '- [NASA: convergencia espacial](https://www.grc.nasa.gov/www/wind/valid/tutorial/spatconv.html).', '- [SciPy 1.15.1: acción de la exponencial](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.sparse.linalg.expm_multiply.html).', '- [Eça–Hoekstra 2014: estimación con dispersión](https://doi.org/10.1016/j.jcp.2014.01.006). Adaptación diagnóstica explícita, sin importar una garantía de cobertura.', '- [Vassallo 1997: interfaces y discretización óptica](https://opg.optica.org/josaa/abstract.cfm?uri=josaa-14-12-3273). Sólo resumen del editor.', '- [Henning–Peterseim 2017: potenciales abruptos](https://arxiv.org/html/1608.02267). Formulación e hipótesis examinadas; método distinto, sin transferencia automática del teorema.', '']
    if la:lines += ['- [Yoshida 1990, artículo original: composición de órdenes superiores](https://tlakoba.w3.uvm.edu/math6737/for_final_topics/SSM_1990_Yoshida.pdf). Secciones2–4 examinadas; la aplicación con absorción se contrastó numéricamente.', '- [SciPy1.15.1: transformada seno multidimensional](https://docs.scipy.org/doc/scipy-1.15.1/reference/generated/scipy.fft.dstn.html).', '']
    if aa:
        lines += ['## L2: precisión práctica frente a referencias calculadas', '', 'L2 utiliza un contrato nuevo, fijado antes de su única trayectoria N400. Reutiliza N626 fino por hash; conserva L1 negativo. No exige ni demuestra orden cuatro, convergencia espacial o exactitud del continuo.', '', '| N | Error relativo de campo | Error de potencia campo / intensidad | Cota respecto a referencia y controles | Todos los criterios L2 |', '|---:|---:|---:|---:|---|']
        for row in aa['rows']:
            lines.append(f"| {row['N']} | {fmt(row['field_relative_error'])} | {fmt(row['power_errors']['field'])} / {fmt(row['power_errors']['intensity'])} | {fmt(row['combined_reference_relative_indicator'])} | {row['pass_']} |")
        lines += ['', f"Resultado L2: {aa['L2_accuracy_pass']}. Sus 32 checkpoints nuevos y criterios fueron recalculados por un auditor separado. La cota se refiere a la solución discretizada calculada; la concordancia de referencias es empírica y no certifica su error exacto.", '', 'El control sintético de la cota pasó, con una incidencia de versionado conservada: código y contrato se escribieron antes del cálculo, pero el primer commit falló y el commit válido fue posterior. Esa incidencia auxiliar no afecta a los contratos ópticos L1/L2 congelados antes de sus trayectorias.', '']
    report=out/'evaluacion_T96_Q4.md';report.write_text('\n'.join(lines),encoding='utf-8')
    records=[]
    for r in e['independent_measurements']:
        records.append(dict(estudio='E',N=r['N'],dx_um=128/r['N'],dz_adi_um=r['dz_m']*1e6,segmentos_exponencial='',detector='celda_constante',P_nucleo_entrada=r['P_core'],P_total_entrada=r['P_total'],campo_sha256=r['final_npz_sha256']))
    for r in g['rows']:
        for m,v in r['methods'].items():records.append(dict(estudio='G2',N=r['N'],dx_um=128/r['N'],dz_adi_um=r['dz_m']*1e6,segmentos_exponencial='',detector='cubico_'+m,P_nucleo_entrada=v['P_core'],P_total_entrada=r['P_total'],campo_sha256=r['field_sha256']))
    for r in h['rows']:
        for part,vals in r['methods'].items():
            sol=r['solutions'][part];cp=read(sol['checkpoints'][-1]['path'])
            for m,v in vals.items():records.append(dict(estudio='H2',N=r['N'],dx_um=128/r['N'],dz_adi_um='',segmentos_exponencial=part,detector='cubico_'+m,P_nucleo_entrada=v['P_core'],P_total_entrada=cp['raw_total']/r['P_in'],campo_sha256=sol['field_sha256']))
    krows=kp['rows']+([k['rows'][0]] if k else [])
    for r in krows:
        n=r['N'];hr=next(v for v in h['rows'] if v['N']==n);part=str(hr['fine_segments']);vals=r['methods'][part] if n==640 else r['methods']
        for m,v in vals.items():records.append(dict(estudio='K',N=n,dx_um=128/n,dz_adi_um='',segmentos_exponencial=part,detector='bilineal_'+m,P_nucleo_entrada=v['P_core'],P_total_entrada=hr['P_total'],campo_sha256=hr['solutions'][part]['field_sha256']))
    if pa:
        for part,vals in pa['methods'].items():
            sol=pe['solutions'][part];cp=read(sol['checkpoints'][-1]['path'])
            for m,v in vals.items():records.append(dict(estudio='K626',N=626,dx_um=128/626,dz_adi_um='',segmentos_exponencial=part,detector='bilineal_'+m,P_nucleo_entrada=v['P_core'],P_total_entrada=cp['raw_total']/pa['P_in'],campo_sha256=sol['field_sha256']))
    if la:
        for row,sol in zip(la['rows'],le['solutions'],strict=True):
            cp=read(sol['checkpoints'][-1]['path'])
            for method,v in row['methods'].items():records.append(dict(estudio='L1_FDST',N=626,dx_um=128/626,dz_adi_um=row['dz_m']*1e6,segmentos_exponencial='',detector='bilineal_'+method,P_nucleo_entrada=v['P_core'],P_total_entrada=row['raw_total']/pa['P_in'],campo_sha256=cp['field_sha256']))
    if aa:
        row=aa['rows'][0];cp=read(ae['checkpoints'][-1]['path'])
        for method,value in row['methods'].items():records.append(dict(estudio='L2_FDST',N=400,dx_um=128/400,dz_adi_um=.002/12800*1e6,segmentos_exponencial='',detector='bilineal_'+method,P_nucleo_entrada=value['P_core'],P_total_entrada=aa['P_total'],campo_sha256=cp['field_sha256']))
    csvpath=out/'potencias_T96_Q4.csv'
    for record in records:
        record['paso_longitudinal_um']=record.pop('dz_adi_um')
        record['integrador']='FDST' if record['estudio'] in ('L1_FDST','L2_FDST') else 'ADI' if record['estudio'] in ('E','G2') else 'Exponencial Taylor'
    with csvpath.open('x',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    files=[epath/'assessment.json',gpath/'assessment.json',gpath/'execution.json',gpath/'integrity_audit.json',hpath/'assessment.json',hpath/'execution.json',hpath/'integrity_audit.json',hpath/'manifest.json',ROOT/'resultados/codex/point03_exponential_20261007_H1/execution.json',ROOT/'resultados/codex/point03_exponential_20261007_H1/prediction.json',kpredpath]
    files += [p for p in (kpath,jpath) if p.exists()]
    files += [ROOT/'resultados/codex/point03_exponential_partition_diagnostic_20261007.json']
    if pa:files += [probe/name for name in ('execution.json','assessment.json','integrity_audit.json','manifest.json','geometry_report.json','geometry_selection.json','geometry_generator_source.txt')]
    files += [ROOT/'scripts'/name for name in ('run_point03_exponential.py','recover_point03_h.py','assess_point03_h_recovered.py','point03_linear_detector.py','predict_point03_linear.py','assess_point03_linear.py','run_point03_k626.py','point03_scatter_uncertainty.py','diagnose_point03_scatter.py')]
    files += [ROOT/'resultados/codex'/name for name in ('point03_linear_detector_preflight_20261007.json','point03_scatter_uncertainty_preflight_20261007_attempt1.json','point03_scatter_uncertainty_preflight_20261007_run2.json')]
    files += [ROOT/'Docs'/name for name in ('POINT-03-ANALYTIC-PROPAGATION-RESULTS.md','POINT-03-G-RESULTS.md','POINT-03-EXPONENTIAL-REFERENCE-CONTRACT.md','POINT-03-H-RECOVERY-CONTRACT.md','POINT-03-LINEAR-DETECTOR-CONTRACT.md','POINT-03-SCATTER-DIAGNOSTIC-CONTRACT.md','POINT-03-INTERFACE-LITERATURE.md','POINT-03-EXPONENTIAL-CODE-REVIEW.md','POINT-03-EXPONENTIAL-PARTITION-RESULTS.md')]
    if la:
        files += [pilot/name for name in ('execution.json','assessment.json','manifest.json','integrity_audit.json')]
        files += [Path(link['path']) for sol in le['solutions'] for link in sol['checkpoints']]
        files += [ROOT/'scripts'/name for name in ('point03_fdst.py','run_point03_fdst_pilot.py','audit_point03_fdst_pilot.py')]
        files += [ROOT/'Docs'/name for name in ('POINT-03-FDST-KERNEL-CONTRACT.md','POINT-03-FDST-PILOT-CONTRACT.md','POINT-03-FDST-LITERATURE.md','POINT-03-K626-RESULTS.md')]
        files += [ROOT/'resultados/codex'/name for name in ('point03_fdst_preflight_attempt1_20261007.json','point03_fdst_manufactured_timing_20261007.json','point03_fdst_manufactured_timing_metadata_audit_20261007.json')]
        files += [ROOT/'resultados/codex'/name for name in ('point03_fdst_scale_diagnostic_20261007.json','point03_fdst_scale_fine_20261007.json')]
        files += [ROOT/'scripts'/name for name in ('diagnose_point03_fdst_scale.py','diagnose_point03_fdst_scale_fine.py')]
        files += [ROOT/'Docs'/name for name in ('POINT-03-FDST-NUMERICAL-SCALE.md','POINT-03-FDST-SCALE-DIAGNOSTIC-CONTRACT.md','POINT-03-FDST-SCALE-DIAGNOSTIC-RESULTS.md','POINT-03-FDST-SCALE-FINE-CONTRACT.md','POINT-03-FDST-SCALE-FINE-RESULTS.md')]
        files += [ROOT/'resultados/codex/point03_fdst_dense_oracle_audit_20261007.json',ROOT/'scripts/audit_point03_fdst_dense_oracle.py',ROOT/'Docs/POINT-03-FDST-DENSE-ORACLE-CONTRACT.md',ROOT/'Docs/POINT-03-FDST-DENSE-ORACLE-RESULTS.md']
    if la:files += [ROOT/'Docs/POINT-03-FDST-PILOT-RESULTS.md']
    if aa:
        files += [accuracy/name for name in ('execution.json','assessment.json','manifest.json','integrity_audit.json','worker_source.txt')]
        files += [Path(link['path']) for link in ae['checkpoints']]
        files += [ROOT/'scripts'/name for name in ('run_point03_fdst_accuracy.py','audit_point03_fdst_accuracy.py','verify_point03_detector_bound.py')]
        files += [ROOT/'Docs'/name for name in ('POINT-03-FDST-ACCURACY-CONTRACT.md','POINT-03-FDST-ACCURACY-AUDIT-CONTRACT.md','POINT-03-FDST-ACCURACY-RESULTS.md','POINT-03-DETECTOR-BOUND-CONTRACT.md','POINT-03-DETECTOR-BOUND-RESULTS.md')]
        files += [ROOT/'resultados/codex'/name for name in ('point03_detector_bound_20261007.json','point03_detector_bound_provenance_note_20261007.json','point03_fdst400_timing_20261007.json','point03_fdst640_timing_20261007.json')]
    manifest={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in files};(out/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    archive=out/'evidencias_T96_Q4.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,str(p.relative_to(ROOT)).replace('\\','/'))
        z.write(out/'SHA256.json','SHA256.json')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name,d in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==d
    visible.mkdir(parents=True,exist_ok=True)
    for p in (report,archive,csvpath):
        target=visible/p.name;assert not target.exists();shutil.copyfile(p,target);assert sha(target)==sha(p)
    result=dict(created_utc=datetime.now(timezone.utc).isoformat(),point03_closed=closed,files={str(visible/p.name):sha(p) for p in (report,archive,csvpath)},csv_rows=len(records),archive_reports=len(files),zip_crc_and_sha_verified=True)
    (out/'export.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result));return result

def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--visible',type=Path,required=True);p.add_argument('--probe',type=Path);p.add_argument('--pilot',type=Path);p.add_argument('--accuracy',type=Path);args=p.parse_args();export(args.out,args.visible,args.probe,args.pilot,args.accuracy)
if __name__=='__main__':main()
