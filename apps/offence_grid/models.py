from django.db import models

# Create your models here.

class QueuedOffence(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    section = models.CharField(max_length=20)
    display = models.CharField(max_length=255)
    offence_name = models.CharField(max_length=255)
    mode = models.CharField(max_length=20)
    crown_election = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.display} - {self.offence_name} — {self.mode} ({self.crown_election})"
