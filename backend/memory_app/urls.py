from django.urls import path
from .views import (
    MemoryCreateAPIView,
    MemoryListAPIView,
    MemorySearchAPIView,
    MemoryDeleteAPIView,
    ChatAPIView
)

urlpatterns = [
    path('memories', MemoryCreateAPIView.as_view()),
    path('memories/all', MemoryListAPIView.as_view()),
    path('memories/search', MemorySearchAPIView.as_view()),
    path('memories/<int:id>', MemoryDeleteAPIView.as_view()),
    path('chat', ChatAPIView.as_view()),
]
