from django.urls import path

from . import views

app_name = 'substitute'

urlpatterns = [
    path('me/', views.UserSubstituteIndexView.as_view(), name='index'),
    path('search/', views.search_substitutes, name='search'),
    path('save/', views.save_product, name='save'),
]
