import customtkinter as ctk
from src.config import THEME
from src.core.security import PasswordAuditor

class StrengthMeter(ctk.CTkFrame):
    """Componente reutilizable de medición de fortaleza y entropía de contraseñas."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        # Barra de progreso
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=5,
            corner_radius=3,
            fg_color=THEME["bg_input"],
            progress_color=THEME["text_muted"]
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(2, 4))

        # Fila de etiquetas
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x")

        self.label_rating = ctk.CTkLabel(
            info_frame,
            text="Seguridad: Sin clave",
            font=("Segoe UI", 11, "bold"),
            text_color=THEME["text_muted"]
        )
        self.label_rating.pack(side="left")

        self.label_entropy = ctk.CTkLabel(
            info_frame,
            text="0 bits de entropía",
            font=("Segoe UI", 10),
            text_color=THEME["text_secondary"]
        )
        self.label_entropy.pack(side="right")

    def update_strength(self, password: str) -> None:
        """Actualiza la barra y etiquetas según la entropía calculada."""
        eval_data = PasswordAuditor.evaluate(password)
        
        self.progress_bar.set(eval_data["score"])
        self.progress_bar.configure(progress_color=eval_data["color"])
        
        self.label_rating.configure(
            text=f"Seguridad: {eval_data['label']}",
            text_color=eval_data["color"]
        )
        self.label_entropy.configure(
            text=f"{eval_data['entropy_bits']} bits (Shannon)"
        )

