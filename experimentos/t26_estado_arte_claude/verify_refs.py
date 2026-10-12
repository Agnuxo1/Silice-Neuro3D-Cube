"""Verify bibliographic records against Crossref and arXiv (T26, guide v2 section 46).

Input: a JSON file {"records": [{"id", "title", "year", "doi"?, "arxiv"?, ...}]}.
For each record with a DOI the Crossref work is fetched; with an arXiv id the
arXiv Atom entry is fetched. A record is VERIFIED when at least one identifier
resolves, the normalized title similarity is >= 0.85 and the year differs by
at most one (online-first versus issue year). Nothing is inferred from the
record's own claims: only identifiers, titles and years are checked here.
Extracted numbers (losses, wavelengths) must be checked against the text by a
person; this script records that it did not do so.

No credentials or personal data are sent. Output paths must be new.
"""
from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

AGENT = "Silice-Neuro3D-Cube-T26-verifier/1.0 (https://github.com/Agnuxo1/Silice-Neuro3D-Cube)"


def normalize(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return " ".join(text.split())


def fetch(url: str, attempts: int = 3) -> tuple[int, bytes]:
    for attempt in range(attempts):
        request = urllib.request.Request(url, headers={"User-Agent": AGENT})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return 404, b""
            if attempt == attempts - 1:
                return error.code, b""
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts - 1:
                return 0, b""
        time.sleep(2 * (attempt + 1))
    return 0, b""


def crossref(doi: str) -> dict:
    status, body = fetch("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
    if status != 200:
        return {"resolved": False, "http_status": status}
    message = json.loads(body)["message"]
    parts = (message.get("published-print") or message.get("published-online")
             or message.get("issued") or {}).get("date-parts", [[None]])
    return {"resolved": True, "http_status": status,
            "title": " ".join(message.get("title") or []),
            "year": parts[0][0],
            "container": " ".join(message.get("container-title") or []),
            "volume": message.get("volume"), "page": message.get("page"),
            "authors": [a.get("family", "") for a in message.get("author", [])][:6]}


def arxiv(identifier: str) -> dict:
    status, body = fetch("http://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(identifier))
    if status != 200:
        return {"resolved": False, "http_status": status}
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entry = ET.fromstring(body).find("a:entry", ns)
    if entry is None or entry.find("a:title", ns) is None:
        return {"resolved": False, "http_status": status}
    published = entry.findtext("a:published", default="", namespaces=ns)
    return {"resolved": True, "http_status": status,
            "title": " ".join(entry.findtext("a:title", namespaces=ns).split()),
            "year": int(published[:4]) if published[:4].isdigit() else None}


def verify(records: list[dict]) -> dict:
    out = []
    for record in records:
        checks = {}
        if record.get("doi"):
            checks["crossref"] = crossref(record["doi"].strip())
            time.sleep(0.5)
        if record.get("arxiv"):
            checks["arxiv"] = arxiv(record["arxiv"].strip())
            time.sleep(3.0)
        verdicts = []
        for source, found in checks.items():
            if not found.get("resolved"):
                continue
            similarity = difflib.SequenceMatcher(
                None, normalize(record.get("title", "")), normalize(found.get("title", ""))).ratio()
            year_ok = (found.get("year") is not None and record.get("year") is not None
                       and abs(int(found["year"]) - int(record["year"])) <= 1)
            found["title_similarity"] = round(similarity, 4)
            found["year_matches"] = year_ok
            verdicts.append(similarity >= 0.85 and year_ok)
        out.append({"id": record.get("id"), "doi": record.get("doi"), "arxiv": record.get("arxiv"),
                    "verified": bool(verdicts) and all(verdicts), "checks": checks})
    return {"records": out, "n_records": len(out),
            "n_verified": sum(r["verified"] for r in out),
            "all_identifiers_verified": all(r["verified"] for r in out) and bool(out),
            "numbers_checked_by_script": False,
            "note": "Identifier, title and year only; extracted values need text verification."}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Output path must be new")
    records = json.loads(args.records.read_text(encoding="utf-8"))["records"]
    result = verify(records)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("n_records", "n_verified", "all_identifiers_verified")}))


if __name__ == "__main__":
    main()
