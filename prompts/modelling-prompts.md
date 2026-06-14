# Modelling prompts

These prompts drove the authoring of the Turtle ontology
(`scripts/build_ontology.py`). The locked modelling decisions below were given to
the model as hard constraints.

## Locked decisions (given as constraints)

> 1. **Reuse a domain ontology.** Align to AIRO (the AI Risk Ontology,
>    `https://w3id.org/airo#`). Where an AIRO class genuinely fits, declare the
>    local class `owl:equivalentClass` or `rdfs:subClassOf` the AIRO class.
>    Inspect AIRO's actual classes first; do not guess alignments. Where AIRO's
>    concept differs (e.g. AIRO `Risk` = likelihood x severity, not a regulatory
>    tier), do **not** force the alignment, and say so.
> 2. **Model risk once.** Do not build a parallel RiskCategory subclass tree.
>    Make `HighRiskAISystem` a **defined class**
>    (`owl:equivalentClass` with a `someValuesFrom` restriction on
>    `operatesInDomain`) so a reasoner infers membership. Risk tiers are
>    individuals of a `RiskLevel` class.
> 3. **Type obligations by kind; attach the bearer with a property.** Obligation
>    subclasses are by kind (transparency, risk management, ...). The actor who
>    bears the obligation is linked with `euai:imposedOn`, never encoded as a
>    subclass.
> 4. **Provenance everywhere.** Every class, practice, domain and obligation gets
>    `rdfs:label`, `skos:definition`, an article/annex reference and a verbatim
>    `legalTextSnippet`. The ontology header records PROV-O pipeline provenance.
> 5. **Honest namespace.** Use a base IRI the author controls
>    (`https://zhaoxing-li.github.io/eu-ai-act-ontology#`). Do not claim a
>    `w3id.org` IRI.
> 6. **Small but axiomatically rich.** If pressed, trim leaf domains or obligation
>    subtypes before cutting reasoning, the defined class, or provenance.

## The key axiom (authored by hand)

```turtle
euai:HighRiskAISystem owl:equivalentClass [
    a owl:Class ;
    owl:intersectionOf ( euai:AISystem
        [ a owl:Restriction ;
          owl:onProperty euai:operatesInDomain ;
          owl:someValuesFrom euai:AnnexIIIDomain ] ) ] .
```

Two demonstration instances assert only `operatesInDomain` an Annex III domain;
the reasoner infers `HighRiskAISystem`. A third (a chatbot) has no Annex III
domain and is deliberately **not** inferred high-risk, to show the model does not
over-classify.

## AIRO alignment actually used (verified against airo.ttl)

| Local | AIRO | Relation |
|-------|------|----------|
| `AISystem` | `airo:AISystem` | equivalentClass |
| `Actor` | `airo:AIOperator` | equivalentClass |
| `Provider` | `airo:AIProvider` | subClassOf |
| `Deployer` | `airo:AIDeployer` | subClassOf |
| `Importer`/`Distributor`/`AuthorisedRepresentative` | `airo:AIOperator` | subClassOf |
| `MarketSurveillanceAuthority` | `airo:Stakeholder` | subClassOf (not an operator) |
| `GeneralPurposeAIModel` | `airo:GPAIModel` | subClassOf |
| `AnnexIIIDomain` | `airo:Domain` | subClassOf |
| `operatesInDomain` | `airo:isAppliedWithinDomain` | subPropertyOf |

**Deliberate non-reuse:** the Act's risk *tiers* (unacceptable/high/limited/
minimal) are modelled locally as `RiskLevel` individuals and are **not** aligned
to `airo:Risk`, because AIRO's `Risk` is a quantitative likelihood x severity
notion, not a regulatory category.
