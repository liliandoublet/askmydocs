"""Runner d'évaluation : fait tourner le dataset et calcule les métriques."""
import json
import time
from pathlib import Path

from askmydocs.config import DATA_DIR
from askmydocs.rag import ingest, ask
from askmydocs.vectorstore import search
from askmydocs.eval.metrics import (
    retrieval_hit_rate,
    retrieval_precision,
    answer_keyword_recall,
    is_refusal,
)

def load_dataset(path: Path) -> dict:
    """Charge le dataset d'évaluation JSON."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_evaluation(dataset_path: Path, document_path: Path) -> list[dict]:
    """Évalue le pipeline RAG sur tout le dataset."""
    dataset = load_dataset(dataset_path)

    print(f"📥 Indexation de {document_path.name}...")
    n = ingest(document_path, reset=True)
    print(f"✅ {n} chunks indexés\n")

    rows = []
    for q in dataset["questions"]:
        results = search(q["question"])
        response = ask(q["question"])

        row = {
            "id": q["id"],
            "question": q["question"],
            "hit_rate": retrieval_hit_rate(results, q["relevant_pages"]),
            "precision": round(retrieval_precision(results, q["relevant_pages"]), 3),
            "kw_recall": round(answer_keyword_recall(response["answer"], q["keywords"]), 3),
            "refused": is_refusal(response["answer"]),
            "answer": response["answer"],
        }
        rows.append(row)

        status = "✅" if row["hit_rate"] == 1.0 and not row["refused"] else "⚠️"
        print(f"{status} {q['id']}: hit={row['hit_rate']} "
              f"prec={row['precision']} kw_recall={row['kw_recall']} "
              f"refused={row['refused']}")
        time.sleep(5)

    return rows


def print_summary(rows: list[dict]) -> None:
    """Affiche un résumé agrégé des métriques."""
    n = len(rows)
    avg_hit = sum(r["hit_rate"] for r in rows) / n
    avg_prec = sum(r["precision"] for r in rows) / n
    avg_kw = sum(r["kw_recall"] for r in rows) / n
    n_refused = sum(1 for r in rows if r["refused"])

    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DE L'ÉVALUATION")
    print("=" * 50)
    print(f"Questions évaluées      : {n}")
    print(f"Hit rate (retrieval)    : {avg_hit:.1%}")
    print(f"Précision (retrieval)   : {avg_prec:.1%}")
    print(f"Keyword recall (génér.) : {avg_kw:.1%}")
    print(f"Refus du LLM            : {n_refused}/{n}")
    print("=" * 50)


if __name__ == "__main__":
    import sys

    dataset_path = DATA_DIR / "eval" / "qa_dataset.json"
    document_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_DIR / "uploads" / "RGPD.pdf"

    rows = run_evaluation(dataset_path, document_path)
    print_summary(rows)

    out_path = DATA_DIR / "eval" / "results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Résultats détaillés sauvegardés dans {out_path}")