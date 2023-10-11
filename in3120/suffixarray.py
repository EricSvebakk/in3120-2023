#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Any, Dict, Iterator, Iterable, Tuple, List
from .corpus import Corpus
from .normalizer import Normalizer
from .tokenizer import Tokenizer
from .sieve import Sieve


class SuffixArray:
    """
    A simple suffix array implementation. Allows us to conduct efficient substring searches.
    The prefix of a suffix is an infix!

    In a serious application we'd make use of least common prefixes (LCPs), pay more attention
    to memory usage, and add more lookup/evaluation features.
    """

    def __init__(self, corpus: Corpus, fields: Iterable[str], normalizer: Normalizer, tokenizer: Tokenizer):
        self.__corpus = corpus
        self.__normalizer = normalizer
        self.__tokenizer = tokenizer
        self.__haystack: List[Tuple[int, str]] = []  # The (<document identifier>, <searchable content>) pairs.
        self.__suffixes: List[Tuple[int, int]] = []  # The sorted (<haystack index>, <start offset>) pairs.
        self.__build_suffix_array(fields)  # Construct the haystack and the suffix array itself.

    def __build_suffix_array(self, fields: Iterable[str]) -> None:
        """
        Builds a simple suffix array from the set of named fields in the document collection.
        The suffix array allows us to search across all named fields in one go.
        """
        
        self.__haystack = [ (doc.document_id, self.__normalize("".join([ doc.get_field(field, None) for field in fields ]))) for doc in self.__corpus ]
        self.__suffixes = [ (h_id, t_start+i) for h_id, searchable_content in self.__haystack for tok, (t_start, _) in self.__tokenizer.tokens(searchable_content) for i in range(len(tok))]
        
        # ADD HAYSTACKS
        # for doc in self.__corpus:
        #     con = "".join([ doc.get_field(field, None) for field in fields ])
        #     res = (doc.document_id, self.__normalize(con))
        #     self.__haystack.append(res)
        
        # ADD SUFFIXES
        # for h_id, searchable_content in self.__haystack:
        #     for t_start, t_end in self.__tokenizer.ranges(searchable_content):
        #         for i in range(t_start, t_end):
        #             self.__suffixes.append((h_id, i))
        
        # sorts suffixes
        self.__suffixes.sort(key = lambda x : self.__find_token(x[0], x[1]))
        
    def __find_token(self, doc_id: int, offset: int, end = None) -> str:
        if (end):
            return self.__haystack[doc_id][1][offset:end]
        return self.__haystack[doc_id][1][offset:]

    def __normalize(self, buffer: str) -> str:
        """
        Produces a normalized version of the given string. Both queries and documents need to be
        identically processed for lookups to succeed.
        """
        
        return self.__normalizer.normalize(self.__normalizer.canonicalize(buffer))

    def __binary_search(self, needle: str) -> int:
        """
        Does a binary search for a given normalized query (the needle) in the suffix array (the haystack).
        Returns the position in the suffix array where the normalized query is either found, or, if not found,
        should have been inserted.

        Kind of silly to roll our own binary search instead of using the bisect module, but seems needed
        prior to Python 3.10 due to how we represent the suffixes via (index, offset) tuples. Version 3.10
        added support for specifying a key.
        """
        
        low, high = 0, len(self.__suffixes) - 1
            
        while low <= high:
            mid = (low + high) // 2
            
            suffix = self.__suffixes[mid]
            tok = self.__find_token(suffix[0], suffix[1])
            
            if tok == needle:
                return mid
            elif tok < needle:
                low = mid + 1
            else:
                high = mid - 1
        
        return low

    def evaluate(self, query: str, options: dict) -> Iterator[Dict[str, Any]]:
        """
        Evaluates the given query, doing a "phrase prefix search".  E.g., for a supplied query phrase like
        "to the be", we return documents that contain phrases like "to the bearnaise", "to the best",
        "to the behemoth", and so on. I.e., we require that the query phrase starts on a token boundary in the
        document, but it doesn't necessarily have to end on one.

        The matching documents are ranked according to how many times the query substring occurs in the document,
        and only the "best" matches are yielded back to the client. Ties are resolved arbitrarily.

        The client can supply a dictionary of options that controls this query evaluation process: The maximum
        number of documents to return to the client is controlled via the "hit_count" (int) option.

        The results yielded back to the client are dictionaries having the keys "score" (int) and
        "document" (Document).
        """
        
        query = self.__normalize(query)
        start_pos = self.__binary_search(query)
        
        matches = {}
        sieve = Sieve(len(self.__suffixes))
        
        # Collect matching documents and count matches
        for i in range(start_pos, len(self.__suffixes)):
            hi, so = self.__suffixes[i]
            
            to_be_checked = self.__find_token(hi, so, so+len(query))
            
            # if start of suffix == query
            if to_be_checked == query:
                
                # if first match
                if (not matches.get(hi, None)):
                    matches[hi] = {
                        "score": 0,
                        "document": self.__corpus[hi]
                    }
                
                matches[hi]["score"] += 1
        
                sieve.sift(matches[hi]["score"], hi)
        
        
        winners = sieve.winners()
        
        # TODO: LIMIT ITERATOR TO HIT_COUNT
        # counter = options.get("hit_count", len(list(winners)))
        # winners = iter(winners[:counter])
        
        for w in winners:
            yield {"score":w[0], "document":self.__corpus[w[1]]}
        