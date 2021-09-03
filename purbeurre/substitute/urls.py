from django.urls import path

from . import views

app_name = 'substitute'

urlpatterns = [
    path('me/', views.index, name='index'),
]
