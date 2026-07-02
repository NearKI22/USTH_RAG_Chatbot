"""
evaluate_retrieval.py
=====================
Standalone script for evaluating the RAG retrieval quality.
Computes 5 standard IR metrics: Hit@k, Recall@k, Precision@k, MRR, nDCG@k

Usage:
    cd ai_service
    python evaluate_retrieval.py

Results are printed to stdout and saved to 'eval_results.txt'.
"""

import os
import math
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# =========================================================
# CONFIG
# =========================================================
# Number of chunks to retrieve per query — should match main.py
K = 6

CHROMA_DB_PATH = "./chroma_db"

# =========================================================
# TEST CASES (20 valid queries from Appendix C)
#
# Each case has:
#   "query"    : the question sent to the RAG retriever
#   "keywords" : expected keywords that should appear in at
#                least one of the retrieved chunks
#                (a chunk is relevant if it contains ANY keyword)
# =========================================================
TEST_CASES = [
    # ---- USTH ----
    {
        "query": "Điểm chuẩn ngành Khoa học máy tính USTH năm 2024 là bao nhiêu?",
        "keywords": ["điểm chuẩn", "khoa học máy tính", "usth", "2024"],
    },
    {
        "query": "USTH có ký túc xá cho sinh viên không?",
        "keywords": ["ký túc xá", "usth", "sinh viên"],
    },
    {
        "query": "USTH đào tạo ngành nào bằng tiếng Anh?",
        "keywords": ["tiếng anh", "usth", "đào tạo", "ngành"],
    },
    {
        "query": "Hotline tuyển sinh USTH là số nào?",
        "keywords": ["hotline", "usth", "tuyển sinh", "liên hệ", "điện thoại"],
    },
    {
        "query": "USTH có ưu tiên cho thí sinh người dân tộc thiểu số không?",
        "keywords": ["dân tộc", "thiểu số", "ưu tiên", "usth"],
    },
    # ---- HUST (Hanoi University of Science and Technology) ----
    {
        "query": "Học phí một năm tại HUST là bao nhiêu?",
        "keywords": ["học phí", "hust", "bách khoa"],
    },
    {
        "query": "Điểm chuẩn ngành Công nghệ thông tin HUST 2024?",
        "keywords": ["công nghệ thông tin", "hust", "điểm chuẩn", "2024"],
    },
    {
        "query": "HUST có ngành Cơ điện tử không, điểm chuẩn bao nhiêu?",
        "keywords": ["cơ điện tử", "hust", "điểm chuẩn"],
    },
    # ---- FTU (Foreign Trade University) ----
    {
        "query": "FTU có ngành Kinh tế quốc tế không?",
        "keywords": ["kinh tế quốc tế", "ftu", "ngoại thương"],
    },
    {
        "query": "FTU có học bổng cho sinh viên giỏi không?",
        "keywords": ["học bổng", "ftu", "sinh viên giỏi", "ngoại thương"],
    },
    {
        "query": "FTU cơ sở Hà Nội đào tạo những ngành gì?",
        "keywords": ["ftu", "hà nội", "ngành", "đào tạo"],
    },
    # ---- NEU (National Economics University) ----
    {
        "query": "NEU xét tuyển theo phương thức nào năm 2024?",
        "keywords": ["xét tuyển", "neu", "kinh tế quốc dân", "phương thức"],
    },
    {
        "query": "Quy trình nộp hồ sơ tuyển sinh NEU như thế nào?",
        "keywords": ["hồ sơ", "nộp", "neu", "tuyển sinh"],
    },
    {
        "query": "NEU có chương trình liên kết quốc tế không?",
        "keywords": ["quốc tế", "liên kết", "neu", "chương trình"],
    },
    {
        "query": "Điều kiện xét tuyển thẳng vào NEU?",
        "keywords": ["xét tuyển thẳng", "neu", "điều kiện"],
    },
    # ---- UET (University of Engineering and Technology - VNU) ----
    {
        "query": "UET có chương trình Kỹ thuật phần mềm không?",
        "keywords": ["kỹ thuật phần mềm", "uet", "công nghệ"],
    },
    {
        "query": "Học phí chương trình tiên tiến UET?",
        "keywords": ["học phí", "tiên tiến", "uet"],
    },
    {
        "query": "UET xét tuyển dựa trên những tổ hợp môn nào?",
        "keywords": ["tổ hợp môn", "xét tuyển", "uet"],
    },
    {
        "query": "Chỉ tiêu tuyển sinh ngành CNTT UET năm 2024?",
        "keywords": ["chỉ tiêu", "cntt", "uet", "2024"],
    },
    # ---- Cross-university comparison ----
    {
        "query": "So sánh học phí HUST và FTU.",
        "keywords": ["học phí", "hust", "ftu"],
    },
]


