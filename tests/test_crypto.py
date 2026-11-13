import os
import sys
from pathlib import Path

# Agregar directorio raíz al PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.crypto import CryptoEngine, DecryptionError

def test_key_derivation_deterministic():
    engine = CryptoEngine(iterations=10_000)
    salt = os.urandom(16)
    key1 = engine.derive_key("MiClaveMaestra123!", salt)
    key2 = engine.derive_key("MiClaveMaestra123!", salt)

    assert len(key1) == 32
    assert key1 == key2

def test_key_derivation_different_salts():
    engine = CryptoEngine(iterations=10_000)
    salt1 = os.urandom(16)
    salt2 = os.urandom(16)
    key1 = engine.derive_key("Clave", salt1)
    key2 = engine.derive_key("Clave", salt2)

    assert key1 != key2

def test_encrypt_decrypt_roundtrip():
    engine = CryptoEngine()
    key = os.urandom(32)
    plaintext = "SuperSecret_Password_2026!"

    encrypted = engine.encrypt(plaintext, key)
    assert encrypted != plaintext.encode()

    decrypted = engine.decrypt(encrypted, key)
    assert decrypted == plaintext

def test_decrypt_with_wrong_key_fails():
    engine = CryptoEngine()
    key1 = os.urandom(32)
    key2 = os.urandom(32)

    encrypted = engine.encrypt("Datos confidenciales", key1)
    
    try:
        engine.decrypt(encrypted, key2)
        assert False, "Debe lanzar DecryptionError con clave errónea"
    except DecryptionError:
        assert True

def test_ciphertext_tampering_fails():
    engine = CryptoEngine()
    key = os.urandom(32)
    encrypted = bytearray(engine.encrypt("IntegridadGCM", key))

    # Modificar un byte del ciphertext
    encrypted[15] ^= 0xFF

    try:
        engine.decrypt(bytes(encrypted), key)
        assert False, "Debe detectar la alteración del payload y lanzar DecryptionError"
    except DecryptionError:
        assert True

if __name__ == "__main__":
    test_key_derivation_deterministic()
    test_key_derivation_different_salts()
    test_encrypt_decrypt_roundtrip()
    test_decrypt_with_wrong_key_fails()
    test_ciphertext_tampering_fails()
    print("✓ Todos los tests criptográficos pasaron exitosamente.")
