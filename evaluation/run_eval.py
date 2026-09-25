import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.pipeline import answer

questions = json.loads((Path(__file__).parent / "questions.json").read_text())
rows, t0 = [], time.time()

for item in questions:
    start = time.time()
    r = answer(item["q"])
    secs = time.time() - start

    if item.get("refuse"):
        ok = r["refused"]
        note = "correctly refused" if ok else "SHOULD HAVE REFUSED"
    else:
        text = r["answer"].lower()
        hit_kw = all(k.lower() in text for k in item["keywords"])
        hit_src = any(s["source"] == item["source"] for s in r["sources"])
        ok = hit_kw and hit_src and not r["refused"]
        note = f"keywords={'ok' if hit_kw else 'MISSING'} source={'ok' if hit_src else 'WRONG'}"

    rows.append({"q": item["q"], "ok": ok, "note": note, "secs": round(secs, 1), "answer": r["answer"][:150]})
    print(f"{'PASS' if ok else 'FAIL'} | {secs:4.1f}s | {item['q']} | {note}")

passed = sum(r["ok"] for r in rows)
print(f"\nScore: {passed}/{len(rows)} ({100 * passed / len(rows):.0f}%) in {time.time() - t0:.0f}s")

out = Path(__file__).parent / "results.json"
out.write_text(json.dumps(rows, indent=2))
print(f"Details saved to {out}")
