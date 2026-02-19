import os
import json
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from memory_app.models import Memory
from memory_app.services.embedding import cosine_similarity, get_embedding


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


def evaluate():
    dataset = load_dataset()
    clear_database()
    insert_memories(dataset)

    correct_top1 = 0
    correct_top3 = 0
    reciprocal_rank_sum = 0
    total = len(dataset)

    print("\n===== EVALUATION START =====\n")

    for item in dataset:
        query_embedding = get_embedding(item["query"])
        memories = Memory.objects.all()

        scored = []
        for memory in memories:
            score = cosine_similarity(query_embedding, memory.embedding)
            scored.append((score, memory.content))

        scored.sort(reverse=True, key=lambda x: x[0])

        top_results = [m for _, m in scored[:3]]

        # --- Top-1 ---
        is_top1 = top_results[0] == item["expected_memory"]

        # --- Top-3 ---
        is_top3 = item["expected_memory"] in top_results

        # --- MRR ---
        for rank, (_, content) in enumerate(scored):
            if content == item["expected_memory"]:
                reciprocal_rank_sum += 1 / (rank + 1)
                break

        if is_top1:
            correct_top1 += 1
        if is_top3:
            correct_top3 += 1

        print(f"Query: {item['query']}")
        print(f"Expected: {item['expected_memory']}")
        print(f"Top 3 Retrieved: {top_results}")
        print(f"Top1 Correct: {is_top1}")
        print("-" * 50)

    top1_accuracy = correct_top1 / total
    top3_hit_rate = correct_top3 / total
    mrr = reciprocal_rank_sum / total

    print("\n===== FINAL RESULTS =====")
    print(f"Top-1 Accuracy: {top1_accuracy:.2f}")
    print(f"Top-3 Hit Rate: {top3_hit_rate:.2f}")
    print(f"MRR: {mrr:.2f}")


if __name__ == "__main__":
    evaluate()
