"""
Vault - Gestor Criptográfico Local de Contraseñas
Arquitectura Zero-Knowledge con cifrado AES-256-GCM y derivación PBKDF2.

Punto de entrada principal de la aplicación.
"""
from src.ui.app import VaultApp

def main():
    app = VaultApp()
    app.mainloop()

if __name__ == "__main__":
    main()
