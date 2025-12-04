"""
Sensitivity Analysis Table Widget
Displays sensitivity analysis results in tabular format
"""

import customtkinter as ctk
import tkinter as tk
from typing import List, Dict, Any, Optional
import numpy as np

# Import ScrollableFrame for horizontal scrolling support
from ui.components.matrix_input import ScrollableFrame


class SensitivityTable(ctk.CTkFrame):
    """
    A widget for displaying sensitivity analysis results in a structured table format
    
    Features:
    - Shadow prices display
    - Reduced costs display
    - Allowable ranges
    - Slack values
    """
    
    def __init__(
        self,
        parent,
        title: str = "Sensitivity Analysis",
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the sensitivity table widgets"""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(10, 5))
        
        # Tab view for different sections
        self.tabview = ctk.CTkTabview(self, height=350)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tabview.add("Shadow Prices")
        self.tabview.add("Reduced Costs")
        self.tabview.add("Constraint Ranges")
        self.tabview.add("Variable Ranges")
        
        # Create scrollable frames with horizontal scrolling in each tab
        self.shadow_container = ScrollableFrame(self.tabview.tab("Shadow Prices"), width=450, height=250)
        self.shadow_container.pack(fill="both", expand=True)
        self.shadow_frame = self.shadow_container.get_inner_frame()
        
        self.reduced_container = ScrollableFrame(self.tabview.tab("Reduced Costs"), width=450, height=250)
        self.reduced_container.pack(fill="both", expand=True)
        self.reduced_frame = self.reduced_container.get_inner_frame()
        
        self.constraint_container = ScrollableFrame(self.tabview.tab("Constraint Ranges"), width=450, height=250)
        self.constraint_container.pack(fill="both", expand=True)
        self.constraint_frame = self.constraint_container.get_inner_frame()
        
        self.variable_container = ScrollableFrame(self.tabview.tab("Variable Ranges"), width=450, height=250)
        self.variable_container.pack(fill="both", expand=True)
        self.variable_frame = self.variable_container.get_inner_frame()
    
    def _create_table_header(self, parent, columns: List[str]):
        """Create a table header row"""
        for j, col in enumerate(columns):
            ctk.CTkLabel(
                parent,
                text=col,
                font=ctk.CTkFont(weight="bold"),
                fg_color=("gray80", "gray30"),
                corner_radius=3,
                width=120
            ).grid(row=0, column=j, padx=2, pady=2, sticky="ew")
    
    def _create_table_row(self, parent, row_idx: int, values: List[str]):
        """Create a table data row"""
        for j, val in enumerate(values):
            # Alternate row colors
            fg_color = ("gray95", "gray25") if row_idx % 2 == 0 else ("white", "gray20")
            
            ctk.CTkLabel(
                parent,
                text=str(val),
                fg_color=fg_color,
                width=120
            ).grid(row=row_idx + 1, column=j, padx=2, pady=1, sticky="ew")
    
    def display_shadow_prices(
        self,
        shadow_prices: np.ndarray,
        slack_values: np.ndarray = None,
        constraint_names: List[str] = None
    ):
        """Display shadow prices and slack values"""
        # Clear existing
        for widget in self.shadow_frame.winfo_children():
            widget.destroy()
        
        # Create header
        columns = ["Constraint", "Shadow Price", "Slack/Surplus", "Status"]
        self._create_table_header(self.shadow_frame, columns)
        
        # Add data rows
        n = len(shadow_prices)
        names = constraint_names or [f"Constraint {i+1}" for i in range(n)]
        slacks = slack_values if slack_values is not None else np.zeros(n)
        
        for i in range(n):
            name = names[i] if i < len(names) else f"Constraint {i+1}"
            sp = shadow_prices[i]
            slack = slacks[i] if i < len(slacks) else 0
            
            # Determine binding status
            if abs(slack) < 1e-6:
                status = "Binding"
            else:
                status = "Non-binding"
            
            values = [name[:20], f"{sp:,.4f}", f"{slack:,.4f}", status]
            self._create_table_row(self.shadow_frame, i, values)
    
    def display_reduced_costs(
        self,
        reduced_costs: np.ndarray,
        solution: np.ndarray = None,
        variable_names: List[str] = None
    ):
        """Display reduced costs"""
        # Clear existing
        for widget in self.reduced_frame.winfo_children():
            widget.destroy()
        
        # Create header
        columns = ["Variable", "Value", "Reduced Cost", "Status"]
        self._create_table_header(self.reduced_frame, columns)
        
        # Add data rows
        n = len(reduced_costs)
        names = variable_names or [f"x{i+1}" for i in range(n)]
        values_arr = solution if solution is not None else np.zeros(n)
        
        for i in range(n):
            name = names[i] if i < len(names) else f"x{i+1}"
            val = values_arr[i] if i < len(values_arr) else 0
            rc = reduced_costs[i]
            
            # Determine status
            if val > 1e-6:
                status = "Basic"
            else:
                status = "Non-basic"
            
            row_values = [name[:20], f"{val:,.4f}", f"{rc:,.4f}", status]
            self._create_table_row(self.reduced_frame, i, row_values)
    
    def display_constraint_ranges(self, ranges: List[Dict]):
        """Display allowable ranges for constraint RHS values"""
        # Clear existing
        for widget in self.constraint_frame.winfo_children():
            widget.destroy()
        
        # Create header
        columns = ["Constraint", "Current RHS", "Shadow Price", "Allow. Increase", "Allow. Decrease"]
        self._create_table_header(self.constraint_frame, columns)
        
        # Add data rows
        for i, r in enumerate(ranges):
            name = r.get('name', f"Constraint {i+1}")[:15]
            current = r.get('current_rhs', 0)
            sp = r.get('shadow_price', 0)
            inc = r.get('allowable_increase', float('inf'))
            dec = r.get('allowable_decrease', 0)
            
            inc_str = "∞" if inc == float('inf') else f"{inc:,.2f}"
            dec_str = f"{dec:,.2f}"
            
            values = [name, f"{current:,.2f}", f"{sp:,.4f}", inc_str, dec_str]
            self._create_table_row(self.constraint_frame, i, values)
    
    def display_variable_ranges(self, ranges: List[Dict]):
        """Display allowable ranges for objective coefficients"""
        # Clear existing
        for widget in self.variable_frame.winfo_children():
            widget.destroy()
        
        # Create header
        columns = ["Variable", "Current Coeff", "Value", "Allow. Increase", "Allow. Decrease"]
        self._create_table_header(self.variable_frame, columns)
        
        # Add data rows
        for i, r in enumerate(ranges):
            name = r.get('name', f"x{i+1}")[:15]
            coeff = r.get('current_coefficient', 0)
            val = r.get('current_value', 0)
            inc = r.get('allowable_increase', float('inf'))
            dec = r.get('allowable_decrease', float('inf'))
            
            inc_str = "∞" if inc == float('inf') else f"{inc:,.2f}"
            dec_str = "∞" if dec == float('inf') else f"{dec:,.2f}"
            
            values = [name, f"{coeff:,.2f}", f"{val:,.4f}", inc_str, dec_str]
            self._create_table_row(self.variable_frame, i, values)
    
    def display_full_analysis(self, sensitivity_report: Dict[str, Any]):
        """Display complete sensitivity analysis from a report dictionary"""
        # Shadow prices
        if 'shadow_prices' in sensitivity_report:
            sp_data = sensitivity_report['shadow_prices']
            shadow_prices = np.array([item['value'] for item in sp_data])
            names = [item.get('name', f"C{i+1}") for i, item in enumerate(sp_data)]
            
            slack = sensitivity_report.get('slack_values', [])
            slack_values = np.array([item['value'] for item in slack]) if slack else None
            
            self.display_shadow_prices(shadow_prices, slack_values, names)
        
        # Reduced costs
        if 'reduced_costs' in sensitivity_report:
            rc_data = sensitivity_report['reduced_costs']
            reduced_costs = np.array([item['value'] for item in rc_data])
            names = [item.get('name', f"x{i+1}") for i, item in enumerate(rc_data)]
            
            self.display_reduced_costs(reduced_costs, variable_names=names)
        
        # Constraint ranges
        if 'rhs_ranges' in sensitivity_report:
            self.display_constraint_ranges(sensitivity_report['rhs_ranges'])
        
        # Variable ranges
        if 'objective_ranges' in sensitivity_report:
            self.display_variable_ranges(sensitivity_report['objective_ranges'])
    
    def clear(self):
        """Clear all tables"""
        for widget in self.shadow_frame.winfo_children():
            widget.destroy()
        for widget in self.reduced_frame.winfo_children():
            widget.destroy()
        for widget in self.constraint_frame.winfo_children():
            widget.destroy()
        for widget in self.variable_frame.winfo_children():
            widget.destroy()
