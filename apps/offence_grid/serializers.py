from rest_framework import serializers
from .models import QueuedOffence

class QueuedOffenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueuedOffence
        fields = [
            'id', 'section', 'display', 'offence_name', 'mode', 'crown_election', 'order', 'created_at'
        ]
