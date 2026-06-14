"""AI-assisted extraction of ontology candidates from the segmented Act.

Pipeline role: the *conceptual* extraction (which concepts, actors, obligations,
practices and domains to model, and which AIRO class each aligns to) was produced
by an LLM (Claude) reading the segmented Act -- see prompts/extraction-prompts.md.
This script makes that extraction *reproducible and source-grounded*: for every
candidate it locates a verbatim anchor phrase inside the cited segment and copies
the surrounding sentence as the source span. A candidate whose anchor cannot be
located verbatim is flagged `review` automatically, so nothing enters the
ontology without a locatable span.

Output: data/extraction-candidates.json
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEGMENTS = json.loads((DATA / "ai-act-segments.json").read_text(encoding="utf-8"))
SEG = {s["id"]: s for s in SEGMENTS}


def span_for(seg_id: str, anchor: str, window: int = 260) -> str:
    """Return a verbatim span from the segment containing the anchor phrase."""
    text = SEG[seg_id]["text"]
    flat = re.sub(r"\s+", " ", text)
    a = re.sub(r"\s+", " ", anchor).strip()
    i = flat.find(a)
    if i == -1:
        return ""
    # Start the snippet exactly at the anchor (the operative phrase) rather than
    # backing up to the previous sentence, so each span lands on its own provision.
    end = i + len(a) + window
    return flat[i:end].strip()


# --- The LLM extraction: (kind, local name, label, ref, segment, anchor, align, flag, note) ---
# anchor must be a verbatim phrase in the cited segment; the script verifies it.
CANDIDATES = [
    # ---- AI system classes ----
    dict(kind="class", name="AISystem", label="AI system", ref="Article 3(1)",
         seg="Article 3", anchor="‘AI system’ means a machine-based system that is designed to operate with varying levels of autonomy",
         align="airo:AISystem", rel="equivalentClass", flag="high"),
    dict(kind="class", name="GeneralPurposeAIModel", label="General-purpose AI model", ref="Article 3(63)",
         seg="Article 3", anchor="‘general-purpose AI model’ means an AI model",
         align="airo:GPAIModel", rel="subClassOf", flag="high"),
    dict(kind="class", name="HighRiskAISystem", label="High-risk AI system", ref="Article 6",
         seg="Article 6", anchor="shall be considered to be high-risk",
         align=None, rel="union", flag="high",
         note="Union of two routes: AnnexIIIHighRiskAISystem (Article 6(2)) and ProductSafetyHighRiskAISystem (Article 6(1))."),
    dict(kind="class", name="AnnexIIIHighRiskAISystem", label="Annex III high-risk AI system", ref="Article 6(2)",
         seg="Annex III", anchor="High-risk AI systems pursuant to Article 6(2) are the AI systems listed",
         align=None, rel="defined", flag="high",
         note="Defined class: AISystem and (operatesInDomain some AnnexIIIDomain). Membership is inferred, not asserted."),
    dict(kind="class", name="ProductSafetyHighRiskAISystem", label="Product-safety high-risk AI system", ref="Article 6(1)",
         seg="Article 6", anchor="intended to be used as a safety component of a product, or the AI system is itself a product, covered by the Union harmonisation legislation listed in Annex I",
         align=None, rel="stub", flag="review",
         note="Article 6(1) product-safety route. Modelled as a stub: it depends on the Annex I product legislation, which is out of scope here."),

    # ---- Actors (definitions anchored at their numbered term in Article 3) ----
    dict(kind="class", name="Actor", label="Actor", ref="Article 3(8)",
         seg="Article 3", anchor="‘operator’ means a provider, product manufacturer, deployer, authorised representative, importer or distributor",
         align="airo:AIOperator", rel="equivalentClass", flag="high",
         note="Act's 'operator' == AIRO AIOperator. 'Actor' is the local umbrella for parties bearing obligations."),
    dict(kind="class", name="Provider", label="Provider", ref="Article 3(3)",
         seg="Article 3", anchor="‘provider’ means a natural or legal person, public authority, agency or other body that develops an AI system",
         align="airo:AIProvider", rel="subClassOf", flag="high"),
    dict(kind="class", name="Deployer", label="Deployer", ref="Article 3(4)",
         seg="Article 3", anchor="‘deployer’ means a natural or legal person, public authority, agency or other body using an AI system under its authority",
         align="airo:AIDeployer", rel="subClassOf", flag="high"),
    dict(kind="class", name="Importer", label="Importer", ref="Article 3(6)",
         seg="Article 3", anchor="‘importer’ means a natural or legal person located or established in the Union that places on the market an AI system",
         align="airo:AIOperator", rel="subClassOf", flag="high"),
    dict(kind="class", name="Distributor", label="Distributor", ref="Article 3(7)",
         seg="Article 3", anchor="‘distributor’ means a natural or legal person in the supply chain, other than the provider or the importer",
         align="airo:AIOperator", rel="subClassOf", flag="high"),
    dict(kind="class", name="AuthorisedRepresentative", label="Authorised representative", ref="Article 3(5)",
         seg="Article 3", anchor="‘authorised representative’ means a natural or legal person located or established in the Union who has received and accepted a written mandate from a provider",
         align="airo:AIOperator", rel="subClassOf", flag="high"),
    dict(kind="class", name="MarketSurveillanceAuthority", label="Market surveillance authority", ref="Article 70",
         seg="Article 70", anchor="market surveillance",
         align="airo:Stakeholder", rel="subClassOf", flag="review",
         note="An authority, not an 'operator'. Aligned to airo:Stakeholder rather than airo:AIOperator. Confirm scope."),

    # ---- Risk levels (individuals, not a class tree) ----
    dict(kind="risklevel", name="UnacceptableRisk", label="Unacceptable risk", ref="Article 5",
         seg="Article 5", anchor="The following AI practices shall be prohibited", flag="high"),
    dict(kind="risklevel", name="HighRisk", label="High risk", ref="Article 6",
         seg="Article 6", anchor="high-risk", flag="high"),
    dict(kind="risklevel", name="LimitedRisk", label="Limited risk", ref="Article 50",
         seg="Article 50", anchor="informed that they are interacting with an AI system", flag="review",
         note="'Limited risk' is the common term for Article 50 transparency-only systems; the term itself is from recitals, not the article body."),
    dict(kind="risklevel", name="MinimalRisk", label="Minimal risk", ref="Recital 165",
         seg="Article 95", anchor="codes of conduct", flag="review",
         note="'Minimal risk' is a recital-level category (voluntary codes of conduct, Art 95). No span in the articles; flagged."),

    # ---- Prohibited practices (Article 5(1)(a)-(h)) ----
    dict(kind="practice", name="SubliminalManipulation", label="Manipulative or deceptive techniques", ref="Article 5(1)(a)",
         seg="Article 5", anchor="deploys subliminal techniques beyond a person", flag="high"),
    dict(kind="practice", name="ExploitationOfVulnerabilities", label="Exploitation of vulnerabilities", ref="Article 5(1)(b)",
         seg="Article 5", anchor="exploits any of the vulnerabilities of a natural person or a specific group of persons", flag="high"),
    dict(kind="practice", name="SocialScoring", label="Social scoring", ref="Article 5(1)(c)",
         seg="Article 5", anchor="evaluation or classification of natural persons or groups of persons over a certain period of time", flag="high"),
    dict(kind="practice", name="IndividualCrimePrediction", label="Individual criminal-offence risk assessment", ref="Article 5(1)(d)",
         seg="Article 5", anchor="risk assessments of natural persons in order to assess or predict the risk", flag="high"),
    dict(kind="practice", name="FacialImageScraping", label="Untargeted facial-image scraping", ref="Article 5(1)(e)",
         seg="Article 5", anchor="create or expand facial recognition databases through the untargeted scraping", flag="high"),
    dict(kind="practice", name="EmotionRecognitionWorkEducation", label="Emotion recognition at work or in education", ref="Article 5(1)(f)",
         seg="Article 5", anchor="infer emotions of a natural person in the areas of workplace and education", flag="high"),
    dict(kind="practice", name="BiometricCategorisationSensitive", label="Sensitive biometric categorisation", ref="Article 5(1)(g)",
         seg="Article 5", anchor="biometric categorisation systems that categorise individually natural persons based on their biometric data", flag="high"),
    dict(kind="practice", name="RealTimeRemoteBiometricID", label="Real-time remote biometric identification for law enforcement", ref="Article 5(1)(h)",
         seg="Article 5", anchor="real-time", flag="review",
         note="Conditional prohibition (permitted under narrow exceptions). Modelled as prohibited; the exceptions are out of scope for the PoC."),

    # ---- Annex III high-risk domains (individuals) ----
    dict(kind="domain", name="Biometrics", label="Biometrics", ref="Annex III(1)",
         seg="Annex III", anchor="Biometrics, in so far as their use is permitted", flag="high"),
    dict(kind="domain", name="CriticalInfrastructure", label="Critical infrastructure", ref="Annex III(2)",
         seg="Annex III", anchor="Critical infrastructure", flag="high"),
    dict(kind="domain", name="EducationAndVocationalTraining", label="Education and vocational training", ref="Annex III(3)",
         seg="Annex III", anchor="Education and vocational training", flag="high"),
    dict(kind="domain", name="EmploymentAndWorkerManagement", label="Employment and worker management", ref="Annex III(4)",
         seg="Annex III", anchor="Employment, workers", flag="high"),
    dict(kind="domain", name="EssentialServices", label="Access to essential services", ref="Annex III(5)",
         seg="Annex III", anchor="essential private services and essential public services and benefits", flag="high"),
    dict(kind="domain", name="LawEnforcement", label="Law enforcement", ref="Annex III(6)",
         seg="Annex III", anchor="Law enforcement, in so far as their use is permitted", flag="high"),
    dict(kind="domain", name="MigrationAsylumBorderControl", label="Migration, asylum and border control", ref="Annex III(7)",
         seg="Annex III", anchor="Migration, asylum and border control management", flag="high"),
    dict(kind="domain", name="AdministrationOfJusticeAndDemocracy", label="Administration of justice and democratic processes", ref="Annex III(8)",
         seg="Annex III", anchor="Administration of justice and democratic processes", flag="high"),

    # ---- Obligation subclasses (typed by kind) + concrete obligation individuals ----
    dict(kind="obligation", name="ob_RiskManagement", label="Risk management obligation", otype="RiskManagementObligation",
         imposed_on="Provider", applies_to="HighRiskAISystem", ref="Article 9", seg="Article 9",
         anchor="risk management system shall be established", flag="high"),
    dict(kind="obligation", name="ob_DataGovernance", label="Data and data governance obligation", otype="DataGovernanceObligation",
         imposed_on="Provider", applies_to="HighRiskAISystem", ref="Article 10", seg="Article 10",
         anchor="shall be subject to data governance and management practices appropriate for the intended purpose", flag="high"),
    dict(kind="obligation", name="ob_TechnicalDocumentation", label="Technical documentation obligation", otype="TechnicalDocumentationObligation",
         imposed_on="Provider", applies_to="HighRiskAISystem", ref="Article 11", seg="Article 11",
         anchor="technical documentation of a high-risk AI system shall be drawn up", flag="high"),
    dict(kind="obligation", name="ob_RecordKeeping", label="Record-keeping (logging) obligation", otype="LoggingObligation",
         imposed_on="Provider", applies_to="HighRiskAISystem", ref="Article 12", seg="Article 12",
         anchor="technically allow for the automatic recording of events", flag="high"),
    dict(kind="obligation", name="ob_ProviderTransparency", label="Transparency and provision of information to deployers", otype="TransparencyObligation",
         imposed_on="Provider", applies_to="HighRiskAISystem", ref="Article 13", seg="Article 13",
         anchor="designed and developed in such a way as to ensure that their operation is sufficiently transparent", flag="high"),
    dict(kind="obligation", name="ob_HumanOversightDesign", label="Human oversight (design) obligation", otype="HumanOversightObligation",
         imposed_on="Provider", applies_to="HighRiskAISystem", ref="Article 14", seg="Article 14",
         anchor="designed and developed in such a way, including with appropriate human-machine interface tools, that they can be effectively overseen", flag="high"),
    dict(kind="obligation", name="ob_AccuracyRobustness", label="Accuracy, robustness and cybersecurity obligation", otype="AccuracyRobustnessObligation",
         imposed_on="Provider", applies_to="HighRiskAISystem", ref="Article 15", seg="Article 15",
         anchor="achieve an appropriate level of accuracy, robustness, and cybersecurity", flag="high"),
    dict(kind="obligation", name="ob_PostMarketMonitoring", label="Post-market monitoring obligation", otype="PostMarketMonitoringObligation",
         imposed_on="Provider", applies_to="HighRiskAISystem", ref="Article 72", seg="Article 72",
         anchor="establish and document a post-market monitoring system", flag="high"),
    dict(kind="obligation", name="ob_DeployerHumanOversight", label="Deployer human oversight obligation", otype="HumanOversightObligation",
         imposed_on="Deployer", applies_to="HighRiskAISystem", ref="Article 26", seg="Article 26",
         anchor="assign human oversight to natural persons who have the necessary competence", flag="high"),
    # Value-chain actor obligations (importer, distributor, authorised representative)
    dict(kind="obligation", name="ob_ImporterConformity", label="Importer conformity verification", otype="ConformityVerificationObligation",
         imposed_on="Importer", applies_to="HighRiskAISystem", ref="Article 23", seg="Article 23",
         anchor="Before placing a high-risk AI system on the market, importers shall ensure that the system is in conformity", flag="high"),
    dict(kind="obligation", name="ob_DistributorVerification", label="Distributor verification", otype="ConformityVerificationObligation",
         imposed_on="Distributor", applies_to="HighRiskAISystem", ref="Article 24", seg="Article 24",
         anchor="Before making a high-risk AI system available on the market, distributors shall verify", flag="high"),
    dict(kind="obligation", name="ob_AuthRepTasks", label="Authorised representative mandate tasks", otype="RepresentationObligation",
         imposed_on="AuthorisedRepresentative", applies_to="HighRiskAISystem", ref="Article 22", seg="Article 22",
         anchor="The authorised representative shall perform the", flag="high"),
    # Article 50 transparency obligations (limited-risk / user-facing)
    dict(kind="obligation", name="ob_AIInteractionDisclosure", label="AI interaction disclosure", otype="TransparencyObligation",
         imposed_on="Provider", applies_to="LimitedRiskAISystem", ref="Article 50(1)", seg="Article 50",
         anchor="informed that they are interacting with an AI system", flag="high"),
    dict(kind="obligation", name="ob_SyntheticContentMarking", label="Synthetic content marking", otype="TransparencyObligation",
         imposed_on="Provider", applies_to="LimitedRiskAISystem", ref="Article 50(2)", seg="Article 50",
         anchor="outputs of the AI system are marked in a machine-readable format", flag="high"),
    dict(kind="obligation", name="ob_DeepfakeDisclosure", label="Deep fake disclosure", otype="TransparencyObligation",
         imposed_on="Deployer", applies_to="LimitedRiskAISystem", ref="Article 50(4)", seg="Article 50",
         anchor="constituting a deep fake, shall disclose that the content has been artificially generated or manipulated", flag="review",
         note="Conditional (exceptions for law-enforcement and artistic works). Modelled as a transparency obligation; exceptions out of scope for the PoC."),
]


def main():
    out = []
    missing = []
    for c in CANDIDATES:
        rec = dict(c)
        span = span_for(c["seg"], c["anchor"])
        rec["source_span"] = span
        if not span:
            rec["flag"] = "review"
            rec["note"] = (rec.get("note", "") + " [anchor not located verbatim -> auto-flagged]").strip()
            missing.append(c["name"])
        out.append(rec)

    (DATA / "extraction-candidates.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    n_high = sum(1 for c in out if c["flag"] == "high")
    n_review = sum(1 for c in out if c["flag"] == "review")
    print(f"Candidates: {len(out)}  (high={n_high}, review={n_review})")
    by_kind = {}
    for c in out:
        by_kind[c["kind"]] = by_kind.get(c["kind"], 0) + 1
    print("By kind:", by_kind)
    if missing:
        print("ANCHORS NOT FOUND (need fixing):", missing)
    else:
        print("OK: every candidate grounded in a verbatim span.")


if __name__ == "__main__":
    main()
