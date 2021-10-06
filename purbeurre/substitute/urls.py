from django.urls import path

from . import views

app_name = 'substitute'

urlpatterns = [
    path('me/', views.UserSubstituteIndexView.as_view(), name='index'),
    path('search/', views.ProductSubstitutesListView.as_view(), name='search'),
    path('save/', views.save_substitute, name='save'),
    path('delete/<int:substitute_id>', views.delete_substitute, name="delete")
]
