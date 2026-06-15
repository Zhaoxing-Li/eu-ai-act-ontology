# Protégé validation

I verify the ontology two ways. The pipeline checks consistency programmatically
with HermiT (`scripts/build_checks.py`), and I also load it in the Protégé GUI to
see the reasoning happen interactively — that GUI run is what the screenshot below
captures.

## How I check it in Protégé

I open `ontology/eu-ai-act-ontology.ttl` in Protégé 5.6 (it bundles its own JRE,
so I don't need a separate Java install), then select **HermiT** from the
**Reasoner** menu and start it. Two things I look for:

- **No unsatisfiable classes** — nothing collapses under `owl:Nothing` in the
  class hierarchy, so the model is logically consistent.
- **The high-risk inference fires.** In the Individuals view I select
  `CVScreeningTool`, which I only asserted to `operatesInDomain
  EmploymentAndWorkerManagement`. With the reasoner on, its inferred type now
  includes `HighRiskAISystem`. The same holds for `ExamProctoringSystem` via the
  education domain, while `CustomerServiceChatbot` stays limited-risk — so the
  model classifies what it should and nothing more.

The two demo individuals exercise the Annex III (Article 6(2)) route. The
Article 6(1) product-safety route is represented as a stub class,
`ProductSafetyHighRiskAISystem`, with no demonstration individual — it depends on
the Annex I product legislation, which is out of scope here. `HighRiskAISystem` is
the union of both routes, so it still subsumes either branch.

The cleanest way I found to show this is the **DL Query** tab: querying
`'High-risk AI system'` with *Instances* checked returns exactly the two
demonstration systems, derived rather than asserted. That is the screenshot I
keep at `docs/protege-inferred-highrisk.png`.

> Result: ontology consistent, no unsatisfiable classes, `CVScreeningTool` and
> `ExamProctoringSystem` inferred `HighRiskAISystem`, `CustomerServiceChatbot`
> not — matching the programmatic run.
