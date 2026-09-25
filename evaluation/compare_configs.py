import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.pipeline import answer

questions = json.loads((Path(__file__).parent / "questions.json").read_text())
CONFIGS = [4, 8]  # top_k values to compare

all_results = {}

for top_k in CONFIGS:
    print(f"\n=== TOP_K = {top_k} ===")
    rows, t0 = [], time.time()

    for item in questions:
        start = time.time()
        r = answer(item["q"], top_k=top_k)
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

        rows.append({
            "q": item["q"], "ok": ok, "note": note,
            "secs": round(secs, 2), "n_sources": len(r["sources"]),
        })
        print(f"{'PASS' if ok else 'FAIL'} | {secs:5.2f}s | sources={len(r['sources'])} | {item['q']} | {note}")

    passed = sum(r["ok"] for r in rows)
    total_time = time.time() - t0
    avg_latency = sum(r["secs"] for r in rows) / len(rows)
    avg_sources = sum(r["n_sources"] for r in rows) / len(rows)

    summary = {
        "top_k": top_k,
        "passed": passed,
        "total": len(rows),
        "pass_rate": round(100 * passed / len(rows), 1),
        "avg_latency_secs": round(avg_latency, 2),
        "avg_sources_per_answer": round(avg_sources, 1),
        "total_run_secs": round(total_time, 1),
        "rows": rows,
    }
    all_results[f"top_k_{top_k}"] = summary
    print(f"\nTOP_K={top_k}: {passed}/{len(rows)} ({summary['pass_rate']}%) | "
          f"avg latency {summary['avg_latency_secs']}s | avg sources {summary['avg_sources_per_answer']}")

out = Path(__file__).parent / "config_comparison.json"
out.write_text(json.dumps(all_results, indent=2))

print("\n" + "=" * 50)
print("COMPARISON SUMMARY")
print("=" * 50)
for key, s in all_results.items():
    print(f"{key}: {s['passed']}/{s['total']} ({s['pass_rate']}%) | "
          f"avg {s['avg_latency_secs']}s/question | avg {s['avg_sources_per_answer']} sources")
print(f"\nFull details saved to {out}")
