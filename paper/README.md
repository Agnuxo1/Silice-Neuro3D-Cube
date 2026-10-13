# Manuscript

`manuscript.tex` is the English manuscript of the 2026-10-12 scientific closure. Build (MiKTeX or TeX Live, two passes):

```bash
cd paper && pdflatex -interaction=nonstopmode manuscript.tex && pdflatex -interaction=nonstopmode manuscript.tex
```

Figures are copied from `resultados/agent/` by `paper/make_figures.py`, which also draws the T24 and T27 figures from their committed JSON results. Every number in the manuscript is traceable to a hashed file listed in `Docs/CIERRE-20261012/CLAIMS-LEDGER-20261013-final.json`.

The manuscript reports numerical models, registered kill tests and retained negative results. It does not report a fabricated device or a measurement.

## Full paper (preprint for review)

`full/paper.pdf` (38 pages: 20 of main text, references, and a supplement with parameter tables, protocol hashes, the review objections and the claims table) is the complete version, built from `full/paper.tex` with `full/make_extra_figures.py`, `full/make_tables.py` and `full/make_references.py`. `full/NUMBERS.md` maps every number in the text to its source file. Build it from `paper/full` with two `pdflatex` passes.
