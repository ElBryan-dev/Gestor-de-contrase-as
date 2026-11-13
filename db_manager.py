"""
Módulo heredado mantenido para compatibilidad hacia atrás.
Importa desde src.database.repository.
"""
from src.database.repository import CredentialRepository

class DBManager:
    def __init__(self, db_name="vault.db"):
        self.repo = CredentialRepository()

    def is_setup(self):
        return self.repo.is_vault_initialized()

    def setup_master(self, salt, key_derived):
        self.repo.setup_master_vault(salt, key_derived)

    def get_salt(self):
        return self.repo.get_salt()

    def verify_master(self, key_derived):
        return self.repo.verify_master_key(key_derived)

    def add_entry(self, site, username, encrypted_password, notes=""):
        return self.repo.add_credential(site, username, encrypted_password, notes)

    def get_all_entries(self):
        records = self.repo.get_all_credentials()
        return [(r.id, r.site, r.username, r.encrypted_password, r.notes) for r in records]

    def delete_entry(self, entry_id):
        self.repo.delete_credential(entry_id)

    def update_entry(self, entry_id, site, username, encrypted_password, notes):
        self.repo.update_credential(entry_id, site, username, encrypted_password, notes)

__all__ = ["DBManager"]
