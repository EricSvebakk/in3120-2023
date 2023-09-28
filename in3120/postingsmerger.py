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
        """
        A generator that yields a simple AND of two posting lists, given
        iterators over these.

        The posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
        
        val1, val2 = next(p1, None), next(p2, None)
        
        while (val1 != None and val2 != None):
            
            if (val1.document_id == val2.document_id):
                yield val1
                val1, val2 = next(p1, None), next(p2, None)
                
            elif (val1.document_id < val2.document_id):
                val1 = next(p1, None)
            
            else:
                val2 = next(p2, None)
        

    @staticmethod
    def union(p1: Iterator[Posting], p2: Iterator[Posting]) -> Iterator[Posting]:
        """
        A generator that yields a simple OR of two posting lists, given
        iterators over these.

        The posting lists are assumed sorted in increasing order according
        to the document identifiers.
        """
    
        val1, val2 = next(p1, None), next(p2, None)
        
        while (val1 and val2):
            
            if (val1.document_id == val2.document_id):
                val1 = next(p1, None)
            
            elif (val1.document_id < val2.document_id):
                yield val1
                val1 = next(p1, None)
                
            else:
                yield val2
                val2 = next(p2, None)
            
        while (val1):
            yield val1
            val1 = next(p1, None)
        
        while (val2):
            yield val2
            val2 = next(p2, None)
        
        