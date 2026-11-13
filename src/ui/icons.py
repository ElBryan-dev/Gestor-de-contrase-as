import os
from pathlib import Path
from typing import Dict, Tuple, Optional
from PIL import Image
import customtkinter as ctk

from src.config import ICONS_DIR

class IconManager:
    """Gestor y caché de iconos vectoriales para CustomTkinter."""

    _cache: Dict[Tuple[str, int, int], ctk.CTkImage] = {}

    @classmethod
    def get_icon(cls, name: str, size: Tuple[int, int] = (20, 20)) -> Optional[ctk.CTkImage]:
        """
        Carga y cachea un icono PNG renderizado con Pillow.
        Retorna una instancia de ctk.CTkImage optimizada para pantallas HiDPI.
        """
        cache_key = (name, size[0], size[1])
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        icon_filename = f"{name}.png" if not name.endswith(".png") else name
        icon_path = ICONS_DIR / icon_filename

        if not icon_path.exists():
            return None

        try:
            pil_img = Image.open(icon_path).convert("RGBA")
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
            cls._cache[cache_key] = ctk_img
            return ctk_img
        except Exception:
            return None

