from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class MaxLengthValidator(object):
    """Max length password validation"""

    def __init__(self, max_length=128):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                _(f"Ensure this field has no more than {self.max_length} characters."),
                code="max_length",
            )

    def get_help_text(self):
        return _(f"Ensure this field has no more than {self.max_length} characters.")
