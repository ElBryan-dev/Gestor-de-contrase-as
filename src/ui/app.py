import threading
import time
from typing import Optional
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from src.config import THEME, CLIPBOARD_CLEAR_DELAY_SEC
from src.core.crypto import CryptoEngine, DecryptionError
from src.database.repository import CredentialRepository, CredentialRecord
from src.ui.components.toast import ToastNotification
from src.ui.views.auth_view import SetupView, LoginView
from src.ui.views.dashboard_view import DashboardView
from src.ui.modals.credential_modal import CredentialModal
from src.ui.modals.details_modal import DetailsModal
from src.ui.modals.generator_modal import GeneratorModal

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class VaultApp(ctk.CTk):
    """Aplicación principal de Vault."""

    def __init__(self):
        super().__init__()

        self.title("Vault • Gestor Criptográfico")
        self.geometry("1020x720")
        self.minsize(900, 620)
        self.configure(fg_color=THEME["bg_main"])

        # Capa de Dominio y Datos
        self.crypto = CryptoEngine()
        self.repo = CredentialRepository()
        self.master_key: Optional[bytes] = None

        # Temporizador para auto-limpieza segura de portapapeles
        self._clipboard_clear_timer: Optional[str] = None
        self._last_copied_sensitive: Optional[str] = None

        self.current_view: Optional[ctk.CTkFrame] = None
        self._navigate_initial_view()

    # ==========================================
    # GESTIÓN DE VISTAS Y NAVEGACIÓN
    # ==========================================
    def _navigate_initial_view(self):
        """Muestra la vista correspondiente según el estado de la base de datos."""
        if not self.repo.is_vault_initialized():
            self._switch_view(SetupView(self, on_setup_complete=self._on_setup_completed))
        else:
            self._switch_view(LoginView(self, on_unlock=self._on_unlock_attempt))

    def _switch_view(self, new_view: ctk.CTkFrame):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = new_view
        self.current_view.pack(fill="both", expand=True)

    # ==========================================
    # MANEJO DE AUTENTICACIÓN
    # ==========================================
    def _on_setup_completed(self, master_password: str):
        salt = self.crypto.generate_salt()
        self.master_key = self.crypto.derive_key(master_password, salt)
        self.repo.setup_master_vault(salt, self.master_key)

        ToastNotification.show(self, "Bóveda configurada y cifrada exitosamente", kind="success")
        self._show_dashboard()

    def _on_unlock_attempt(self, master_password: str):
        salt = self.repo.get_salt()
        if not salt:
            CTkMessagebox(title="Error", message="No se encontró la configuración de la bóveda.", icon="cancel")
            return

        attempt_key = self.crypto.derive_key(master_password, salt)
        if self.repo.verify_master_key(attempt_key):
            self.master_key = attempt_key
            self._show_dashboard()
            ToastNotification.show(self, "Bóveda desbloqueada", kind="info")
        else:
            CTkMessagebox(
                title="Acceso Denegado",
                message="Contraseña maestra incorrecta. Verifica tus credenciales.",
                icon="cancel"
            )

    def _lock_vault(self):
        """Cero-conocimiento: purga la clave maestra de memoria y regresa al login."""
        self.master_key = None
        self._clear_clipboard_now()
        self._switch_view(LoginView(self, on_unlock=self._on_unlock_attempt))
        ToastNotification.show(self, "Bóveda bloqueada y memoria purgada", kind="info")

    def _show_dashboard(self):
        dashboard = DashboardView(
            self,
            on_add_request=self._open_add_modal,
            on_open_generator=self._open_generator_modal,
            on_lock_vault=self._lock_vault,
            on_view_details=self._open_details_modal,
            on_copy_password=self._copy_credential_password,
            on_copy_username=self._copy_username,
            on_delete_request=self._confirm_delete,
            get_credentials_func=self.repo.get_all_credentials
        )
        self._switch_view(dashboard)

    # ==========================================
    # PORTAPAPELES Y AUTO-LIMPIEZA DE SEGURIDAD
    # ==========================================
    def copy_sensitive_data(self, data: str, label_hint: str):
        """Copia datos sensibles e inicia un temporizador de autodestrucción en el portapapeles."""
        self.clipboard_clear()
        self.clipboard_append(data)
        self._last_copied_sensitive = data

        ToastNotification.show(
            self,
            f"{label_hint} copiado (se limpiará en {CLIPBOARD_CLEAR_DELAY_SEC}s)",
            kind="success"
        )

        # Cancelar temporizador previo si existe
        if self._clipboard_clear_timer:
            self.after_cancel(self._clipboard_clear_timer)

        # Programar limpieza segura
        self._clipboard_clear_timer = self.after(
            CLIPBOARD_CLEAR_DELAY_SEC * 1000,
            self._auto_clear_clipboard
        )

    def _auto_clear_clipboard(self):
        try:
            current_clipboard = self.clipboard_get()
            if current_clipboard == self._last_copied_sensitive:
                self.clipboard_clear()
                self._last_copied_sensitive = None
                ToastNotification.show(self, "Portapapeles limpiado por seguridad", kind="info")
        except Exception:
            pass
        self._clipboard_clear_timer = None

    def _clear_clipboard_now(self):
        try:
            self.clipboard_clear()
            self._last_copied_sensitive = None
        except Exception:
            pass

    # ==========================================
    # OPERACIONES CRUD Y MODALES
    # ==========================================
    def _open_add_modal(self):
        CredentialModal(self, on_save=self._save_credential)

    def _open_generator_modal(self):
        GeneratorModal(self, on_copy=self.copy_sensitive_data)

    def _open_details_modal(self, cred: CredentialRecord):
        try:
            decrypted = self.crypto.decrypt(cred.encrypted_password, self.master_key)
        except DecryptionError:
            CTkMessagebox(title="Error", message="No se pudo descifrar la contraseña.", icon="cancel")
            return

        DetailsModal(
            self,
            credential=cred,
            decrypted_password=decrypted,
            on_copy=self.copy_sensitive_data,
            on_edit_request=self._open_edit_modal
        )

    def _open_edit_modal(self, cred: CredentialRecord, decrypted_password: str):
        CredentialModal(
            self,
            on_save=self._save_credential,
            credential=cred,
            decrypted_password=decrypted_password
        )

    def _save_credential(self, site: str, user: str, pwd: str, notes: str, cred_id: Optional[int]):
        encrypted = self.crypto.encrypt(pwd, self.master_key)
        if cred_id:
            self.repo.update_credential(cred_id, site, user, encrypted, notes)
            ToastNotification.show(self, f"Credencial de {site} actualizada", kind="success")
        else:
            self.repo.add_credential(site, user, encrypted, notes)
            ToastNotification.show(self, f"Credencial de {site} guardada", kind="success")

        if isinstance(self.current_view, DashboardView):
            self.current_view.refresh_list()

    def _copy_credential_password(self, cred: CredentialRecord):
        try:
            decrypted = self.crypto.decrypt(cred.encrypted_password, self.master_key)
            self.copy_sensitive_data(decrypted, f"Clave de {cred.site}")
        except DecryptionError:
            CTkMessagebox(title="Error", message="Error al descifrar la credencial.", icon="cancel")

    def _copy_username(self, username: str):
        self.clipboard_clear()
        self.clipboard_append(username)
        ToastNotification.show(self, "Usuario copiado", kind="info")

    def _confirm_delete(self, cred: CredentialRecord):
        confirm = CTkMessagebox(
            title="Confirmar Eliminación",
            message=f"¿Deseas eliminar permanentemente la credencial de '{cred.site}'?\nEsta acción es irreversible.",
            icon="warning",
            option_1="Cancelar",
            option_2="Eliminar"
        )
        if confirm.get() == "Eliminar":
            self.repo.delete_credential(cred.id)
            ToastNotification.show(self, f"Registro de {cred.site} eliminado", kind="info")
            if isinstance(self.current_view, DashboardView):
                self.current_view.refresh_list()

