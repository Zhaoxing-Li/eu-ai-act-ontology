# Human verification gate

Only the candidates the pipeline flagged **review** are listed (paraphrased span, multi-article scope, recital-level, or stub). Every other candidate is grounded in a verbatim span and mapped with high confidence.

Decisions (accept / reject / fix) were applied back to extraction-candidates.json before the ontology was built.

| # | Candidate | Kind | Ref | Why flagged | Decision |
|---|-----------|------|-----|-------------|----------|
| 1 | **ProductSafetyHighRiskAISystem** | class | Article 6(1) | Article 6(1) product-safety route. Modelled as a stub: it depends on the Annex I product legislation, which is out of scope here. | **accept** |
| 2 | **MarketSurveillanceAuthority** | class | Article 70 | An authority, not an 'operator'. Aligned to airo:Stakeholder rather than airo:AIOperator. Confirm scope. | **accept** |
| 3 | **LimitedRisk** | risklevel | Article 50 | 'Limited risk' is the common term for Article 50 transparency-only systems; the term itself is from recitals, not the article body. | **accept** |
| 4 | **MinimalRisk** | risklevel | Recital 165 | 'Minimal risk' is a recital-level category (voluntary codes of conduct, Art 95). No span in the articles; flagged. | **accept** |
| 5 | **RealTimeRemoteBiometricID** | practice | Article 5(1)(h) | Conditional prohibition (permitted under narrow exceptions). Modelled as prohibited; the exceptions are out of scope for the PoC. | **accept** |
| 6 | **ob_DeepfakeDisclosure** | obligation | Article 50(4) | Conditional (exceptions for law-enforcement and artistic works). Modelled as a transparency obligation; exceptions out of scope for the PoC. | **accept** |

## Source spans for the flagged items

- **ProductSafetyHighRiskAISystem** (Article 6(1)): "intended to be used as a safety component of a product, or the AI system is itself a product, covered by the Union harmonisation legislation listed in Annex I; (b) the product whose safety component pursuant to point (a)..."
- **MarketSurveillanceAuthority** (Article 70): "market surveillance authority for the purposes of this Regulation. Those national competent authorities shall exercise their powers independently, impartially and without bias so as to safeguard the objectivity of their ..."
- **LimitedRisk** (Article 50): "informed that they are interacting with an AI system, unless this is obvious from the point of view of a natural person who is reasonably well-informed, observant and circumspect, taking into account the circumstances an..."
- **MinimalRisk** (Recital 165): "codes of conduct, including related governance mechanisms, intended to foster the voluntary application to AI systems, other than high-risk AI systems, of some or all of the requirements set out in Chapter III, Section 2..."
- **RealTimeRemoteBiometricID** (Article 5(1)(h)): "real-time’ remote biometric identification systems in publicly accessible spaces for the purposes of law enforcement, unless and in so far as such use is strictly necessary for one of the following objectives: (i) the ta..."
- **ob_DeepfakeDisclosure** (Article 50(4)): "constituting a deep fake, shall disclose that the content has been artificially generated or manipulated. This obligation shall not apply where the use is authorised by law to detect, prevent, investigate or prosecute cr..."