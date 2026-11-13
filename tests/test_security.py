import sys
from pathlib import Path

# Agregar directorio raíz al PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.security import PasswordAuditor, PasswordGenerator

def test_password_entropy_calculation():
    weak = PasswordAuditor.evaluate("123456")
    assert weak["score"] < 0.5
    assert weak["label"] == "Débil"

    strong = PasswordAuditor.evaluate("Correct-Horse-Battery-Staple-2026!")
    assert strong["score"] >= 0.8
    assert strong["entropy_bits"] > 70

def test_password_generator_guarantees():
    for _ in range(20):
        pwd = PasswordGenerator.generate(
            length=16,
            use_upper=True,
            use_lower=True,
            use_digits=True,
            use_special=True
        )
        assert len(pwd) == 16
        assert any(c.isupper() for c in pwd)
        assert any(c.islower() for c in pwd)
        assert any(c.isdigit() for c in pwd)
        assert any(c in PasswordGenerator.DEFAULT_SPECIAL_CHARS for c in pwd)

def test_password_generator_custom_length():
    pwd32 = PasswordGenerator.generate(length=32)
    assert len(pwd32) == 32

    pwd8 = PasswordGenerator.generate(length=8)
    assert len(pwd8) == 8

if __name__ == "__main__":
    test_password_entropy_calculation()
    test_password_generator_guarantees()
    test_password_generator_custom_length()
    print("✓ Todos los tests de seguridad y generación pasaron exitosamente.")
