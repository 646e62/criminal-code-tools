from django.shortcuts import render, get_object_or_404
from django.contrib import messages
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
from apps.data_processing.ingestion.case_metadata import (
    CaseMetadataIngester,
    InvalidCitationError,
    CaseNotFoundError,
    CaseIngestionError,
    CaseAlreadyExistsError
)

# Create your views here.

def view_case(request, case_id):
    """View for displaying case details."""
    case = get_object_or_404(CaseMetadata, case_id=case_id)
    return render(request, 'data_processing/view_case.html', {'case': case})

def ingest_case_view(request):
    """View for ingesting case metadata from citations."""
    existing_cases = CaseMetadata.objects.all().order_by('-decision_date')[:10]
    context = {'existing_cases': existing_cases}

    if request.method == 'POST':
        citation = request.POST.get('citation', '').strip()
        force = request.POST.get('force', '').lower() == 'true'
        
        if not citation:
            messages.error(request, 'Please enter a citation')
            return render(request, 'data_processing/ingest_case.html', context)
        
        try:
            ingester = CaseMetadataIngester()
            case, created = ingester.ingest_citation(citation, force=force)
            context['case'] = case
            if created:
                messages.success(request, 'Case metadata ingested successfully')
            else:
                messages.success(request, 'Case metadata updated successfully')
        except InvalidCitationError as e:
            messages.error(request, f'Invalid citation format: {str(e)}')
        except CaseNotFoundError as e:
            messages.error(request, f'Case not found: {str(e)}')
        except CaseAlreadyExistsError as e:
            messages.warning(request, f'Case already exists: {str(e)}. Check "Force Update" to overwrite.')
        except CaseIngestionError as e:
            messages.error(request, f'Error ingesting case metadata: {str(e)}')
        except Exception as e:
            messages.error(request, f'Unexpected error: {str(e)}')
    
    return render(request, 'data_processing/ingest_case.html', context)

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
