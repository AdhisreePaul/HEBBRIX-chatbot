import os
import json
import django

# 1️⃣ Tell Django where settings are
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 2️⃣ Setup Django
django.setup()

# 3️⃣ Now import models
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
    total = len(dataset)

    for item in dataset:
        query_embedding = get_embedding(item["query"])
        memories = Memory.objects.all()

        scored = []
        for memory in memories:
            score = cosine_similarity(query_embedding, memory.embedding)
            scored.append((score, memory.content))

        scored.sort(reverse=True, key=lambda x: x[0])
        top_results = [m for _, m in scored[:3]]

        is_top1 = top_results[0] == item["expected_memory"]
        is_top3 = item["expected_memory"] in top_results

        if is_top1:
            correct_top1 += 1
        if is_top3:
            correct_top3 += 1

        print("\nQuery:", item["query"])
        print("Expected:", item["expected_memory"])
        print("Top 3:", top_results)
        print("Top1 Correct:", is_top1)

    print("\n========== RESULTS ==========")
    print("Top-1 Accuracy:", correct_top1 / total)
    print("Top-3 Hit Rate:", correct_top3 / total)


if __name__ == "__main__":
    evaluate()
