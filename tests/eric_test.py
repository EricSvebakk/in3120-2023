
import unittest
from context import in3120


# merger = in3120.PostingsMerger()

# posting = in3120.Posting(123, 4)
# a0 = list(merger.intersection(iter([]), iter([]))), []
# a1 = list(merger.intersection(iter([]), iter([posting]))), []
# a2 = list(merger.intersection(iter([posting]), iter([]))), []
# # a3 = list(merger.union(iter([]), iter([]))), []
# a3 = None

# print("a", a0, a1, a2, a3)

# postings1 = [in3120.Posting(1, 0), in3120.Posting(2, 0), in3120.Posting(3, 0)]
# postings2 = [in3120.Posting(2, 0), in3120.Posting(3, 0), in3120.Posting(6, 0)]
# result12 = list(map(lambda p: p.document_id, merger.intersection(iter(postings1), iter(postings2))))
# result21 = list(map(lambda p: p.document_id, merger.intersection(iter(postings2), iter(postings1))))

# c1 = result12, [2, 3]
# c2 = result12, result21

# print("c", c1, c2)

# # exit()

# b1 = [p.document_id for p in merger.union(iter([]), iter([posting]))], [posting.document_id]
# b2 = [p.document_id for p in merger.union(iter([posting]), iter([]))], [posting.document_id]

# print("b", b1, b2)

# result12 = list(map(lambda p: p.document_id, merger.union(iter(postings1), iter(postings2))))
# result21 = list(map(lambda p: p.document_id, merger.union(iter(postings2), iter(postings1))))

# d1 = result12, [1, 2, 3, 6]
# d2 = result12, result21

# print("d", d1, d2)

# ======

normalizer = in3120.SimpleNormalizer()
tokenizer = in3120.SimpleTokenizer()
compressed = False  # Compression disabled.

corpus = in3120.InMemoryCorpus()
corpus.add_document(in3120.InMemoryDocument(0, {"body": "this is a Test"}))
corpus.add_document(in3120.InMemoryDocument(1, {"body": "test TEST prØve"}))


d1 = list(map(lambda x: x.get_field("body", None), corpus))
index = in3120.InMemoryInvertedIndex(corpus, ["body"], normalizer, tokenizer, compressed)

print("d body", d1)
print("d indx", index)
print()

a1 = list(index.get_terms("PRøvE wtf tesT"))
a2 = ["prøve", "wtf", "test"]

print("a", a1, a2, a1 == a2, "\n")

b1 = [(p.document_id, p.term_frequency) for p in index["prøve"]], [(1, 1)]
b2 = [(p.document_id, p.term_frequency) for p in index.get_postings_iterator("wtf")], []
b3 = [(p.document_id, p.term_frequency) for p in index["test"]], [(0, 1), (1, 2)]
print("b", b1, b2, b3, "\n")

c1 = index.get_document_frequency("wtf"), 0
c2 = index.get_document_frequency("prøve"), 1
c3 = index.get_document_frequency("test"), 2
print("c", c1, c2, c3, "\n")