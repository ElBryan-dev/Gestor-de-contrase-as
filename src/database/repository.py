import sqlite3
import hashlib
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from src.config import DEFAULT_DB_PATH

@dataclass
class CredentialRecord:
    id: int
    site: str
    username: str
    encrypted_password: bytes
    notes: str = ""

class CredentialRepository:
    """
    Repositorio para persistencia de datos en SQLite.
    Aplica buenas prácticas de conexión, consultas parametrizadas y abstracción de dominio.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = str(db_path or DEFAULT_DB_PATH)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Crea una conexión con claves foráneas activadas y row_factory configurable."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        """Inicializa las tablas base si no existen."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meta (
                    id INTEGER PRIMARY KEY,
                    salt BLOB NOT NULL,
                    verifier BLOB NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site TEXT NOT NULL,
                    username TEXT NOT NULL,
                    encrypted_password BLOB NOT NULL,
                    notes TEXT
                )
            """)
            conn.commit()

    def is_vault_initialized(self) -> bool:
        """Verifica si la bóveda ya tiene configurada una clave maestra."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM meta")
            row = cursor.fetchone()
            return (row[0] if row else 0) > 0

    def setup_master_vault(self, salt: bytes, derived_key: bytes) -> None:
        """Configura por primera vez el salt y el verificador criptográfico de la clave maestra."""
        verifier = hashlib.sha256(derived_key).digest()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM meta")  # Asegurar único registro
            cursor.execute("INSERT INTO meta (salt, verifier) VALUES (?, ?)", (salt, verifier))
            conn.commit()

    def get_salt(self) -> Optional[bytes]:
        """Obtiene el salt criptográfico guardado."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT salt FROM meta LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else None

    def verify_master_key(self, derived_key_attempt: bytes) -> bool:
        """Comprueba si el hash de la clave derivada coincide con el verificador almacenado."""
        expected_verifier = hashlib.sha256(derived_key_attempt).digest()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT verifier FROM meta LIMIT 1")
            row = cursor.fetchone()
            if not row:
                return False
            # Comparación en tiempo constante para mitigar ataques de temporización
            return hmac_constant_time_compare(row[0], expected_verifier)

    def get_all_credentials(self, search_query: Optional[str] = None) -> List[CredentialRecord]:
        """Obtiene todas las credenciales, con soporte opcional de búsqueda por texto."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if search_query and search_query.strip():
                pattern = f"%{search_query.strip().lower()}%"
                cursor.execute("""
                    SELECT id, site, username, encrypted_password, COALESCE(notes, '')
                    FROM entries
                    WHERE LOWER(site) LIKE ? OR LOWER(username) LIKE ? OR LOWER(COALESCE(notes, '')) LIKE ?
                    ORDER BY LOWER(site) ASC
                """, (pattern, pattern, pattern))
            else:
                cursor.execute("""
                    SELECT id, site, username, encrypted_password, COALESCE(notes, '')
                    FROM entries
                    ORDER BY LOWER(site) ASC
                """)

            rows = cursor.fetchall()
            return [
                CredentialRecord(
                    id=r[0],
                    site=r[1],
                    username=r[2],
                    encrypted_password=r[3],
                    notes=r[4]
                )
                for r in rows
            ]

    def add_credential(self, site: str, username: str, encrypted_password: bytes, notes: str = "") -> int:
        """Inserta una nueva credencial cifrada en la base de datos."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO entries (site, username, encrypted_password, notes)
                VALUES (?, ?, ?, ?)
            """, (site.strip(), username.strip(), encrypted_password, notes.strip()))
            conn.commit()
            return cursor.lastrowid

    def update_credential(self, credential_id: int, site: str, username: str, encrypted_password: bytes, notes: str = "") -> None:
        """Actualiza una credencial existente."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE entries
                SET site = ?, username = ?, encrypted_password = ?, notes = ?
                WHERE id = ?
            """, (site.strip(), username.strip(), encrypted_password, notes.strip(), credential_id))
            conn.commit()

    def delete_credential(self, credential_id: int) -> None:
        """Elimina permanentemente una credencial."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM entries WHERE id = ?", (credential_id,))
            conn.commit()

    def get_stats(self) -> dict:
        """Retorna estadísticas clave de la bóveda."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM entries")
            count = cursor.fetchone()[0]
            return {"total_credentials": count}

def hmac_constant_time_compare(val1: bytes, val2: bytes) -> bool:
    """Comparación segura en tiempo constante."""
    import hmac
    return hmac.compare_digest(val1, val2)

