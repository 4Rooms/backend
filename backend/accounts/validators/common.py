from django.core.exceptions import ValidationError


class WhitespaceValidator:
    """
    Validator to check if the value starts or ends with a whitespace.
    """

    def __init__(self, message=None):
        self.message = message or "This value should not start or end with a whitespace."

    def __call__(self, value):
        if len(value) < 1:
            return

        if value[0] == " " or value[-1] == " ":
            raise ValidationError(self.message)
