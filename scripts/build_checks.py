"""Reason, materialise, measure and test the ontology.

Steps:
  1. Parse the Turtle and export RDF/XML (.owl).
  2. Run HermiT (via owlready2) -> assert consistency; check the high-risk
     inference expectations.
  3. Materialise inferences (inferred instance types + subclass closure) into
     ontology/eu-ai-act-ontology-reasoned.ttl.
  4. Compute simple metrics -> docs/metrics.tsv.
  5. Run the five competency-question SPARQL files against the reasoned graph
     and write queries/results/cqN.csv.

Run:  JAVA_HOME=... python3 scripts/build_checks.py
"""
import csv
import os
import sys
from pathlib import Path

import rdflib
from rdflib import RDF, RDFS, OWL, URIRef

ROOT = Path(__file__).resolve().parents[1]
TTL = ROOT / "ontology" / "eu-ai-act-ontology.ttl"
OWL_OUT = ROOT / "ontology" / "eu-ai-act-ontology.owl"
REASONED = ROOT / "ontology" / "eu-ai-act-ontology-reasoned.ttl"
QUERIES = ROOT / "queries"
RESULTS = QUERIES / "results"
METRICS = ROOT / "docs" / "metrics.tsv"
BASE = "https://zhaoxing-li.github.io/eu-ai-act-ontology#"
EUAI = rdflib.Namespace(BASE)

EXPECT_HIGH_RISK = {"CVScreeningTool", "ExamProctoringSystem"}
EXPECT_NOT_HIGH_RISK = {"CustomerServiceChatbot"}


def reason_and_materialise():
    import owlready2 as o2
    jh = os.environ.get("JAVA_HOME")
    if jh:
        o2.JAVA_EXE = str(Path(jh) / "bin" / "java")

    g = rdflib.Graph()
    g.parse(TTL, format="turtle")
    g.serialize(OWL_OUT, format="pretty-xml")
    print(f"[1] exported {OWL_OUT.relative_to(ROOT)}  ({len(g)} asserted triples)")

    onto = o2.get_ontology("file://" + str(OWL_OUT.resolve())).load()
    with onto:
        try:
            o2.sync_reasoner_hermit(infer_property_values=False)
        except o2.OwlReadyInconsistentOntologyError:
            print("[2] FAIL: ontology is INCONSISTENT under HermiT")
            sys.exit(1)
    print("[2] HermiT: ontology is CONSISTENT, no unsatisfiable classes")

    # Identify named individuals from the RDF graph: euai-typed subjects that are
    # not themselves classes/properties. (onto.individuals() is unreliable here
    # because the export puns several class IRIs.)
    decls = set(g.subjects(RDF.type, OWL.Class)) | \
        set(g.subjects(RDF.type, OWL.ObjectProperty)) | \
        set(g.subjects(RDF.type, OWL.AnnotationProperty)) | \
        set(g.subjects(RDF.type, OWL.Ontology))
    individuals = {s for s, _, o in g.triples((None, RDF.type, None))
                   if isinstance(s, URIRef) and str(s).startswith(BASE)
                   and isinstance(o, URIRef) and str(o).startswith(BASE)
                   and s not in decls}

    # Collect inferred instance types and add them to the rdflib graph.
    inferred = 0
    got_high = set()
    for s in individuals:
        ent = onto.search_one(iri=str(s))
        if ent is None:
            continue
        for cls in getattr(ent, "is_a", []):
            iri = getattr(cls, "iri", None)
            if not iri or not iri.startswith(BASE):
                continue
            # The directly-inferred class is AnnexIIIHighRiskAISystem (Art 6(2)
            # route), a subclass of HighRiskAISystem.
            if iri.endswith("#HighRiskAISystem") or iri.endswith("#AnnexIIIHighRiskAISystem"):
                got_high.add(str(s).split("#")[-1])
            if (s, RDF.type, URIRef(iri)) not in g:
                g.add((s, RDF.type, URIRef(iri)))
                inferred += 1
    ok_pos = EXPECT_HIGH_RISK <= got_high
    ok_neg = not (EXPECT_NOT_HIGH_RISK & got_high)
    print(f"    inferred high-risk (Annex III route): {sorted(got_high)}")
    assert ok_pos, f"expected {EXPECT_HIGH_RISK} to be high-risk"
    assert ok_neg, f"{EXPECT_NOT_HIGH_RISK} must NOT be high-risk"
    print("    inference expectations: PASS")

    # Materialise rdfs:subClassOf closure on instance types (so plain SPARQL works).
    sub = {}
    for s, _, o in g.triples((None, RDFS.subClassOf, None)):
        if isinstance(o, URIRef):
            sub.setdefault(s, set()).add(o)

    def ancestors(c, seen=None):
        seen = seen or set()
        for p in sub.get(c, ()):
            if p not in seen:
                seen.add(p)
                ancestors(p, seen)
        return seen

    closure_added = 0
    for s, _, c in list(g.triples((None, RDF.type, None))):
        for anc in ancestors(c):
            if anc.startswith(BASE) and (s, RDF.type, anc) not in g:
                g.add((s, RDF.type, anc))
                closure_added += 1

    g.serialize(REASONED, format="turtle")
    print(f"[3] materialised {inferred} inferred + {closure_added} subclass-closure types "
          f"-> {REASONED.relative_to(ROOT)}")
    return g


