from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_phone_number(value):
    if len(value) != 10:
        raise ValidationError(
            _('Phone number must be exactly 10 digits long.'),
        )
    if not value.isdigit():
        raise ValidationError(
            _('Phone number must contain only numeric digits.'),
        )
    if value[0] == '0':
        raise ValidationError(
            _('Phone number must not start with a "0".'),
        )
