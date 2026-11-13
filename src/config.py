import os
from pathlib import Path

# Directorios del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
DEFAULT_DB_PATH = BASE_DIR / "vault.db"

# Parámetros de Seguridad Criptográfica
PBKDF2_ITERATIONS = 100_000
SALT_SIZE_BYTES = 16
AES_KEY_SIZE_BYTES = 32  # 256 bits
GCM_NONCE_SIZE_BYTES = 12
CLIPBOARD_CLEAR_DELAY_SEC = 30  # Auto-limpieza de portapapeles por seguridad

# Tokens de Diseño (Paleta Dark Slate / Zinc Profesional)
THEME = {
    "bg_main": "#121316",         # Fondo principal ultra oscuro
    "bg_sidebar": "#18191D",      # Sidebar navegación
    "bg_surface": "#202127",      # Superficies y tarjetas elevadas
    "bg_surface_hover": "#2B2C34",# Hover de tarjetas
    "bg_input": "#16171B",        # Fondos de input
    "border": "#2D2E36",          # Bordes sutiles
    "border_focus": "#10B981",    # Foco de inputs
    
    # Colores semánticos
    "accent": "#10B981",          # Verde esmeralda primario
    "accent_hover": "#059669",
    "accent_subtle": "#064E3B",
    "accent_text": "#34D399",
    
    "danger": "#EF4444",          # Rojo destructivo
    "danger_hover": "#DC2626",
    "danger_subtle": "#451A1A",
    
    "warning": "#F59E0B",         # Advertencia
    "info": "#3B82F6",            # Información / Azul
    
    # Tipografía
    "text_primary": "#F4F4F5",    # Texto principal
    "text_secondary": "#9CA3AF",  # Texto secundario/dim
    "text_muted": "#6B7280",      # Texto tenue
}

# Paleta discreta y elegante para avatares de servicios
AVATAR_PALETTE = [
    "#3B82F6",  # Azul
    "#8B5CF6",  # Púrpura
    "#EC4899",  # Rosa
    "#10B981",  # Esmeralda
    "#F59E0B",  # Ámbar
    "#06B6D4",  # Cian
    "#6366F1",  # Índigo
    "#14B8A6",  # Turquesa
]

