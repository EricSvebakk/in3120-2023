#!/usr/bin/python
# -*- coding: utf-8 -*-

from .ranker import Ranker
from .corpus import Corpus
from .posting import Posting
from .invertedindex import InvertedIndex
import math


class BetterRanker(Ranker):
    """
    A ranker that does traditional TF-IDF ranking, possibly combining it with
    a static document score (if present).

    The static document score is assumed accessible in a document field named
    "static_quality_score". If the field is missing or doesn't have a value, a
    default value of 0.0 is assumed for the static document score.

    See Section 7.1.4 in https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf.
    """

    def __init__(self, corpus: Corpus, inverted_index: InvertedIndex):
        self._score = 0.0
        self._document_id = None
        self._corpus = corpus
        self._inverted_index = inverted_index
        self._dynamic_score_weight = 1.0  # TODO: Make this configurable.
        self._static_score_weight = 1.0  # TODO: Make this configurable.
        self._static_score_field_name = "static_quality_score"  # TODO: Make this configurable.

    def reset(self, document_id: int) -> None:
        self._document_id = document_id
        self._score = 0
        

    def update(self, term: str, multiplicity: int, posting: Posting) -> None:
        
        assert self._document_id == posting.document_id, "document_id does not match"
        
        tf = posting.term_frequency
        df = self._inverted_index.get_document_frequency(term)
        N = len(self._corpus)
        idf = math.log(N/df) # 1/df => N/df
        
        tf_idf = tf * idf
        
        dynamic_score = tf_idf * multiplicity
        self._score += dynamic_score

    def evaluate(self) -> float:
        
        document = self._corpus.get_document(self._document_id)
        static_score = document.get_field(self._static_score_field_name, self._static_score_weight)
        
        return self._score * static_score
