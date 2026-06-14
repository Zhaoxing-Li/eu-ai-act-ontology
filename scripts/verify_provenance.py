"""Provenance + hallucination back-check.

(a) Every modelled euai class / practice / domain / obligation / risk level must
    carry an article OR annex reference.
(b) Every euai:legalTextSnippet must still occur verbatim in the segmented source
    text (data/ai-act-segments.json). A snippet that does not match is a potential
    hallucination and is reported.

Exit non-zero if any check fails.
"""
import json
import re
import sys
from pathlib import Path

import rdflib
from rdflib import RDF, RDFS, OWL, URIRef

ROOT = Path(__file__).resolve().parents[1]
TTL = ROOT / "ontology" / "eu-ai-act-ontology.ttl"
SEGMENTS = json.loads((ROOT / "data" / "ai-act-segments.json").read_text(encoding="utf-8"))
BASE = "https://zhaoxing-li.github.io/eu-ai-act-ontology#"
EUAI = rdflib.Namespace(BASE)

# One big normalised corpus to test snippet membership against.
CORPUS = re.sub(r"\s+", " ", " ".join(s["text"] for s in SEGMENTS))


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    g = rdflib.Graph(); g.parse(TTL, format="turtle")

    # Entities that should carry a legal reference: euai classes + euai individuals,
    # excluding pure scaffolding (Actor umbrella, RiskLevel/Obligation/AIPractice tops,
    # demo instances, and property declarations).
    SKIP = {"RiskLevel", "Obligation", "AIPractice", "AnnexIIIDomain",
            "CVScreeningTool", "ExamProctoringSystem", "CustomerServiceChatbot"}
    subjects = {s for s in set(g.subjects()) if isinstance(s, URIRef) and str(s).startswith(BASE)}
    props = set(g.subjects(RDF.type, OWL.ObjectProperty)) | set(g.subjects(RDF.type, OWL.AnnotationProperty))
    onto_iri = URIRef(BASE.rstrip("#"))

    missing_ref = []
    checked = 0
    for s in sorted(subjects):
        local = str(s).split("#")[-1]
        if s in props or s == onto_iri or local in SKIP:
            continue
        # must be a class or an individual (has rdf:type)
        if (s, RDF.type, None) not in g:
            continue
        checked += 1
        has_ref = (s, EUAI.hasArticleReference, None) in g or (s, EUAI.hasAnnexReference, None) in g
        if not has_ref:
            missing_ref.append(local)

    # (b) snippet back-check
    bad_snippets = []
    n_snip = 0
    for s, _, lit in g.triples((None, EUAI.legalTextSnippet, None)):
        n_snip += 1
        snip = norm(str(lit))
        # Snippets are truncated to a word boundary; test the leading 80 chars to be robust.
        probe = snip[:80].rsplit(" ", 1)[0]
        if probe and probe not in CORPUS:
            bad_snippets.append((str(s).split("#")[-1], snip[:80]))

    print(f"(a) reference check: {checked} entities checked, {len(missing_ref)} missing a reference")
    if missing_ref:
        print("    MISSING:", missing_ref)
    print(f"(b) snippet back-check: {n_snip} snippets checked, {len(bad_snippets)} not found verbatim")
    if bad_snippets:
        for name, probe in bad_snippets:
            print(f"    UNMATCHED {name}: {probe!r}")

    if missing_ref or bad_snippets:
        print("\nFAIL: provenance issues found.")
        sys.exit(1)
    print("\nPASS: zero missing references, zero unmatched snippets.")


if __name__ == "__main__":
    main()
