from typing import Optional, Callable
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from src.config import THEME
from src.core.security import PasswordGenerator
from src.database.repository import CredentialRecord
from src.ui.icons import IconManager
from src.ui.components.strength_meter import StrengthMeter
from src.ui.components.service_badge import ServiceBadge

class CredentialModal(ctk.CTkToplevel):
    """Modal para creación y edición de credenciales."""

    def __init__(
        self,
        parent: ctk.CTk,
        on_save: Callable[[str, str, str, str, Optional[int]], None],
        credential: Optional[CredentialRecord] = None,
        decrypted_password: str = ""
    ):
        super().__init__(parent)
        self.on_save = on_save
        self.credential = credential
        self.is_edit = credential is not None

        title_text = "Editar Credencial" if self.is_edit else "Nueva Credencial"
        self.title(f"Vault • {title_text}")
        self.geometry("480x620")
        self.configure(fg_color=THEME["bg_main"])
        self.attributes("-topmost", True)
        self.resizable(False, False)

        self._show_pass = False
        self._build_ui(decrypted_password)

    def _build_ui(self, decrypted_password: str):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=35, pady=(28, 15))

        title = "Editar Credencial" if self.is_edit else "Crear Nueva Credencial"
        ctk.CTkLabel(
            header,
            text=title,
            font=("Segoe UI", 20, "bold"),
            text_color=THEME["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Los datos sensibles se cifran con AES-256-GCM antes de persistir.",
            font=("Segoe UI", 11),
            text_color=THEME["text_secondary"]
        ).pack(anchor="w", pady=(2, 0))

        # Contenedor del Formulario
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=35)

        # 1. Servicio / Sitio
        ctk.CTkLabel(form, text="Servicio o Sitio Web", font=("Segoe UI", 12, "bold"), text_color=THEME["text_secondary"]).pack(anchor="w")
        self.entry_site = ctk.CTkEntry(
            form,
            placeholder_text="ej. Google, GitHub, Netflix",
            height=40,
            fg_color=THEME["bg_surface"],
            border_color=THEME["border"],
            corner_radius=8,
            font=("Segoe UI", 13)
        )
        self.entry_site.pack(fill="x", pady=(4, 12))

        # 2. Usuario / Email
        ctk.CTkLabel(form, text="Usuario o Correo", font=("Segoe UI", 12, "bold"), text_color=THEME["text_secondary"]).pack(anchor="w")
        self.entry_user = ctk.CTkEntry(
            form,
            placeholder_text="ej. usuario@ejemplo.com",
            height=40,
            fg_color=THEME["bg_surface"],
            border_color=THEME["border"],
            corner_radius=8,
            font=("Segoe UI", 13)
        )
        self.entry_user.pack(fill="x", pady=(4, 12))

        # 3. Contraseña con toggle de visibilidad y generador
        ctk.CTkLabel(form, text="Contraseña", font=("Segoe UI", 12, "bold"), text_color=THEME["text_secondary"]).pack(anchor="w")
        pass_row = ctk.CTkFrame(form, fg_color="transparent")
        pass_row.pack(fill="x", pady=(4, 2))

        self.entry_pass = ctk.CTkEntry(
            pass_row,
            placeholder_text="Escribe o genera una clave segura",
            show="*",
            height=40,
            fg_color=THEME["bg_surface"],
            border_color=THEME["border"],
            corner_radius=8,
            font=("Segoe UI", 13)
        )
        self.entry_pass.pack(side="left", fill="x", expand=True)

        icon_eye_off = IconManager.get_icon("eye-off", size=(16, 16))
        self.btn_eye = ctk.CTkButton(
            pass_row,
            text="",
            image=icon_eye_off,
            width=38,
            height=40,
            fg_color=THEME["bg_surface"],
            hover_color=THEME["bg_surface_hover"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=8,
            command=self._toggle_pass_visibility
        )
        self.btn_eye.pack(side="left", padx=(6, 0))

        icon_key = IconManager.get_icon("key", size=(16, 16))
        btn_gen = ctk.CTkButton(
            pass_row,
            text=" Generar",
            image=icon_key,
            compound="left",
            width=88,
            height=40,
            fg_color=THEME["bg_surface"],
            hover_color=THEME["bg_surface_hover"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=8,
            font=("Segoe UI", 11, "bold"),
            command=self._quick_generate
        )
        btn_gen.pack(side="left", padx=(6, 0))

        # Medidor de entropía dinámico
        self.strength_meter = StrengthMeter(form)
        self.strength_meter.pack(fill="x", pady=(4, 12))
        self.entry_pass.bind("<KeyRelease>", lambda e: self.strength_meter.update_strength(self.entry_pass.get()))

        # 4. Notas opcionales
        ctk.CTkLabel(form, text="Notas Adicionales (Opcional)", font=("Segoe UI", 12, "bold"), text_color=THEME["text_secondary"]).pack(anchor="w")
        self.entry_notes = ctk.CTkTextbox(
            form,
            height=65,
            fg_color=THEME["bg_surface"],
            border_color=THEME["border"],
            corner_radius=8,
            font=("Segoe UI", 12)
        )
        self.entry_notes.pack(fill="x", pady=(4, 18))

        # Rellenar datos si es edición
        if self.is_edit and self.credential:
            self.entry_site.insert(0, self.credential.site)
            self.entry_user.insert(0, self.credential.username)
            self.entry_pass.insert(0, decrypted_password)
            if self.credential.notes:
                self.entry_notes.insert("1.0", self.credential.notes)
            self.strength_meter.update_strength(decrypted_password)

        # Botón Guardar
        btn_action_text = "Guardar Cambios" if self.is_edit else "Guardar Credencial"
        btn_save = ctk.CTkButton(
            form,
            text=btn_action_text,
            height=44,
            corner_radius=8,
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            font=("Segoe UI", 13, "bold"),
            command=self._handle_save
        )
        btn_save.pack(fill="x", pady=(5, 15))

        self.entry_site.focus_set()

    def _toggle_pass_visibility(self):
        self._show_pass = not self._show_pass
        self.entry_pass.configure(show="" if self._show_pass else "*")
        new_icon_name = "eye" if self._show_pass else "eye-off"
        self.btn_eye.configure(image=IconManager.get_icon(new_icon_name, size=(16, 16)))

    def _quick_generate(self):
        new_pwd = PasswordGenerator.generate(length=18)
        self.entry_pass.delete(0, "end")
        self.entry_pass.insert(0, new_pwd)
        self.strength_meter.update_strength(new_pwd)

    def _handle_save(self):
        site = self.entry_site.get().strip()
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()
        notes = self.entry_notes.get("1.0", "end-1c").strip()

        if not site or not user or not pwd:
            CTkMessagebox(
                title="Campos Incompletos",
                message="El sitio web, usuario y contraseña son campos obligatorios.",
                icon="warning"
            )
            return

        cred_id = self.credential.id if self.is_edit and self.credential else None
        self.on_save(site, user, pwd, notes, cred_id)
        self.destroy()

