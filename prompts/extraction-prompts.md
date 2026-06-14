# Extraction prompts

The AI in my pipeline is a large language model (Claude) running inside an agentic
coding environment. I extract by giving the model the segmented Act and the prompt
below, then grounding its output in verbatim source spans with
`scripts/extract_fragments.py`. The script auto-flags any candidate whose anchor
phrase I cannot locate verbatim, so the model can never introduce a concept that
is not backed by source text.

## System framing

> You are assisting with ontology engineering for the EU AI Act (Regulation (EU)
> 2024/1689). You propose candidate ontology elements from the legal text. You do
> not decide what the law means; a human reviewer resolves anything uncertain.
> Never invent an article reference. If a concept cannot be tied to a specific
> article or annex, flag it for review.

## Extraction prompt (per relevant segment)

> Here is one segment of the EU AI Act, tagged with its article or annex number:
>
> ```
> {segment_id}: {segment_text}
> ```
>
> Extract candidate ontology elements of these kinds only:
> - **class** (an AI system type or actor type)
> - **actor** (provider, deployer, importer, distributor, authorised
>   representative, authority)
> - **obligation** (typed by kind: transparency, risk management, data
>   governance, technical documentation, logging, human oversight, post-market
>   monitoring, accuracy/robustness)
> - **practice** (a prohibited practice under Article 5)
> - **domain** (an Annex III high-risk application area)
> - **risk level** (unacceptable, high, limited, minimal)
>
> For each candidate return: a short local name, a human label, the kind, the
> governing article/annex reference, and a **verbatim anchor phrase** copied from
> this segment. Set `confidence = review` if the mapping is uncertain, the span
> is paraphrased, or the provision is conditional/exception-laden. Otherwise
> `confidence = high`. Do not output any candidate you cannot anchor in this
> segment's text.

## Accuracy controls

1. **Source grounding.** Every candidate carries a verbatim anchor; the script
   re-locates it in the cited segment and copies the surrounding sentence as the
   `source_span`. Anchors that do not match are auto-flagged `review`.
2. **Strict flagging.** Conditional provisions (e.g. Article 5(1)(h) real-time
   biometric identification, Article 50(4) deep fakes) and recital-level terms
   (minimal risk) were flagged for human decision rather than asserted.
3. **Human verification gate.** All `review` candidates were tabled in
   `data/verification-table.md` and resolved by a human before authoring.
4. **Hallucination back-check.** `scripts/verify_provenance.py` re-checks every
   snippet in the finished ontology against the source corpus (0 unmatched).

## Segments actually used for extraction

Article 3 (definitions), Article 5 (prohibited practices), Article 6 +
Annex III (high-risk classification + domains), Articles 9–15 (high-risk
requirements), Article 16 (provider obligations), Article 26 (deployer
obligations), Article 50 (transparency), Article 70 (authorities), Article 72
(post-market monitoring), Article 95 / Recital 165 (codes of conduct / minimal
risk).
