# VERIFICACION V2 - Grupo G (acoplador) y prefactor de T8

Verificador independiente y adversarial. Modelo numerico escalar; no es dispositivo ni medida.
Fecha de ejecucion: 2026-10-10, 04:13 a 04:50 UTC. Plan previo con umbrales: `v2_contrato_previo.md`.
Todo en CPU, un hilo, `python -B`. No se ha tocado nada fuera de esta carpeta. Los codigos propios no importan el solver ni el BPM de G (solo `v_reproduce_solver2d.py` los importa, para reproducir sus cifras).

## Resumen

| # | Paso pedido | Veredicto | Evidencia clave |
|---|---|---|---|
| 1 | Contratos y JSON leidos | PASA | G1/G2 coinciden con el log; hashes SHA256 de solver2d, analitico y acoplo_paralelo iguales a los registrados en el JSON |
| 2 | Preregistro (ls -l --time-style=full-iso) | PASA con una anomalia documental | contrato 06:01:37+02 (04:01:37 UTC) < g1_g2_modal.py 06:01:55 < arranque 04:02:00 UTC; ver seccion 2 |
| 3 | kappa_FD con otra malla / s_sub; cociente independiente de la malla | PASA | FD propio: cociente 0,9976 a 1,0011 en 18 configuraciones; rango en h: 1,5e-4 a 1,5e-3 |
| 4 | kappa del modelo con integral propia | PASA | dblquad propio coincide con `acoplo_paralelo.kappa` a 1e-13 relativo; rejilla cartesiana a 3,7e-5 |
| 5 | Longitud de transferencia del BPM con otro dz | PASA (L_c, kappa) y RIESGO (perdida) | z_max dentro de 0,94 % de L_c; kappa ajustado a 0,13 % (d=14); perdida a z_max 1,2e-3 y 2,0e-3 con dz = 1 |
| 6 | H-T8-1 (P2 = 0,141 a 20 um y 10 mm) | PASA (refutada en el modelo, confirmada) | sin^2(kappa L) = 0,1411; BPM propio 0,1404; d critico 20,43 um |
| - | Resultados G3 del propio grupo G | NO COMPROBABLE | `resultados_g3_bpm.json` no existe a las 04:47 UTC; solo hay el script `g3_bpm_p2.py` |

## 1. Lectura y hashes

- `resultados_g1_g2.json`: arranque 04:02:00 UTC, fin 04:02:55 UTC. Todos los G1.1 a G1.5 y G2.1 con pass = true.
- SHA256 actuales = registrados: solver2d.py 5d5cba11..., analitico_lp01.py 5a0a377b..., acoplo_paralelo.py 907cfd9e.... Los ficheros no cambiaron tras la ejecucion.
- Reproduccion exacta con `solver2d.solve` (`v_reproduce_solver2d.py`): d = 14, h = 0,125, s_sub = 8 da kappa_FD = 4,7163941832e-4 /um (identico al JSON); d = 20 da 3,851257119356e-5 /um (identico).

## 2. Preregistro

```
CONTRATO-acoplador.md  2026-10-10 06:01:37.74 +0200  (04:01:37 UTC)
g1_g2_modal.py         06:01:55.10
g3_bpm_p2.py           06:02:27.24
log_g1_g2.txt / resultados_g1_g2.json  06:02:55.2
```
- El contrato precede al codigo (18 s) y a los resultados (78 s). Los umbrales G1.1 a G3.4 estan en el contrato antes de la primera cifra. PASA.
- Anomalia documental: la Enmienda E-1 dice "2026-10-10 04:12 UTC, antes de cualquier cifra", pero el fichero que la contiene tiene fecha de modificacion 04:01:37 UTC, y el log de G1/G2 arranca a las 04:02:00 UTC. Una hora de las 04:12 es imposible (posterior a los resultados que dice preceder). El contenido de la enmienda si se aplico antes de ejecutar (G1.5 se evaluo con L = 40,4 um, N = 405 como dice la enmienda). Es un error de hora escrita, no una modificacion de umbrales; no puedo demostrarlo mas alla de las fechas de ficheros (no hay hash del contrato).
- Segunda anomalia (documental): `CONTRATO-ACOPLO.md` define I(d) = integral 2 psi1 psi2 dA (factor 2), pero el codigo y `RESULTADOS-ACOPLO.md` usan sin factor 2. Ver seccion 4: el factor 2 del texto es erroneo; el codigo es correcto.

## 3. kappa_FD con otra malla: el cociente no depende de la malla

FD propio (`v_fd_propio.py`: promediado subpixel propio, eigsh propio, sin importar solver2d), L = 40 um de semilado, cociente = kappa_FD / kappa_modelo, con kappa_modelo del punto 4:

