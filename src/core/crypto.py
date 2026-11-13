import os
from typing import Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag

from src.config import (
    PBKDF2_ITERATIONS,
    SALT_SIZE_BYTES,
    AES_KEY_SIZE_BYTES,
    GCM_NONCE_SIZE_BYTES,
)

class CryptoError(Exception):
    """Excepción base para errores criptográficos."""
    pass

class DecryptionError(CryptoError):
    """Lanzada cuando falla la autenticación de integridad o descifrado AES-GCM."""
    pass

class CryptoEngine:
    """
    Motor criptográfico de grado militar.
    Implementa PBKDF2-HMAC-SHA256 para derivación de claves
    y AES-256-GCM para cifrado autenticado de datos en reposo.
    """

    def __init__(self, iterations: int = PBKDF2_ITERATIONS):
        self.iterations = iterations
        self.backend = default_backend()

    def generate_salt(self, length: int = SALT_SIZE_BYTES) -> bytes:
        """Genera un salt criptográficamente seguro mediante os.urandom."""
        return os.urandom(length)

    def derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Deriva una clave simétrica de 256 bits a partir de la contraseña maestra y un salt
        usando PBKDF2 con SHA-256 y un alto recuento de iteraciones.
        """
        if not password or not salt:
            raise ValueError("La contraseña y el salt son obligatorios para la derivación.")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=AES_KEY_SIZE_BYTES,
            salt=salt,
            iterations=self.iterations,
            backend=self.backend
        )
        return kdf.derive(password.encode("utf-8"))

    def encrypt(self, plaintext: str, key: bytes) -> bytes:
        """
        Cifra texto plano usando AES-256-GCM.
        Genera un nonce único de 12 bytes por operación para prevenir repetición.
        Retorna: nonce (12 bytes) + texto cifrado + tag de autenticación (16 bytes).
        """
        if not plaintext:
            raise ValueError("El texto a cifrar no puede estar vacío.")
        if len(key) != AES_KEY_SIZE_BYTES:
            raise ValueError(f"Clave inválida: se requieren {AES_KEY_SIZE_BYTES} bytes.")

        aesgcm = AESGCM(key)
        nonce = os.urandom(GCM_NONCE_SIZE_BYTES)
        encrypted_payload = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
        return nonce + encrypted_payload

    def decrypt(self, ciphertext_package: bytes, key: bytes) -> str:
        """
        Descifra un paquete cifrado con AES-256-GCM.
        Extrae los primeros 12 bytes como nonce y valida la autenticidad del payload.
        Lanza DecryptionError si la clave es incorrecta o los datos fueron alterados.
        """
        if len(ciphertext_package) <= GCM_NONCE_SIZE_BYTES:
            raise DecryptionError("Paquete cifrado corrupto o de longitud insuficiente.")
        if len(key) != AES_KEY_SIZE_BYTES:
            raise ValueError(f"Clave inválida: se requieren {AES_KEY_SIZE_BYTES} bytes.")

        nonce = ciphertext_package[:GCM_NONCE_SIZE_BYTES]
        actual_ciphertext = ciphertext_package[GCM_NONCE_SIZE_BYTES:]

        aesgcm = AESGCM(key)
        try:
            decrypted_bytes = aesgcm.decrypt(nonce, actual_ciphertext, None)
            return decrypted_bytes.decode("utf-8")
        except InvalidTag as e:
            raise DecryptionError("Fallo de autenticación: clave incorrecta o datos manipulados.") from e
        except Exception as e:
            raise DecryptionError(f"Error inesperado al descifrar: {str(e)}") from e

