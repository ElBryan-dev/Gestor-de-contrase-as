from typing import Callable, Optional
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from src.config import THEME
from src.database.repository import CredentialRecord
from src.ui.icons import IconManager
from src.ui.components.service_badge import ServiceBadge

class DashboardView(ctk.CTkFrame):
    """Vista principal de gestión de credenciales con barra lateral e interacción moderna."""

    def __init__(
        self,
        parent,
        on_add_request: Callable[[], None],
        on_open_generator: Callable[[], None],
        on_lock_vault: Callable[[], None],
        on_view_details: Callable[[CredentialRecord], None],
        on_copy_password: Callable[[CredentialRecord], None],
        on_copy_username: Callable[[str], None],
        on_delete_request: Callable[[CredentialRecord], None],
        get_credentials_func: Callable[[Optional[str]], list]
    ):
        super().__init__(parent, fg_color=THEME["bg_main"])
        self.on_add_request = on_add_request
        self.on_open_generator = on_open_generator
        self.on_lock_vault = on_lock_vault
        self.on_view_details = on_view_details
        self.on_copy_password = on_copy_password
        self.on_copy_username = on_copy_username
        self.on_delete_request = on_delete_request
        self.get_credentials_func = get_credentials_func

        self.search_query = ""
        self._build_layout()

    def _build_layout(self):
        # 1. Sidebar de Navegación Lateral
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_sidebar"],
            corner_radius=0,
            width=230
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=20, pady=(24, 20))

        icon_shield = IconManager.get_icon("shield", size=(26, 26))
        lbl_brand_icon = ctk.CTkLabel(brand_frame, text="", image=icon_shield)
        lbl_brand_icon.pack(side="left", padx=(0, 10))

        brand_text_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        brand_text_box.pack(side="left")

        ctk.CTkLabel(
            brand_text_box,
            text="VAULT",
            font=("Segoe UI", 16, "bold"),
            text_color=THEME["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_text_box,
            text="Local Security",
            font=("Segoe UI", 10),
            text_color=THEME["text_muted"]
        ).pack(anchor="w")

        # Botones de Navegación
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=14, pady=10)

        icon_vault = IconManager.get_icon("shield", size=(16, 16))
        self.btn_nav_vault = ctk.CTkButton(
            nav_frame,
            text="  Bóveda Principal",
            image=icon_vault,
            compound="left",
            anchor="w",
            height=40,
            corner_radius=8,
            fg_color=THEME["bg_surface"],
            hover_color=THEME["bg_surface_hover"],
            font=("Segoe UI", 12, "bold"),
            text_color=THEME["text_primary"],
            command=self.refresh_list
        )
        self.btn_nav_vault.pack(fill="x", pady=4)

        icon_key = IconManager.get_icon("key", size=(16, 16))
        self.btn_nav_gen = ctk.CTkButton(
            nav_frame,
            text="  Generador de Claves",
            image=icon_key,
            compound="left",
            anchor="w",
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=THEME["bg_surface_hover"],
            font=("Segoe UI", 12),
            text_color=THEME["text_secondary"],
            command=self.on_open_generator
        )
        self.btn_nav_gen.pack(fill="x", pady=4)

        # Footer del Sidebar (Status y Bloqueo)
        sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_footer.pack(side="bottom", fill="x", padx=14, pady=20)

        # Badge de cifrado
        badge_frame = ctk.CTkFrame(
            sidebar_footer,
            fg_color=THEME["bg_surface"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=6,
            height=30
        )
        badge_frame.pack(fill="x", pady=(0, 12))
        badge_frame.pack_propagate(False)

        ctk.CTkLabel(
            badge_frame,
            text="● AES-256-GCM Activo",
            font=("Segoe UI", 10, "bold"),
            text_color=THEME["accent_text"]
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Botón Bloquear
        icon_lock = IconManager.get_icon("lock", size=(15, 15))
        btn_lock = ctk.CTkButton(
            sidebar_footer,
            text=" Bloquear Bóveda",
            image=icon_lock,
            compound="left",
            height=38,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=THEME["border"],
            hover_color=THEME["bg_surface_hover"],
            font=("Segoe UI", 12),
            text_color=THEME["text_secondary"],
            command=self.on_lock_vault
        )
        btn_lock.pack(fill="x")

        # 2. Área de Contenido Principal
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", fill="both", expand=True, padx=25, pady=20)

        # Barra Superior: Búsqueda y Acción Primaria
        top_bar = ctk.CTkFrame(self.main_content, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 16))

        # Buscador con icono
        search_box = ctk.CTkFrame(
            top_bar,
            fg_color=THEME["bg_surface"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=8,
            height=42
        )
        search_box.pack(side="left", fill="x", expand=True, padx=(0, 14))
        search_box.pack_propagate(False)

        icon_search = IconManager.get_icon("search", size=(16, 16))
        lbl_search_icon = ctk.CTkLabel(search_box, text="", image=icon_search)
        lbl_search_icon.pack(side="left", padx=(12, 6))

        self.search_entry = ctk.CTkEntry(
            search_box,
            placeholder_text="Buscar credenciales por servicio, usuario o notas...",
            fg_color="transparent",
            border_width=0,
            font=("Segoe UI", 12)
        )
        self.search_entry.pack(side="left", fill="both", expand=True)
        self.search_entry.bind("<KeyRelease>", self._on_search)

        # Botón + Nueva Credencial
        icon_plus = IconManager.get_icon("plus", size=(15, 15))
        btn_add = ctk.CTkButton(
            top_bar,
            text=" Nueva Credencial",
            image=icon_plus,
            compound="left",
            width=160,
            height=42,
            corner_radius=8,
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            font=("Segoe UI", 12, "bold"),
            command=self.on_add_request
        )
        btn_add.pack(side="right")

        # Fila de Métricas / KPI Cards
        stats_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 16))

        self.kpi_count = self._create_kpi_card(stats_frame, "Total Registros", "0", side="left")
        self.kpi_crypto = self._create_kpi_card(stats_frame, "Cifrado Criptográfico", "AES-256-GCM", side="left", padx=12)
        self.kpi_model = self._create_kpi_card(stats_frame, "Modelo de Seguridad", "Zero-Knowledge", side="left")

        # Contenedor con Scroll de Tarjetas
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_content,
            fg_color="transparent",
            border_width=0
        )
        self.scroll_frame.pack(fill="both", expand=True)

        self.refresh_list()

    def _create_kpi_card(self, parent, title: str, value: str, side="left", padx=0):
        card = ctk.CTkFrame(
            parent,
            fg_color=THEME["bg_surface"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=8,
            height=62
        )
        card.pack(side=side, fill="x", expand=True, padx=padx)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 10, "bold"),
            text_color=THEME["text_muted"]
        ).pack(anchor="w", padx=14, pady=(8, 0))

        val_lbl = ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 14, "bold"),
            text_color=THEME["text_primary"]
        )
        val_lbl.pack(anchor="w", padx=14, pady=(0, 8))
        return val_lbl

    def _on_search(self, event=None):
        self.search_query = self.search_entry.get().strip()
        self.refresh_list()

    def refresh_list(self):
        """Reconstruye el listado de tarjetas según la búsqueda actual."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        credentials = self.get_credentials_func(self.search_query)
        total_count = len(self.get_credentials_func(None))
        self.kpi_count.configure(text=f"{total_count} credenciales")

        if not credentials:
            self._render_empty_state()
            return

        for cred in credentials:
            self._render_credential_card(cred)

    def _render_empty_state(self):
        empty_box = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        empty_box.pack(pady=60)

        icon_shield = IconManager.get_icon("shield", size=(40, 40))
        lbl_icon = ctk.CTkLabel(empty_box, text="", image=icon_shield)
        lbl_icon.pack(pady=(0, 10))

        if self.search_query:
            ctk.CTkLabel(
                empty_box,
                text="Sin resultados de búsqueda",
                font=("Segoe UI", 16, "bold"),
                text_color=THEME["text_primary"]
            ).pack()
            ctk.CTkLabel(
                empty_box,
                text=f"No se encontraron credenciales que coincidan con '{self.search_query}'.",
                font=("Segoe UI", 12),
                text_color=THEME["text_secondary"]
            ).pack(pady=(4, 14))

            btn_clear = ctk.CTkButton(
                empty_box,
                text="Limpiar Búsqueda",
                height=34,
                corner_radius=6,
                fg_color=THEME["bg_surface"],
                hover_color=THEME["bg_surface_hover"],
                border_width=1,
                border_color=THEME["border"],
                font=("Segoe UI", 11, "bold"),
                command=lambda: [self.search_entry.delete(0, "end"), self._on_search()]
            )
            btn_clear.pack()
        else:
            ctk.CTkLabel(
                empty_box,
                text="Tu bóveda está lista",
                font=("Segoe UI", 16, "bold"),
                text_color=THEME["text_primary"]
            ).pack()
            ctk.CTkLabel(
                empty_box,
                text="Aún no tienes credenciales registradas. Añade tu primera cuenta protegida.",
                font=("Segoe UI", 12),
                text_color=THEME["text_secondary"]
            ).pack(pady=(4, 16))

            icon_plus = IconManager.get_icon("plus", size=(15, 15))
            btn_start = ctk.CTkButton(
                empty_box,
                text=" Añadir Primera Credencial",
                image=icon_plus,
                compound="left",
                height=38,
                corner_radius=8,
                fg_color=THEME["accent"],
                hover_color=THEME["accent_hover"],
                font=("Segoe UI", 12, "bold"),
                command=self.on_add_request
            )
            btn_start.pack()

    def _render_credential_card(self, cred: CredentialRecord):
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=THEME["bg_surface"],
            border_width=1,
            border_color=THEME["border"],
            corner_radius=10,
            height=72
        )
        card.pack(fill="x", pady=4, padx=2)
        card.pack_propagate(False)

        # Monogram badge
        badge = ServiceBadge(card, cred.site, size=40)
        badge.pack(side="left", padx=(16, 12))

        # Texto identificador
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="y", padx=2)

        ctk.CTkLabel(
            info,
            text=cred.site,
            font=("Segoe UI", 14, "bold"),
            text_color=THEME["text_primary"]
        ).pack(anchor="w", pady=(14, 0))

        ctk.CTkLabel(
            info,
            text=cred.username,
            font=("Segoe UI", 11),
            text_color=THEME["text_secondary"]
        ).pack(anchor="w")

        # Botones de Acción (Lado derecho)
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(side="right", padx=14)

        # 1. Eliminar
        icon_trash = IconManager.get_icon("trash", size=(15, 15))
        btn_del = ctk.CTkButton(
            actions,
            text="",
            image=icon_trash,
            width=34,
            height=34,
            corner_radius=6,
            fg_color="transparent",
            hover_color=THEME["danger_subtle"],
            command=lambda c=cred: self.on_delete_request(c)
        )
        btn_del.pack(side="right", padx=(4, 0))

        # 2. Detalles / Editar
        icon_edit = IconManager.get_icon("edit", size=(14, 14))
        btn_view = ctk.CTkButton(
            actions,
            text=" Detalles",
            image=icon_edit,
            compound="left",
            width=88,
            height=34,
            corner_radius=6,
            fg_color=THEME["bg_input"],
            hover_color=THEME["bg_surface_hover"],
            border_width=1,
            border_color=THEME["border"],
            font=("Segoe UI", 11, "bold"),
            text_color=THEME["text_primary"],
            command=lambda c=cred: self.on_view_details(c)
        )
        btn_view.pack(side="right", padx=4)

        # 3. Copiar Contraseña Directo (1 Clic)
        icon_copy = IconManager.get_icon("copy", size=(14, 14))
        btn_copy_pwd = ctk.CTkButton(
            actions,
            text=" Clave",
            image=icon_copy,
            compound="left",
            width=80,
            height=34,
            corner_radius=6,
            fg_color=THEME["accent_subtle"],
            hover_color=THEME["accent_hover"],
            border_width=1,
            border_color=THEME["accent"],
            font=("Segoe UI", 11, "bold"),
            text_color=THEME["accent_text"],
            command=lambda c=cred: self.on_copy_password(c)
        )
        btn_copy_pwd.pack(side="right", padx=4)

        # 4. Copiar Usuario Directo
        icon_user = IconManager.get_icon("user", size=(14, 14))
        btn_copy_usr = ctk.CTkButton(
            actions,
            text=" Usuario",
            image=icon_user,
            compound="left",
            width=84,
            height=34,
            corner_radius=6,
            fg_color="transparent",
            hover_color=THEME["bg_surface_hover"],
            border_width=1,
            border_color=THEME["border"],
            font=("Segoe UI", 11),
            text_color=THEME["text_secondary"],
            command=lambda u=cred.username: self.on_copy_username(u)
        )
        btn_copy_usr.pack(side="right", padx=4)

