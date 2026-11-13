"""
Módulo heredado mantenido para compatibilidad hacia atrás.
Importa desde src.core.crypto.
"""
from src.core.crypto import CryptoEngine as CryptoManager, CryptoError, DecryptionError

__all__ = ["CryptoManager", "CryptoError", "DecryptionError"]
