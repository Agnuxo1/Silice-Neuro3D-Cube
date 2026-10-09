# Tamaño del repositorio y archivo de evidencias

Medición del 2026-10-09 sobre `origin/main` (commit `b344dcf`, 187 commits de historial). Esta página fija la política para que el crecimiento no siga sin control. **No se reescribe el historial**: los hashes de evidencia y las referencias a commits del protocolo dependen de él.

## Medición

Se midieron los blobs únicos de todo el historial (`git rev-list --objects --all` con `git cat-file`), no solo el árbol de trabajo.

| Magnitud | Valor |
|---|---|
| Blobs únicos en el historial | 3.109 |
| Tamaño sin comprimir de esos blobs | 947,5 MB |
| Paquete Git comprimido (`size-pack`) | 776,7 MiB |
| Árbol de HEAD en `b344dcf` | 3.309 ficheros, 944,5 MB |
| Blobs mayores de 5 MB | 32 |
| Blobs mayores de 50 MB | 1 (`Silice_M2_R1_20261009.zip`, 69,6 MB) |
| Blobs mayores de 100 MB | 0 |

Por tipo de fichero (historial): **NPZ 751,4 MB en 675 ficheros (79 %)**, ZIP 131,0 MB en 6, JSON 23,0 MB en 1.612, NPY 19,3 MB en 13, GIF 8,6 MB en 16.

Por carpeta: `resultados/` 918,8 MB (97 %), `experimentos/` 12,9 MB, `assets/` 8,6 MB, `coordinacion/` 4,4 MB.

Los ficheros grandes más pesados son ZIP de paquetes de ejecución (M2-R1 69,6 MB; C1 30,4 MB; F1 14,0 MB) y NPZ de entradas de simulación (p. ej. `n767_input.npz`, 23,5 MB).

Referencias de límites: GitHub rechaza ficheros a partir de 100 MiB y recomienda mantener el repositorio por debajo de 1 GB ([documentación](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)). Una release admite assets de menos de 2 GiB cada uno ([documentación](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)). Zenodo admite hasta 50 GB y 100 ficheros por registro ([soporte de Zenodo](https://support.zenodo.org/help/en-gb/1-upload-deposit/80-what-are-the-size-limitations-of-zenodo)).

## Política

1. **Historial anterior: sin cambios.** Ningún fichero del historial se elimina ni se reescribe.
2. **Ficheros nuevos de más de 10 MB no se añaden a Git.** Se publican como asset de una release etiquetada (p. ej. `evidencia-AAAAMMDD`), o en un registro de Zenodo si hay autorización. Si un fichero pasa de 2 GiB, se parte en trozos y se documenta el procedimiento.
3. **Manifiesto en Git.** Cada fichero externo tiene una entrada en un manifiesto versionado con su tamaño, su SHA-256, su URL y el commit que lo genera. La verificación de hash se hace tras descargar.
4. **Guardián en CI.** `tools/repo_size_guard.py` falla si un cambio añade un blob mayor de 10 MB. Se comprobó con un control positivo (el commit `626310e`, que añadió el ZIP de 69,6 MB, falla con código 1) y un control negativo (los commits de esta auditoría, todos menores de 10 MB, pasan).
5. **Git LFS descartado por ahora.** Su cuota gratuita no admite migrar los 776 MiB existentes, y no evita el problema de fondo.

## Pendiente de decisión del titular

- **Subir a Zenodo las evidencias de más de 10 MB ya versionadas** (unos 0,9 GB de NPZ y ZIP). Es una acción externa con registro público y DOI. **No se ha hecho.**
- Si además se quiere reducir el paquete Git, eso exigiría reescribir el historial. Se desaconseja, porque rompe las referencias de hash y de commit de los informes.

## Reproducir la medición

```bash
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' > objetos.txt
python tools/repo_size_guard.py --base b344dcf --head HEAD --limit-mb 10
```

El primer comando lista todos los blobs del historial con su tamaño. El segundo informa de los blobs añadidos entre dos revisiones que superen el límite.