# =========================================================
# METRIC FUNCTIONS
# =========================================================

def is_relevant(chunk_content: str, keywords: list) -> bool:
    """
    Returns True if the chunk contains at least one of the expected keywords.
    Matching is case-insensitive.
    """
    content_lower = chunk_content.lower()
    return any(kw.lower() in content_lower for kw in keywords)


def compute_hit_at_k(relevant_flags: list) -> int:
    """Hit@k = 1 if at least one chunk in top-k is relevant, else 0."""
    return 1 if any(relevant_flags) else 0


def compute_precision_at_k(relevant_flags: list) -> float:
    """Precision@k = (number of relevant chunks) / k"""
    if not relevant_flags:
        return 0.0
    return sum(relevant_flags) / len(relevant_flags)


def compute_rr(relevant_flags: list) -> float:
    """
    Reciprocal Rank = 1 / rank_of_first_relevant_chunk.
    Rank is 1-indexed. Returns 0 if no relevant chunk found.
    """
    for i, flag in enumerate(relevant_flags):
        if flag:
            return 1.0 / (i + 1)
    return 0.0


def compute_ndcg_at_k(relevant_flags: list) -> float:
    """
    Binary nDCG@k:
        DCG  = sum( rel_i / log2(i+2) )  for i = 0..k-1
        IDCG = ideal DCG when all chunks are relevant
        nDCG = DCG / IDCG
    """
    k = len(relevant_flags)
    dcg = sum(
        (1.0 / math.log2(i + 2)) if relevant_flags[i] else 0.0
        for i in range(k)
    )
    idcg = sum(1.0 / math.log2(i + 2) for i in range(k))
    return dcg / idcg if idcg > 0 else 0.0


# =========================================================
# MAIN EVALUATION FUNCTION
# =========================================================

