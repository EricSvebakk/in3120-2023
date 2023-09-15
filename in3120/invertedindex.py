#!/usr/bin/python
# -*- coding: utf-8 -*-

import itertools
from abc import ABC, abstractmethod
from collections import Counter
from typing import Iterable, Iterator, List
from .dictionary import InMemoryDictionary
from .normalizer import Normalizer
from .tokenizer import Tokenizer
from .corpus import Corpus
from .posting import Posting
from .postinglist import CompressedInMemoryPostingList, InMemoryPostingList, PostingList


class InvertedIndex(ABC):
    """
    Abstract base class for a simple inverted index.
    """

    def __getitem__(self, term: str) -> Iterator[Posting]:
        return self.get_postings_iterator(term)

    def __contains__(self, term: str) -> bool:
        return self.get_document_frequency(term) > 0

    @abstractmethod
    def get_terms(self, buffer: str) -> Iterator[str]:
        """
        Processes the given text buffer and returns an iterator that yields normalized
        terms as they are indexed. Both query strings and documents need to be
        identically processed.
        """
        pass

    @abstractmethod
    def get_postings_iterator(self, term: str) -> Iterator[Posting]:
        """
        Returns an iterator that can be used to iterate over the term's associated
        posting list. For out-of-vocabulary terms we associate empty posting lists.
        """
        pass

    @abstractmethod
    def get_document_frequency(self, term: str) -> int:
        """
        Returns the number of documents in the indexed corpus that contains the given term.
        """
        pass


class InMemoryInvertedIndex(InvertedIndex):
    """
    A simple in-memory implementation of an inverted index, suitable for small corpora.

    In a serious application we'd have configuration to allow for field-specific NLP,
    scale beyond current memory constraints, have a positional index, and so on.

    If index compression is enabled, only the posting lists are compressed. Dictionary
    compression is currently not supported.
    """

    def __init__(
        self,
        corpus: Corpus,
        fields: Iterable[str],
        normalizer: Normalizer,
        tokenizer: Tokenizer,
        compressed: bool = False,
    ):
        self.__corpus = corpus
        self.__normalizer = normalizer
        self.__tokenizer = tokenizer
        self.__posting_lists: List[PostingList] = []
        self.__dictionary = InMemoryDictionary()
        self.__build_index(fields, compressed)

    def __repr__(self):
        # print("hey")
        # for (term, term_id) in self.__dictionary:
        #     print(term, term_id)
        
        return str({term: list(self.__posting_lists[term_id]) for (term, term_id) in self.__dictionary})

    def __build_index(self, fields: Iterable[str], compressed: bool) -> None:
        
        for c in self.__corpus:
        
            for f in fields:
        
                phrase = c.get_field(f, None)
                
                terms = list(self.get_terms(phrase))
                
                x = Counter(terms)
                
                print("xc", list(x.elements()))
                
                for t in terms:
                    id = self.__dictionary.add_if_absent(t)
                    
                    if (len(self.__posting_lists) == id):
                        self.__posting_lists.append(InMemoryPostingList())
                    
                    p = Posting(id, x.get(t))
                    
                    x1 = len(self.__posting_lists) == 0
                    x2 = p
                    x3 = self.__posting_lists[len(self.__posting_lists)-1].get_iterator()
                    x4 = list(x3)
                    # x2 = self.__posting_lists[id].get_iterator()
                    
                    print("x", x1, x2, x4)
                    
                    self.__posting_lists[id].append_posting(p)
                    
        print("pl", list(map(lambda x: x, self.__posting_lists)))
        print()


    # done
    def get_terms(self, buffer: str) -> Iterator[str]:
        
        n = self.__normalizer.normalize(buffer)
        t = self.__tokenizer.strings(n)
        i = iter(t)

        return i

    #  
    def get_postings_iterator(self, term: str) -> Iterator[Posting]:
        
        if (id := self.__dictionary.get_term_id(term)):
            print("yes.", term)
            return iter(self.__posting_lists[id])
        
        return []
    
        # raise NotImplementedError("You need to implement this as part of the assignment.")

    # 
    def get_document_frequency(self, term: str) -> int:
        pass
        # raise NotImplementedError("You need to implement this as part of the assignment.")