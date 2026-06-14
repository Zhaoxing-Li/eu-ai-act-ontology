# Validation prompts and notes

## Reasoning

Reasoning is run with **HermiT** through `owlready2` (`scripts/build_checks.py`).
HermiT needs Java 11+. ROBOT (the OBO tool) was the first-choice runner but Java
was not preinstalled on the build machine; a local Temurin JDK 17 was installed
and HermiT used directly. The programmatic HermiT run is the machine evidence of
consistency; the final Protégé GUI load (see `docs/protege-validation.md`) is the
human confirmation the task asks for.

Prompt used:

> Load the ontology, run HermiT, and (a) assert it is consistent with no
> unsatisfiable classes; (b) confirm that the two demonstration AI systems are
> **inferred** to be `HighRiskAISystem` (they are not asserted as such), and that
> the chatbot instance is **not**. Fail loudly if any expectation is unmet.

Result: consistent; `CVScreeningTool` and `ExamProctoringSystem` inferred
high-risk; `CustomerServiceChatbot` not. See terminal output reproduced in the
README.

## Competency-question testing

> Write one SPARQL file per competency question. Run each against the
> **reasoned** graph (`eu-ai-act-ontology-reasoned.ttl`). Every query must return
> a non-empty, correct result. If one is empty, fix the ontology, do not weaken
> the question.

Result: all five CQs return non-empty results
(`queries/results/cq1.csv` ... `cq5.csv`).

## Hallucination back-check

> For every `legalTextSnippet` in the ontology, confirm the text still occurs
> verbatim in the segmented source. Report any snippet that does not match, and
> confirm every modelled element carries an article or annex reference.

Result (`scripts/verify_provenance.py`): 52 entities checked, 0 missing a
reference; 42 snippets checked, 0 unmatched.

## Notes / limitations

- AIRO is **aligned to but not imported**, to keep the file self-contained and
  fast to load. Alignment axioms reference AIRO IRIs directly; a reasoner treats
  them as external classes. Importing AIRO is a one-line change for full
  cross-ontology reasoning.
- Several class IRIs are used both as classes and as individuals (OWL 2 punning)
  so that `imposedOn`/`appliesToSystem` can point at an actor/system *kind*. This
  is valid OWL 2 DL and HermiT accepts it; the ontology stays consistent.
