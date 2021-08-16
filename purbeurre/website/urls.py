from django.urls import path

from . import views

# App namespace for urls.
app_name = 'website'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home')
]
