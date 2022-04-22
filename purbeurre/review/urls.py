from django.urls import path

from . import views

app_name = 'review'

urlpatterns = [
    path('', views.store, name='store'),
    path('<int:pk>/', views.Review.as_view(), name='review'),
]
