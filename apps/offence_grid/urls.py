from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from .api import QueuedOffenceViewSet

app_name = 'offence_grid'

router = DefaultRouter()
router.register(r'api/queue', QueuedOffenceViewSet, basename='queuedoffence')

urlpatterns = [
    path('', views.offence_grid, name='index'),
]

urlpatterns += router.urls
