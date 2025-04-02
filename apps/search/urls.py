from django.urls import path
from apps.search import views

urlpatterns = [
    path('', views.search_view, name='search'),
]
