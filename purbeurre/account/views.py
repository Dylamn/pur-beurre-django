from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core import serializers


@login_required
def profile(request):
    return render(request, 'account/profile.html')
