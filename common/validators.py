from datetime import date
from rest_framework.exceptions import ValidationError


def validate_age_from_token(user, min_age=18):
    birthdate = user.birthdate
    
    if not birthdate:
        raise ValidationError('Укажите дату рождения, чтобы создать продукт.')
    
    age = date.today().year - birthdate.year
    
    if age < min_age:
        raise ValidationError(f' Доступ запрещён! Вам должно быть {min_age} лет, чтобы создать продукт.')
    
    return True