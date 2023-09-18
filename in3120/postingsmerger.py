#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Iterator
from .posting import Posting


class PostingsMerger:
    """
    Utility class for merging posting lists.

    It is currently left unspecified what to do with the term frequency field
    in the returned postings when document identifiers overlap. Different
    approaches are possible, e.g., an arbitrary one of the two postings could
    be returned, or the posting having the smallest/largest term frequency, or
    a new one that produces an averaged value, or something else.
    """

    @staticmethod
    def intersection(p1: Iterator[Posting], p2: Iterator[Posting]) -> Iterator[Posting]:
        
        result = []
        
        val1, val2 = next(p1, None), next(p2, None)
        
        while (val1 != None and val2 != None):
            
            if (val1.document_id == val2.document_id):
                
                result.append(val1)
                
                val1, val2 = next(p1, None), next(p2, None)
                
            elif (val1.document_id < val2.document_id):
                val1 = next(p1, None)
            
            else:
                val2 = next(p2, None)
        
        return result
            
        
        """
        A generator that yields a simple AND of two posting lists, given
        iterators over these.

        The posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        
        # raise NotImplementedError("You need to implement this as part of the assignment.")

    @staticmethod
    def union(p1: Iterator[Posting], p2: Iterator[Posting]) -> Iterator[Posting]:
        """
        A generator that yields a simple OR of two posting lists, given
        iterators over these.

        The posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        
        ids = set()
        result = []
        
        for p in p1:
            if (not p.document_id in ids):
                ids.add(p.document_id)
                result.append(p)
            
        for p in p2:
            if (not p.document_id in ids):
                ids.add(p.document_id)
                result.append(p)
        
        return sorted(result, key=lambda x: x.document_id)
        
        # raise NotImplementedError("You need to implement this as part of the assignment.")
