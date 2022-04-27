from django.urls import path

from . import views

app_name = 'product'

urlpatterns = [
    path('search/', views.index, name="search"),
    path('<int:pk>/', views.ProductDetailView.as_view(), name="show")
]
