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
      
      for i, c in enumerate(self.__corpus):
          assert i == c.document_id, "document_id is not equal to i"

          terms = []
          for f in fields:
            terms.extend(self.get_terms(c.get_field(f, None)))

          for k, v in Counter(terms).items():
              
              term_id = self.__dictionary.add_if_absent(k)

              if len(self.__posting_lists) == term_id:
                  self.__posting_lists.append(compressed and CompressedInMemoryPostingList() or InMemoryPostingList())

              self.__posting_lists[term_id].append_posting(Posting(i, v))


    # done
    def get_terms(self, buffer: str) -> Iterator[str]:
        
        n = self.__normalizer.normalize(buffer)
        n = self.__normalizer.canonicalize(n)
        t = self.__tokenizer.strings(n)
        i = iter(t)

        return i

    #  
    def get_postings_iterator(self, term: str) -> Iterator[Posting]:
        
        # print(self.__dictionary.get_term_id(term))
        # print("term:", term, end="")
        
        if (id := self.__dictionary.get_term_id(term) != None):
            # print("yes.", term)
            return iter(self.__posting_lists[id])
        # print()
        
        return []
    
        # raise NotImplementedError("You need to implement this as part of the assignment.")

    # 
    def get_document_frequency(self, term: str) -> int:
        
        id = self.__dictionary.get_term_id(term)
        
        if (id != None):
            return len(self.__posting_lists[id])
        
        return 0
        # raise NotImplementedError("You need to implement this as part of the assignment.")