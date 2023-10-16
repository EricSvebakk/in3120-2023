#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import Counter
from typing import Iterator, Dict, Any
from .sieve import Sieve
from .ranker import Ranker
from .corpus import Corpus
from .invertedindex import InvertedIndex


class SimpleSearchEngine:
    """
    Realizes a simple query evaluator that efficiently performs N-of-M matching over an inverted index.
    I.e., if the query contains M unique query terms, each document in the result set should contain at
    least N of these m terms. For example, 2-of-3 matching over the query 'orange apple banana' would be
    logically equivalent to the following predicate:

       (orange AND apple) OR (orange AND banana) OR (apple AND banana)
       
    Note that N-of-M matching can be viewed as a type of "soft AND" evaluation, where the degree of match
    can be smoothly controlled to mimic either an OR evaluation (1-of-M), or an AND evaluation (M-of-M),
    or something in between.

    The evaluator uses the client-supplied ratio T = N/M as a parameter as specified by the client on a
    per query basis. For example, for the query 'john paul george ringo' we have M = 4 and a specified
    threshold of T = 0.7 would imply that at least 3 of the 4 query terms have to be present in a matching
    document.
    """

    def __init__(self, corpus: Corpus, inverted_index: InvertedIndex):
        self.__corpus = corpus
        self.__inverted_index = inverted_index

    def evaluate(self, query: str, options: dict, ranker: Ranker) -> Iterator[Dict[str, Any]]:
        """
        Evaluates the given query, doing N-out-of-M ranked retrieval. I.e., for a supplied query having M
        unique terms, a document is considered to be a match if it contains at least N <= M of those terms.

        The matching documents, if any, are ranked by the supplied ranker, and only the "best" matches are yielded
        back to the client as dictionaries having the keys "score" (float) and "document" (Document).

        The client can supply a dictionary of options that controls the query evaluation process: The value of
        N is inferred from the query via the "match_threshold" (float) option, and the maximum number of documents
        to return to the client is controlled via the "hit_count" (int) option.
        """
        
        
        # all terms in query
        query_terms = self.__inverted_index.get_terms(query)
        
        unique_query_terms = list(Counter(query_terms).items())
        
        m = len(unique_query_terms)
        
        # calculate n from m and t
        n = max(1, min(m, int(options["match_threshold"] * m)))
        
        # posting => (doc_id, term_frequency)
        
        posting_lists = [self.__inverted_index.get_postings_iterator(a) for (a,b) in unique_query_terms ]  
        
        # move pointers in posting_lists
        all_cursors = [next(p, None) for p in posting_lists]
        
        # all cursors that remain (not None)
        active_cursors = [cursor for cursor in all_cursors if cursor != None]
        
        # when all valid docs are found: score, rank, yield
        sieve = Sieve(options["hit_count"])
        
        
        
        # remaining_cursor_ids >= n
        while len(active_cursors) >= n:
            
            # determine lowest frontier
            doc_id = min([ x.document_id for x in active_cursors ])
            frontier = [ p for p in active_cursors if p.document_id == doc_id ]
            
            if (len(frontier) >= n):
            
                # rank each document
                # for c in active_cursors:
                ranker.reset(doc_id)
                
                # rank document using ranker
                for (terms, multiplicity), p in zip(unique_query_terms, all_cursors):
                    
                    if (p and p.document_id == doc_id):
                        
                        ranker.update(terms, multiplicity, p)
                
                sieve.sift(ranker.evaluate(), doc_id)
                
                
            for i, (posting, posting_list) in enumerate(zip(all_cursors, posting_lists)):
                
                if (posting and posting.document_id == doc_id):
                    
                    all_cursors[i] = next(posting_list, None)
                
                active_cursors = [ p for p in all_cursors if p ]
                
            #==INVARIANT==# active_cursors only contains N-of-M matched postings
            
            # move lowest frontier (cursor with the lowest index)
            # move all frontiers that points to the same document as the lowest frontier
            # for i, pl in enumerate(posting_lists):
                
            #     if (pl != None and all_cursors[i].document_id == doc_id):
            #         posting_lists[i] = next(pl, None)
            #     # else:
            #     #     pl
                
            # all_cursors = [ (next(pl, None) if (pl != None and pl.document_id == doc_id) else pl) for pl in posting_lists ]
            
            # all cursors that remain (not None)
            # active_cursors_ids = [cursor for cursor in all_cursors if cursor != None]
        
        
        
        
        for w in sieve.winners():
            yield {"score": w[0], "document": self.__corpus[w[1]]}
        
        
        
        