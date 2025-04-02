from django.urls import path
from . import views

app_name = 'offence_grid'

urlpatterns = [
    path('', views.offence_grid, name='index'),
]
