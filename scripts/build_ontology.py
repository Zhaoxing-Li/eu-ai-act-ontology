"""Assemble the Turtle ontology from verified extraction candidates.

The axiomatic core (the defined class HighRiskAISystem, AIRO alignment, the
property box and the demonstration instances) is hand-designed here; the
repetitive, provenance-bearing assertions (actors, prohibited practices,
Annex III domains, obligations) are generated from data/extraction-candidates.json
so that every class/individual automatically carries its label, definition,
article/annex reference and a verbatim legal snippet. This keeps provenance
exhaustive and the build reproducible.

Output: ontology/eu-ai-act-ontology.ttl
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDS = json.loads((ROOT / "data" / "extraction-candidates.json").read_text(encoding="utf-8"))
OUT = ROOT / "ontology" / "eu-ai-act-ontology.ttl"

BASE = "https://zhaoxing-li.github.io/eu-ai-act-ontology#"
CELEX = "http://data.europa.eu/eli/reg/2024/1689/oj"
GENERATED_AT = "2026-06-14T12:00:00Z"

by_kind = {}
for c in CANDS:
    by_kind.setdefault(c["kind"], []).append(c)
by_name = {c["name"]: c for c in CANDS}


def esc(s: str) -> str:
    """Escape a string for a single-line Turtle literal."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def snippet(c, n=220):
    return esc(c["source_span"][:n].rstrip())


def ann(c, indent="        "):
    """Common annotation block: definition, ref, snippet, source."""
    lines = []
    ref = c.get("ref", "")
    if ref.startswith("Annex"):
        lines.append(f'{indent}euai:hasAnnexReference "{esc(ref)}" ;')
    else:
        lines.append(f'{indent}euai:hasArticleReference "{esc(ref)}" ;')
    lines.append(f'{indent}euai:legalTextSnippet "{snippet(c)}" ;')
    lines.append(f'{indent}dcterms:source <{CELEX}> ;')
    if c.get("note"):
        lines.append(f'{indent}rdfs:comment "{esc(c["note"])}" ;')
    return "\n".join(lines)


P = []  # output parts
w = P.append

# ---------------------------------------------------------------- header
w(f"""@prefix euai:    <{BASE}> .
@prefix airo:    <https://w3id.org/airo#> .
@prefix owl:     <http://www.w3.org/2002/07/owl#> .
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos:    <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix prov:    <http://www.w3.org/ns/prov#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .

#################################################################
#  Ontology metadata + PROV-O pipeline provenance
#################################################################

<{BASE.rstrip('#')}> a owl:Ontology ;
    dcterms:title "EU AI Act Ontology (proof of concept)" ;
    dcterms:description "A proof-of-concept ontology of the key concepts, actors and obligations of Regulation (EU) 2024/1689 (the EU AI Act), built with an AI-assisted, human-verified pipeline and aligned to the AI Risk Ontology (AIRO)." ;
    dcterms:creator "Zhaoxing Li" ;
    dcterms:license <https://creativecommons.org/licenses/by/4.0/> ;
    owl:versionInfo "0.1.0" ;
    dcterms:source <{CELEX}> ;
    prov:wasDerivedFrom <{CELEX}> ;
    prov:generatedAtTime "{GENERATED_AT}"^^xsd:dateTime ;
    prov:wasGeneratedBy [ a prov:Activity ;
        rdfs:label "AI-assisted ontology engineering pipeline" ;
        rdfs:comment "Fetch + segment (EUR-Lex) -> LLM candidate extraction with verbatim source spans -> human verification gate -> Turtle authoring -> HermiT reasoning -> SPARQL competency-question testing -> provenance back-check." ] ;
    rdfs:comment "Risk is modelled once: HighRiskAISystem is a DEFINED class and membership is INFERRED by a reasoner, not asserted. Obligations are typed by kind and the bearer is attached with euai:imposedOn." .
""")

