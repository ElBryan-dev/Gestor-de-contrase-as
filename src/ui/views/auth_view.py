from typing import Callable
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from src.config import THEME
from src.ui.icons import IconManager
from src.ui.components.strength_meter import StrengthMeter

class SetupView(ctk.CTkFrame):
    """Pantalla para inicializar la bóveda por primera vez."""

    def __init__(self, parent, on_setup_complete: Callable[[str], None]):
        super().__init__(parent, fg_color=THEME["bg_main"])
        self.on_setup_complete = on_setup_complete
        self._show_pass = False

        self._build_ui()

    def _build_ui(self):
        # Card central
        card = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_surface"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=16,
            width=460,
            height=540
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        # Icono de marca
        icon_shield = IconManager.get_icon("shield", size=(42, 42))
        lbl_icon = ctk.CTkLabel(card, text="", image=icon_shield)
        lbl_icon.pack(pady=(40, 8))

        ctk.CTkLabel(
            card,
            text="Inicializar Bóveda",
            font=("Segoe UI", 24, "bold"),
            text_color=THEME["text_primary"]
        ).pack()

        ctk.CTkLabel(
            card,
            text="Configura tu contraseña maestra para cifrar tus datos.\nEsta clave nunca se almacena en texto plano.",
            font=("Segoe UI", 12),
            text_color=THEME["text_secondary"],
            justify="center"
        ).pack(pady=(6, 22))

        # Campo 1
        pass_row = ctk.CTkFrame(card, fg_color="transparent")
        pass_row.pack(fill="x", padx=45, pady=4)

        self.entry_pass = ctk.CTkEntry(
            pass_row,
            placeholder_text="Contraseña Maestra",
            show="*",
            height=44,
            fg_color=THEME["bg_input"],
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
            width=40,
            height=44,
            fg_color=THEME["bg_surface"],
            hover_color=THEME["bg_surface_hover"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=8,
            command=self._toggle_pass
        )
        self.btn_eye.pack(side="left", padx=(6, 0))

        # Medidor de fortaleza
        self.meter = StrengthMeter(card)
        self.meter.pack(fill="x", padx=45, pady=(2, 10))
        self.entry_pass.bind("<KeyRelease>", lambda e: self.meter.update_strength(self.entry_pass.get()))

        # Campo 2 (Confirmación)
        self.entry_confirm = ctk.CTkEntry(
            card,
            placeholder_text="Confirmar Contraseña Maestra",
            show="*",
            height=44,
            fg_color=THEME["bg_input"],
            border_color=THEME["border"],
            corner_radius=8,
            font=("Segoe UI", 13)
        )
        self.entry_confirm.pack(fill="x", padx=45, pady=6)

        # Botón Crear
        btn_create = ctk.CTkButton(
            card,
            text="Crear Bóveda Cifrada",
            height=46,
            corner_radius=8,
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            font=("Segoe UI", 13, "bold"),
            command=self._submit
        )
        btn_create.pack(fill="x", padx=45, pady=(20, 30))

        # Atajos de teclado
        self.entry_pass.bind("<Return>", lambda e: self._submit())
        self.entry_confirm.bind("<Return>", lambda e: self._submit())
        self.entry_pass.focus_set()

    def _toggle_pass(self):
        self._show_pass = not self._show_pass
        self.entry_pass.configure(show="" if self._show_pass else "*")
        new_icon = "eye" if self._show_pass else "eye-off"
        self.btn_eye.configure(image=IconManager.get_icon(new_icon, size=(16, 16)))

    def _submit(self):
        p1 = self.entry_pass.get()
        p2 = self.entry_confirm.get()

        if not p1 or not p2:
            CTkMessagebox(title="Validación", message="Debes ingresar y confirmar tu contraseña maestra.", icon="warning")
            return

        if p1 != p2:
            CTkMessagebox(title="Discrepancia", message="Las contraseñas no coinciden.", icon="cancel")
            return

        if len(p1) < 8:
            CTkMessagebox(
                title="Contraseña Vulnerable",
                message="Por seguridad de tu portafolio, la contraseña maestra debe contener al menos 8 caracteres.",
                icon="warning"
            )
            return

        self.on_setup_complete(p1)

class LoginView(ctk.CTkFrame):
    """Pantalla de desbloqueo de la bóveda."""

    def __init__(self, parent, on_unlock: Callable[[str], None]):
        super().__init__(parent, fg_color=THEME["bg_main"])
        self.on_unlock = on_unlock
        self._show_pass = False

        self._build_ui()

    def _build_ui(self):
        card = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_surface"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=16,
            width=430,
            height=440
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        # Logo
        icon_shield = IconManager.get_icon("shield", size=(44, 44))
        lbl_icon = ctk.CTkLabel(card, text="", image=icon_shield)
        lbl_icon.pack(pady=(45, 10))

        ctk.CTkLabel(
            card,
            text="VAULT",
            font=("Segoe UI", 24, "bold"),
            text_color=THEME["text_primary"]
        ).pack()

        ctk.CTkLabel(
            card,
            text="Gestor Criptográfico Local • AES-256-GCM",
            font=("Segoe UI", 11),
            text_color=THEME["text_secondary"]
        ).pack(pady=(2, 28))

        # Input con toggle
        pass_row = ctk.CTkFrame(card, fg_color="transparent")
        pass_row.pack(fill="x", padx=45, pady=4)

        self.entry_pass = ctk.CTkEntry(
            pass_row,
            placeholder_text="Introduce tu Contraseña Maestra",
            show="*",
            height=46,
            fg_color=THEME["bg_input"],
            border_color=THEME["border"],
            corner_radius=8,
            font=("Segoe UI", 13),
            justify="center"
        )
        self.entry_pass.pack(side="left", fill="x", expand=True)

        icon_eye_off = IconManager.get_icon("eye-off", size=(16, 16))
        self.btn_eye = ctk.CTkButton(
            pass_row,
            text="",
            image=icon_eye_off,
            width=40,
            height=46,
            fg_color=THEME["bg_surface"],
            hover_color=THEME["bg_surface_hover"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=8,
            command=self._toggle_pass
        )
        self.btn_eye.pack(side="left", padx=(6, 0))

        # Botón Desbloquear
        btn_unlock = ctk.CTkButton(
            card,
            text="Desbloquear Bóveda",
            height=46,
            corner_radius=8,
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            font=("Segoe UI", 13, "bold"),
            command=self._submit
        )
        btn_unlock.pack(fill="x", padx=45, pady=(20, 20))

        # Atajo Enter y Foco
        self.entry_pass.bind("<Return>", lambda e: self._submit())
        self.entry_pass.focus_set()

    def _toggle_pass(self):
        self._show_pass = not self._show_pass
        self.entry_pass.configure(show="" if self._show_pass else "*")
        new_icon = "eye" if self._show_pass else "eye-off"
        self.btn_eye.configure(image=IconManager.get_icon(new_icon, size=(16, 16)))

    def _submit(self):
        pwd = self.entry_pass.get()
        if not pwd:
            CTkMessagebox(title="Requerido", message="Por favor, escribe tu contraseña maestra.", icon="warning")
            return
        self.on_unlock(pwd)

