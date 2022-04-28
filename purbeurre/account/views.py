from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, reverse, redirect
from django.views import View

from .forms import RegisterUserForm
from .services import ProfileService


def register(request):
    status = 200

    if request.user.is_authenticated:
        return redirect(reverse('home:index'))

    if request.method == "POST":
        # `is_active` default at True because there's no email verification currently.
        form = RegisterUserForm(request.POST, initial={"is_active": True})

        if form.is_valid():
            user = form.save()

            login(request, user)  # Log in the new user.

            return redirect(reverse('home:index'))
        else:
            # Validation error append
            status = 400
    else:
        form = RegisterUserForm()

    return render(request, 'account/register.html', context={"form": form}, status=status)


class ProfileView(LoginRequiredMixin, View):
    @staticmethod
    def get(request, *args, **kwargs):
        return render(request, 'account/profile.html')

    @staticmethod
    def post(request, *args, **kwargs):
        if "current_password" in request.POST:
            ctx = ProfileService.update_password(request, *args, **kwargs)
        else:
            ctx = ProfileService.update_user_information(request, *args, **kwargs)

        return render(request, template_name='account/profile.html', context=ctx)
