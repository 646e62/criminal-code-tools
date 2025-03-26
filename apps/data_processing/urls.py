from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.data_processing.views import (
    CaseMetadataViewSet,
    FactPatternViewSet,
    SentencingRangeViewSet,
    OffenceViewSet
)

router = DefaultRouter()
router.register(r'cases', CaseMetadataViewSet, basename='casemetadata')
router.register(r'fact-patterns', FactPatternViewSet, basename='factpattern')
router.register(r'sentencing-ranges', SentencingRangeViewSet, basename='sentencingrange')
router.register(r'offences', OffenceViewSet, basename='offence')

urlpatterns = router.urls
