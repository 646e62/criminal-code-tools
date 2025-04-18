from django.urls import path
from apps.data_processing.views import (
    ingest_case_view,
    view_case,
    popular_citations_view
)

# Main URL patterns for views
urlpatterns = [
    path('ingest/', ingest_case_view, name='ingest_case'),
    path('case/<str:case_id>/', view_case, name='view_case'),
    path('popular-citations/', popular_citations_view, name='popular_citations'),
]
