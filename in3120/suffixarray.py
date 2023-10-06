#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Any, Dict, Iterator, Iterable, Tuple, List
from .corpus import Corpus
from .normalizer import Normalizer
from .tokenizer import Tokenizer


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
        
        for doc_id, doc in enumerate(self.__corpus):
            assert doc_id == doc.document_id, "document_id is not equal to i"
            
            for field in fields:
                
                terms = self.__tokenizer.strings(self.__normalize(doc.get_field(field, None)))
                
                # add suffixes
                for t in terms:
                    self.__haystack.extend([ (doc_id, t[i:]) for i in range(len(t)) ])
                
        # sort suffixes
        self.__haystack.sort(key = lambda x : x[1])
        
        # iterate over suffixes
        for doc_id, suffix in self.__haystack:
            words_in_suffix = suffix.split()
            
            # add offsets to self.__suffixes
            for i in range(len(words_in_suffix)):
                self.__suffixes.append((doc_id, i))
                

    def __normalize(self, buffer: str) -> str:
        """
        Produces a normalized version of the given string. Both queries and documents need to be
        identically processed for lookups to succeed.
        """
        
        return self.__normalizer.canonicalize(buffer)

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
            
            suffix = self.__haystack[mid][1]
            
            if suffix == needle:
                return mid
            elif suffix < needle:
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
        
        # wilcard at end of query (mon*):
        # * follow b-tree for symbols (m,o,n)
        # * enumerate set W of terms with prefix mon
        # * use |W| lookups on SII to retrieve docs containing any term in W
        
        query = self.__normalize(query)
        start_pos = self.__binary_search(query)

        match_count = {}
        
        # Collect matching documents and count matches
        for i in range(start_pos, len(self.__suffixes)):
        
            if self.__haystack[i][1].startswith(query):
                
                doc_id = self.__haystack[i][0]
                match_count[doc_id] = match_count.get(doc_id, 0) + 1
        
        # Sort matches and 
        sorted_matches = sorted(match_count.items(), key=lambda x: x[1], reverse=True)
        hit_count = options.get("hit_count", None)
        
        # iterate and yield matching documents by match count
        for doc_id, score in sorted_matches[:hit_count]:
            yield {"score": score, "document": self.__corpus.get_document(doc_id)}