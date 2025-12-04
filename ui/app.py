"""
Main Application Window
Contains navigation and view management with professional UI
"""

import customtkinter as ctk
import tkinter as tk
from config.settings import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, 
    MIN_WIDTH, MIN_HEIGHT, COLORS, FONTS
)
from ui.dashboard import DashboardView
from ui.simplex_view import SimplexView
from ui.assignment_view import AssignmentView
from ui.transportation_view import TransportationView


class App(ctk.CTk):
    """
    Main application window for PP Chemicals OR Solver
    
    Features:
    - Modern sidebar navigation with icons
    - Tab-based views
    - Theme toggle (Light/Dark)
    - Windows-optimized rendering
    """
    
    def __init__(self):
        super().__init__()
        
        # Windows-specific optimizations
        self._configure_windows()
        
        # Configure window
        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        
        # Center window on screen
        self._center_window()
        
        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Configure default font
        self.default_font = ctk.CTkFont(family=FONTS["family"], size=FONTS["size_md"])
        
        # Track current theme
        self.is_dark_mode = False
        
        # Create UI
        self._create_layout()
        self._create_sidebar()
        self._create_views()
        
        # Show dashboard
        self._show_view("dashboard")
    
    def _configure_windows(self):
        """Apply Windows-specific optimizations"""
        try:
            # Enable DPI awareness for sharp text on high-DPI displays
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        # Set window icon (if available)
        try:
            self.iconbitmap(default='')
        except:
            pass
    
    def _center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2 - 30
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    
    def _create_layout(self):
        """Create the main layout structure"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar frame with gradient-like effect
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=COLORS["sidebar_bg"]
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Main content frame with subtle background
        self.main_frame = ctk.CTkFrame(
            self, 
            corner_radius=0,
            fg_color=COLORS["background"]
        )
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
    
    def _create_sidebar(self):
        """Create the navigation sidebar with modern design"""
        # Logo container with padding
        logo_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_container.pack(fill="x", padx=20, pady=(25, 15))
        
        # Logo text with modern styling
        logo_frame = ctk.CTkFrame(logo_container, fg_color="transparent")
        logo_frame.pack(anchor="w")
        
        ctk.CTkLabel(
            logo_frame,
            text="PP",
            font=ctk.CTkFont(family=FONTS["family"], size=32, weight="bold"),
            text_color="#FFFFFF"
        ).pack(side="left")
        
        ctk.CTkLabel(
            logo_frame,
            text="CHEMICALS",
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(side="left", padx=(5, 0), pady=(10, 0))
        
        # Tagline
        ctk.CTkLabel(
            logo_container,
            text="Operations Research Suite",
            font=ctk.CTkFont(family=FONTS["family"], size=11),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", pady=(5, 0))
        
        # Divider with accent color
        divider_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        divider_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkFrame(
            divider_frame,
            height=2,
            fg_color=COLORS["secondary"]
        ).pack(fill="x")
        
        # Navigation section label
        ctk.CTkLabel(
            self.sidebar,
            text="MAIN MENU",
            font=ctk.CTkFont(family=FONTS["family"], size=10, weight="bold"),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=25, pady=(5, 10))
        
        # Navigation buttons with modern icons
        self.nav_buttons = {}
        
        nav_items = [
            ("dashboard", "⌂", "Dashboard", "Home & Overview"),
            ("simplex", "◈", "Linear Programming", "Simplex Method"),
            ("assignment", "◫", "Assignment", "Hungarian Algorithm"),
            ("transportation", "⇄", "Transportation", "VAM + MODI")
        ]
        
        for view_id, icon, label, subtitle in nav_items:
            btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            btn_frame.pack(fill="x", padx=12, pady=3)
            
            btn = ctk.CTkButton(
                btn_frame,
                text="",
                width=216,
                height=52,
                corner_radius=10,
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                command=lambda v=view_id: self._show_view(v)
            )
            btn.pack(fill="x")
            
            # Custom button content
            inner_frame = ctk.CTkFrame(btn, fg_color="transparent")
            inner_frame.place(relx=0.02, rely=0.5, anchor="w")
            inner_frame.bind("<Button-1>", lambda e, v=view_id: self._show_view(v))
            
            # Icon with colored background
            icon_bg = ctk.CTkFrame(
                inner_frame,
                width=36,
                height=36,
                corner_radius=8,
                fg_color=COLORS["sidebar_hover"]
            )
            icon_bg.pack(side="left", padx=(8, 12))
            icon_bg.pack_propagate(False)
            icon_bg.bind("<Button-1>", lambda e, v=view_id: self._show_view(v))
            
            icon_label = ctk.CTkLabel(
                icon_bg,
                text=icon,
                font=ctk.CTkFont(size=16),
                text_color="#FFFFFF"
            )
            icon_label.place(relx=0.5, rely=0.5, anchor="center")
            icon_label.bind("<Button-1>", lambda e, v=view_id: self._show_view(v))
            
            # Text content
            text_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="y")
            text_frame.bind("<Button-1>", lambda e, v=view_id: self._show_view(v))
            
            main_label = ctk.CTkLabel(
                text_frame,
                text=label,
                font=ctk.CTkFont(family=FONTS["family"], size=13, weight="bold"),
                text_color="#FFFFFF",
                anchor="w"
            )
            main_label.pack(anchor="w")
            main_label.bind("<Button-1>", lambda e, v=view_id: self._show_view(v))
            
            sub_label = ctk.CTkLabel(
                text_frame,
                text=subtitle,
                font=ctk.CTkFont(family=FONTS["family"], size=10),
                text_color=COLORS["text_muted"],
                anchor="w"
            )
            sub_label.pack(anchor="w")
            sub_label.bind("<Button-1>", lambda e, v=view_id: self._show_view(v))
            
            self.nav_buttons[view_id] = (btn, icon_bg)
        
        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)
        
        # Bottom section divider
        ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=COLORS["sidebar_hover"]
        ).pack(fill="x", padx=20, pady=10)
        
        # Theme toggle section
        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=10)
        
        theme_label_frame = ctk.CTkFrame(theme_frame, fg_color="transparent")
        theme_label_frame.pack(side="left")
        
        ctk.CTkLabel(
            theme_label_frame,
            text="☀" if not self.is_dark_mode else "☾",
            font=ctk.CTkFont(size=16),
            text_color="#FFFFFF"
        ).pack(side="left")
        
        ctk.CTkLabel(
            theme_label_frame,
            text="  Light Mode" if not self.is_dark_mode else "  Dark Mode",
            font=ctk.CTkFont(family=FONTS["family"], size=12),
            text_color="#FFFFFF"
        ).pack(side="left")
        
        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="",
            command=self._toggle_theme,
            width=45,
            height=24,
            progress_color=COLORS["accent"],
            button_color="#FFFFFF",
            button_hover_color="#F0F0F0"
        )
        self.theme_switch.pack(side="right")
        
        # Version info with styling
        version_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS["primary_dark"])
        version_frame.pack(fill="x", side="bottom")
        
        ctk.CTkLabel(
            version_frame,
            text="PP Chemicals OR Suite v1.0.0",
            font=ctk.CTkFont(family=FONTS["family"], size=10),
            text_color=COLORS["text_muted"]
        ).pack(pady=12)
    
    def _create_views(self):
        """Create all view frames"""
        self.views = {}
        
        # Dashboard
        self.views["dashboard"] = DashboardView(
            self.main_frame,
            on_navigate=self._show_view
        )
        
        # Simplex view
        self.views["simplex"] = SimplexView(self.main_frame)
        
        # Assignment view
        self.views["assignment"] = AssignmentView(self.main_frame)
        
        # Transportation view
        self.views["transportation"] = TransportationView(self.main_frame)
    
    def _show_view(self, view_name: str):
        """Show a specific view with smooth transition"""
        # Hide all views
        for view in self.views.values():
            view.grid_forget()
        
        # Show selected view
        if view_name in self.views:
            self.views[view_name].grid(row=0, column=0, sticky="nsew")
        
        # Update nav button states with visual feedback
        for name, (btn, icon_bg) in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color=COLORS["sidebar_active"])
                icon_bg.configure(fg_color=COLORS["accent"])
            else:
                btn.configure(fg_color="transparent")
                icon_bg.configure(fg_color=COLORS["sidebar_hover"])
    
    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        self.is_dark_mode = self.theme_switch.get()
        
        if self.is_dark_mode:
            ctk.set_appearance_mode("dark")
            self.main_frame.configure(fg_color=COLORS["background_dark"])
        else:
            ctk.set_appearance_mode("light")
            self.main_frame.configure(fg_color=COLORS["background"])


def run():
    """Run the application"""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run()
