# Negation

The `negation` pipeline uses a simple rule-based algorithm to detect negated spans. It was designed at AP-HP's EDS, following the insights of the NegEx algorithm by {footcite:t}`chapman_simple_2001`.

## Declared extensions

The `negation` pipeline declares two [Spacy extensions](https://spacy.io/usage/processing-pipelines#custom-components-attributes), on both `Span` and `Token` objects :

1. The `negated` attribute is a boolean, set to `True` if the pipeline predicts that the span/token is negated.
2. The `polarity_` property is a human-readable string, computed from the `negated` attribute. It implements a simple getter function that outputs `AFF` or `NEG`, depending on the value of `negated`.

## Usage

The following snippet matches a simple terminology, and checks the polarity of the extracted entities. It is complete and can be run _as is_.

```python
import spacy
from edsnlp import components

nlp = spacy.blank("fr")
nlp.add_pipe("sentences")
# Dummy matcher
nlp.add_pipe(
    "matcher",
    config=dict(terms=dict(patient="patient", fracture="fracture")),
)
nlp.add_pipe("negation")

text = (
    "Le patient est admis le 23 août 2021 pour une douleur au bras. "
    "Le scanner ne détecte aucune fracture."
)

doc = nlp(text)

doc.ents
# Out: [patient, fracture]

doc.ents[0]._.polarity_
# Out: 'AFF'

doc.ents[1]._.polarity_
# Out: 'NEG'
```

## Performance

The pipeline's performance is measured on three datasets :

- The ESSAI ({footcite:t}`dalloux:hal-01659637`) and CAS ({footcite:t}`grabar:hal-01937096`) datasets were developped at the CNRS. The two are concatenated.
- The NegParHyp corpus was specifically developed at EDS to test the pipeline on actual medical notes, using pseudonymised notes from the EDS.

| Version | Dataset   | Negation F1 |
| ------- | --------- | ----------- |
| v0.0.1  | CAS/ESSAI | 79%         |
| v0.0.2  | CAS/ESSAI | 71%         |
| v0.0.2  | NegParHyp | 88%         |

Note that we favour the NegParHyp corpus, since it is comprised of actual medical notes from the data warehouse. The table shows that the pipeline does not perform as well on other datasets.

## Authors and citation

The `negation` pipeline was developed at the Data and Innovation unit, IT department, AP-HP.

## References

```{eval-rst}
.. footbibliography::
```