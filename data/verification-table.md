# Human verification gate

Only the candidates the pipeline flagged **review** are listed (paraphrased span, multi-article scope, or uncertain class mapping). Every other candidate is grounded in a verbatim span and mapped with high confidence.

Fill the **Decision** column with accept / reject / fix (+ note). Decisions are applied back to extraction-candidates.json before the ontology is built.

| # | Candidate | Kind | Ref | Why flagged | Proposed mapping | Decision |
|---|-----------|------|-----|-------------|------------------|----------|
| 1 | **MarketSurveillanceAuthority** | class | Article 70 | An authority, not an 'operator'. Aligned to airo:Stakeholder rather than airo:AIOperator. Confirm scope. | class MarketSurveillanceAuthority | **accept** (human, 14 Jun 2026) |
| 2 | **LimitedRisk** | risklevel | Article 50 | 'Limited risk' is the common term for Article 50 transparency-only systems; the term itself is from recitals, not the article body. | individual RiskLevel | **accept** (human, 14 Jun 2026) |
| 3 | **MinimalRisk** | risklevel | Recital 165 | 'Minimal risk' is a recital-level category (voluntary codes of conduct, Art 95). No span in the articles; flagged. | individual RiskLevel | **accept** (human, 14 Jun 2026) |
| 4 | **RealTimeRemoteBiometricID** | practice | Article 5(1)(h) | Conditional prohibition (permitted under narrow exceptions). Modelled as prohibited; the exceptions are out of scope for the PoC. | individual ProhibitedPractice | **accept** (human, 14 Jun 2026) |
| 5 | **ob_DeepfakeDisclosure** | obligation | Article 50(4) | Conditional (exceptions for law-enforcement and artistic works). Modelled as a transparency obligation; exceptions out of scope for the PoC. | TransparencyObligation on Deployer | **accept** (human, 14 Jun 2026) |

## Source spans for the flagged items

- **MarketSurveillanceAuthority** (Article 70): "Each Member State shall establish or designate as national competent authorities at least one notifying authority and at least one market surveillance authority for the purposes of this Regulation. Those national competent authorities shall..."
- **LimitedRisk** (Article 50): "Providers shall ensure that AI systems intended to interact directly with natural persons are designed and developed in such a way that the natural persons concerned are informed that they are interacting with an AI system, unless this is o..."
- **MinimalRisk** (Recital 165): "The AI Office and the Member States shall encourage and facilitate the drawing up of codes of conduct, including related governance mechanisms, intended to foster the voluntary application to AI systems, other than high-risk AI systems, of ..."
- **RealTimeRemoteBiometricID** (Article 5(1)(h)): "The following AI practices shall be prohibited: (a) the placing on the market, the putting into service or the use of an AI system that deploys subliminal techniques beyond a person’s consciousness or purposefully manipulative or deceptive ..."
- **ob_DeepfakeDisclosure** (Article 50(4)): "Deployers of an AI system that generates or manipulates image, audio or video content constituting a deep fake, shall disclose that the content has been artificially generated or manipulated. This obligation shall not apply where the use is..."