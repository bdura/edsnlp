from typing import List, Union, Optional, Dict, Any

from edsnlp.pipelines.generic import GenericMatcher
from spacy.language import Language
from spacy.tokens import Token, Span, Doc

from loguru import logger

from edsnlp.utils.filter_matches import _filter_matches


class Antecedents(GenericMatcher):
    """
    Implements an antecedents detection algorithm.

    The components looks for terms indicating antecedents in the text.

    Parameters
    ----------
    nlp: Language
        spaCy nlp pipeline to use for matching.
    antecedents: List[str]
        List of terms indicating antecedent reference.
    termination: List[str]
        List of syntagme termination terms.
    use_sections: bool
        Whether to use section pipeline to detect antecedent section.
    fuzzy: bool
         Whether to perform fuzzy matching on the terms.
    filter_matches: bool
        Whether to filter out overlapping matches.
    annotation_scheme: str
        Whether to require that all tokens in the matching span possess the desired label (`annotation_scheme = 'all'`),
        or at least one token matching (`annotation_scheme = 'any'`).
    attr: str
        spaCy's attribute to use:
        a string with the value "TEXT" or "NORM", or a dict with the key 'term_attr'
        we can also add a key for each regex.
    on_ents_only: bool
        Whether to look for matches around detected entities only.
        Useful for faster inference in downstream tasks.
    regex: Optional[Dict[str, Union[List[str], str]]]
        A dictionnary of regex patterns.
    fuzzy_kwargs: Optional[Dict[str, Any]]
        Default options for the fuzzy matcher, if used.
    """

    split_on_punctuation = False

    def __init__(
        self,
        nlp: Language,
        antecedents: List[str],
        termination: List[str],
        use_sections: bool,
        fuzzy: bool,
        filter_matches: bool,
        annotation_scheme: str,
        attr: str,
        on_ents_only: bool,
        regex: Optional[Dict[str, Union[List[str], str]]],
        fuzzy_kwargs: Optional[Dict[str, Any]],
        **kwargs,
    ):

        super().__init__(
            nlp,
            terms=dict(antecedent=antecedents, termination=termination),
            fuzzy=fuzzy,
            filter_matches=filter_matches,
            attr=attr,
            on_ents_only=on_ents_only,
            regex=regex,
            fuzzy_kwargs=fuzzy_kwargs,
            **kwargs,
        )

        self.annotation_scheme = annotation_scheme

        def antecedent_getter(token_or_span: Union[Token, Span]):
            if token_or_span._.antecedent is None:
                return "NOTSET"
            elif token_or_span._.antecedent:
                return "ATCD"
            else:
                return "CURRENT"

        if not Token.has_extension("antecedent"):
            Token.set_extension("antecedent", default=None)

        if not Token.has_extension("antecedent_"):
            Token.set_extension(
                "antecedent_",
                getter=antecedent_getter,
            )

        if not Span.has_extension("antecedent"):
            Span.set_extension("antecedent", default=None)

        if not Span.has_extension("antecedent_"):
            Span.set_extension(
                "antecedent_",
                getter=antecedent_getter,
            )

        if not Doc.has_extension("antecedents"):
            Doc.set_extension("antecedents", default=[])

        self.sections = use_sections and "sections" in self.nlp.pipe_names
        if use_sections and not self.sections:
            logger.warning(
                "You have requested that the pipeline use annotations "
                "provided by the `section` pipeline, but it was not set. "
                "Skipping that step."
            )

    def annotate_entity(self, span: Span) -> bool:
        """
        Annotates entities.

        Parameters
        ----------
        span:
            A given span to annotate.

        Returns
        -------
        The annotation for the entity.
        """
        if self.annotation_scheme == "all":
            return all([t._.antecedent for t in span])
        elif self.annotation_scheme == "any":
            return any([t._.antecedent for t in span])
        raise KeyError(f"The annotation scheme {self.annotate_scheme} is not defined.")

    def __call__(self, doc: Doc) -> Doc:
        """
        Finds entities related to antecedents.

        Parameters
        ----------
        doc:
            spaCy Doc object

        Returns
        -------
        doc:
            spaCy Doc object, annotated for antecedents
        """

        matches = self.process(doc)

        terminations = _filter_matches(matches, "termination")
        antecedents = _filter_matches(matches, "antecedent")

        boundaries = self._boundaries(doc, terminations=terminations)

        ents = []

        if self.sections:
            ents = [
                Span(doc, section.start, section.end, label="ATCD")
                for section in doc._.sections
                if section.label_ == "antécédents"
            ]

        for start, end in boundaries:
            if self.on_ents_only and not doc[start:end].ents:
                continue

            for token in doc[start:end]:
                token._.antecedent = False

            sub_matches = [m for m in antecedents if start <= m.start < end]

            if sub_matches:
                span = Span(doc, start, end, label="ATCD")
                span._.antecedent = True
                ents.append(span)

        doc._.antecedents = ents

        for ent in ents:
            for token in ent:
                token._.antecedent = True

        for ent in doc.ents:
            ent._.antecedent = self.annotate_entity(ent)

        return doc