import customtkinter as ctk
from typing import Optional
from src.config import THEME
from src.ui.icons import IconManager

class ToastNotification:
    """Notificación flotante no intrusiva con temporizador de auto-cierre."""

    _active_toast: Optional[ctk.CTkFrame] = None

    @classmethod
    def show(cls, parent: ctk.CTk, message: str, kind: str = "success", duration_ms: int = 2500) -> None:
        """Muestra una notificación toast elegante y suave en la base de la ventana."""
        if cls._active_toast:
            try:
                cls._active_toast.destroy()
            except Exception:
                pass
            cls._active_toast = None

        bg_color = THEME["accent_subtle"] if kind == "success" else THEME["bg_surface"]
        border_color = THEME["accent"] if kind == "success" else THEME["border"]
        text_color = THEME["accent_text"] if kind == "success" else THEME["text_primary"]
        icon_name = "check" if kind == "success" else "shield"

        toast_frame = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            corner_radius=12,
            border_width=1,
            border_color=border_color
        )
        toast_frame.place(relx=0.5, rely=0.92, anchor="center")

        icon_img = IconManager.get_icon(icon_name, size=(16, 16))
        if icon_img:
            icon_lbl = ctk.CTkLabel(toast_frame, text="", image=icon_img)
            icon_lbl.pack(side="left", padx=(14, 6), pady=8)

        text_lbl = ctk.CTkLabel(
            toast_frame,
            text=message,
            font=("Segoe UI", 12, "bold"),
            text_color=text_color
        )
        text_lbl.pack(side="left", padx=(4 if icon_img else 14, 16), pady=8)

        cls._active_toast = toast_frame

        # Desvanecer y destruir
        parent.after(duration_ms, lambda: cls._dismiss(toast_frame))

    @classmethod
    def _dismiss(cls, frame_ref: ctk.CTkFrame) -> None:
        try:
            if cls._active_toast == frame_ref:
                frame_ref.destroy()
                cls._active_toast = None
        except Exception:
            pass

