from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.data_processing.models import CaseMetadata, FactPattern, SentencingRange, Offence
from apps.data_processing.serializers import (
    CaseMetadataSerializer,
    FactPatternSerializer,
    SentencingRangeSerializer,
    OffenceSerializer
)

# Create your views here.

class CaseMetadataViewSet(viewsets.ModelViewSet):
    queryset = CaseMetadata.objects.all()
    serializer_class = CaseMetadataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['year', 'court', 'jurisdiction', 'court_level', 'language']
    search_fields = ['style_of_cause', 'citation', 'keywords']
    ordering_fields = ['year', 'decision_date']

class FactPatternViewSet(viewsets.ModelViewSet):
    queryset = FactPattern.objects.all()
    serializer_class = FactPatternSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['case']

class SentencingRangeViewSet(viewsets.ModelViewSet):
    queryset = SentencingRange.objects.all()
    serializer_class = SentencingRangeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['section', 'offender', 'mode', 'appeal']
    search_fields = ['conditions']
    ordering_fields = ['date']

class OffenceViewSet(viewsets.ModelViewSet):
    queryset = Offence.objects.all()
    serializer_class = OffenceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['section']
    search_fields = ['offence_name']
    ordering_fields = ['section']
