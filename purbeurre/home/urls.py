from django.urls import path

from . import views

# App namespace for urls.
app_name = 'home'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index')
]
