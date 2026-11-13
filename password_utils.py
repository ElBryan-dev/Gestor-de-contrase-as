"""
Módulo heredado mantenido para compatibilidad hacia atrás.
Importa desde src.core.security.
"""
from src.core.security import PasswordGenerator, PasswordAuditor, BreachChecker

def generate_password(length=16, use_upper=True, use_lower=True, use_digits=True, use_special=True):
    return PasswordGenerator.generate(
        length=length,
        use_upper=use_upper,
        use_lower=use_lower,
        use_digits=use_digits,
        use_special=use_special
    )

def evaluate_strength(password: str):
    res = PasswordAuditor.evaluate(password)
    return res["score"], res["label"], res["color"]

def check_pwned_api(password: str) -> int:
    return BreachChecker.check_breaches(password)

__all__ = ["generate_password", "evaluate_strength", "check_pwned_api"]