| d (um) | h=0,2 s=16 | h=0,15 s=16 | h=0,1 s=16 | h=0,2 s=4 | h=0,2 s=1 (escalonado) |
|---|---|---|---|---|---|
| 14 | 1,00072 | 1,00058 | 1,00062 | 1,00102 | 0,99755 |
| 16 | 0,99996 | 0,99983 | 0,99967 | 1,00021 | 0,99790 |
| 20 | 1,00088 | 1,00041 | 1,00020 | 1,00106 | 1,00025 |

- G (solver2d h = 0,125, s = 8): 1,00081 / 0,99987 / 1,00043. Coincide con mi barrido.
- h = 0,15 coloca d/2 fuera de nodo (7/0,15 = 46,67 nodos): el cociente no cambia. Umbral R2 (variacion < 0,005): maxima variacion entre mallas con s = 16: 0,0013 (d = 14: 1,00072 a 1,00058; d = 20: 1,00088 a 1,00020). PASA.
- Sin submuestreo (s = 1, escalonado) el cociente baja hasta 0,9976; sigue dentro de 0,25 %.
- La malla h = 0,2 con s = 16 de solver2d (cociente 4,715966e-4 /um) y la del FD propio coinciden en todos los digitos (8 cifras): los dos codigos discretizan igual el mismo problema, por lo que esta comparacion prueba coherencia de implementacion mas que independencia de metodo; el contraste independiente de metodo es FD frente a la integral analitica del punto 4.
- Caso de diseno defectuoso mio (no usado como evidencia): desplazar los dos nucleos 0,07 um en x rompe la simetria especular (error de paridad 2,2e-2 en el modo par); el cociente sigue en 1,0007 / 0,9999 / 1,0008 porque kappa es invariante a la traslacion.
- Conclusion: el cociente medio es 1,0004 (0,9997 a 1,0011 con s >= 4); la diferencia con 1 es de orden 1e-3, 100 veces menor que el umbral de G2.1 (10 %). No distingue entre mallas.

## 4. kappa del modelo con integral propia

`v_kappa_modelo.py`: LP01 de salto con raiz propia (brentq, 4000 puntos de escaneo, un unico cero; U = 1,7568771017, W = 2,3325353271, beta = 5,846168145 /um, n_eff = 1,44219216546), norma por cuadratura numerica (448,1109), integral sobre el nucleo 2 en polares (dblquad) y en rejilla cartesiana (0,02 y 0,01 um).

| d | kappa propio (dblquad) /um | kappa `acoplo_paralelo` /um | dif. relativa | rejilla 0,01 um |
|---|---|---|---|---|
| 14 | 4,7125839031e-4 | 4,7125839031e-4 | 2,0e-13 | 3,7e-5 |
| 16 | 2,0308102496e-4 | 2,0308102496e-4 | 9,8e-14 | 3,7e-5 |
| 20 | 3,8495830330e-5 | 3,8495830330e-5 | 1,0e-13 | 3,7e-5 |

PASA (umbral R3: 1e-4). Con el factor 2 literal de `CONTRATO-ACOPLO.md` habria kappa = 9,425e-4 /um (d = 14), cociente FD/kappa = 0,5004, que el FD refuta. El prefactor del codigo, (k0^2/2beta)(n1^2 - n2^2) por la integral sin factor 2, queda confirmado por un metodo (supermodos por diferencias finitas) que no lo usa.

## 5. Longitud de transferencia del BPM con otros dz

BPM propio (`v_bpm_propio.py`, split-step Strang con Fourier, n_ref = n1, CAP cuadratico 28 um al borde con 0,5 /um, malla h = 0,2, N = 405, modos de un nucleo por FD propio). kappa_FD de G1 (h = 0,125): d = 14: 4,716394e-4 (L_c = 3330,50 um); d = 16: 2,030540e-4 (L_c = 7735,86 um).

| d | dz (um) | z_max (um) | dev. vs L_c | P2 max | perdida a z_max | kappa ajustado / kappa_FD - 1 |
|---|---|---|---|---|---|---|
| 14 | 10 | 3336,4 | 0,18 % | 0,921 | 7,6e-2 | +1,59 % |
| 14 | 5 | 3351,8 | 0,64 % | 0,976 | 2,3e-2 | +0,61 % |
| 14 | 2 | 3358,4 | 0,84 % | 0,988 | 1,0e-2 | +0,33 % |
| 14 | 1 | 3361,7 | 0,94 % | 0,9972 | 1,24e-3 | +0,13 % |
| 14 | 0,5 | 3362,0 | 0,95 % | 0,9979 | 5,5e-4 | +0,12 % |
| 16 | 5 | 7621,7 | 1,48 % | 0,952 | 4,7e-2 | +1,17 % |
| 16 | 1 | 7670,7 | 0,84 % | 0,9970 | 2,03e-3 | -0,03 % |

