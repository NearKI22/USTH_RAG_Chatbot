"""
ablation_study.py
=================
Compares different RAG retrieval configurations (Ablation Study).

Experiment A — Effect of chunk count (k):
    k = 3, 4, 6, 8  using Similarity Search

Experiment B — Effect of search strategy:
    k = 6, Similarity Search  (current production config)
    k = 6, MMR (Maximal Marginal Relevance)

Usage:
    cd ai_service
    python ablation_study.py

Results are saved to: ablation_results.txt
Estimated runtime: 5-10 minutes (multiple Gemini Embedding API calls)
"""

import os
import math
import time
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# TEST CASES — same 20 queries used in evaluate_retrieval.py
TEST_CASES = [
    {"query": "Điểm chuẩn ngành Khoa học máy tính USTH năm 2024 là bao nhiêu?",
     "keywords": ["điểm chuẩn", "khoa học máy tính", "usth", "2024"]},
    {"query": "USTH có ký túc xá cho sinh viên không?",
     "keywords": ["ký túc xá", "usth", "sinh viên"]},
    {"query": "USTH đào tạo ngành nào bằng tiếng Anh?",
     "keywords": ["tiếng anh", "usth", "đào tạo", "ngành"]},
    {"query": "Hotline tuyển sinh USTH là số nào?",
     "keywords": ["hotline", "usth", "tuyển sinh", "liên hệ", "điện thoại"]},
    {"query": "USTH có ưu tiên cho thí sinh người dân tộc thiểu số không?",
     "keywords": ["dân tộc", "thiểu số", "ưu tiên", "usth"]},
    {"query": "Học phí một năm tại HUST là bao nhiêu?",
     "keywords": ["học phí", "hust", "bách khoa"]},
    {"query": "Điểm chuẩn ngành Công nghệ thông tin HUST 2024?",
     "keywords": ["công nghệ thông tin", "hust", "điểm chuẩn", "2024"]},
    {"query": "HUST có ngành Cơ điện tử không, điểm chuẩn bao nhiêu?",
     "keywords": ["cơ điện tử", "hust", "điểm chuẩn"]},
    {"query": "FTU có ngành Kinh tế quốc tế không?",
     "keywords": ["kinh tế quốc tế", "ftu", "ngoại thương"]},
    {"query": "FTU có học bổng cho sinh viên giỏi không?",
     "keywords": ["học bổng", "ftu", "sinh viên giỏi", "ngoại thương"]},
    {"query": "FTU cơ sở Hà Nội đào tạo những ngành gì?",
     "keywords": ["ftu", "hà nội", "ngành", "đào tạo"]},
    {"query": "NEU xét tuyển theo phương thức nào năm 2024?",
     "keywords": ["xét tuyển", "neu", "kinh tế quốc dân", "phương thức"]},
    {"query": "Quy trình nộp hồ sơ tuyển sinh NEU như thế nào?",
     "keywords": ["hồ sơ", "nộp", "neu", "tuyển sinh"]},
    {"query": "NEU có chương trình liên kết quốc tế không?",
     "keywords": ["quốc tế", "liên kết", "neu", "chương trình"]},
    {"query": "Điều kiện xét tuyển thẳng vào NEU?",
     "keywords": ["xét tuyển thẳng", "neu", "điều kiện"]},
    {"query": "UET có chương trình Kỹ thuật phần mềm không?",
     "keywords": ["kỹ thuật phần mềm", "uet", "công nghệ"]},
    {"query": "Học phí chương trình tiên tiến UET?",
     "keywords": ["học phí", "tiên tiến", "uet"]},
    {"query": "UET xét tuyển dựa trên những tổ hợp môn nào?",
     "keywords": ["tổ hợp môn", "xét tuyển", "uet"]},
    {"query": "Chỉ tiêu tuyển sinh ngành CNTT UET năm 2024?",
     "keywords": ["chỉ tiêu", "cntt", "uet", "2024"]},
    {"query": "So sánh học phí HUST và FTU.",
     "keywords": ["học phí", "hust", "ftu"]},
]

CHROMA_DB_PATH = "./chroma_db"


# METRIC HELPERS (k is derived dynamically from the doc list)

def is_relevant(content: str, keywords: list) -> bool:
    c = content.lower()
    return any(kw.lower() in c for kw in keywords)

