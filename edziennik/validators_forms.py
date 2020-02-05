from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Parent, Lector

def UniquePhoneValidator(phone):
    if Parent.objects.filter(phone_number=phone).exists():
        raise ValidationError(_(
            "%(phone)s już jest w przypisany do Użytkownika, wybierz inny nr tel lub użyj tego Użytkownika"),
            params={'phone': phone})


def UniqueEmailValidator(email):
    if Parent.objects.filter(email=email).exists():
        raise ValidationError(_(
            "%(email)s już jest w przypisany do Użytkownika, wybierz inny email lub użyj tego Użytkownika"),
            params={'email': email})


def UniqueEmailValidator_Lector(email):
    if Lector.objects.filter(user__email=email).exists():
        raise ValidationError(_(
            "%(email)s już jest w przypisany do Użytkownika, wybierz inny email lub użyj tego Użytkownika"),
            params={'email': email})
