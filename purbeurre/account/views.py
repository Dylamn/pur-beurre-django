from django.shortcuts import render, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

from .forms import RegisterUserForm


def register(request):
    status = 200

    if request.user.is_authenticated:
        return redirect(reverse('home:index'), permanent=True)

    if request.method == "POST":
        # `is_active` initially True because there's actually no email verification.
        form = RegisterUserForm(request.POST, initial={"is_active": True})

        if form.is_valid():
            user = form.save()

            login(request, user)  # Log in the new user.

            return redirect(reverse('home:index'), permanent=True)
        else:
            # Validation error append
            status = 400
    else:
        form = RegisterUserForm()

    return render(request, 'account/register.html', context={"form": form}, status=status)


@login_required
def profile(request):
    return render(request, 'account/profile.html')