def compute_metrics(docs, keywords):
    """Compute Hit, Precision@k, MRR, and nDCG@k for a single query."""
    flags = [is_relevant(d.page_content, keywords) for d in docs]
    k = len(flags)

    hit  = 1 if any(flags) else 0
    prec = sum(flags) / k if k > 0 else 0.0

    rr = 0.0
    for i, f in enumerate(flags):
        if f:
            rr = 1.0 / (i + 1)
            break

    # Binary nDCG@k
    dcg  = sum((1.0 / math.log2(i + 2)) if flags[i] else 0.0 for i in range(k))
    idcg = sum(1.0 / math.log2(i + 2) for i in range(k))
    ndcg = dcg / idcg if idcg > 0 else 0.0

    return hit, prec, rr, ndcg


def run_one_config(retriever, config_name, k):
    """Run all 20 test queries against one retriever config, return averaged metrics."""
    print(f"\n  ▶ Running: {config_name}  (k={k})")
    hits, precs, rrs, ndcgs = [], [], [], []

    for i, case in enumerate(TEST_CASES, 1):
        try:
            docs = retriever.invoke(case["query"])
            hit, prec, rr, ndcg = compute_metrics(docs, case["keywords"])
            hits.append(hit)
            precs.append(prec)
            rrs.append(rr)
            ndcgs.append(ndcg)

            status = "✓" if hit else "✗"
            print(f"    [{i:02d}] {status}  P={prec:.2f}  RR={rr:.2f}  nDCG={ndcg:.3f}")

            # Short pause between queries to stay within API rate limits
            if i < len(TEST_CASES):
                time.sleep(0.5)

        except Exception as e:
            print(f"    [{i:02d}] ERROR: {e}")
            hits.append(0); precs.append(0); rrs.append(0); ndcgs.append(0)

    n = len(hits)
    return {
        "config":    config_name,
        "k":         k,
        "n":         n,
        "recall":    sum(hits) / n,       # Hit@k == Recall@k (binary)
        "precision": sum(precs) / n,
        "mrr":       sum(rrs) / n,
        "ndcg":      sum(ndcgs) / n,
        "hits":      sum(hits),
    }


# MAIN

