from django.core.exceptions import ValidationError


def xlsx_only(file):
    if not file.name.lower().endswith('.xlsx'):
        raise ValidationError('Only .xlsx files accepted')
