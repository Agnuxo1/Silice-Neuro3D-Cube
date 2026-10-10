"""Comprueba la tabla de SK-1310 de Docs/SK1310-FUENTES.md frente a la ficha OHARA.

Valores de la ficha OHARA SK-1310 (tabla de la segunda pagina del PDF SK1310.pdf,
columna 25 C en aire). Se leyeron de la imagen del PDF, no de texto.
Convencion del proyecto: indice en vacio = indice en aire * 1,000277.
Criterio P3c (fijado en CONTRATO-literatura-V5.md): |diferencia| <= 1e-4 en cada longitud de onda.
"""
FACTOR_AIRE_A_VACIO = 1.000277
UMBRAL = 1e-4

# Lambda (um) del proyecto, indice en vacio de Docs/SK1310-FUENTES.md
proyecto_vacio = [
    (0.3650, 1.47516),
    (0.4047, 1.47023),
    (0.4358, 1.46730),
    (0.4861, 1.46374),
    (0.5461, 1.46068),
    (0.5876, 1.45906),
    (0.6563, 1.45697),
]

# Ficha OHARA, 25 C en aire, (lambda nm, indice)
ohara_aire = {
    365.015: 1.47475,  # i
    404.656: 1.46982,  # h
    435.835: 1.46689,  # g
    486.133: 1.46333,  # F
    546.075: 1.46028,  # e
    587.562: 1.45866,  # d
    656.273: 1.45657,  # C
}

print(f"{'lambda_um':>10} {'vacio_proy':>11} {'aire_calc':>11} {'ohara_aire':>11} {'dif':>11} {'veredicto':>10}")
max_abs = 0.0
todos_ok = True
for lam_um, n_vac in proyecto_vacio:
    lam_nm = round(lam_um * 1000, 3)
    # Emparejar con la linea OHARA mas cercana (tolerancia 0,5 nm)
    cercana = min(ohara_aire, key=lambda k: abs(k - lam_nm))
    if abs(cercana - lam_nm) > 0.5:
        print(f"{lam_um:10.4f} sin linea OHARA emparejada")
        todos_ok = False
        continue
    n_aire_calc = n_vac / FACTOR_AIRE_A_VACIO
    n_ohara = ohara_aire[cercana]
    dif = n_aire_calc - n_ohara
    max_abs = max(max_abs, abs(dif))
    ok = abs(dif) <= UMBRAL
    todos_ok = todos_ok and ok
    print(f"{lam_um:10.4f} {n_vac:11.5f} {n_aire_calc:11.6f} {n_ohara:11.5f} {dif:+11.2e} {'CONFIRMADO' if ok else 'REFUTADO':>10}")

print()
print(f"Maxima |diferencia| = {max_abs:.2e} (umbral {UMBRAL:.0e})")
print(f"Todas las longitudes de onda dentro de umbral: {todos_ok}")
