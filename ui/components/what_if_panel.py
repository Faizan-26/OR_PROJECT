"""
What-If Analysis Panel
Interactive panel for sensitivity analysis with add/remove constraints and variables
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Any, List, Optional, Callable
import numpy as np

try:
    from config.settings import COLORS, FONTS
except ImportError:
    COLORS = {"primary": "#0F4C75", "accent": "#FF6B35", "success": "#00C853", 
              "error": "#FF1744", "background": "#F8FAFC", "border": "#E2E8F0",
              "text_primary": "#1E293B", "text_secondary": "#64748B"}
    FONTS = {"family": "Segoe UI", "size_sm": 12, "size_md": 14, "size_lg": 16}


class WhatIfPanel(ctk.CTkFrame):
    """
    Interactive What-If Analysis Panel for Linear Programming
    
    Features:
    - Add/Remove decision variables
    - Add/Remove constraints
    - Modify objective coefficients
    - Modify RHS values
    - Real-time re-solve
    - Sensitivity range visualization
    """
    
    def __init__(
        self,
        parent,
        on_resolve: Optional[Callable] = None,
        on_variable_change: Optional[Callable] = None,
        on_constraint_change: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.on_resolve = on_resolve
        self.on_variable_change = on_variable_change
        self.on_constraint_change = on_constraint_change
        
        # Current problem data
        self.num_variables = 0
        self.num_constraints = 0
        self.variable_names: List[str] = []
        self.constraint_names: List[str] = []
        self.objective_coeffs: List[float] = []
        self.constraint_matrix: np.ndarray = None
        self.rhs_values: List[float] = []
        self.solution: Dict[str, Any] = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the panel widgets"""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="🔬 What-If Analysis",
            font=ctk.CTkFont(family=FONTS.get("family", "Segoe UI"), size=18, weight="bold"),
            text_color=COLORS.get("text_primary", "#1E293B")
        ).pack(side="left")
        
        # Re-solve button
        self.resolve_btn = ctk.CTkButton(
            title_frame,
            text="⟳ Re-Solve",
            width=100,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=COLORS.get("success", "#00C853"),
            hover_color="#00A040",
            command=self._on_resolve
        )
        self.resolve_btn.pack(side="right")
        
        # Tabview for different analysis types
        self.tabview = ctk.CTkTabview(self, height=500)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tabview.add("Variables")
        self.tabview.add("Constraints")
        self.tabview.add("Objective")
        self.tabview.add("RHS Values")
        self.tabview.add("Ranges")
        
        # Setup each tab
        self._setup_variables_tab()
        self._setup_constraints_tab()
        self._setup_objective_tab()
        self._setup_rhs_tab()
        self._setup_ranges_tab()
    
    def _setup_variables_tab(self):
        """Setup the variables management tab"""
        tab = self.tabview.tab("Variables")
        
        # Header with add button
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text="Decision Variables",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="+ Add Variable",
            width=120,
            height=30,
            fg_color=COLORS.get("primary", "#0F4C75"),
            command=self._add_variable
        ).pack(side="right")
        
        # Variables list frame
        self.variables_frame = ctk.CTkScrollableFrame(tab, height=350)
        self.variables_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Variable count label
        self.var_count_label = ctk.CTkLabel(
            tab,
            text="Total: 0 variables",
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get("text_secondary", "#64748B")
        )
        self.var_count_label.pack(pady=5)
    
    def _setup_constraints_tab(self):
        """Setup the constraints management tab"""
        tab = self.tabview.tab("Constraints")
        
        # Header with add button
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text="Constraints",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="+ Add Constraint",
            width=130,
            height=30,
            fg_color=COLORS.get("primary", "#0F4C75"),
            command=self._add_constraint
        ).pack(side="right")
        
        # Constraints list frame
        self.constraints_frame = ctk.CTkScrollableFrame(tab, height=350)
        self.constraints_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Constraint count label
        self.const_count_label = ctk.CTkLabel(
            tab,
            text="Total: 0 constraints",
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get("text_secondary", "#64748B")
        )
        self.const_count_label.pack(pady=5)
    
    def _setup_objective_tab(self):
        """Setup the objective coefficients tab"""
        tab = self.tabview.tab("Objective")
        
        # Header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text="Objective Function Coefficients",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="Apply Changes",
            width=120,
            height=30,
            fg_color=COLORS.get("accent", "#FF6B35"),
            command=self._apply_objective_changes
        ).pack(side="right")
        
        # Description
        ctk.CTkLabel(
            tab,
            text="Modify coefficients to see how changes affect the optimal solution",
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get("text_secondary", "#64748B")
        ).pack(padx=10, anchor="w")
        
        # Coefficients frame
        self.objective_frame = ctk.CTkScrollableFrame(tab, height=350)
        self.objective_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _setup_rhs_tab(self):
        """Setup the RHS values tab"""
        tab = self.tabview.tab("RHS Values")
        
        # Header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text="Right-Hand Side Values",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header,
            text="Apply Changes",
            width=120,
            height=30,
            fg_color=COLORS.get("accent", "#FF6B35"),
            command=self._apply_rhs_changes
        ).pack(side="right")
        
        # Description
        ctk.CTkLabel(
            tab,
            text="Modify resource availability to analyze impact on optimal solution",
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get("text_secondary", "#64748B")
        ).pack(padx=10, anchor="w")
        
        # RHS frame
        self.rhs_frame = ctk.CTkScrollableFrame(tab, height=350)
        self.rhs_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _setup_ranges_tab(self):
        """Setup the sensitivity ranges tab"""
        tab = self.tabview.tab("Ranges")
        
        # Header
        ctk.CTkLabel(
            tab,
            text="Sensitivity Ranges",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(padx=10, pady=10, anchor="w")
        
        ctk.CTkLabel(
            tab,
            text="Shows allowable changes before the optimal basis changes",
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get("text_secondary", "#64748B")
        ).pack(padx=10, anchor="w")
        
        # Ranges display frame
        self.ranges_frame = ctk.CTkScrollableFrame(tab, height=380)
        self.ranges_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def load_problem(
        self,
        num_variables: int,
        num_constraints: int,
        variable_names: List[str],
        constraint_names: List[str],
        objective_coeffs: List[float],
        constraint_matrix: np.ndarray,
        rhs_values: List[float],
        solution: Dict[str, Any] = None
    ):
        """Load a problem into the what-if panel"""
        self.num_variables = num_variables
        self.num_constraints = num_constraints
        self.variable_names = variable_names.copy()
        self.constraint_names = constraint_names.copy()
        self.objective_coeffs = list(objective_coeffs)
        self.constraint_matrix = constraint_matrix.copy() if constraint_matrix is not None else None
        self.rhs_values = list(rhs_values)
        self.solution = solution or {}
        
        # Refresh all displays
        self._refresh_variables_display()
        self._refresh_constraints_display()
        self._refresh_objective_display()
        self._refresh_rhs_display()
        self._refresh_ranges_display()
    
    def _refresh_variables_display(self):
        """Refresh the variables list display"""
        # Clear existing
        for widget in self.variables_frame.winfo_children():
            widget.destroy()
        
        if not self.variable_names:
            ctk.CTkLabel(
                self.variables_frame,
                text="No variables defined. Add variables to begin.",
                text_color=COLORS.get("text_secondary", "#64748B")
            ).pack(pady=20)
            self.var_count_label.configure(text="Total: 0 variables")
            return
        
        # Create variable rows
        for i, name in enumerate(self.variable_names):
            self._create_variable_row(i, name)
        
        self.var_count_label.configure(text=f"Total: {len(self.variable_names)} variables")
    
    def _create_variable_row(self, index: int, name: str):
        """Create a single variable row"""
        row = ctk.CTkFrame(self.variables_frame, fg_color=COLORS.get("background", "#F8FAFC"))
        row.pack(fill="x", pady=3, padx=5)
        
        # Variable index
        ctk.CTkLabel(
            row,
            text=f"x{index + 1}",
            width=40,
            font=ctk.CTkFont(weight="bold"),
            text_color=COLORS.get("primary", "#0F4C75")
        ).pack(side="left", padx=10, pady=8)
        
        # Variable name (editable)
        name_entry = ctk.CTkEntry(row, width=140, height=30)
        name_entry.insert(0, name)
        name_entry.pack(side="left", padx=5)
        
        # Current value (if solution exists)
        if self.solution and 'solution' in self.solution:
            sol = self.solution['solution']
            if index < len(sol):
                val = sol[index]
                ctk.CTkLabel(
                    row,
                    text=f"= {val:.4f}",
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS.get("success", "#00C853") if val > 0 else COLORS.get("text_secondary", "#64748B")
                ).pack(side="left", padx=5)
        
        # Edit column coefficients button
        ctk.CTkButton(
            row,
            text="✏️",
            width=30,
            height=30,
            fg_color=COLORS.get("secondary", "#00A8CC"),
            hover_color="#008AAA",
            command=lambda idx=index: self._edit_variable_coefficients(idx)
        ).pack(side="right", padx=5)
        
        # Delete button
        ctk.CTkButton(
            row,
            text="✕",
            width=30,
            height=30,
            fg_color=COLORS.get("error", "#FF1744"),
            hover_color="#CC1133",
            command=lambda idx=index: self._remove_variable(idx)
        ).pack(side="right", padx=5)
    
    def _refresh_constraints_display(self):
        """Refresh the constraints list display"""
        # Clear existing
        for widget in self.constraints_frame.winfo_children():
            widget.destroy()
        
        if not self.constraint_names:
            ctk.CTkLabel(
                self.constraints_frame,
                text="No constraints defined. Add constraints to begin.",
                text_color=COLORS.get("text_secondary", "#64748B")
            ).pack(pady=20)
            self.const_count_label.configure(text="Total: 0 constraints")
            return
        
        # Create constraint rows
        for i, name in enumerate(self.constraint_names):
            self._create_constraint_row(i, name)
        
        self.const_count_label.configure(text=f"Total: {len(self.constraint_names)} constraints")
    
    def _create_constraint_row(self, index: int, name: str):
        """Create a single constraint row"""
        row = ctk.CTkFrame(self.constraints_frame, fg_color=COLORS.get("background", "#F8FAFC"))
        row.pack(fill="x", pady=3, padx=5)
        
        # Constraint index
        ctk.CTkLabel(
            row,
            text=f"C{index + 1}",
            width=40,
            font=ctk.CTkFont(weight="bold"),
            text_color=COLORS.get("secondary", "#00A8CC")
        ).pack(side="left", padx=10, pady=8)
        
        # Constraint name (editable)
        name_entry = ctk.CTkEntry(row, width=140, height=30)
        name_entry.insert(0, name)
        name_entry.pack(side="left", padx=5)
        
        # Binding status (if solution exists)
        if self.solution and 'slack_values' in self.solution:
            slacks = self.solution['slack_values']
            if index < len(slacks):
                slack = slacks[index]
                status = "Binding" if abs(slack) < 1e-6 else "Non-binding"
                status_color = COLORS.get("accent", "#FF6B35") if status == "Binding" else COLORS.get("text_secondary", "#64748B")
                ctk.CTkLabel(
                    row,
                    text=f"[{status}]",
                    font=ctk.CTkFont(size=11),
                    text_color=status_color
                ).pack(side="left", padx=5)
        
        # Edit coefficients button
        ctk.CTkButton(
            row,
            text="✏️",
            width=30,
            height=30,
            fg_color=COLORS.get("primary", "#0F4C75"),
            hover_color=COLORS.get("primary_dark", "#0A3655"),
            command=lambda idx=index: self._edit_constraint_coefficients(idx)
        ).pack(side="right", padx=5)
        
        # Delete button
        ctk.CTkButton(
            row,
            text="✕",
            width=30,
            height=30,
            fg_color=COLORS.get("error", "#FF1744"),
            hover_color="#CC1133",
            command=lambda idx=index: self._remove_constraint(idx)
        ).pack(side="right", padx=10)
    
    def _refresh_objective_display(self):
        """Refresh the objective coefficients display"""
        # Clear existing
        for widget in self.objective_frame.winfo_children():
            widget.destroy()
        
        if not self.variable_names:
            ctk.CTkLabel(
                self.objective_frame,
                text="No variables defined.",
                text_color=COLORS.get("text_secondary", "#64748B")
            ).pack(pady=20)
            return
        
        self.obj_entries = []
        
        # Create header
        header = ctk.CTkFrame(self.objective_frame, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(header, text="Variable", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Coefficient", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="New Value", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        # Create coefficient rows
        for i, name in enumerate(self.variable_names):
            row = ctk.CTkFrame(self.objective_frame, fg_color=COLORS.get("background", "#F8FAFC"))
            row.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(
                row,
                text=name[:15],
                width=100,
                anchor="w"
            ).pack(side="left", padx=10, pady=5)
            
            current = self.objective_coeffs[i] if i < len(self.objective_coeffs) else 0
            ctk.CTkLabel(
                row,
                text=f"{current:.2f}",
                width=100,
                text_color=COLORS.get("primary", "#0F4C75")
            ).pack(side="left", padx=5)
            
            entry = ctk.CTkEntry(row, width=100, height=28)
            entry.insert(0, str(current))
            entry.pack(side="left", padx=5)
            self.obj_entries.append(entry)
    
    def _refresh_rhs_display(self):
        """Refresh the RHS values display"""
        # Clear existing
        for widget in self.rhs_frame.winfo_children():
            widget.destroy()
        
        if not self.constraint_names:
            ctk.CTkLabel(
                self.rhs_frame,
                text="No constraints defined.",
                text_color=COLORS.get("text_secondary", "#64748B")
            ).pack(pady=20)
            return
        
        self.rhs_entries = []
        
        # Create header
        header = ctk.CTkFrame(self.rhs_frame, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(header, text="Constraint", width=120, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Current RHS", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="New Value", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Shadow Price", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        # Create RHS rows
        for i, name in enumerate(self.constraint_names):
            row = ctk.CTkFrame(self.rhs_frame, fg_color=COLORS.get("background", "#F8FAFC"))
            row.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(
                row,
                text=name[:18],
                width=120,
                anchor="w"
            ).pack(side="left", padx=10, pady=5)
            
            current = self.rhs_values[i] if i < len(self.rhs_values) else 0
            ctk.CTkLabel(
                row,
                text=f"{current:.2f}",
                width=100,
                text_color=COLORS.get("primary", "#0F4C75")
            ).pack(side="left", padx=5)
            
            entry = ctk.CTkEntry(row, width=100, height=28)
            entry.insert(0, str(current))
            entry.pack(side="left", padx=5)
            self.rhs_entries.append(entry)
            
            # Shadow price
            sp = 0
            if self.solution and 'shadow_prices' in self.solution:
                sps = self.solution['shadow_prices']
                if i < len(sps):
                    sp = sps[i]
            
            sp_color = COLORS.get("success", "#00C853") if sp > 0 else COLORS.get("text_secondary", "#64748B")
            ctk.CTkLabel(
                row,
                text=f"{sp:.4f}",
                width=100,
                text_color=sp_color
            ).pack(side="left", padx=5)
    
    def _refresh_ranges_display(self):
        """Refresh the sensitivity ranges display"""
        # Clear existing
        for widget in self.ranges_frame.winfo_children():
            widget.destroy()
        
        if not self.solution:
            ctk.CTkLabel(
                self.ranges_frame,
                text="Solve the problem first to see sensitivity ranges.",
                text_color=COLORS.get("text_secondary", "#64748B")
            ).pack(pady=20)
            return
        
        # Objective coefficient ranges section
        if 'objective_ranges' in self.solution:
            self._create_ranges_section(
                "Objective Coefficient Ranges",
                self.solution['objective_ranges'],
                is_objective=True
            )
        
        # RHS ranges section
        if 'rhs_ranges' in self.solution:
            self._create_ranges_section(
                "RHS (Resource) Ranges",
                self.solution['rhs_ranges'],
                is_objective=False
            )
    
    def _create_ranges_section(self, title: str, ranges: List[Dict], is_objective: bool):
        """Create a ranges display section"""
        # Section title
        section = ctk.CTkFrame(self.ranges_frame, fg_color="transparent")
        section.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS.get("primary", "#0F4C75")
        ).pack(anchor="w", padx=5)
        
        # Header
        header = ctk.CTkFrame(section, fg_color=COLORS.get("primary", "#0F4C75"))
        header.pack(fill="x", padx=5, pady=5)
        
        cols = ["Name", "Current", "Allow ↓", "Allow ↑"]
        for col in cols:
            ctk.CTkLabel(
                header,
                text=col,
                width=90,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white"
            ).pack(side="left", padx=5, pady=5)
        
        # Data rows
        for r in ranges:
            row = ctk.CTkFrame(section, fg_color=COLORS.get("background", "#F8FAFC"))
            row.pack(fill="x", padx=5, pady=1)
            
            name = r.get('name', 'N/A')[:12]
            current = r.get('current_coefficient' if is_objective else 'current_rhs', 0)
            dec = r.get('allowable_decrease', 0)
            inc = r.get('allowable_increase', float('inf'))
            
            dec_str = f"{dec:.2f}" if dec != float('inf') else "∞"
            inc_str = f"{inc:.2f}" if inc != float('inf') else "∞"
            
            ctk.CTkLabel(row, text=name, width=90, anchor="w").pack(side="left", padx=5, pady=3)
            ctk.CTkLabel(row, text=f"{current:.2f}", width=90).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=dec_str, width=90, text_color=COLORS.get("error", "#FF1744")).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=inc_str, width=90, text_color=COLORS.get("success", "#00C853")).pack(side="left", padx=5)
    
    def _add_variable(self):
        """Add a new decision variable"""
        new_idx = len(self.variable_names) + 1
        new_name = f"Variable {new_idx}"
        
        self.variable_names.append(new_name)
        self.objective_coeffs.append(0.0)
        self.num_variables += 1
        
        # Add column to constraint matrix
        if self.constraint_matrix is not None:
            new_col = np.zeros((self.constraint_matrix.shape[0], 1))
            self.constraint_matrix = np.hstack([self.constraint_matrix, new_col])
        
        self._refresh_variables_display()
        self._refresh_objective_display()
        
        if self.on_variable_change:
            self.on_variable_change('add', new_idx - 1, new_name)
    
    def _edit_variable_coefficients(self, variable_index: int):
        """Open a dialog to edit variable's column coefficients in constraints"""
        if self.constraint_matrix is None or self.num_constraints == 0:
            messagebox.showwarning("No Data", "No constraint matrix data available.")
            return
        
        var_name = self.variable_names[variable_index] if variable_index < len(self.variable_names) else f"x{variable_index+1}"
        
        # Create dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit Variable: {var_name}")
        dialog.geometry("500x400")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 500) // 2
        y = (dialog.winfo_screenheight() - 400) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        ctk.CTkLabel(
            dialog,
            text=f"Edit Coefficients for {var_name}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS.get("primary", "#0F4C75")
        ).pack(pady=15)
        
        # Description
        ctk.CTkLabel(
            dialog,
            text="Modify how this variable appears in each constraint:",
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get("text_secondary", "#64748B")
        ).pack(pady=5)
        
        # Scrollable frame for coefficients
        coeff_frame = ctk.CTkScrollableFrame(dialog, height=250)
        coeff_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create header
        header = ctk.CTkFrame(coeff_frame, fg_color="transparent")
        header.pack(fill="x", pady=5)
        ctk.CTkLabel(header, text="Constraint", width=150, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Coefficient", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        # Store entries
        coeff_entries = []
        
        # Create entry for each constraint
        for i in range(self.num_constraints):
            row = ctk.CTkFrame(coeff_frame, fg_color=COLORS.get("background", "#F8FAFC"))
            row.pack(fill="x", pady=2)
            
            const_name = self.constraint_names[i] if i < len(self.constraint_names) else f"C{i+1}"
            ctk.CTkLabel(
                row,
                text=const_name[:20],
                width=150,
                anchor="w"
            ).pack(side="left", padx=10, pady=5)
            
            current_val = self.constraint_matrix[i, variable_index] if i < self.constraint_matrix.shape[0] and variable_index < self.constraint_matrix.shape[1] else 0
            entry = ctk.CTkEntry(row, width=100, height=28)
            entry.insert(0, str(current_val))
            entry.pack(side="left", padx=5)
            coeff_entries.append(entry)
        
        # Button frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        def apply_changes():
            """Apply coefficient changes"""
            for i, entry in enumerate(coeff_entries):
                try:
                    val = float(entry.get())
                    if i < self.constraint_matrix.shape[0] and variable_index < self.constraint_matrix.shape[1]:
                        self.constraint_matrix[i, variable_index] = val
                except ValueError:
                    pass
            dialog.destroy()
            messagebox.showinfo("Applied", f"Coefficients for {var_name} updated. Click 'Re-Solve' to see results.")
        
        def cancel():
            """Cancel without saving"""
            dialog.destroy()
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=100,
            fg_color=COLORS.get("text_secondary", "#64748B"),
            hover_color="#475569",
            command=cancel
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Apply Changes",
            width=120,
            fg_color=COLORS.get("success", "#00C853"),
            hover_color="#00A040",
            command=apply_changes
        ).pack(side="right", padx=10)

    def _remove_variable(self, index: int):
        """Remove a decision variable"""
        if len(self.variable_names) <= 1:
            messagebox.showwarning("Cannot Remove", "Must have at least one variable.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Remove variable '{self.variable_names[index]}'?"):
            del self.variable_names[index]
            if index < len(self.objective_coeffs):
                del self.objective_coeffs[index]
            self.num_variables -= 1
            
            # Remove column from constraint matrix
            if self.constraint_matrix is not None and self.constraint_matrix.shape[1] > index:
                self.constraint_matrix = np.delete(self.constraint_matrix, index, axis=1)
            
            self._refresh_variables_display()
            self._refresh_objective_display()
            
            if self.on_variable_change:
                self.on_variable_change('remove', index, None)
    
    def _add_constraint(self):
        """Add a new constraint"""
        new_idx = len(self.constraint_names) + 1
        new_name = f"Constraint {new_idx}"
        
        self.constraint_names.append(new_name)
        self.rhs_values.append(0.0)
        self.num_constraints += 1
        
        # Add row to constraint matrix
        if self.constraint_matrix is not None:
            new_row = np.zeros((1, self.constraint_matrix.shape[1]))
            self.constraint_matrix = np.vstack([self.constraint_matrix, new_row])
        elif self.num_variables > 0:
            self.constraint_matrix = np.zeros((1, self.num_variables))
        
        self._refresh_constraints_display()
        self._refresh_rhs_display()
        
        if self.on_constraint_change:
            self.on_constraint_change('add', new_idx - 1, new_name)
    
    def _remove_constraint(self, index: int):
        """Remove a constraint"""
        if len(self.constraint_names) <= 1:
            messagebox.showwarning("Cannot Remove", "Must have at least one constraint.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Remove constraint '{self.constraint_names[index]}'?"):
            del self.constraint_names[index]
            if index < len(self.rhs_values):
                del self.rhs_values[index]
            self.num_constraints -= 1
            
            # Remove row from constraint matrix
            if self.constraint_matrix is not None and self.constraint_matrix.shape[0] > index:
                self.constraint_matrix = np.delete(self.constraint_matrix, index, axis=0)
            
            self._refresh_constraints_display()
            self._refresh_rhs_display()
            
            if self.on_constraint_change:
                self.on_constraint_change('remove', index, None)
    
    def _edit_constraint_coefficients(self, constraint_index: int):
        """Open a dialog to edit constraint coefficients"""
        if self.constraint_matrix is None or self.num_variables == 0:
            messagebox.showwarning("No Data", "No constraint matrix data available.")
            return
        
        # Create dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit Constraint: {self.constraint_names[constraint_index]}")
        dialog.geometry("500x400")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 500) // 2
        y = (dialog.winfo_screenheight() - 400) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        ctk.CTkLabel(
            dialog,
            text=f"Edit Coefficients for {self.constraint_names[constraint_index]}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS.get("primary", "#0F4C75")
        ).pack(pady=15)
        
        # Description
        ctk.CTkLabel(
            dialog,
            text="Modify the coefficient for each variable in this constraint:",
            font=ctk.CTkFont(size=11),
            text_color=COLORS.get("text_secondary", "#64748B")
        ).pack(pady=5)
        
        # Scrollable frame for coefficients
        coeff_frame = ctk.CTkScrollableFrame(dialog, height=250)
        coeff_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create header
        header = ctk.CTkFrame(coeff_frame, fg_color="transparent")
        header.pack(fill="x", pady=5)
        ctk.CTkLabel(header, text="Variable", width=150, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header, text="Coefficient", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        # Store entries
        coeff_entries = []
        
        # Create entry for each variable
        for i in range(self.num_variables):
            row = ctk.CTkFrame(coeff_frame, fg_color=COLORS.get("background", "#F8FAFC"))
            row.pack(fill="x", pady=2)
            
            var_name = self.variable_names[i] if i < len(self.variable_names) else f"x{i+1}"
            ctk.CTkLabel(
                row,
                text=var_name[:20],
                width=150,
                anchor="w"
            ).pack(side="left", padx=10, pady=5)
            
            current_val = self.constraint_matrix[constraint_index, i] if constraint_index < self.constraint_matrix.shape[0] else 0
            entry = ctk.CTkEntry(row, width=100, height=28)
            entry.insert(0, str(current_val))
            entry.pack(side="left", padx=5)
            coeff_entries.append(entry)
        
        # Button frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        def apply_changes():
            """Apply coefficient changes"""
            for i, entry in enumerate(coeff_entries):
                try:
                    val = float(entry.get())
                    if constraint_index < self.constraint_matrix.shape[0] and i < self.constraint_matrix.shape[1]:
                        self.constraint_matrix[constraint_index, i] = val
                except ValueError:
                    pass
            dialog.destroy()
            messagebox.showinfo("Applied", f"Coefficients for {self.constraint_names[constraint_index]} updated. Click 'Re-Solve' to see results.")
        
        def cancel():
            """Cancel without saving"""
            dialog.destroy()
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=100,
            fg_color=COLORS.get("text_secondary", "#64748B"),
            hover_color="#475569",
            command=cancel
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Apply Changes",
            width=120,
            fg_color=COLORS.get("success", "#00C853"),
            hover_color="#00A040",
            command=apply_changes
        ).pack(side="right", padx=10)

    def _apply_objective_changes(self):
        """Apply changes to objective coefficients"""
        if hasattr(self, 'obj_entries'):
            for i, entry in enumerate(self.obj_entries):
                try:
                    val = float(entry.get())
                    if i < len(self.objective_coeffs):
                        self.objective_coeffs[i] = val
                except ValueError:
                    pass
        
        messagebox.showinfo("Applied", "Objective coefficient changes applied. Click 'Re-Solve' to see results.")
    
    def _apply_rhs_changes(self):
        """Apply changes to RHS values"""
        if hasattr(self, 'rhs_entries'):
            for i, entry in enumerate(self.rhs_entries):
                try:
                    val = float(entry.get())
                    if i < len(self.rhs_values):
                        self.rhs_values[i] = val
                except ValueError:
                    pass
        
        messagebox.showinfo("Applied", "RHS value changes applied. Click 'Re-Solve' to see results.")
    
    def _on_resolve(self):
        """Trigger re-solve with current modifications"""
        if self.on_resolve:
            self.on_resolve()
    
    def get_modified_problem(self) -> Dict[str, Any]:
        """Get the modified problem data"""
        return {
            'num_variables': self.num_variables,
            'num_constraints': self.num_constraints,
            'variable_names': self.variable_names,
            'constraint_names': self.constraint_names,
            'objective_coeffs': self.objective_coeffs,
            'constraint_matrix': self.constraint_matrix,
            'rhs_values': self.rhs_values
        }
    
    def update_solution(self, solution: Dict[str, Any]):
        """Update with new solution after re-solve"""
        self.solution = solution
        self._refresh_variables_display()
        self._refresh_constraints_display()
        self._refresh_rhs_display()
        self._refresh_ranges_display()
