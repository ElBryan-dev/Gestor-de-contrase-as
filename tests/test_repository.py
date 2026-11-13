import tempfile
import os
import sys
import gc
from pathlib import Path

# Agregar directorio raíz al PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database.repository import CredentialRepository

def test_repository_lifecycle():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    try:
        repo = CredentialRepository(db_path=db_path)
        assert not repo.is_vault_initialized()

        # Configurar clave maestra
        salt = os.urandom(16)
        key = os.urandom(32)
        repo.setup_master_vault(salt, key)
        assert repo.is_vault_initialized()
        assert repo.verify_master_key(key)
        assert not repo.verify_master_key(os.urandom(32))

        # Añadir credencial
        cred_id = repo.add_credential("GitHub", "dev@user.com", b"encrypted_payload", "Token API")
        assert cred_id > 0

        # Listar y filtrar
        items = repo.get_all_credentials()
        assert len(items) == 1
        assert items[0].site == "GitHub"

        # Búsqueda
        search_match = repo.get_all_credentials("git")
        assert len(search_match) == 1

        search_no_match = repo.get_all_credentials("netflix")
        assert len(search_no_match) == 0

        # Actualizar
        repo.update_credential(cred_id, "GitHub Enterprise", "admin@user.com", b"new_encrypted_payload", "Actualizado")
        updated_items = repo.get_all_credentials()
        assert updated_items[0].site == "GitHub Enterprise"
        assert updated_items[0].username == "admin@user.com"

        # Eliminar
        repo.delete_credential(cred_id)
        assert len(repo.get_all_credentials()) == 0

        # Liberar referencia para Windows
        del repo
        gc.collect()

    finally:
        try:
            if db_path.exists():
                os.remove(db_path)
        except OSError:
            pass

if __name__ == "__main__":
    test_repository_lifecycle()
    print("✓ Todos los tests de repositorio pasaron exitosamente.")
