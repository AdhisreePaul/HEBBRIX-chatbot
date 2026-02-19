from django.db import models

class Memory(models.Model):
    content = models.TextField()
    embedding = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    importance_score = models.FloatField(default=0.5)


    def __str__(self):
        return self.content[:50]
