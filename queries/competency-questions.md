# Competency questions

Competency questions (CQs) are the functional specification of the ontology.
They were written *before* modelling and the ontology must answer all of them
after reasoning. Each CQ names the governing provision of Regulation (EU)
2024/1689 (the EU AI Act) and the SPARQL file that tests it.

| CQ | Question | Governing provision | Query |
|----|----------|---------------------|-------|
| CQ1 | Which AI practices are prohibited, and which article prohibits each? | Article 5 | `cq1.rq` |
| CQ2 | Which obligations apply to providers of high-risk AI systems? | Articles 9–15 (requirements) and 72 (post-market monitoring) | `cq2.rq` |
| CQ3 | Which actors bear obligations regarding high-risk AI systems, and which obligation does each bear? | Articles 16, 22, 23, 24, 26 | `cq3.rq` |
| CQ4 | Which AI systems are (inferred to be) high-risk, and via which Annex III domain? | Article 6(2), Annex III | `cq4.rq` |
| CQ5 | Which transparency obligations apply to providers/deployers of certain (limited-risk) AI systems? | Article 50 | `cq5.rq` |

## Notes on answerability

- **CQ4 must rely on inference.** No instance is asserted as `HighRiskAISystem`.
  The reasoner classifies a system as high-risk because it `operatesInDomain`
  an `AnnexIIIDomain` (Article 6(2)). The query therefore runs on the
  **reasoned** graph, not the asserted graph.
- **CQ1, CQ3, CQ5** test that provenance (article references) and the
  obligation–bearer modelling (`imposedOn`) are present and queryable.
- **CQ2** tests that provider obligations for high-risk systems are reachable,
  combining the obligation type hierarchy with the bearer property.

These five CQs jointly exercise the three headline modelling decisions:
reuse/alignment (AIRO), reasoning over a defined class (`HighRiskAISystem`),
and obligations typed by kind with the bearer attached by a property.
