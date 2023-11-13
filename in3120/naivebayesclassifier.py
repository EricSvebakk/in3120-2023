#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Any, Dict, Iterable, Iterator
from .dictionary import InMemoryDictionary
from .normalizer import Normalizer
from .tokenizer import Tokenizer
from .corpus import Corpus
import math

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

        print()
        # Train the classifier, i.e., estimate all probabilities.
        self.__compute_priors(training_set)
        self.__compute_vocabulary(training_set, fields)
        self.__compute_posteriors(training_set, fields)


    # The probability of seeing a class regardless of the term
    def __compute_priors(self, training_set: Dict[str, Corpus]):
        """
        Estimates all prior probabilities needed for the naive Bayes classifier.
        """
        
        total_docs = sum([corpus.size() for corpus in training_set.values()])
        
        print("\ncompute_priors:")
        # 
        for key, corpus in training_set.items():
            
            self.__priors[key] = corpus.size() / total_docs
            
            print(key, self.__priors[key])
        
        
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

    # 
    def __compute_posteriors(self, training_set, fields):
        """
        Estimates all conditional probabilities needed for the naive Bayes classifier.
        """
        print("\ncompute_posterior:")
                
        for cat_name, corpus in training_set.items():
            terms = []
            
            # compute terms
            for doc in corpus:
                for field in fields:
                    terms.extend(self.__get_terms(doc.get_field(field, None)))
            
            self.__denominators[cat_name] = len(terms) + self.__vocabulary.size()
            
            # 
            self.__conditionals[cat_name] = dict()
            
            c = Counter(terms)
            
            for term in terms:

                self.__conditionals[cat_name][term] = (c.get(term, 0) + 1) / self.__denominators[cat_name]
                print(self.__conditionals[cat_name][term], c.get(term, 0), self.__denominators[cat_name], term)


    # 
    def __get_terms(self, buffer) -> list[str]:
        """
        Processes the given text buffer and returns the sequence of normalized
        terms as they appear. Both the documents in the training set and the buffers
        we classify need to be identically processed.
        """
        
        tokens = self.__tokenizer.strings(self.__normalizer.canonicalize(buffer))
        return list(self.__normalizer.normalize(t) for t in tokens)
        
        # return [ x for x in self.__tokenizer.strings(self.__normalizer.canonicalize(buffer))]
     

    def classify(self, buffer: str) -> Iterator[Dict[str, Any]]:
        """
        Classifies the given buffer according to the multinomial naive Bayes rule. The computed (score, category) pairs
        are emitted back to the client via the supplied callback sorted according to the scores. The reported scores
        are log-probabilities, to minimize numerical underflow issues. Logarithms are base e.

        The results yielded back to the client are dictionaries having the keys "score" (float) and
        "category" (str).
        """
        
        print("\nclassify:")
        
        # remove terms that are not in vocab
        terms = [term for term in self.__get_terms(buffer) if term in self.__vocabulary] 
        scores =  self.__priors.copy()
        
        print(scores)
        
        for cat_name in self.__priors.keys():
            
            scores[cat_name] = math.log(scores[cat_name])
            default_val = 1 / self.__denominators[cat_name]
            
            for term in terms:
                
                scores[cat_name] += math.log(self.__conditionals[cat_name].get(term, default_val))
                
                print(term, self.__conditionals[cat_name].get(term, default_val), default_val)
                # if self.__conditionals[cat_name].get(term, None):
                #     scores[cat_name] += math.log(self.__conditionals[cat_name].get(term))
                # else:
                #     scores[cat_name] += default_val
                
                
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        for key, val in sorted_scores:
            yield {"score": val, "category": key}