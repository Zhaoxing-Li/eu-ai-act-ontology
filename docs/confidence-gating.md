# Illustrative conformal-style review gating

Instead of hand-set high/review flags, every extraction candidate gets an interpretable confidence score, and a split-conformal threshold decides which are auto-accepted and which are routed to a human. The aim is to show how uncertainty quantification can drive the human-in-the-loop gate — it is a proof of concept, **not** a guarantee of legal correctness.

## Method

- **Score.** A transparent logistic score over four grounding-quality features: verbatim anchor match, article-body (vs recital) grounding, unconditional (vs carve-out/exception) application, and unambiguous (vs noted-uncertain/paraphrased) mapping.
- **Calibration set.** 53 examples: 47 source-grounded positives plus 6 synthesised hard negatives (mis-grounded extractions the gate should catch).
- **Split-conformal threshold.** tau = the finite-sample alpha-quantile (alpha=0.1) of the positive scores: tau = 0.961.
- **Coverage statement (under this calibration setup).** A genuinely-correct candidate is auto-accepted with probability >= 1 - alpha = 0.90 (split-conformal, Vovk et al.). With a small, partly synthetic calibration set this is illustrative rather than a strong production-grade bound — the threshold is one point on a tunable risk-coverage curve, not a fixed ad-hoc rule.

## Risk-coverage curve (tunable alpha)

| alpha | # routed to human review | candidates |
|-------|--------------------------|------------|
| 0.05 | 0 | - |
| 0.10 | 2 | RealTimeRemoteBiometricID, ob_DeepfakeDisclosure |
| 0.15 | 6 | LimitedRisk, MarketSurveillanceAuthority, MinimalRisk, ProductSafetyHighRiskAISystem, RealTimeRemoteBiometricID, ob_DeepfakeDisclosure |
| 0.20 | 6 | LimitedRisk, MarketSurveillanceAuthority, MinimalRisk, ProductSafetyHighRiskAISystem, RealTimeRemoteBiometricID, ob_DeepfakeDisclosure |

At the primary operating point alpha=0.1, the gate routes ['RealTimeRemoteBiometricID', 'ob_DeepfakeDisclosure'] to a human. The hand-set heuristic flags were ['LimitedRisk', 'MarketSurveillanceAuthority', 'MinimalRisk', 'ProductSafetyHighRiskAISystem', 'RealTimeRemoteBiometricID', 'ob_DeepfakeDisclosure']; the gate recovers them as alpha is loosened toward ~0.15-0.20, ordering candidates by calibrated confidence rather than by ad-hoc rules.

An auxiliary, deliberately-loose false-acceptance check on the same threshold (Hoeffding over the negatives): empirical risk 0.00, upper bound 0.18. At this calibration size that bound is not tight - reported honestly, not relied upon.

**Scope note.** This is a proof of concept: a small calibration set and synthesised negatives. The point is the mechanism - where uncertainty quantification plugs into the gating logic. It generalises directly to a multi-agent Extractor / Modeller / Critic pipeline, where an adversarial Critic agent's per-axiom refutation rate becomes the nonconformity score.