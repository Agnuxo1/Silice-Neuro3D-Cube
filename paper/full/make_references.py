"""Build the bibliography of the full paper from identifier-checked metadata.

Input: paper/full/references_crossref.json (Crossref /works records and arXiv API
records of every cited work, fetched on 2026-10-13) and paper/full/paper.tex.
Output: paper/full/references.tex, a thebibliography ordered by first citation.
Only works whose identifiers are verified in the repository
(resultados/agent/t26_sota_20261012/verification.json,
resultados/agent/t24_energy_20261012/sources_verification.json), already cited in
paper/manuscript.tex, or the two added classics (Reck 1994, Saygin 2020) appear.

  python -B paper/full/make_references.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Corrections of markup or name parsing in the deposited metadata (content unchanged).
TITLE = {
    "Caragiulo2021": r"A 2$\times$ time-interleaved 28-GS/s 8-bit 0.03-mm$^2$ switched-capacitor DAC in 16-nm FinFET CMOS",
    "Levy2024": r"8-$\lambda$ $\times$ 50 Gbps/$\lambda$ heterogeneously integrated Si-Ph DWDM transmitter",
    "LiuGe2025": r"Near-infrared germanium PIN-photodiodes with $>$1\,A/W responsivity",
    "Garrod2014": r"50\,\% continuous-wave wallplug efficiency from 1.53\,$\mu$m-emitting broad-area diode lasers",
    "Mori2026": r"A 3 nm FinFET 125 TOPS/W-29 TFLOPS/W, 90 TOPS/mm$^2$-17 TFLOPS/mm$^2$ SRAM-based INT8, and FP16 digital-CIM compiler with support for multi-weight update/cycle",
    "Horowitz2014": r"Computing's energy problem (and what we can do about it)",
    "Hao2023": r"A single-channel 2.6GS/s 10b dynamic pipelined ADC with time-assisted residue generation scheme achieving intrinsic PVT robustness",
    "Nazemi2015": r"A 36Gb/s PAM4 transmitter using an 8b 18GS/S DAC in 28nm CMOS",
    "Lin2018": r"A 40Gb/s optical NRZ transmitter based on monolithic microring modulators in 45nm SOI CMOS",
    "WangKuo2023": r"A 3mW 2.7GS/s 8b subranging ADC with multiple-reference-embedded comparators",
}
AUTHORS = {
    "Clements2016": {"Walsmley": "Walmsley"},
    "DiMicco2026": {"Micco": "Di Micco", "Salles": "Carvalho de Salles", "Giano": "Di Giano"},
}
GIVEN = {"DiMicco2026": {"Di Micco": "Simone", "Carvalho de Salles": "Daniel", "Di Giano": "Niki"}}
NOTES = {
    "Zhou2025": "Full text not read in this study (see Sec.~\\ref{sec:t26}).",
    "Djogo2026": "Preprint: arXiv:2512.01972.",
    "Garrod2014": "Multimode laser; value recorded but not used (Sec.~\\ref{sec:t24}).",
    "Kanold2024": "Multimode laser; value recorded but not used (Sec.~\\ref{sec:t24}).",
}
MAX_AUTHORS = 12
SHOWN_IF_LONG = 10


def latex_text(text: str) -> str:
    text = text.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<")
    for a, b in (("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_")):
        text = text.replace(a, b)
    return text


def initials(given: str) -> str:
    parts = []
    for word in re.split(r"\s+", given.strip()):
        if not word:
            continue
        pieces = [p for p in word.split("-") if p]
        parts.append("-".join(p[0] + "." for p in pieces))
    return "~".join(parts)


def authors(key: str, entry: dict) -> str:
    fix, gfix = AUTHORS.get(key, {}), GIVEN.get(key, {})
    names = []
    for given, family in entry["authors"]:
        family = fix.get(family, family)
        given = gfix.get(family, given)
        names.append((initials(given) + "~" if given else "") + latex_text(family))
    if len(names) > MAX_AUTHORS:
        return ", ".join(names[:SHOWN_IF_LONG]) + ", \\emph{et al.}"
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return names[0] + " and " + names[1]
    return ", ".join(names[:-1]) + ", and " + names[-1]


def bibitem(key: str, entry: dict) -> str:
    title = TITLE.get(key, latex_text(entry["title"]))
    head = authors(key, entry) + ", ``" + title + ",'' "
    if entry["type"] == "arxiv":
        body = "arXiv:%s (%d)." % (entry["arxiv"], entry["year"])
        link = r" \href{https://arxiv.org/abs/%s}{arxiv.org/abs/%s}" % (entry["arxiv"], entry["arxiv"])
        return "\\bibitem{%s} %s%s%s" % (key, head, body, link)
    container = latex_text(entry["container"]).replace("Solid- State", "Solid-State")
    number = entry.get("article_number")
    page = (entry.get("page") or "").replace("-", "--")
    if entry["type"] == "proceedings-article":
        body = "in \\emph{%s}" % container
        if page:
            body += ", pp.~" + page
        body += " (%d)." % entry["year"]
    else:
        body = "\\emph{%s}" % container
        if entry.get("volume"):
            body += " \\textbf{%s}" % entry["volume"]
            if entry.get("issue"):
                body += "(%s)" % entry["issue"]
        loc = number or page
        if loc:
            body += ", " + loc
        body += " (%d)." % entry["year"]
    doi = entry["doi"]
    link = r" \href{https://doi.org/%s}{doi:%s}" % (doi, latex_text(doi))
    note = (" " + NOTES[key]) if key in NOTES else ""
    return "\\bibitem{%s} %s%s%s%s" % (key, head, body, link, note)


def main() -> None:
    meta = json.loads((HERE / "references_crossref.json").read_text(encoding="utf-8"))
    tex = (HERE / "paper.tex").read_text(encoding="utf-8")
    body = tex.split("\\begin{document}", 1)[1]
    order = []
    for group in re.findall(r"\\cite[pt]?\*?(?:\[[^\]]*\])?\{([^}]*)\}", body):
        for key in (k.strip() for k in group.split(",")):
            if key and key not in order:
                order.append(key)
    missing = [k for k in order if k not in meta]
    if missing:
        raise SystemExit("Cited keys without verified metadata: " + ", ".join(missing))
    unused = sorted(set(meta) - set(order))
    lines = ["% Generated by make_references.py from references_crossref.json; do not edit by hand.",
             "\\begin{thebibliography}{%d}" % len(order), "\\small", "\\setlength{\\itemsep}{1pt}"]
    lines += [bibitem(k, meta[k]) for k in order]
    lines.append("\\end{thebibliography}")
    (HERE / "references.tex").write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    print("cited:", len(order), "unused metadata:", unused)


if __name__ == "__main__":
    main()
