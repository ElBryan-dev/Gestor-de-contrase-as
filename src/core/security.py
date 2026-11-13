import math
import secrets
import string
import hashlib
from typing import Tuple, Dict, Any
import requests

class PasswordAuditor:
    """
    Auditor de seguridad para contraseñas.
    Calcula entropía de la información de Shannon en bits y clasifica la robustez.
    """

    @staticmethod
    def calculate_entropy(password: str) -> float:
        """
        Calcula la entropía de Shannon en bits: H = L * log2(R),
        donde L es la longitud y R es el tamaño del conjunto de caracteres posibles.
        """
        if not password:
            return 0.0

        pool_size = 0
        if any(c.islower() for c in password):
            pool_size += 26
        if any(c.isupper() for c in password):
            pool_size += 26
        if any(c.isdigit() for c in password):
            pool_size += 10
        if any(c in string.punctuation for c in password):
            pool_size += len(string.punctuation)
        # Caracteres fuera de ASCII básico
        if any(ord(c) > 127 for c in password):
            pool_size += 32

        if pool_size == 0:
            return 0.0

        entropy_bits = len(password) * math.log2(pool_size)
        return round(entropy_bits, 1)

    @classmethod
    def evaluate(cls, password: str) -> Dict[str, Any]:
        """
        Evalúa integralmente una contraseña y retorna métricas de seguridad.
        """
        if not password:
            return {
                "score": 0.0,
                "label": "Sin contraseña",
                "color": "#6B7280",
                "entropy_bits": 0.0,
                "description": "El campo está vacío."
            }

        bits = cls.calculate_entropy(password)
        length = len(password)

        # Criterio estándar NIST / Bitwarden:
        # < 36 bits: Muy débil
        # 36 - 59 bits: Débil
        # 60 - 79 bits: Media / Aceptable
        # 80 - 100 bits: Fuerte
        # > 100 bits: Muy Fuerte / Militar
        if bits < 36 or length < 8:
            score = max(0.15, min(0.3, bits / 60))
            return {
                "score": score,
                "label": "Débil",
                "color": "#EF4444",
                "entropy_bits": bits,
                "description": f"{bits} bits • Vulnerable a ataques de fuerza bruta rápidos."
            }
        elif bits < 60 or length < 10:
            score = 0.5
            return {
                "score": score,
                "label": "Aceptable",
                "color": "#F59E0B",
                "entropy_bits": bits,
                "description": f"{bits} bits • Protección moderada para cuentas no críticas."
            }
        elif bits < 85 or length < 14:
            score = 0.8
            return {
                "score": score,
                "label": "Fuerte",
                "color": "#10B981",
                "entropy_bits": bits,
                "description": f"{bits} bits • Alta seguridad contra ataques distribuidos."
            }
        else:
            return {
                "score": 1.0,
                "label": "Excelente",
                "color": "#059669",
                "entropy_bits": bits,
                "description": f"{bits} bits • Grado criptográfico óptimo."
            }

class PasswordGenerator:
    """Generador criptográficamente seguro basado en CSPRNG (secrets)."""

    DEFAULT_SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?"

    @classmethod
    def generate(
        cls,
        length: int = 16,
        use_upper: bool = True,
        use_lower: bool = True,
        use_digits: bool = True,
        use_special: bool = True,
        special_chars: str = DEFAULT_SPECIAL_CHARS
    ) -> str:
        """
        Genera una clave aleatoria garantizando al menos un carácter
        de cada grupo seleccionado para evitar sub-representación.
        """
        pools = []
        guaranteed = []

        if use_upper:
            pools.append(string.ascii_uppercase)
            guaranteed.append(secrets.choice(string.ascii_uppercase))
        if use_lower:
            pools.append(string.ascii_lowercase)
            guaranteed.append(secrets.choice(string.ascii_lowercase))
        if use_digits:
            pools.append(string.digits)
            guaranteed.append(secrets.choice(string.digits))
        if use_special and special_chars:
            pools.append(special_chars)
            guaranteed.append(secrets.choice(special_chars))

        if not pools:
            # Fallback seguro por defecto
            combined_pool = string.ascii_letters + string.digits
            guaranteed = [secrets.choice(combined_pool)]
        else:
            combined_pool = "".join(pools)

        length = max(len(guaranteed), length)
        remaining = length - len(guaranteed)
        password_list = guaranteed + [secrets.choice(combined_pool) for _ in range(remaining)]

        # Mezcla criptográfica in-place
        secrets.SystemRandom().shuffle(password_list)
        return "".join(password_list)

class BreachChecker:
    """Cliente para la API HaveIBeenPwned con k-Anonymity (SHA-1 prefix/suffix)."""

    API_URL = "https://api.pwnedpasswords.com/range/{prefix}"

    @classmethod
    def check_breaches(cls, password: str, timeout: int = 5) -> int:
        """
        Consulta si la contraseña ha sido filtrada públicamente.
        Solo transmite los primeros 5 caracteres del hash SHA-1 (modelo k-Anonymity),
        garantizando que la contraseña nunca salga del dispositivo en texto ni en hash completo.
        """
        if not password:
            return 0

        sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        prefix = sha1[:5]
        suffix = sha1[5:]

        try:
            res = requests.get(cls.API_URL.format(prefix=prefix), timeout=timeout)
            if res.status_code != 200:
                return 0

            for line in res.text.splitlines():
                if ":" in line:
                    h, count = line.split(":", 1)
                    if h.strip() == suffix:
                        return int(count.strip())
            return 0
        except Exception:
            # En caso de fallo de red o timeout, retorna 0 de forma segura sin bloquear la UI
            return 0

