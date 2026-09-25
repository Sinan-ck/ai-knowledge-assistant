import json
from app.rag.embeddings import search

MIN_OLD = 0.25
MIN_NEW = 0.15
RELATIVE_CUTOFF = 0.7

def filtered(hits, min_score):
    good = [h for h in hits if h['score'] >= min_score]
    if not good:
        return []
    best = good[0]['score']
    return [h for h in good if h['score'] >= best * RELATIVE_CUTOFF]

q = "What is the early-bird discount?"
hits = search(q)

print("All retrieved chunks (score, source, page):")
for h in hits:
    print(" ", h['score'], h['metadata']['source'], h['metadata']['page'])

for label, min_score in [("OLD (0.25)", MIN_OLD), ("NEW (0.15)", MIN_NEW)]:
    kept = filtered(hits, min_score)
    kept_sources = [(h['metadata']['source'], h['metadata']['page']) for h in kept]
    has_answer_chunk = ('02_fee_structure.pdf', 1) in kept_sources
    print()
    print(label, "-> kept chunks:", kept_sources, "| answer chunk included:", has_answer_chunk)