def main():
    print("=" * 65)
    print("   ABLATION STUDY — RAG RETRIEVAL CONFIGURATION COMPARISON")
    print("=" * 65)
    print(f"   Test cases : {len(TEST_CASES)}")
    print(f"   ChromaDB   : {CHROMA_DB_PATH}")
    print("=" * 65)

    # Connect to ChromaDB
    try:
        from langchain_chroma import Chroma
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from app.config import GEMINI_API_KEY, GEMINI_EMBEDDING_MODEL

        os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
        embeddings_model = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBEDDING_MODEL)
        db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings_model)
        print("\n[✓] Connected to ChromaDB successfully.")
    except Exception as e:
        print(f"\n[✗] Failed to connect to ChromaDB: {e}")
        print("    Make sure ingest_clean_data.py has been run first.")
        sys.exit(1)

    results = []

    # EXPERIMENT A: Compare k = 3, 4, 6, 8
    # Strategy: Similarity Search (cosine distance, default)
    print("\n" + "─" * 65)
    print("  EXPERIMENT A — Effect of retrieved chunk count (k)")
    print("  Strategy: Similarity Search (cosine)")
    print("─" * 65)

    for k_val in [3, 4, 6, 8]:
        retriever = db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k_val}
        )
        label = f"Similarity Search, k={k_val}"
        res = run_one_config(retriever, label, k_val)
        results.append(res)

        if k_val != 8:
            print(f"\n    [Sleeping 5 s before next config...]")
            time.sleep(5)

    # EXPERIMENT B: MMR vs Similarity Search at k=6
    # MMR (Maximal Marginal Relevance) trades some accuracy
    # for diversity — selects chunks that are both relevant
    # and different from each other.
    print("\n" + "─" * 65)
    print("  EXPERIMENT B — Effect of search strategy (k=6)")
    print("  Similarity Search already ran in Experiment A (k=6)")
    print("  Now running: MMR (Maximal Marginal Relevance)")
    print("─" * 65)
    print(f"\n    [Sleeping 5 s before MMR run...]")
    time.sleep(5)

    retriever_mmr = db.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 6,           # final number of chunks returned
            "fetch_k": 20,    # MMR first fetches 20 candidates, then picks the 6 most diverse
            "lambda_mult": 0.5  # 0 = max diversity, 1 = max similarity
        }
    )
    res_mmr = run_one_config(retriever_mmr, "MMR (λ=0.5), k=6", 6)
    results.append(res_mmr)

    # PRINT SUMMARY TABLE
    print("\n\n" + "=" * 65)
    print("   SUMMARY — ABLATION STUDY RESULTS")
    print("=" * 65)

    print(f"\n  {'Config':<30} {'Hit@k':>8} {'Prec@k':>8} {'MRR':>8} {'nDCG@k':>8}")
    print(f"  {'─'*30} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")

    print(f"\n  [EXPERIMENT A — Effect of k]")
    for r in results:
        if "Similarity" in r["config"]:
            marker = " ◄ (current)" if r["k"] == 6 else ""
            print(f"  {'k='+str(r['k'])+', Similarity':<30} "
                  f"{r['hits']}/{r['n']} ({r['recall']:.0%}){'':< 2}"
                  f"{r['precision']:>8.4f}"
                  f"{r['mrr']:>8.4f}"
                  f"{r['ndcg']:>8.4f}"
                  f"{marker}")

    print(f"\n  [EXPERIMENT B — Effect of search strategy, k=6]")
    k6_sim = next(r for r in results if r["k"] == 6 and "Similarity" in r["config"])
    print(f"  {'k=6, Similarity (SimSrch)':<30} "
          f"{k6_sim['hits']}/{k6_sim['n']} ({k6_sim['recall']:.0%}){'':< 2}"
          f"{k6_sim['precision']:>8.4f}"
          f"{k6_sim['mrr']:>8.4f}"
          f"{k6_sim['ndcg']:>8.4f}"
          f"  ◄ (current)")
    for r in results:
        if "MMR" in r["config"]:
            print(f"  {'k=6, MMR':<30} "
                  f"{r['hits']}/{r['n']} ({r['recall']:.0%}){'':< 2}"
                  f"{r['precision']:>8.4f}"
                  f"{r['mrr']:>8.4f}"
                  f"{r['ndcg']:>8.4f}")

    print(f"\n{'='*65}")

    # SAVE RESULTS TO FILE
    output_path = "ablation_results.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("ABLATION STUDY — RAG RETRIEVAL CONFIGURATION COMPARISON\n")
        f.write("=" * 65 + "\n")
        f.write(f"Test cases: {len(TEST_CASES)}\n\n")

        f.write("EXPERIMENT A — Effect of retrieved chunk count (k)\n")
        f.write(f"{'Config':<35} {'Hit@k':>8} {'Prec@k':>8} {'MRR':>8} {'nDCG@k':>8}\n")
        f.write("─" * 67 + "\n")
        for r in results:
            if "Similarity" in r["config"]:
                marker = " [CURRENT]" if r["k"] == 6 else ""
                f.write(f"k={r['k']}, Similarity Search{'':<14}"
                        f"{r['hits']}/{r['n']}={r['recall']:.4f}"
                        f"{r['precision']:>8.4f}"
                        f"{r['mrr']:>8.4f}"
                        f"{r['ndcg']:>8.4f}"
                        f"{marker}\n")

        f.write("\nEXPERIMENT B — Effect of search strategy (k=6)\n")
        f.write("─" * 67 + "\n")
        f.write(f"k=6, Similarity Search{'':<13}"
                f"{k6_sim['hits']}/{k6_sim['n']}={k6_sim['recall']:.4f}"
                f"{k6_sim['precision']:>8.4f}"
                f"{k6_sim['mrr']:>8.4f}"
                f"{k6_sim['ndcg']:>8.4f}"
                f"  [CURRENT]\n")
        for r in results:
            if "MMR" in r["config"]:
                f.write(f"k=6, MMR (lambda=0.5){'':<14}"
                        f"{r['hits']}/{r['n']}={r['recall']:.4f}"
                        f"{r['precision']:>8.4f}"
                        f"{r['mrr']:>8.4f}"
                        f"{r['ndcg']:>8.4f}\n")

    print(f"\n[✓] Results saved to: {output_path}\n")


if __name__ == "__main__":
    main()
