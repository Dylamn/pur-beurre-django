from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home/index.html'


class TermsView(TemplateView):
    """Display the terms and conditions page of the site."""
    template_name = 'home/terms.html'
