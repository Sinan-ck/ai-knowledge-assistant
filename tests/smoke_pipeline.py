from app.rag.pipeline import answer

for q in [
    "What is the refund policy?",
    "How much attendance do I need for placement assistance?",
    "Can I combine the early-bird discount with a scholarship?",
    "Do I need my own laptop?",
    "What is the capital of France?",
]:
    r = answer(q)
    print(f"\nQ: {q}\nA: {r['answer']}")
    for s in r["sources"]:
        print(f"   - {s['source']} p{s['page']} ({s['score']})")
        