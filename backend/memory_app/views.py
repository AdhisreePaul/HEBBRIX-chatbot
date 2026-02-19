from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Memory
from .serializers import MemorySerializer
from .services.embedding import get_embedding, cosine_similarity
from .services.extractor import extract_memories
from .services.retrieval import hybrid_search
from .services.chat import generate_response


class MemoryCreateAPIView(APIView):

    def post(self, request):
        text = request.data.get("text")

        if not text:
            return Response({"error": "Text is required"}, status=400)

        facts = extract_memories(text)
        created_memories = []

        existing_memories = Memory.objects.all()

        for fact in facts:
            new_embedding = get_embedding(fact)

            duplicate = False
            for memory in existing_memories:
                sim = cosine_similarity(new_embedding, memory.embedding)
                if sim > 0.9:
                    duplicate = True
                    break

            if not duplicate:
                memory = Memory.objects.create(
                    content=fact,
                    embedding=new_embedding
                )
                created_memories.append(memory)

        serializer = MemorySerializer(created_memories, many=True)
        return Response(serializer.data, status=201)


class MemoryListAPIView(APIView):

    def get(self, request):
        memories = Memory.objects.all()
        serializer = MemorySerializer(memories, many=True)
        return Response(serializer.data)


class MemorySearchAPIView(APIView):

    def get(self, request):
        query = request.GET.get("q")

        if not query:
            return Response({"error": "Query required"}, status=400)

        memories = Memory.objects.all()
        top_memories = hybrid_search(query, memories)

        serializer = MemorySerializer(top_memories, many=True)
        return Response(serializer.data)


class MemoryDeleteAPIView(APIView):

    def delete(self, request, id):
        try:
            memory = Memory.objects.get(id=id)
        except Memory.DoesNotExist:
            return Response({"error": "Memory not found"}, status=404)

        memory.delete()
        return Response({"message": "Deleted"}, status=200)


class ChatAPIView(APIView):

    def post(self, request):
        query = request.data.get("query")
        history = request.data.get("history", [])

        if not query:
            return Response({"error": "Query required"}, status=400)

        answer, memories_used = generate_response(query, history)

        return Response({
            "answer": answer,
            "memories_used": memories_used
        })
