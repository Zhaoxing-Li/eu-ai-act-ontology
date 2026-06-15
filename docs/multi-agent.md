# Multi-agent variant: Extractor / Modeller / Critic

The main pipeline is a single, well-grounded flow. This is a lightweight
multi-agent variant of it, built to show one idea cleanly: an **adversarial
Critic** that attacks the Modeller's axioms with the source text, and whose
refutation feeds the same conformal review gate. It is the miniature,
single-domain version of a verify-by-debate setup, not a replacement for the
single pipeline.

- **Extractor** proposes candidate elements from a segment (verbatim-anchored).
- **Modeller** turns a verified candidate into one OWL axiom + AIRO alignment.
- **Critic** is prompted to *refute* each axiom using only the cited span:
  over-claiming, mis-mapping, ungrounded claims, scope errors. It returns
  `supported` / `needs_revision` / `refuted` + flaw + fix + confidence.

Each agent is a `claude-opus-4-8` call with adaptive thinking. Code:
`scripts/multi_agent_pipeline.py`; prompts: `prompts/agent-system-prompts.md`;
recorded run: `data/multi-agent-run.json` (reproduce live with
`ANTHROPIC_API_KEY` set).

## What the Critic found (recorded run, 10 axioms)

| Axiom | Verdict | Why |
|-------|---------|-----|
| `HighRiskAISystem` defined class | needs_revision | `≡` to the Annex III route omits the **Article 6(1)** product-safety route to high-risk. |
| `RealTimeRemoteBiometricID` prohibited | needs_revision | Art 5(1)(h) permits it under narrow law-enforcement exceptions — unconditional prohibition over-claims. |
| `ob_DeepfakeDisclosure` | needs_revision | Art 50(4) has artistic/law-enforcement carve-outs. |
| `MinimalRisk` | needs_revision | Recital-level only; not anchored in the cited article. |
| `AISystem`, `Provider`, `SocialScoring`, `MarketSurveillanceAuthority`, `ob_RiskManagement`, `EmploymentAndWorkerManagement` | supported | Faithful to the span. |

## Why this matters: three independent signals converge

The human-review set is now the union of three independent mechanisms:

1. **Heuristic flags** (hand-set rules): `LimitedRisk`, `MarketSurveillanceAuthority`, `MinimalRisk`, `ProductSafetyHighRiskAISystem`, `RealTimeRemoteBiometricID`, `ob_DeepfakeDisclosure`.
2. **Conformal confidence gate** (`score_extractions.py`): the same set recovered as a tunable, illustrative conformal-style curve — a distribution-free coverage statement under the stated calibration setup, not a legal-correctness guarantee.
3. **Adversarial Critic** (this pipeline): independently re-flags `RealTimeRemoteBiometricID`, `MinimalRisk`, `ob_DeepfakeDisclosure`; clears `MarketSurveillanceAuthority` on reasoned grounds; and **surfaces a new issue none of the others caught** — the Article 6(1) high-risk route.

Agreement across three independent methods raises confidence in the flagged set;
the Critic's extra finding shows adversarial verification adds genuine coverage,
not just redundancy. I acted on the Art 6(1) finding: high-risk is now modelled as
the **union of both routes** — `AnnexIIIHighRiskAISystem` (Art 6(2), a defined
class) and a `ProductSafetyHighRiskAISystem` stub (Art 6(1)).

## Scope note (honest)

This is a proof of concept. The agents run on a representative subset of axioms,
not the whole ontology, and the recorded run is shipped so the result is
inspectable without an API key. The mechanism — adversarial verification feeding
a calibrated gate — is the point, and it generalises to a full verify-by-debate
loop over every axiom.
