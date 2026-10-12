# Manuscript

`manuscript.tex` is the English manuscript of the 2026-10-12 scientific closure. Build (MiKTeX or TeX Live, two passes):

```bash
cd paper && pdflatex -interaction=nonstopmode manuscript.tex && pdflatex -interaction=nonstopmode manuscript.tex
```

Figures are copied from `resultados/agent/` by `paper/make_figures.py`, which also draws the T24 and T27 figures from their committed JSON results. Every number in the manuscript is traceable to a hashed file listed in `Docs/CIERRE-20261012/CLAIMS-LEDGER-20261012-final.json`.

The manuscript reports numerical models, registered kill tests and retained negative results. It does not report a fabricated device or a measurement.
