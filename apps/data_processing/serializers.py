from rest_framework import serializers
from .models import CaseMetadata, FactPattern, SentencingRange, Offence

class CaseMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseMetadata
        fields = '__all__'

class FactPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactPattern
        fields = '__all__'

class SentencingRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentencingRange
        fields = '__all__'

class OffenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offence
        fields = '__all__'
