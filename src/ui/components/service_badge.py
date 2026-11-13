import customtkinter as ctk
from src.config import AVATAR_PALETTE

class ServiceBadge(ctk.CTkFrame):
    """Badge de identificación visual con inicial estilizada del servicio."""

    def __init__(self, parent, service_name: str, size: int = 42, **kwargs):
        color = self._get_deterministic_color(service_name)
        super().__init__(
            parent,
            width=size,
            height=size,
            corner_radius=10,
            fg_color=color,
            **kwargs
        )
        self.pack_propagate(False)

        initial = (service_name[:1].upper() if service_name else "?")
        lbl = ctk.CTkLabel(
            self,
            text=initial,
            font=("Segoe UI", int(size * 0.44), "bold"),
            text_color="#FFFFFF"
        )
        lbl.place(relx=0.5, rely=0.5, anchor="center")

    @staticmethod
    def _get_deterministic_color(name: str) -> str:
        if not name:
            return AVATAR_PALETTE[0]
        hash_val = sum(ord(c) for c in name.strip())
        return AVATAR_PALETTE[hash_val % len(AVATAR_PALETTE)]