- z_max dentro de 1 % de L_c para dz <= 5 (umbral G3.1 del contrato: 10 %); sensibilidad a dz entre 1 y 0,5 um: 3361,73 frente a 3362,00 (0,008 %, umbral G3.4: 1 %). R4 (kappa dentro de 2 %, z_max dentro de 5 %, dz dentro de 1 %): PASA para dz <= 2. Para dz = 10 el kappa deja de cumplir R4 (1,6 % cumple, pero la perdida del 7,6 % invalida P2).
- P2 max >= 0,90 (G3.2): mis valores a dz = 1 son 0,997.
- RIESGO para G3.3 (perdida <= 1e-3 en z_max): con dz = 1 mi BPM pierde 1,24e-3 (d = 14) y 2,03e-3 (d = 16), por encima del umbral. La perdida crece con dz (por z: dz = 0,5: 5,1e-4 a 3 mm; dz = 2: 8,9e-3; dz = 5: 2,0e-2; dz = 10: 6,9e-2), por lo que es un artefacto numerico del split-step y del CAP, no fisica. Coherente con el C5 de `bpm_claude` (2,46e-4 por mm, umbral 1e-5, ya FALLA). Prediccion mia, no comprobada contra G: G3.3 de G fallara o quedara en el limite para d = 14 y fallara para d = 16 y 20 si usa dz = 1 y el mismo CAP. Lo que si concluyo: G3.3 no es un criterio robusto del BPM de partida.
- El pequeno exceso de z_max sobre L_c (+0,8 a +0,9 %) es consistente con la absorcion del CAP (atenua el campo) mas la diferencia paraxial; no cambia ningun veredicto.

## 6. H-T8-1

- sin^2(kappa_FD * 1e4 um) con kappa_FD(20) = 3,851257e-5 /um: 0,14113. Con el kappa del modelo: 0,14102. Con los cocientes extremos de mi barrido de mallas (0,9975 a 1,0009): 0,1403 a 0,1413.
- BPM propio, d = 20, dz = 1, 10 mm: P2 = 0,1404 (perdida total 0,26 %). Con dz = 5: 0,1318 (perdida 5,9 %); P2/P_total = 0,1402. Con dz = 10: 0,1127 (perdida 19,8 %, no fiable). Con dz = 1 el BPM coincide con 0,141.
- kappa critico para P2 = 0,10: arcsin(sqrt(0,10))/1e4 um = 3,2175e-5 /um (0,03218 /mm). kappa_modelo(20) lo supera un 19,6 % (FD 19,7 %). Un error de prefactor de 20 % haria falta para rescatar la hipotesis; los cocientes medidos son 1,000 +- 0,003.
- Separacion minima para P2 <= 0,10 a 10 mm: d = 20,43 um (modelo, raiz de kappa(d) = kappa critico).
- Veredicto: H-T8-1 refutada en el modelo. G4 de G ("no rescatada") es correcto. Con el contraste FD y con el BPM, P2(20 um, 10 mm) = 0,140 a 0,141, no 0,10.

## 7. Riesgos no cubiertos por los criterios

1. G3 no existe aun. Los criterios G3.1 a G3.4 y G4 con BPM del grupo G no son verificables; solo tengo mi BPM como contraste.
2. G3.3 (perdida <= 1e-3) depende de dz y del CAP, como se ve arriba; riesgo alto de fallo con dz = 1.
3. Umbral G2.1 (10 %) es 100 veces mas laxo que lo observado (0,04 a 0,09 %); no hay riesgo, pero el umbral no discrimina entre errores de prefactor menores que 10 %. El factor 2 si se discrimina (0,50).
4. Solo guias identicas, de salto, escalares, d = 14, 16, 20 um y dn = 0,005. Nada sobre trincheras fs (anisotropia), dn = -0,003, polarizacion, curvas, cruces ni acoplo vertical 3D. Los resultados son prediccion de un modelo, no medida.
5. P2 = sin^2(kappa L) supone fase igualada, acoplo de primer orden y sin perdidas. El BPM da kappa dentro de 0,1 a 1,5 % y L_c dentro de 1 %; no se ha comparado en regimen de acoplo fuerte (d < 14 um).
6. Hora de la Enmienda E-1 imposible (04:12 UTC frente a 04:01 UTC de modificacion del fichero); contrato sin hash. Texto del factor 2 en `CONTRATO-ACOPLO.md` no corregido (se debe anotar, no cambiar umbrales).
7. Sensibilidad de kappa de 0,1 % a la malla es pequena frente al efecto de la tolerancia geometrica real: dkappa/kappa ~ -0,41 por um de separacion (d = 20): 0,44 um de error de separacion cambia P2 de 0,141 a 0,10.
8. El FD propio y solver2d comparten esquema (5 puntos, promediado de n^2 por celda). Un fallo comun del esquema no se detectaria; la integral analitica independiente del punto 4 reduce el riesgo (coinciden a 1e-3).

## Ficheros

`v_kappa_modelo.py/.json`, `v_fd_propio.py/.json`, `v_reproduce_solver2d.py/.json`, `v_bpm_propio.py`, `v_bpm_propio_*.json`, `v_curva_*.npz`, logs `log_*.txt`, plan `v2_contrato_previo.md`.
