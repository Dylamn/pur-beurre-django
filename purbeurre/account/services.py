from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .forms import UserUpdateForm


class ProfileService:
    @staticmethod
    def update_user_information(request: HttpRequest, *args, **kwargs):
        user = request.user
        form = UserUpdateForm(data=request.POST, instance=user)
        ctx = {}

        if form.is_valid():
            form.save()
            ctx['information_update_success'] = True
        else:
            ctx['information_errors'] = form.errors

        return ctx

    @staticmethod
    def update_password(request: HttpRequest, *args, **kwargs):
        user = request.user
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')
        ctx = {}

        if not user.check_password(current_password):
            ctx['password_errors'] = {
                'current_password': _('Le mot de passe actuel est erroné.')
            }
        elif new_password != confirm_new_password:
            ctx['password_errors'] = {
                'confirm_password': _('La confirmation du mot de passe est différente.')
            }
        elif current_password == new_password:
            ctx['password_errors'] = {
                'new_password': _("Le nouveau mot de passe est identique à l'ancien.")
            }
        else:
            ctx['password_update_success'] = True
            user.set_password(new_password)
            user.save()

        return ctx
