"""
Main Dashboard View
Home screen with company branding and quick navigation
"""

import customtkinter as ctk
from config.settings import APP_NAME, COMPANY_NAME, COLORS


class DashboardView(ctk.CTkFrame):
    """
    Dashboard/Home view with company branding and quick access to problem types
    """
    
    def __init__(self, parent, on_navigate=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.on_navigate = on_navigate
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dashboard widgets"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=30)
        
        # Company name and title
        ctk.CTkLabel(
            header_frame,
            text="PP CHEMICALS",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=COLORS["primary"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_frame,
            text="Operations Research Decision Support System",
            font=ctk.CTkFont(size=18),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(5, 0))
        
        # Divider
        ctk.CTkFrame(self, height=2, fg_color=COLORS["primary"]).pack(fill="x", padx=40, pady=20)
        
        # Description
        desc_frame = ctk.CTkFrame(self, fg_color="transparent")
        desc_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(
            desc_frame,
            text="Welcome to the PP Chemicals OR Solver. This application helps optimize "
                 "production, workforce allocation, and distribution operations using "
                 "advanced Operations Research techniques.",
            font=ctk.CTkFont(size=14),
            wraplength=900,
            justify="left"
        ).pack(anchor="w")
        
        # Problem type cards
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Configure grid
        cards_frame.columnconfigure((0, 1, 2), weight=1)
        cards_frame.rowconfigure(0, weight=1)
        
        # Simplex card
        self._create_card(
            cards_frame,
            title="Linear Programming",
            subtitle="Simplex Method with Sensitivity Analysis",
            description="Optimize production planning with multiple products and "
                       "resource constraints. Determine the best mix of chemicals "
                       "to maximize profit or minimize costs.",
            icon="📊",
            features=["10+ decision variables", "10+ constraints", "Shadow prices", "Reduced costs"],
            color=COLORS["primary"],
            command=lambda: self._navigate("simplex"),
            row=0, col=0
        )
        
        # Assignment card
        self._create_card(
            cards_frame,
            title="Assignment Problem",
            subtitle="Hungarian Algorithm",
            description="Assign workers to tasks optimally. Match employees to "
                       "jobs based on skills, efficiency, or costs to maximize "
                       "overall productivity.",
            icon="👥",
            features=["10x10+ matrix", "Maximize/Minimize", "One-to-one matching", "Visual results"],
            color=COLORS["secondary"],
            command=lambda: self._navigate("assignment"),
            row=0, col=1
        )
        
        # Transportation card
        self._create_card(
            cards_frame,
            title="Transportation Problem",
            subtitle="VAM + MODI Method",
            description="Plan cost-effective distribution from plants to "
                       "construction sites. Minimize shipping costs while "
                       "meeting all supply and demand requirements.",
            icon="🚚",
            features=["10x10+ sources/destinations", "Multiple methods", "MODI optimization", "Route details"],
            color=COLORS["accent"],
            command=lambda: self._navigate("transportation"),
            row=0, col=2
        )
        
        # Footer
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=40, pady=20)
        
        ctk.CTkLabel(
            footer_frame,
            text="PP Chemicals - Manufacturing Excellence for Roads & Buildings",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            footer_frame,
            text="OR Solver v1.0.0",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(side="right")
    
    def _create_card(
        self,
        parent,
        title: str,
        subtitle: str,
        description: str,
        icon: str,
        features: list,
        color: str,
        command,
        row: int,
        col: int
    ):
        """Create a problem type card"""
        card = ctk.CTkFrame(parent, corner_radius=15)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        # Color accent bar
        accent = ctk.CTkFrame(card, height=8, fg_color=color, corner_radius=5)
        accent.pack(fill="x", padx=15, pady=(15, 0))
        
        # Icon
        ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=48)
        ).pack(pady=(20, 10))
        
        # Title
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(5, 0))
        
        # Subtitle
        ctk.CTkLabel(
            card,
            text=subtitle,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(pady=(0, 10))
        
        # Description
        ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(size=12),
            wraplength=250,
            justify="center"
        ).pack(padx=15, pady=5)
        
        # Features
        features_frame = ctk.CTkFrame(card, fg_color="transparent")
        features_frame.pack(pady=15)
        
        for feature in features:
            ctk.CTkLabel(
                features_frame,
                text=f"✓ {feature}",
                font=ctk.CTkFont(size=11),
                text_color=color
            ).pack(anchor="w", padx=10)
        
        # Button
        ctk.CTkButton(
            card,
            text="Open Solver →",
            command=command,
            fg_color=color,
            hover_color=self._darken_color(color),
            width=200,
            height=40
        ).pack(pady=20)
    
    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color by 20%"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
    
    def _navigate(self, view_name: str):
        """Navigate to a specific view"""
        if self.on_navigate:
            self.on_navigate(view_name)