# ---------------------------------------------------------------- annotation + object properties
w("""#################################################################
#  Annotation properties (provenance)
#################################################################

euai:hasArticleReference a owl:AnnotationProperty ;
    rdfs:label "has article reference" ;
    rdfs:comment "Article of Regulation (EU) 2024/1689 that grounds this element." .

euai:hasAnnexReference a owl:AnnotationProperty ;
    rdfs:label "has annex reference" ;
    rdfs:comment "Annex of Regulation (EU) 2024/1689 that grounds this element." .

euai:legalTextSnippet a owl:AnnotationProperty ;
    rdfs:label "legal text snippet" ;
    rdfs:comment "Verbatim excerpt of the source provision (for traceability / hallucination back-check)." .

#################################################################
#  Object properties
#################################################################

euai:operatesInDomain a owl:ObjectProperty ;
    rdfs:subPropertyOf airo:isAppliedWithinDomain ;
    rdfs:label "operates in domain" ;
    rdfs:domain euai:AISystem ;
    rdfs:range euai:AnnexIIIDomain ;
    rdfs:comment "Links an AI system to an Annex III high-risk application area (Article 6(2))." .

euai:hasRiskLevel a owl:ObjectProperty ;
    rdfs:label "has risk level" ;
    rdfs:domain euai:AISystem ;
    rdfs:range euai:RiskLevel ;
    rdfs:comment "Regulatory risk tier of an AI system." .

euai:imposesObligation a owl:ObjectProperty ;
    rdfs:label "imposes obligation" ;
    owl:inverseOf euai:imposedOn ;
    rdfs:comment "A legal source imposes an obligation." .

euai:imposedOn a owl:ObjectProperty ;
    rdfs:label "imposed on" ;
    rdfs:domain euai:Obligation ;
    rdfs:comment "The actor (bearer) on whom an obligation falls. Points to an actor class used as an individual (OWL 2 punning)." .

euai:appliesToSystem a owl:ObjectProperty ;
    rdfs:label "applies to system" ;
    rdfs:domain euai:Obligation ;
    rdfs:comment "The kind of AI system an obligation applies to. Points to a system class used as an individual (OWL 2 punning)." .

euai:prohibitedBy a owl:ObjectProperty ;
    rdfs:label "prohibited by" ;
    rdfs:comment "Links a prohibited practice to the provision that prohibits it." .
""")

# ---------------------------------------------------------------- AI system classes
w("""#################################################################
#  AI system classes
#################################################################
""")
ai = by_name["AISystem"]
w(f"""euai:AISystem a owl:Class ;
    owl:equivalentClass airo:AISystem ;
    rdfs:label "AI system" ;
    skos:definition "A machine-based system designed to operate with varying levels of autonomy, that may exhibit adaptiveness, and that infers from inputs how to generate outputs." ;
{ann(ai)}
    rdfs:isDefinedBy <{BASE.rstrip('#')}> .
""")

gp = by_name["GeneralPurposeAIModel"]
w(f"""euai:GeneralPurposeAIModel a owl:Class ;
    rdfs:subClassOf airo:GPAIModel ;
    rdfs:label "General-purpose AI model" ;
    skos:definition "An AI model, including one trained with a large amount of data using self-supervision at scale, that displays significant generality and competence across tasks." ;
{ann(gp)} .
""")

w("""euai:LimitedRiskAISystem a owl:Class ;
    rdfs:subClassOf euai:AISystem ;
    rdfs:label "Limited-risk AI system" ;
    skos:definition "An AI system that is not high-risk but is subject to the transparency obligations of Article 50 (e.g. systems interacting with people, or generating synthetic content)." ;
    euai:hasArticleReference "Article 50" .
""")

hr = by_name["HighRiskAISystem"]
w(f"""# --- The key axiom: HighRiskAISystem is a DEFINED class (membership is inferred) ---
euai:HighRiskAISystem a owl:Class ;
    owl:equivalentClass [ a owl:Class ;
        owl:intersectionOf ( euai:AISystem
            [ a owl:Restriction ;
              owl:onProperty euai:operatesInDomain ;
              owl:someValuesFrom euai:AnnexIIIDomain ] ) ] ;
    rdfs:subClassOf euai:AISystem ;
    rdfs:label "High-risk AI system" ;
    skos:definition "An AI system that operates in one of the high-risk application areas of Annex III (Article 6(2)). Class membership is inferred by a reasoner, never asserted on instances." ;
{ann(hr)} .
""")

# ---------------------------------------------------------------- actors
w("""#################################################################
#  Actors  (Act 'operator' == airo:AIOperator)
#################################################################
""")
ACTOR_PARENT = {
    "Actor": None,
    "Provider": "euai:Actor", "Deployer": "euai:Actor", "Importer": "euai:Actor",
    "Distributor": "euai:Actor", "AuthorisedRepresentative": "euai:Actor",
    "MarketSurveillanceAuthority": None,
}
for c in by_kind["class"]:
    if c["name"] not in ACTOR_PARENT:
        continue
    name = c["name"]
    lines = [f"euai:{name} a owl:Class ;"]
    align, rel = c.get("align"), c.get("rel")
    if name == "Actor":
        lines.append("    owl:equivalentClass airo:AIOperator ;")
    else:
        if ACTOR_PARENT[name]:
            lines.append(f"    rdfs:subClassOf {ACTOR_PARENT[name]} ;")
        if align:
            lines.append(f"    rdfs:subClassOf {align} ;")
    lines.append(f'    rdfs:label "{esc(c["label"])}" ;')
    lines.append(ann(c, indent="    "))
    w("\n".join(lines).rstrip(" ;\n") + " .\n")

# ---------------------------------------------------------------- risk levels
w("""#################################################################
#  Risk levels  (individuals, NOT a parallel class tree)
#################################################################

euai:RiskLevel a owl:Class ;
    rdfs:label "Risk level" ;
    skos:definition "A regulatory risk tier of the EU AI Act." .
""")
for c in by_kind["risklevel"]:
    w(f"""euai:{c['name']} a euai:RiskLevel ;
    rdfs:label "{esc(c['label'])}" ;
{ann(c, indent='    ')} .
""")

