import os
import json
import django

# -------------------------------
# Django Setup
# -------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from memory_app.models import Memory
from memory_app.services.embedding import cosine_similarity, get_embedding


# -------------------------------
# Utility Functions
# -------------------------------

def load_dataset():
    dataset_path = os.path.join(os.path.dirname(__file__), "dataset.json")
    with open(dataset_path, "r") as f:
        return json.load(f)


def clear_database():
    Memory.objects.all().delete()


def insert_memories(dataset):
    for item in dataset:
        embedding = get_embedding(item["memory"])
        Memory.objects.create(
            content=item["memory"],
            embedding=embedding
        )


# -------------------------------
# Evaluation Logic
# -------------------------------

def evaluate():
    dataset = load_dataset()
    clear_database()
    insert_memories(dataset)

    correct_top1 = 0
    correct_top3 = 0
    reciprocal_rank_sum = 0
    total = len(dataset)

    print("\n========== MEMORY SYSTEM EVALUATION ==========\n")

    for index, item in enumerate(dataset, start=1):
        query = item["query"]
        expected = item["expected_memory"]

        query_embedding = get_embedding(query)
        memories = Memory.objects.all()

        scored = []
        for memory in memories:
            score = cosine_similarity(query_embedding, memory.embedding)
            scored.append((score, memory.content))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Extract ranked contents
        ranked_memories = [m for _, m in scored]
        top3 = ranked_memories[:3]

        # --- Top-1 ---
        is_top1 = ranked_memories[0] == expected

        # --- Top-3 ---
        is_top3 = expected in top3

        # --- MRR ---
        rank_position = None
        for rank, (score, memory) in enumerate(scored):
            if memory == expected:
                rank_position = rank + 1
                reciprocal_rank_sum += 1 / rank_position
                break

        if rank_position is None:
            rank_position = "Not Found"

        if is_top1:
            correct_top1 += 1
        if is_top3:
            correct_top3 += 1

        # -------------------------------
        # Per Query Output
        # -------------------------------
        print(f"Query {index}: {query}")
        print(f"Expected Memory: {expected}")
        print("Top 3 Retrieved:")

        for rank, (score, memory) in enumerate(scored[:3], start=1):
            print(f"  Rank {rank}: {memory}  (Similarity: {score:.4f})")

        print(f"Top-1 Correct: {is_top1}")
        print(f"Top-3 Hit: {is_top3}")
        print(f"Expected Memory Rank: {rank_position}")
        print("-" * 60)

    # -------------------------------
    # Final Metrics
    # -------------------------------

    top1_accuracy = correct_top1 / total
    top3_hit_rate = correct_top3 / total
    mrr = reciprocal_rank_sum / total

    print("\n========== FINAL RESULTS ==========")
    print(f"Total Queries: {total}")
    print(f"Top-1 Accuracy: {top1_accuracy:.2f}")
    print(f"Top-3 Hit Rate: {top3_hit_rate:.2f}")
    print(f"Mean Reciprocal Rank (MRR): {mrr:.2f}")

    # -------------------------------
    # Save Report
    # -------------------------------

    report_path = os.path.join(os.path.dirname(__file__), "evaluation_report.txt")

    with open(report_path, "w") as f:
        f.write("========== MEMORY SYSTEM EVALUATION REPORT ==========\n\n")
        f.write(f"Total Queries: {total}\n")
        f.write(f"Top-1 Accuracy: {top1_accuracy:.4f}\n")
        f.write(f"Top-3 Hit Rate: {top3_hit_rate:.4f}\n")
        f.write(f"Mean Reciprocal Rank (MRR): {mrr:.4f}\n")

    print(f"\nEvaluation report saved to: {report_path}")


# -------------------------------
# Run
# -------------------------------

if __name__ == "__main__":
    evaluate()