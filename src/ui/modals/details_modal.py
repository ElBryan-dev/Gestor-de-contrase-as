import threading
from typing import Callable
import customtkinter as ctk

from src.config import THEME
from src.core.security import BreachChecker
from src.database.repository import CredentialRecord
from src.ui.icons import IconManager
from src.ui.components.service_badge import ServiceBadge

class DetailsModal(ctk.CTkToplevel):
    """Modal para inspeccionar credenciales, verificar brechas y copiar datos."""

    def __init__(
        self,
        parent: ctk.CTk,
        credential: CredentialRecord,
        decrypted_password: str,
        on_copy: Callable[[str, str], None],
        on_edit_request: Callable[[CredentialRecord, str], None]
    ):
        super().__init__(parent)
        self.credential = credential
        self.decrypted_password = decrypted_password
        self.on_copy = on_copy
        self.on_edit_request = on_edit_request

        self.title(f"Vault • {credential.site}")
        self.geometry("460x540")
        self.configure(fg_color=THEME["bg_main"])
        self.attributes("-topmost", True)
        self.resizable(False, False)

        self._show_pass = False
        self._build_ui()
        self._start_breach_check()

    def _build_ui(self):
        # Header con Badge
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=35, pady=(28, 15))

        badge = ServiceBadge(header, self.credential.site, size=48)
        badge.pack(side="left", padx=(0, 14))

        info_box = ctk.CTkFrame(header, fg_color="transparent")
        info_box.pack(side="left", fill="y")

        ctk.CTkLabel(
            info_box,
            text=self.credential.site,
            font=("Segoe UI", 18, "bold"),
            text_color=THEME["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_box,
            text=self.credential.username,
            font=("Segoe UI", 12),
            text_color=THEME["text_secondary"]
        ).pack(anchor="w")

        # Contenedor central
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=35)

        # Campo Contraseña
        ctk.CTkLabel(content, text="Contraseña Almacenada", font=("Segoe UI", 12, "bold"), text_color=THEME["text_secondary"]).pack(anchor="w")
        pass_card = ctk.CTkFrame(
            content,
            fg_color=THEME["bg_surface"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=8,
            height=46
        )
        pass_card.pack(fill="x", pady=(4, 15))
        pass_card.pack_propagate(False)

        self.entry_pass = ctk.CTkEntry(
            pass_card,
            fg_color="transparent",
            border_width=0,
            font=("Consolas", 14),
            show="*"
        )
        self.entry_pass.insert(0, self.decrypted_password)
        self.entry_pass.configure(state="readonly")
        self.entry_pass.pack(side="left", padx=12, fill="both", expand=True)

        # Eye toggle
        icon_eye_off = IconManager.get_icon("eye-off", size=(16, 16))
        self.btn_eye = ctk.CTkButton(
            pass_card,
            text="",
            image=icon_eye_off,
            width=34,
            height=32,
            corner_radius=6,
            fg_color="transparent",
            hover_color=THEME["bg_surface_hover"],
            command=self._toggle_pass
        )
        self.btn_eye.pack(side="left", padx=2)

        # Botón Copiar
        icon_copy = IconManager.get_icon("copy", size=(15, 15))
        btn_copy = ctk.CTkButton(
            pass_card,
            text=" Copiar",
            image=icon_copy,
            compound="left",
            width=76,
            height=32,
            corner_radius=6,
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            font=("Segoe UI", 11, "bold"),
            command=lambda: self.on_copy(self.decrypted_password, "Contraseña")
        )
        btn_copy.pack(side="right", padx=6)

        # Auditoría de Brechas HIBP
        ctk.CTkLabel(content, text="Auditoría k-Anonymity (HaveIBeenPwned)", font=("Segoe UI", 11, "bold"), text_color=THEME["text_secondary"]).pack(anchor="w")
        self.card_breach = ctk.CTkFrame(
            content,
            fg_color=THEME["bg_surface"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=8
        )
        self.card_breach.pack(fill="x", pady=(4, 15))

        self.lbl_breach = ctk.CTkLabel(
            self.card_breach,
            text="Comprobando seguridad en bases de brechas públicas...",
            font=("Segoe UI", 11),
            text_color=THEME["text_muted"]
        )
        self.lbl_breach.pack(padx=14, pady=10, anchor="w")

        # Notas
        if self.credential.notes:
            ctk.CTkLabel(content, text="Notas", font=("Segoe UI", 11, "bold"), text_color=THEME["text_secondary"]).pack(anchor="w")
            note_box = ctk.CTkTextbox(
                content,
                height=70,
                fg_color=THEME["bg_surface"],
                border_width=1,
                border_color=THEME["border"],
                corner_radius=8,
                font=("Segoe UI", 12)
            )
            note_box.pack(fill="x", pady=(4, 15))
            note_box.insert("1.0", self.credential.notes)
            note_box.configure(state="disabled")

        # Botones inferiores
        bottom_bar = ctk.CTkFrame(content, fg_color="transparent")
        bottom_bar.pack(fill="x", pady=(10, 15))

        icon_edit = IconManager.get_icon("edit", size=(15, 15))
        btn_edit = ctk.CTkButton(
            bottom_bar,
            text=" Editar Credencial",
            image=icon_edit,
            compound="left",
            height=40,
            corner_radius=8,
            fg_color=THEME["bg_surface"],
            hover_color=THEME["bg_surface_hover"],
            border_width=1,
            border_color=THEME["border"],
            font=("Segoe UI", 12, "bold"),
            command=self._handle_edit
        )
        btn_edit.pack(fill="x")

    def _toggle_pass(self):
        self._show_pass = not self._show_pass
        self.entry_pass.configure(show="" if self._show_pass else "*")
        new_icon_name = "eye" if self._show_pass else "eye-off"
        self.btn_eye.configure(image=IconManager.get_icon(new_icon_name, size=(16, 16)))

    def _handle_edit(self):
        self.destroy()
        self.on_edit_request(self.credential, self.decrypted_password)

    def _start_breach_check(self):
        def worker():
            count = BreachChecker.check_breaches(self.decrypted_password)
            if count > 0:
                self.lbl_breach.configure(
                    text=f"Alerta: Esta contraseña aparece en {count:,} brechas públicas conocidas.",
                    text_color=THEME["danger"]
                )
                self.card_breach.configure(border_color=THEME["danger"])
            else:
                self.lbl_breach.configure(
                    text="Segura: No se encontró registro en brechas públicas analizadas.",
                    text_color=THEME["accent_text"]
                )
                self.card_breach.configure(border_color=THEME["accent"])

        threading.Thread(target=worker, daemon=True).start()

