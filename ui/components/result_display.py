"""
Result Display Widget
Formatted display for solution results with highlighting
"""

import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any, Optional, List
import numpy as np

# Import ScrollableFrame from matrix_input
from ui.components.matrix_input import ScrollableFrame


class ResultDisplay(ctk.CTkFrame):
    """
    A formatted result display widget for showing solution details
    
    Features:
    - Clear status indicators
    - Tabular data display
    - Value highlighting
    - Copy to clipboard support
    """
    
    def __init__(
        self,
        parent,
        title: str = "Results",
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the display widgets"""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(10, 5))
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_indicator = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=ctk.CTkFont(size=20),
            text_color="gray"
        )
        self.status_indicator.pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="No solution yet",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(side="left", padx=5)
        
        # Main content area
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            height=300
        )
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Text display
        self.text_display = ctk.CTkTextbox(
            self.content_frame,
            height=250,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.text_display.pack(fill="both", expand=True)
    
    def set_status(self, success: bool, message: str = ""):
        """Set the status indicator"""
        if success:
            self.status_indicator.configure(text_color="#4CAF50")
            self.status_label.configure(text=message or "Optimal Solution Found")
        else:
            self.status_indicator.configure(text_color="#F44336")
            self.status_label.configure(text=message or "No Feasible Solution")
    
    def display_text(self, text: str):
        """Display plain text content"""
        self.text_display.delete("1.0", "end")
        self.text_display.insert("1.0", text)
    
    def display_lp_result(self, result: Dict[str, Any], variable_names: List[str] = None):
        """Display Linear Programming result"""
        lines = []
        
        lines.append("=" * 50)
        lines.append("LINEAR PROGRAMMING SOLUTION")
        lines.append("=" * 50)
        
        if result.get('success', False):
            self.set_status(True, "Optimal Solution Found")
            
            lines.append(f"\nOptimal Value: {result.get('optimal_value', 0):,.4f}")
            lines.append(f"Iterations: {result.get('iterations', 0)}")
            
            lines.append("\n" + "-" * 40)
            lines.append("DECISION VARIABLES")
            lines.append("-" * 40)
            
            solution = result.get('solution', [])
            names = variable_names or [f"x{i+1}" for i in range(len(solution))]
            
            for i, val in enumerate(solution):
                name = names[i] if i < len(names) else f"x{i+1}"
                lines.append(f"  {name:.<30} {val:>12.4f}")
            
            # Sensitivity Analysis
            if 'shadow_prices' in result and len(result['shadow_prices']) > 0:
                lines.append("\n" + "-" * 40)
                lines.append("SENSITIVITY ANALYSIS")
                lines.append("-" * 40)
                
                lines.append("\nShadow Prices:")
                for i, sp in enumerate(result['shadow_prices']):
                    lines.append(f"  Constraint {i+1}: {sp:>12.4f}")
                
                if 'slack_values' in result:
                    lines.append("\nSlack/Surplus Values:")
                    for i, sv in enumerate(result['slack_values']):
                        lines.append(f"  Constraint {i+1}: {sv:>12.4f}")
        else:
            self.set_status(False, result.get('message', 'No solution'))
            lines.append(f"\nStatus: {result.get('message', 'No feasible solution')}")
        
        self.display_text("\n".join(lines))
    
    def display_assignment_result(
        self, 
        result: Dict[str, Any],
        row_names: List[str] = None,
        col_names: List[str] = None
    ):
        """Display Assignment Problem result"""
        lines = []
        
        lines.append("=" * 50)
        lines.append("ASSIGNMENT PROBLEM SOLUTION")
        lines.append("=" * 50)
        
        if result.get('success', False):
            self.set_status(True, "Optimal Assignment Found")
            
            total = result.get('total_cost', 0)
            obj_type = "Efficiency" if result.get('maximize', False) else "Cost"
            lines.append(f"\nTotal {obj_type}: {total:,.2f}")
            
            lines.append("\n" + "-" * 40)
            lines.append("OPTIMAL ASSIGNMENTS")
            lines.append("-" * 40)
            
            assignments = result.get('assignments', [])
            individual_costs = result.get('individual_costs', [])
            
            for i, (r, c) in enumerate(assignments):
                row_name = row_names[r] if row_names and r < len(row_names) else f"Worker {r+1}"
                col_name = col_names[c] if col_names and c < len(col_names) else f"Task {c+1}"
                cost = individual_costs[i] if i < len(individual_costs) else 0
                
                lines.append(f"  {row_name:.<20} → {col_name:.<15} ({obj_type}: {cost:.0f})")
        else:
            self.set_status(False, result.get('message', 'No solution'))
            lines.append(f"\nStatus: {result.get('message', 'No feasible solution')}")
        
        self.display_text("\n".join(lines))
    
    def display_transportation_result(
        self,
        result: Dict[str, Any],
        source_names: List[str] = None,
        dest_names: List[str] = None
    ):
        """Display Transportation Problem result"""
        lines = []
        
        lines.append("=" * 50)
        lines.append("TRANSPORTATION PROBLEM SOLUTION")
        lines.append("=" * 50)
        
        if result.get('success', False):
            is_optimal = result.get('is_optimal', False)
            self.set_status(True, "Optimal Solution" if is_optimal else "Feasible Solution")
            
            lines.append(f"\nTotal Transportation Cost: Rs. {result.get('total_cost', 0):,.2f}")
            lines.append(f"Initial Method: {result.get('initial_method', 'N/A')}")
            lines.append(f"MODI Iterations: {result.get('iterations', 0)}")
            
            lines.append("\n" + "-" * 40)
            lines.append("SHIPPING ROUTES")
            lines.append("-" * 40)
            
            routes = result.get('routes', [])
            
            for route in routes:
                qty = route.get('quantity', 0)
                if qty > 0.001:
                    src = route.get('from', 'Source')
                    dest = route.get('to', 'Dest')
                    cost = route.get('unit_cost', 0)
                    total = route.get('route_cost', 0)
                    
                    lines.append(f"  {src:.<15} → {dest:.<15}")
                    lines.append(f"      Quantity: {qty:>8.0f} units @ Rs. {cost:.0f}/unit = Rs. {total:,.0f}")
        else:
            self.set_status(False, result.get('message', 'No solution'))
            lines.append(f"\nStatus: {result.get('message', 'No feasible solution')}")
        
        self.display_text("\n".join(lines))
    
    def clear(self):
        """Clear the display"""
        self.status_indicator.configure(text_color="gray")
        self.status_label.configure(text="No solution yet")
        self.text_display.delete("1.0", "end")


class AllocationMatrixDisplay(ctk.CTkFrame):
    """
    Display widget for showing allocation/assignment matrices with highlighting
    """
    
    def __init__(
        self,
        parent,
        title: str = "Allocation Matrix",
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the display widgets"""
        self.title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.pack(pady=(5, 10))
        
        # Use ScrollableFrame for both horizontal and vertical scrolling
        self.scroll_container = ScrollableFrame(
            self,
            width=450,
            height=300
        )
        self.scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        self.matrix_frame = self.scroll_container.get_inner_frame()
    
    def display_matrix(
        self,
        matrix: np.ndarray,
        cost_matrix: np.ndarray = None,
        row_names: List[str] = None,
        col_names: List[str] = None,
        highlight_nonzero: bool = True
    ):
        """Display a matrix with optional highlighting"""
        # Clear existing widgets
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        
        rows, cols = matrix.shape
        row_names = row_names or [f"R{i+1}" for i in range(rows)]
        col_names = col_names or [f"C{j+1}" for j in range(cols)]
        
        cell_width = 70
        cell_height = 30
        
        # Corner cell
        ctk.CTkLabel(
            self.matrix_frame,
            text="",
            width=80,
            height=cell_height
        ).grid(row=0, column=0)
        
        # Column headers
        for j, name in enumerate(col_names):
            ctk.CTkLabel(
                self.matrix_frame,
                text=name[:8],
                width=cell_width,
                height=cell_height,
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=("gray80", "gray30"),
                corner_radius=3
            ).grid(row=0, column=j+1, padx=1, pady=1)
        
        # Rows
        for i in range(rows):
            # Row header
            ctk.CTkLabel(
                self.matrix_frame,
                text=row_names[i][:10] if i < len(row_names) else f"R{i+1}",
                width=80,
                height=cell_height,
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=("gray80", "gray30"),
                corner_radius=3
            ).grid(row=i+1, column=0, padx=1, pady=1)
            
            # Data cells
            for j in range(cols):
                value = matrix[i, j]
                
                # Format display text
                if cost_matrix is not None:
                    text = f"{value:.0f}" if value > 0 else ""
                else:
                    text = f"{value:.0f}"
                
                # Determine colors
                if highlight_nonzero and value > 0.001:
                    fg_color = ("#4CAF50", "#2E7D32")
                    text_color = "white"
                else:
                    fg_color = ("white", "gray20")
                    text_color = ("black", "white")
                
                ctk.CTkLabel(
                    self.matrix_frame,
                    text=text,
                    width=cell_width,
                    height=cell_height,
                    fg_color=fg_color,
                    text_color=text_color,
                    corner_radius=3
                ).grid(row=i+1, column=j+1, padx=1, pady=1)
    
    def clear(self):
        """Clear the display"""
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
