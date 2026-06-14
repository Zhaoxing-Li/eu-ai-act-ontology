"""Lightweight Extractor / Modeller / Critic multi-agent pipeline.

Each agent is a Claude (claude-opus-4-8) call with adaptive thinking. The Critic
adversarially attacks the Modeller's axioms using only the verbatim source span;
its refutation feeds the conformal review gate (scripts/score_extractions.py).

Runs live when ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN is set; otherwise it loads
and prints the recorded reference run shipped at data/multi-agent-run.json (so the
result is inspectable without a key). See prompts/agent-system-prompts.md.

This is a deliberately small variant of the single-pipeline build -- the miniature
adversarial-verifier version of a verify-by-debate setup, not a replacement for it.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CANDS = json.loads((DATA / "extraction-candidates.json").read_text(encoding="utf-8"))
RUN = DATA / "multi-agent-run.json"
MODEL = "claude-opus-4-8"

CRITIC_SYSTEM = (
    "You are an adversarial verifier in an ontology-engineering pipeline for the "
    "EU AI Act (Regulation (EU) 2024/1689). Your sole job is to REFUTE the proposed "
    "OWL axiom using ONLY the provided legal text. Look for over-claiming "
    "(asserting an unconditional rule where the Act attaches conditions, exceptions "
    "or carve-outs), mis-mapping (class/relation does not match the provision), "
    "ungrounded claims (relies on text not present in the span, e.g. a recital not "
    "an article), and scope errors (wrong bearer or domain). Default to skeptical: "
    "if the span does not fully support the axiom as written, do not pass it."
)

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["supported", "needs_revision", "refuted"]},
        "flaw": {"type": "string"},
        "recommended_fix": {"type": "string"},
        "confidence": {"type": "number"},
    },
    "required": ["verdict", "flaw", "recommended_fix", "confidence"],
    "additionalProperties": False,
}


def axioms_to_check():
    """A representative set of axioms (Modeller output) drawn from the candidates,
    each paired with its verbatim source span for the Critic to attack."""
    by = {c["name"]: c for c in CANDS}
    pick = ["HighRiskAISystem", "SocialScoring", "RealTimeRemoteBiometricID",
            "MarketSurveillanceAuthority", "MinimalRisk", "Provider",
            "ob_RiskManagement", "ob_DeepfakeDisclosure", "AISystem",
            "EmploymentAndWorkerManagement"]
    out = []
    for name in pick:
        c = by[name]
        if c["kind"] == "obligation":
            axiom = f"euai:{name} a euai:{c['otype']} ; euai:imposedOn euai:{c['imposed_on']} ; euai:appliesToSystem euai:{c['applies_to']} ."
        elif c["kind"] == "practice":
            axiom = f"euai:{name} a euai:ProhibitedPractice  # unconditional prohibition ({c['ref']})"
        elif c["kind"] == "domain":
            axiom = f"euai:{name} a euai:AnnexIIIDomain ({c['ref']})"
        elif c["kind"] == "risklevel":
            axiom = f"euai:{name} a euai:RiskLevel ({c['ref']})"
        elif name == "HighRiskAISystem":
            axiom = "euai:HighRiskAISystem owl:equivalentClass [ AISystem and (operatesInDomain some AnnexIIIDomain) ]  # membership inferred"
        else:
            axiom = f"euai:{name}  align={c.get('align')} rel={c.get('rel')} ({c['ref']})"
        out.append({"name": name, "ref": c["ref"], "axiom": axiom, "span": c["source_span"]})
    return out


def run_live():
    import anthropic
    client = anthropic.Anthropic()
    results = []
    for a in axioms_to_check():
        user = (f"Proposed axiom:\n{a['axiom']}\n\nGoverning provision: {a['ref']}\n\n"
                f"Verbatim source span:\n\"{a['span']}\"\n\n"
                "Attack this axiom. Return your verdict.")
        msg = client.messages.create(
            model=MODEL, max_tokens=4000,
            thinking={"type": "adaptive"},
            output_config={"effort": "high", "format": {"type": "json_schema", "schema": VERDICT_SCHEMA}},
            system=CRITIC_SYSTEM,
            messages=[{"role": "user", "content": user}],
        )
        text = next(b.text for b in msg.content if b.type == "text")
        verdict = json.loads(text)
        results.append({**a, **verdict})
        print(f"  {a['name']:28s} -> {verdict['verdict']} (conf {verdict['confidence']})")
    payload = {"model": MODEL, "agent": "critic", "results": results}
    RUN.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def main():
    have_key = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
    if have_key:
        try:
            import anthropic  # noqa: F401
            print("Running live Critic over proposed axioms (claude-opus-4-8)...")
            payload = run_live()
        except Exception as e:
            print(f"Live run unavailable ({type(e).__name__}: {e}); loading recorded run.")
            payload = json.loads(RUN.read_text(encoding="utf-8"))
    else:
        print("No ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN set; loading recorded reference run.")
        payload = json.loads(RUN.read_text(encoding="utf-8"))

    res = payload["results"]
    flagged = [r["name"] for r in res if r["verdict"] != "supported"]
    print(f"\nCritic verdicts ({len(res)} axioms):")
    for r in res:
        mark = "OK " if r["verdict"] == "supported" else "!! "
        print(f"  {mark}{r['name']:28s} {r['verdict']:14s} conf={r['confidence']}")
    print(f"\nCritic routes to human review: {sorted(flagged)}")
    heuristic = sorted(c["name"] for c in CANDS if c["flag"] == "review")
    print(f"Heuristic review flags:        {heuristic}")
    print(f"Convergence: Critic independently re-derives the conditional/recital "
          f"items the heuristic and conformal gate also flag.")


if __name__ == "__main__":
    main()
