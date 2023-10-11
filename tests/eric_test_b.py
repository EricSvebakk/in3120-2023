#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from context import in3120
import tracemalloc
import inspect



normalizer = in3120.SimpleNormalizer()
tokenizer = in3120.SimpleTokenizer()

# ===========================================
def process_query_and_verify_winner(engine, query, winners, score):
	options = {"debug": True, "hit_count": 5, "winners": winners}
	matches = list(engine.evaluate(query, options))

	# for i in engine.evaluate(query, options):
	# 	print("i", i)
	# print(query, matches)
	print("query :", f"'{query}'")
	print("len   :", len(matches), 5 >= len(matches) and len(matches) >= 1)
	# print("check :", 5, ">=",  len(matches), ">=", 1, 5 >= len(matches) and len(matches) >= 1)
	print("scores:")
	for m in matches:
		print(m["score"], end=" ")
		print(m["document"].document_id in winners)
		
	print()
	
	# print("result:", matches[0]["document"].document_id, "in", winners, "=", matches[0]["document"].document_id in winners)
	# print()

	# print(matches)	


# test_canonicalized_corpus ===========================================
print("A")
corpus = in3120.InMemoryCorpus()
corpus.add_document(in3120.InMemoryDocument(corpus.size(), {"a": "Japanese リンク"}))
corpus.add_document(in3120.InMemoryDocument(corpus.size(), {"a": "Cedilla \u0043\u0327 and \u00C7 foo"}))
engine = in3120.SuffixArray(corpus, ["a"], normalizer, tokenizer)
process_query_and_verify_winner(engine, "ﾘﾝｸ", [0], 1)  # Should match "リンク".
process_query_and_verify_winner(engine, "\u00C7", [1], 2)  # Should match "\u0043\u0327".



# test_cran_corpus ===========================================
print("B")
corpus = in3120.InMemoryCorpus("../data/cran.xml")
engine = in3120.SuffixArray(corpus, ["body"], normalizer, tokenizer)
process_query_and_verify_winner(engine, "visc", [328], 11)
process_query_and_verify_winner(engine, "Of  A", [946], 10)
# process_query_and_verify_winner(engine, "", [], None)
# process_query_and_verify_winner(engine, "approximate solution", [159, 1374], 3)

# test_memory_usage ===========================================
# corpus = in3120.InMemoryCorpus()
# corpus.add_document(in3120.InMemoryDocument(0, {"a": "o  o\n\n\no\n\no", "b": "o o\no   \no"}))
# corpus.add_document(in3120.InMemoryDocument(1, {"a": "ba", "b": "b bab"}))
# corpus.add_document(in3120.InMemoryDocument(2, {"a": "o  o O o", "b": "o o"}))
# corpus.add_document(in3120.InMemoryDocument(3, {"a": "oO" * 10000, "b": "o"}))
# corpus.add_document(in3120.InMemoryDocument(4, {"a": "cbab o obab O ", "b": "o o " * 10000}))
# tracemalloc.start()
# snapshot1 = tracemalloc.take_snapshot()
# engine = in3120.SuffixArray(corpus, ["a", "b"], normalizer, tokenizer)
# snapshot2 = tracemalloc.take_snapshot()
# tracemalloc.stop()

# test_multiple_fields ===========================================
# corpus = in3120.InMemoryCorpus()
# corpus.add_document(in3120.InMemoryDocument(0, {"field1": "a b c", "field2": "b c d"}))
# corpus.add_document(in3120.InMemoryDocument(1, {"field1": "x", "field2": "y"}))
# corpus.add_document(in3120.InMemoryDocument(2, {"field1": "y", "field2": "z"}))
# engine0 = in3120.SuffixArray(corpus, ["field1", "field2"], normalizer, tokenizer)
# engine1 = in3120.SuffixArray(corpus, ["field1"], normalizer, tokenizer)
# engine2 = in3120.SuffixArray(corpus, ["field2"], normalizer, tokenizer)
# process_query_and_verify_winner(engine0, "b c", [0], 2)
# process_query_and_verify_winner(engine0, "y", [1, 2], 1)
# process_query_and_verify_winner(engine1, "x", [1], 1)
# process_query_and_verify_winner(engine1, "y", [2], 1)
# process_query_and_verify_winner(engine1, "z", [], None)
# process_query_and_verify_winner(engine2, "z", [2], 1)

# test_uses_yield ===========================================
# import types
# corpus = in3120.InMemoryCorpus()
# corpus.add_document(in3120.InMemoryDocument(0, {"a": "the foo bar"}))
# engine = in3120.SuffixArray(corpus, ["a"], normalizer, tokenizer)
# matches = engine.evaluate("foo", {})

