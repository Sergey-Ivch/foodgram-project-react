from django.core.exceptions import ValidationError
import re

def validate_hex(value):
    # Проверка "а заполнено ли поле?"
    if not re.fullmatch('^#[a-fA-F0-9]{6}', value):
        raise ValidationError(
            'Не валидный HEX-code.'
        )