def run_evaluation():
    print("=" * 60)
    print("   RETRIEVAL QUALITY EVALUATION — RAG ADMISSIONS CHATBOT")
    print("=" * 60)
    print(f"   Test cases   : {len(TEST_CASES)}")
    print(f"   Chunks (k)   : {K}")
    print(f"   ChromaDB     : {CHROMA_DB_PATH}")
    print("=" * 60)

    # Connect to ChromaDB
    try:
        from langchain_chroma import Chroma
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from app.config import GEMINI_API_KEY, GEMINI_EMBEDDING_MODEL

        os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
        embeddings_model = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBEDDING_MODEL)
        db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings_model)
        retriever = db.as_retriever(search_kwargs={"k": K})
        print("\n[✓] Connected to ChromaDB successfully.\n")
    except Exception as e:
        print(f"\n[✗] Failed to connect to ChromaDB: {e}")
        print("    Make sure you have run ingest_clean_data.py first.")
        sys.exit(1)

    all_hits        = []
    all_precisions  = []
    all_rr          = []
    all_ndcg        = []
    per_case_results = []

    print(f"{'#':<4} {'Query (truncated)':<45} {'Hit':>5} {'P@k':>6} {'RR':>6} {'nDCG':>6}")
    print("-" * 75)

    for idx, case in enumerate(TEST_CASES, start=1):
        query    = case["query"]
        keywords = case["keywords"]

        try:
            docs = retriever.invoke(query)
        except Exception as e:
            print(f"  [{idx:02d}] ERROR during retrieval: {e}")
            continue

        relevant_flags = [is_relevant(doc.page_content, keywords) for doc in docs]

        hit   = compute_hit_at_k(relevant_flags)
        prec  = compute_precision_at_k(relevant_flags)
        rr    = compute_rr(relevant_flags)
        ndcg  = compute_ndcg_at_k(relevant_flags)

        all_hits.append(hit)
        all_precisions.append(prec)
        all_rr.append(rr)
        all_ndcg.append(ndcg)

        short_q  = query[:42] + "..." if len(query) > 45 else query
        hit_icon = "✓" if hit else "✗"
        print(f"  {idx:<3} {short_q:<45} {hit_icon:>5} {prec:>6.2f} {rr:>6.2f} {ndcg:>6.3f}")

        per_case_results.append({
            "query": query,
            "keywords": keywords,
            "relevant_flags": relevant_flags,
            "hit": hit,
            "precision_at_k": prec,
            "rr": rr,
            "ndcg": ndcg,
        })

    # Aggregate scores
    n = len(all_hits)
    recall_at_k   = sum(all_hits) / n
    avg_precision = sum(all_precisions) / n
    mrr           = sum(all_rr) / n
    avg_ndcg      = sum(all_ndcg) / n

    print("\n" + "=" * 60)
    print("   OVERALL RESULTS")
    print("=" * 60)
    print(f"   Queries evaluated    : {n}")
    print(f"   Hit@{K}  (Recall@{K})  : {sum(all_hits)}/{n} = {recall_at_k:.1%}")
    print(f"   Precision@{K}         : {avg_precision:.4f}  ({avg_precision:.1%})")
    print(f"   MRR                  : {mrr:.4f}")
    print(f"   nDCG@{K}              : {avg_ndcg:.4f}")
    print("=" * 60)

    # Report any failed queries (Hit = 0)
    failed_cases = [r for r in per_case_results if r["hit"] == 0]
    if failed_cases:
        print(f"\n[!] {len(failed_cases)} queries returned no relevant chunk:")
        for fc in failed_cases:
            print(f"    - {fc['query']}")
            print(f"      Keywords: {fc['keywords']}")
    else:
        print("\n[✓] All queries returned at least one relevant chunk.")

    # Save detailed results
    output_path = "eval_results.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("ĐÁNH GIÁ CHẤT LƯỢNG RETRIEVAL — RAG CHATBOT TUYỂN SINH\n")
        f.write("=" * 60 + "\n")
        f.write(f"Số câu hỏi kiểm thử : {n}\n")
        f.write(f"k (số chunk lấy)    : {K}\n\n")
        f.write(f"Hit@{K} / Recall@{K}  : {sum(all_hits)}/{n} = {recall_at_k:.4f} ({recall_at_k:.1%})\n")
        f.write(f"Precision@{K}        : {avg_precision:.4f} ({avg_precision:.1%})\n")
        f.write(f"MRR                 : {mrr:.4f}\n")
        f.write(f"nDCG@{K}             : {avg_ndcg:.4f}\n\n")
        f.write("CHI TIẾT TỪNG CÂU HỎI\n")
        f.write("-" * 60 + "\n")
        for i, r in enumerate(per_case_results, 1):
            f.write(f"[{i:02d}] {r['query']}\n")
            f.write(f"     Hit={r['hit']}  P@k={r['precision_at_k']:.2f}  RR={r['rr']:.2f}  nDCG={r['ndcg']:.3f}\n")
            f.write(f"     Relevant flags (vị trí 1-{K}): {r['relevant_flags']}\n\n")

    print(f"\n[✓] Detailed results saved to: {output_path}\n")

    return {
        "recall_at_k"   : recall_at_k,
        "precision_at_k": avg_precision,
        "mrr"           : mrr,
        "ndcg_at_k"     : avg_ndcg,
        "n"             : n,
        "k"             : K,
    }


# =========================================================
# ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    results = run_evaluation()
