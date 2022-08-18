from flask import request


def get_form_value(key: str) -> str:
    return request.form[key] if key in request.form else None