def metrics(reasoned):
    asserted = rdflib.Graph(); asserted.parse(TTL, format="turtle")
    m = {
        "asserted_triples": len(asserted),
        "reasoned_triples": len(reasoned),
        "owl_classes": len(set(asserted.subjects(RDF.type, OWL.Class))),
        "object_properties": len(set(asserted.subjects(RDF.type, OWL.ObjectProperty))),
        "annotation_properties": len(set(asserted.subjects(RDF.type, OWL.AnnotationProperty))),
        "named_individuals": len({
            s for s, _, o in asserted.triples((None, RDF.type, None))
            if str(s).startswith(BASE) and isinstance(o, URIRef) and str(o).startswith(BASE)
            and (s, RDF.type, OWL.Class) not in asserted
            and (s, RDF.type, OWL.ObjectProperty) not in asserted
            and (s, RDF.type, OWL.AnnotationProperty) not in asserted}),
        "airo_alignment_axioms": len([1 for s, p, o in asserted
                                      if isinstance(o, URIRef) and "w3id.org/airo" in str(o)
                                      and p in (RDFS.subClassOf, OWL.equivalentClass, RDFS.subPropertyOf)]),
        "defined_classes": len(set(asserted.subjects(OWL.equivalentClass, None))),
        "article_references": len(set(asserted.subject_objects(EUAI.hasArticleReference))),
        "annex_references": len(set(asserted.subject_objects(EUAI.hasAnnexReference))),
    }
    METRICS.parent.mkdir(exist_ok=True)
    with METRICS.open("w", newline="") as f:
        wtr = csv.writer(f, delimiter="\t")
        wtr.writerow(["metric", "value"])
        for k, v in m.items():
            wtr.writerow([k, v])
    print(f"[4] metrics -> {METRICS.relative_to(ROOT)}")
    for k, v in m.items():
        print(f"      {k:26s} {v}")
    return m


def run_cqs(reasoned):
    RESULTS.mkdir(exist_ok=True)
    all_ok = True
    for i in range(1, 6):
        q = (QUERIES / f"cq{i}.rq").read_text(encoding="utf-8")
        res = reasoned.query(q)
        rows = list(res)
        out = RESULTS / f"cq{i}.csv"
        with out.open("w", newline="") as f:
            wtr = csv.writer(f)
            wtr.writerow([str(v) for v in res.vars])
            for r in rows:
                wtr.writerow([(str(x).split("#")[-1] if x else "") for x in r])
        status = "OK" if rows else "EMPTY (FAIL)"
        all_ok &= bool(rows)
        print(f"[5] CQ{i}: {len(rows)} rows -> {out.relative_to(ROOT)}  {status}")
    if not all_ok:
        print("    WARNING: a competency question returned no rows.")
        sys.exit(2)
    print("    all competency questions return non-empty results: PASS")


def main():
    reasoned = reason_and_materialise()
    metrics(reasoned)
    run_cqs(reasoned)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
