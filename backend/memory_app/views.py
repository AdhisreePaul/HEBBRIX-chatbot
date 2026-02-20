from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Memory
from .serializers import MemorySerializer
from .services.embedding import get_embedding, cosine_similarity
from .services.extractor import extract_memories
from .services.retrieval import hybrid_rank_memories, keyword_overlap_score
from .services.chat import generate_response


DUPLICATE_THRESHOLD = 0.90


class MemoryCreateAPIView(APIView):
    """
    Extracts durable facts from text,
    deduplicates via cosine similarity,
    and stores new memories.
    """

    @transaction.atomic
    def post(self, request):
        text = request.data.get("text")

        if not text:
            return Response(
                {"error": "Feild 'text' is required"},
                status=400
            )

        facts = extract_memories(text)
        if not facts:
            return Response(
                {"message": "No durable facts extracted."},
                status=status.HTTP_200_OK
            )

        created_memories = []

        for fact in facts:
            new_embedding = get_embedding(fact)

            # Check against current DB state (including newly created ones)
            is_duplicate = False
            for memory in Memory.objects.all():
                similarity = cosine_similarity(
                    new_embedding,
                    memory.embedding
                )

                if similarity >= DUPLICATE_THRESHOLD:
                    is_duplicate = True
                    break

            if not is_duplicate:
                memory = Memory.objects.create(
                    content=fact,
                    embedding=new_embedding
                )
                created_memories.append(memory)

        serializer = MemorySerializer(created_memories, many=True)

        return Response(
            {
                "stored_count": len(created_memories),
                "memories": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class MemoryListAPIView(APIView):
    """
    Returns all stored memories (without embeddings).
    """

    def get(self, request):
        memories = Memory.objects.all().order_by("-created_at")
        serializer = MemorySerializer(memories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MemorySearchAPIView(APIView):

    def get(self, request):
        query = request.GET.get("q")

        if not query:
            return Response(
                {"error": "Query parameter 'q' is required"},
                status=400
            )

        memories = Memory.objects.all()

        if not memories.exists():
            return Response({
                "query": query,
                "results": []
            })

        # 🔥 Use hybrid ranking properly
        ranked_results = hybrid_rank_memories(query, memories)

        # Return top 5 (or all if fewer)
        return Response({
            "query": query,
            "results": ranked_results[:5]
        })


class MemoryDeleteAPIView(APIView):
    """
    Deletes a memory by ID.
    """

    def delete(self, request, id):
        try:
            memory = Memory.objects.get(id=id)
        except Memory.DoesNotExist:
            return Response(
                {"error": "Memory not found"},
                status=404
            )

        memory.delete()

        return Response(
            {"message": f"Memory {id} deleted successfully."}
        )


class ChatAPIView(APIView):
    """
    Handles conversational queries using:
    - Short-term history
    - Long-term memory retrieval
    """

    def post(self, request):
        query = request.data.get("query")
        history = request.data.get("history", [])

        if not query:
            return Response(
                {"error": "Query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        answer, memories_used = generate_response(query, history)

        return Response(
            {
                "answer": answer,
                "memories_used": memories_used
            },
            status=status.HTTP_200_OK
        )