# ---------------------------------------------------------------- practices
w("""#################################################################
#  AI practices / prohibited practices  (Article 5)
#################################################################

euai:AIPractice a owl:Class ;
    rdfs:label "AI practice" ;
    skos:definition "A way an AI system is placed on the market, put into service or used." .

euai:ProhibitedPractice a owl:Class ;
    rdfs:subClassOf euai:AIPractice ;
    rdfs:label "Prohibited practice" ;
    skos:definition "An AI practice prohibited under Article 5 of the EU AI Act." ;
    euai:hasArticleReference "Article 5" .
""")
for c in by_kind["practice"]:
    w(f"""euai:{c['name']} a euai:ProhibitedPractice ;
    rdfs:label "{esc(c['label'])}" ;
    euai:hasRiskLevel euai:UnacceptableRisk ;
{ann(c, indent='    ')} .
""")

# ---------------------------------------------------------------- Annex III domains
w("""#################################################################
#  Annex III high-risk application domains  (individuals)
#################################################################

euai:AnnexIIIDomain a owl:Class ;
    rdfs:subClassOf airo:Domain ;
    rdfs:label "Annex III domain" ;
    skos:definition "A high-risk application area listed in Annex III of the EU AI Act (Article 6(2))." ;
    euai:hasAnnexReference "Annex III" .
""")
for c in by_kind["domain"]:
    w(f"""euai:{c['name']} a euai:AnnexIIIDomain ;
    rdfs:label "{esc(c['label'])}" ;
{ann(c, indent='    ')} .
""")

# ---------------------------------------------------------------- obligations
w("""#################################################################
#  Obligations  (typed by KIND; bearer attached with euai:imposedOn)
#################################################################

euai:Obligation a owl:Class ;
    rdfs:label "Obligation" ;
    skos:definition "A duty imposed by the EU AI Act on an actor in respect of an AI system." .
""")
OBLIG_SUBCLASSES = {
    "TransparencyObligation": ("Articles 13, 50", "Duty to disclose information about an AI system or its outputs."),
    "RiskManagementObligation": ("Article 9", "Duty to establish a risk management system (Article 9)."),
    "DataGovernanceObligation": ("Article 10", "Duty over training, validation and testing data quality and governance (Article 10)."),
    "TechnicalDocumentationObligation": ("Article 11", "Duty to draw up and keep technical documentation (Article 11)."),
    "LoggingObligation": ("Article 12", "Duty to enable automatic recording of events / logs (Article 12)."),
    "HumanOversightObligation": ("Articles 14, 26", "Duty to enable or ensure effective human oversight (Articles 14, 26)."),
    "PostMarketMonitoringObligation": ("Article 72", "Duty to monitor systems after they are placed on the market (Article 72)."),
    "AccuracyRobustnessObligation": ("Article 15", "Duty to achieve appropriate accuracy, robustness and cybersecurity (Article 15)."),
}
for sub, (ref, defn) in OBLIG_SUBCLASSES.items():
    w(f"""euai:{sub} a owl:Class ;
    rdfs:subClassOf euai:Obligation ;
    rdfs:label "{sub[:-len('Obligation')]} obligation" ;
    skos:definition "{esc(defn)}" ;
    euai:hasArticleReference "{ref}" .
""")
for c in by_kind["obligation"]:
    w(f"""euai:{c['name']} a euai:{c['otype']} ;
    rdfs:label "{esc(c['label'])}" ;
    euai:imposedOn euai:{c['imposed_on']} ;
    euai:appliesToSystem euai:{c['applies_to']} ;
{ann(c, indent='    ')} .
""")

# ---------------------------------------------------------------- demonstration instances
w(f"""#################################################################
#  Demonstration instances
#  (NO HighRiskAISystem type is asserted -- the reasoner must infer it)
#################################################################

euai:CVScreeningTool a euai:AISystem ;
    rdfs:label "ACME CV screening tool" ;
    rdfs:comment "Demo instance: should be INFERRED as a HighRiskAISystem via the employment domain (Annex III(4))." ;
    euai:operatesInDomain euai:EmploymentAndWorkerManagement .

euai:ExamProctoringSystem a euai:AISystem ;
    rdfs:label "Online exam proctoring system" ;
    rdfs:comment "Demo instance: should be INFERRED as a HighRiskAISystem via the education domain (Annex III(3))." ;
    euai:operatesInDomain euai:EducationAndVocationalTraining .

euai:CustomerServiceChatbot a euai:LimitedRiskAISystem ;
    rdfs:label "Customer-service chatbot" ;
    rdfs:comment "Demo instance: NOT high-risk (no Annex III domain); subject only to Article 50 transparency. Confirms the reasoner does not over-classify." ;
    euai:hasRiskLevel euai:LimitedRisk .
""")

OUT.write_text("\n".join(P), encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size} bytes)")
