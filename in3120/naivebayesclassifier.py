#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Any, Dict, Iterable, Iterator
from .dictionary import InMemoryDictionary
from .normalizer import Normalizer
from .tokenizer import Tokenizer
from .corpus import Corpus

from collections import Counter

class NaiveBayesClassifier:
    """
    Defines a multinomial naive Bayes text classifier.
    """

    def __init__(self, training_set: Dict[str, Corpus], fields: Iterable[str],
                 normalizer: Normalizer, tokenizer: Tokenizer):
        """
        Constructor. Trains the classifier from the named fields in the documents in
        the given training set.
        """
        # Used for breaking the text up into discrete classification features.
        self.__normalizer = normalizer
        self.__tokenizer = tokenizer

        # The vocabulary we've seen during training.
        self.__vocabulary = InMemoryDictionary()

        # Maps a category c to the prior probability Pr(c).
        self.__priors: Dict[str, float] = {}

        # Maps a category c and a term t to the conditional probability Pr(t | c).
        self.__conditionals: Dict[str, Dict[str, float]] = {}

        # Maps a category c to the denominator used when doing Laplace smoothing.
        self.__denominators: Dict[str, int] = {}

        # Train the classifier, i.e., estimate all probabilities.
        self.__compute_priors(training_set)
        self.__compute_vocabulary(training_set, fields)
        self.__compute_posteriors(training_set, fields)


    # The probability of seeing a class regardless of the term
    def __compute_priors(self, training_set: Dict[str, Corpus]):
        """
        Estimates all prior probabilities needed for the naive Bayes classifier.
        """
        
        # 
        # category_size = [(key, len(corpus)) for key, corpus in training_set.items()]
        # total_size = sum(map(lambda x: x[1], category_size))
        
        # 
        # category_size2 = [(key, corpus.size()) for key, corpus in training_set.items()]
        # total_siz2 = sum(map(lambda x: x[1], category_size2))
        
        # 
        for key, corpus in training_set.items():
            
            # print("key", key)
            
            self.__denominators[key] = corpus.size()
        
        
    # 
    def __compute_vocabulary(self, training_set: Dict[str, Corpus], fields: Iterable[str]):
        """
        Builds up the overall vocabulary as seen in the training set.
        """
        
        for corpus in training_set.values():
            for doc in corpus:
                for field in fields:
                    for x in self.__get_terms(doc.get_field(field, None)):
                        
                        self.__vocabulary.add_if_absent(x)
                    
        # print(self.__vocabulary)


    # 
    def __compute_posteriors(self, training_set, fields):
        """
        Estimates all conditional probabilities needed for the naive Bayes classifier.
        """
        
        # vocab_size = self.__vocabulary.size()
        
        for key, corpus in training_set.items():
            for doc in corpus:
                for field in fields:

                    terms = self.__get_terms(doc.get_field(field, None))
                    
                    c = Counter(terms)
                    
                    # self.__denominators[key] = len(terms) + vocab_size
                    self.__conditionals[key] = dict()
                    
                    for term in terms:
                    
                        result = (c[term] + 1) / self.__denominators[key]
                        self.__conditionals[key][term] = result
        
        # print(self.__conditionals)


    # 
    def __get_terms(self, buffer) -> list[str]:
        """
        Processes the given text buffer and returns the sequence of normalized
        terms as they appear. Both the documents in the training set and the buffers
        we classify need to be identically processed.
        """
        
        return [ x for x in self.__tokenizer.strings(self.__normalizer.canonicalize(buffer))]
     

    def classify(self, buffer: str) -> Iterator[Dict[str, Any]]:
        """
        Classifies the given buffer according to the multinomial naive Bayes rule. The computed (score, category) pairs
        are emitted back to the client via the supplied callback sorted according to the scores. The reported scores
        are log-probabilities, to minimize numerical underflow issues. Logarithms are base e.

        The results yielded back to the client are dictionaries having the keys "score" (float) and
        "category" (str).
        """
        
        # use terms somehow
        terms = self.__get_terms(buffer)
        scores = self.__priors.copy()
        
        for cat_name in self.__priors.keys():
            for cat in self.__conditionals.values():
                
                for cat_term_value in cat.values():
            
                    scores[cat_name] += cat_term_value
                
                yield {"score": scores[cat_name], "category": cat_name}
        
        # print(scores)
        
        # return scores
        
        # raise NotImplementedError("You need to implement this as part of the assignment.")
