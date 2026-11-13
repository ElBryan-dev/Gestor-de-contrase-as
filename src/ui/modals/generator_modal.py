from typing import Callable
import customtkinter as ctk

from src.config import THEME
from src.core.security import PasswordGenerator
from src.ui.icons import IconManager
from src.ui.components.strength_meter import StrengthMeter

class GeneratorModal(ctk.CTkToplevel):
    """Herramienta interactiva para generación criptográfica de contraseñas de alta entropía."""

    def __init__(self, parent: ctk.CTk, on_copy: Callable[[str, str], None]):
        super().__init__(parent)
        self.on_copy = on_copy

        self.title("Vault • Generador de Contraseñas")
        self.geometry("460x520")
        self.configure(fg_color=THEME["bg_main"])
        self.attributes("-topmost", True)
        self.resizable(False, False)

        self._build_ui()
        self._regenerate()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=35, pady=(28, 15))

        ctk.CTkLabel(
            header,
            text="Generador Criptográfico",
            font=("Segoe UI", 20, "bold"),
            text_color=THEME["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Genera contraseñas aleatorias utilizando CSPRNG (os.urandom).",
            font=("Segoe UI", 11),
            text_color=THEME["text_secondary"]
        ).pack(anchor="w", pady=(2, 0))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=35)

        # Output Box
        output_frame = ctk.CTkFrame(
            content,
            fg_color=THEME["bg_surface"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=8,
            height=48
        )
        output_frame.pack(fill="x", pady=(0, 6))
        output_frame.pack_propagate(False)

        self.entry_result = ctk.CTkEntry(
            output_frame,
            fg_color="transparent",
            border_width=0,
            font=("Consolas", 15, "bold"),
            justify="center",
            text_color=THEME["text_primary"]
        )
        self.entry_result.pack(side="left", padx=10, fill="both", expand=True)

        icon_copy = IconManager.get_icon("copy", size=(15, 15))
        btn_copy = ctk.CTkButton(
            output_frame,
            text=" Copiar",
            image=icon_copy,
            compound="left",
            width=76,
            height=34,
            corner_radius=6,
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            font=("Segoe UI", 11, "bold"),
            command=self._handle_copy
        )
        btn_copy.pack(side="right", padx=6)

        # Strength Meter
        self.strength_meter = StrengthMeter(content)
        self.strength_meter.pack(fill="x", pady=(0, 15))

        # Panel de Configuración
        config_card = ctk.CTkFrame(
            content,
            fg_color=THEME["bg_surface"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=8
        )
        config_card.pack(fill="x", pady=(0, 15))

        # Slider de Longitud
        slider_header = ctk.CTkFrame(config_card, fg_color="transparent")
        slider_header.pack(fill="x", padx=16, pady=(14, 2))

        ctk.CTkLabel(slider_header, text="Longitud de clave", font=("Segoe UI", 12, "bold"), text_color=THEME["text_primary"]).pack(side="left")
        self.lbl_length = ctk.CTkLabel(slider_header, text="18 caracteres", font=("Segoe UI", 12, "bold"), text_color=THEME["accent_text"])
        self.lbl_length.pack(side="right")

        self.slider = ctk.CTkSlider(
            config_card,
            from_=8,
            to=48,
            number_of_steps=40,
            button_color=THEME["accent"],
            button_hover_color=THEME["accent_hover"],
            progress_color=THEME["accent"],
            command=self._on_slider_change
        )
        self.slider.set(18)
        self.slider.pack(fill="x", padx=16, pady=(2, 14))

        # Checkboxes de juego de caracteres
        self.var_upper = ctk.BooleanVar(value=True)
        self.var_lower = ctk.BooleanVar(value=True)
        self.var_digits = ctk.BooleanVar(value=True)
        self.var_symbols = ctk.BooleanVar(value=True)

        def add_opt(text: str, var: ctk.BooleanVar):
            cb = ctk.CTkCheckBox(
                config_card,
                text=text,
                variable=var,
                font=("Segoe UI", 12),
                checkmark_color="#FFFFFF",
                fg_color=THEME["accent"],
                hover_color=THEME["accent_hover"],
                border_color=THEME["border"],
                command=self._regenerate
            )
            cb.pack(anchor="w", padx=16, pady=4)

        add_opt("Letras mayúsculas (A-Z)", self.var_upper)
        add_opt("Letras minúsculas (a-z)", self.var_lower)
        add_opt("Dígitos numéricos (0-9)", self.var_digits)
        add_opt("Símbolos y caracteres especiales (!@#$...)", self.var_symbols)

        ctk.CTkFrame(config_card, height=10, fg_color="transparent").pack()

        # Botón Regenerar
        icon_key = IconManager.get_icon("key", size=(16, 16))
        btn_regen = ctk.CTkButton(
            content,
            text=" Regenerar Nueva Clave",
            image=icon_key,
            compound="left",
            height=42,
            corner_radius=8,
            fg_color=THEME["bg_surface"],
            hover_color=THEME["bg_surface_hover"],
            border_width=1,
            border_color=THEME["border"],
            font=("Segoe UI", 12, "bold"),
            command=self._regenerate
        )
        btn_regen.pack(fill="x")

    def _on_slider_change(self, val):
        self.lbl_length.configure(text=f"{int(val)} caracteres")
        self._regenerate()

    def _regenerate(self):
        length = int(self.slider.get())
        pwd = PasswordGenerator.generate(
            length=length,
            use_upper=self.var_upper.get(),
            use_lower=self.var_lower.get(),
            use_digits=self.var_digits.get(),
            use_special=self.var_symbols.get()
        )
        self.entry_result.delete(0, "end")
        self.entry_result.insert(0, pwd)
        self.strength_meter.update_strength(pwd)

    def _handle_copy(self):
        pwd = self.entry_result.get()
        if pwd:
            self.on_copy(pwd, "Contraseña")

