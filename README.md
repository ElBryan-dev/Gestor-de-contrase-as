# Vault • Secure Local Password Manager

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Security](https://img.shields.io/badge/Security-AES--256--GCM-10B981?style=for-the-badge&logo=shield&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Zero--Knowledge-6366F1?style=for-the-badge)
![UI](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge)

**Vault** es un gestor de contraseñas de escritorio moderno, seguro y de alto rendimiento construido con Python y CustomTkinter. Diseñado bajo el principio de **Zero-Knowledge** (conocimiento cero), garantiza que tus credenciales sensibles nunca abandonen tu dispositivo en texto plano ni se sincronicen con servidores de terceros no confiables.

</div>

---

## 🛡️ Modelo de Seguridad y Criptografía

El sistema implementa estándares criptográficos reconocidos por la industria (NIST):

1. **Derivación de Clave Maestra (PBKDF2-HMAC-SHA256):**
   - La clave simétrica de 256 bits no se almacena en disco. Se deriva en tiempo de ejecución a partir de la contraseña maestra del usuario y un `salt` criptográfico de 16 bytes generado con `os.urandom`.
   - Se aplican **100,000 iteraciones** para mitigar ataques masivos de diccionario y ataques basados en hardware acelerado (GPU/ASIC).

2. **Cifrado Autenticado (AES-256-GCM):**
   - Cada entrada se cifra mediante **AES-256 en modo Galois/Counter Mode (GCM)**.
   - Proporciona tanto confidencialidad como integridad autenticada (AEAD).
   - Se genera un **nonce único de 12 bytes** por cada operación de cifrado, impidiendo ataques de repetición (*replay attacks*) o análisis de frecuencia.
   - Cualquier alteración accidental o maliciosa del archivo de base de datos invalida la etiqueta de autenticación (tag de 16 bytes) y rechaza el descifrado.

3. **Auditoría de Brechas con k-Anonymity (HaveIBeenPwned API):**
   - Para verificar si una contraseña ha sido expuesta en filtraciones públicas, se calcula su hash SHA-1 y **únicamente se transmiten los primeros 5 caracteres** del hash.
   - El servicio retorna el rango de coincidencias anónimas y la comparación se resuelve en local, preservando la total privacidad de la contraseña.

4. **Auto-Limpieza Segura del Portapapeles:**
   - Toda contraseña copiada al portapapeles del sistema operativo se purga automáticamente tras **30 segundos** para evitar que aplicaciones en segundo plano lean datos confidenciales.

5. **Entropía de la Información (Shannon):**
   - Medidor analítico en tiempo real que calcula los bits de entropía teóricos ($H = L \cdot \log_2(R)$) para evaluar la robustez contra fuerza bruta.

---

## ✨ Características Principales

- **Interfaz de Usuario Moderna:** Diseñada con la paleta Dark Zinc / Slate, tipografía escalonada y espaciado consistente de 8pt.
- **Iconografía Vectorial Nítida:** Gráficos vectoriales monocromáticos renderizados con Pillow (sin emojis infantiles).
- **Búsqueda Instantánea:** Filtrado en tiempo real por servicio, usuario o notas sin bloqueos de interfaz.
- **Acciones a 1 Clic:** Copia rápida de usuario o contraseña directamente desde las tarjetas de credenciales.
- **Notificaciones Toast No Intrusivas:** Confirmaciones visuales flotantes y temporales que sustituyen las ventanas emergentes del sistema operativo.
- **Generador Criptográfico Integrado:** Sliders de longitud (8 a 48 caracteres), selectores de conjuntos y garantía de distribución de caracteres.
- **Arquitectura Limpia y Modular:** Código desacoplado en capas de Dominio, Persistencia (Repository Pattern) e Interfaz Gráfica (MVC).

---

## 📂 Estructura del Proyecto

```plaintext
gestor-de-contraseñas/
├── assets/
│   └── icons/                 # Iconos vectoriales monocromáticos (PNG/Pillow)
├── src/
│   ├── __init__.py
│   ├── config.py              # Tokens de diseño, rutas y constantes de seguridad
│   ├── core/
│   │   ├── __init__.py
│   │   ├── crypto.py          # Motor AES-256-GCM y derivación PBKDF2
│   │   └── security.py        # Auditoría de entropía, k-Anonymity y generador
│   ├── database/
│   │   ├── __init__.py
│   │   └── repository.py      # Repositorio SQLite con consultas parametrizadas
│   └── ui/
│       ├── __init__.py
│       ├── app.py             # Ventana principal y orquestador de estado
│       ├── icons.py           # Gestor de caché para CTkImage
│       ├── components/        # Toasts, medidor de entropía, badges
│       ├── views/             # LoginView, SetupView, DashboardView
│       └── modals/            # Modales de credencial, detalle y generador
├── tests/
│   ├── test_crypto.py         # Pruebas unitarias de integridad y cifrado
│   ├── test_security.py       # Pruebas de generador y cálculo de entropía
│   └── test_repository.py     # Pruebas del ciclo de vida de persistencia
├── main.py                    # Punto de entrada de la aplicación
├── requirements.txt           # Dependencias fijadas del proyecto
├── .gitignore                 # Exclusiones seguras de Git (evita subir bases de datos)
└── README.md                  # Documentación del proyecto
```

---

## 🚀 Instalación y Uso

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/vault-password-manager.git
cd vault-password-manager
```

### 2. Crear y Activar Entorno Virtual (Recomendado)

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación

```bash
python main.py
```

---

## 🧪 Ejecución de Pruebas Unitarias

El proyecto cuenta con una suite completa de pruebas unitarias que validan la resistencia criptográfica, la detección de alteraciones y la persistencia:

```bash
python tests/test_crypto.py
python tests/test_security.py
python tests/test_repository.py
```

O ejecutando mediante `pytest`:

```bash
pytest tests/
```

---

## 🔒 Consideraciones de Seguridad para Producción

- **Clave Maestra:** Vault no implementa puertas traseras ni recuperación de contraseña maestra. Si se pierde la contraseña maestra, los datos cifrados son irrecuperables matemáticamente.
- **Git Hygiene:** El archivo `.gitignore` previene que archivos `.db` o respaldos locales sean incluidos por accidente en el historial de control de versiones.

---

## 📄 Licencia

Este proyecto está distribuido bajo la licencia **MIT**. Para más detalles, consulta el archivo `LICENSE`.

