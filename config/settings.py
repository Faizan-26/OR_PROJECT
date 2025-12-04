"""
Application settings and constants for PP Chemicals OR Solver
"""

# Application Info
APP_NAME = "PP Chemicals - OR Problem Solver"
APP_VERSION = "1.0.0"
COMPANY_NAME = "PP Chemicals"

# Window Settings
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 900
MIN_WIDTH = 1280
MIN_HEIGHT = 720

# Theme Colors (Modern Professional PP Chemicals Branding)
COLORS = {
    # Primary palette
    "primary": "#0F4C75",          # Deep corporate blue
    "primary_light": "#3282B8",    # Lighter blue
    "primary_dark": "#0A3655",     # Darker blue
    
    # Secondary palette
    "secondary": "#00A8CC",        # Teal accent
    "secondary_light": "#40C4DD",  # Light teal
    
    # Accent colors
    "accent": "#FF6B35",           # Vibrant orange
    "accent_light": "#FF8A5B",     # Light orange
    "accent_hover": "#E55A2B",     # Darker orange for hover
    
    # Status colors
    "success": "#00C853",          # Bright green
    "success_light": "#69F0AE",    # Light green
    "warning": "#FFB300",          # Amber warning
    "error": "#FF1744",            # Red error
    "error_light": "#FF5252",      # Light red
    
    # Neutral colors
    "background": "#F8FAFC",       # Very light gray-blue
    "background_dark": "#1A1A2E",  # Dark mode background
    "surface": "#FFFFFF",          # White surface
    "surface_dark": "#16213E",     # Dark mode surface
    "card": "#FFFFFF",             # Card background
    "card_dark": "#1F2940",        # Dark mode card
    
    # Text colors
    "text_primary": "#1E293B",     # Dark slate
    "text_secondary": "#64748B",   # Slate gray
    "text_muted": "#94A3B8",       # Muted text
    "text_light": "#F1F5F9",       # Light text for dark bg
    
    # Border colors
    "border": "#E2E8F0",           # Light border
    "border_dark": "#334155",      # Dark mode border
    
    # Sidebar colors
    "sidebar_bg": "#0F4C75",       # Sidebar background
    "sidebar_hover": "#1A6FA8",    # Sidebar hover
    "sidebar_active": "#3282B8",   # Sidebar active item
    
    # Gradient colors
    "gradient_start": "#0F4C75",
    "gradient_end": "#00A8CC"
}

# Font settings
FONTS = {
    "family": "Segoe UI",          # Windows default
    "family_mono": "Consolas",     # Monospace for data
    "size_xs": 10,
    "size_sm": 12,
    "size_md": 14,
    "size_lg": 16,
    "size_xl": 20,
    "size_2xl": 24,
    "size_3xl": 32,
    "size_hero": 42
}

# Default Problem Sizes
DEFAULT_LP_VARIABLES = 10
DEFAULT_LP_CONSTRAINTS = 10
DEFAULT_MATRIX_SIZE = 10

# PP Chemicals Product Names (for demo data)
PRODUCTS = [
    "Bitumen Emulsion",
    "Modified Bitumen",
    "Concrete Plasticizer",
    "Curing Compound",
    "Waterproofing Compound",
    "Road Marking Paint",
    "Anti-Strip Agent",
    "Concrete Hardener",
    "Epoxy Coating",
    "Polymer Modified Bitumen"
]

# Worker Names (for assignment demo)
WORKERS = [
    "Ahmed Khan", "Bilal Hussain", "Chaudhry Tariq", "Danish Ali", "Ejaz Ahmed",
    "Farhan Malik", "Ghulam Abbas", "Hassan Raza", "Imran Shah", "Junaid Iqbal"
]

# Task Names (for assignment demo)
TASKS = [
    "Mixing", "Heating", "Testing", "Packing", "Loading",
    "Quality Control", "Maintenance", "Documentation", "Safety Check", "Dispatch"
]

# Plant Names (for transportation demo)
PLANTS = [
    "Karachi Plant", "Lahore Plant", "Islamabad Plant", "Faisalabad Plant",
    "Rawalpindi Plant", "Multan Plant", "Peshawar Plant", "Quetta Plant",
    "Sialkot Plant", "Gujranwala Plant"
]

# Destination Names (for transportation demo)
DESTINATIONS = [
    "M-2 Motorway Project", "Lahore Metro Station", "Attock Bridge Project",
    "Karachi Flyover", "GT Road Widening", "Lowari Tunnel Project",
    "Islamabad Airport", "Gwadar Port Terminal", "Peshawar Railway", "Multan Stadium"
]

# Currency Settings
CURRENCY = {
    "name": "Pakistani Rupee",
    "symbol": "Rs.",
    "code": "PKR"
}

# Constraint Types
CONSTRAINT_TYPES = ["≤", "≥", "="]

# Resource Names (for LP demo)
RESOURCES = [
    "Raw Material A (kg)",
    "Raw Material B (kg)",
    "Production Line 1 (hrs)",
    "Production Line 2 (hrs)",
    "Storage Capacity (tons)",
    "Labor Hours (man-hrs)",
    "Minimum Production (tons)",
    "Quality Control (tests)",
    "Environmental Limit (units)",
    "Energy Consumption (kWh)"
]
