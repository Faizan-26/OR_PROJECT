"""
Simplex (Linear Programming) View
UI for inputting and solving LP problems with sensitivity analysis
"""

import customtkinter as ctk
import numpy as np
from tkinter import messagebox
from typing import Optional, List

from ui.components.matrix_input import MatrixInput, VectorInput
from ui.components.result_display import ResultDisplay
from ui.components.sensitivity_table import SensitivityTable
from ui.components.what_if_panel import WhatIfPanel
from algorithms.simplex import SimplexSolver, create_sample_problem
from config.settings import PRODUCTS, RESOURCES, DEFAULT_LP_VARIABLES, DEFAULT_LP_CONSTRAINTS, COLORS


class SimplexView(ctk.CTkFrame):
    """
    View for Linear Programming (Simplex) problems
    
    Features:
    - Objective function input
    - Constraint matrix input
    - Maximize/Minimize toggle
    - Solve with sensitivity analysis
    - Load sample problem
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.num_variables = DEFAULT_LP_VARIABLES
        self.num_constraints = DEFAULT_LP_CONSTRAINTS
        
        self._create_layout()
        self._create_widgets()
    
    def _create_layout(self):
        """Create the main layout structure"""
        # Container for all panels
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # Left panel (inputs)
        self.left_panel = ctk.CTkScrollableFrame(self.main_container, width=600)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Middle panel (results)
        self.middle_panel = ctk.CTkFrame(self.main_container, width=400)
        self.middle_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Right panel (What-If Analysis) - collapsible
        self.right_panel_visible = True
        self.right_panel = ctk.CTkFrame(self.main_container, width=420)
        self.right_panel.pack(side="right", fill="both", expand=False, padx=5, pady=5)
        
        # Store last solution for what-if analysis
        self.last_result = None
        self.last_solver = None
    
    def _create_widgets(self):
        """Create all UI widgets"""
        self._create_header()
        self._create_problem_settings()
        self._create_objective_input()
        self._create_constraints_input()
        self._create_action_buttons()
        self._create_results_panel()
        self._create_whatif_panel()
    
    def _create_header(self):
        """Create the header section"""
        header_frame = ctk.CTkFrame(self.left_panel)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="Linear Programming (Simplex Method)",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left", padx=10)
        
        # Load sample button
        ctk.CTkButton(
            header_frame,
            text="Load PP Chemicals Example",
            command=self._load_sample,
            width=180,
            fg_color="#F18F01",
            hover_color="#D17E01"
        ).pack(side="right", padx=10)
    
    def _create_problem_settings(self):
        """Create problem settings section"""
        settings_frame = ctk.CTkFrame(self.left_panel)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # Size settings
        size_frame = ctk.CTkFrame(settings_frame)
        size_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(size_frame, text="Variables:").pack(side="left", padx=5)
        self.var_spinbox = ctk.CTkEntry(size_frame, width=60, justify="center")
        self.var_spinbox.insert(0, str(self.num_variables))
        self.var_spinbox.pack(side="left", padx=5)
        
        ctk.CTkLabel(size_frame, text="Constraints:").pack(side="left", padx=15)
        self.const_spinbox = ctk.CTkEntry(size_frame, width=60, justify="center")
        self.const_spinbox.insert(0, str(self.num_constraints))
        self.const_spinbox.pack(side="left", padx=5)
        
        ctk.CTkButton(
            size_frame,
            text="Resize",
            command=self._resize_problem,
            width=80
        ).pack(side="left", padx=15)
        
        # Objective type
        obj_frame = ctk.CTkFrame(settings_frame)
        obj_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(obj_frame, text="Objective:").pack(side="left", padx=5)
        
        self.objective_var = ctk.StringVar(value="maximize")
        ctk.CTkRadioButton(
            obj_frame,
            text="Maximize",
            variable=self.objective_var,
            value="maximize"
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            obj_frame,
            text="Minimize",
            variable=self.objective_var,
            value="minimize"
        ).pack(side="left", padx=10)
    
    def _create_objective_input(self):
        """Create objective function input section"""
        obj_frame = ctk.CTkFrame(self.left_panel)
        obj_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            obj_frame,
            text="Objective Function Coefficients (Profit/Cost per unit)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        self.objective_input = VectorInput(
            obj_frame,
            size=self.num_variables,
            labels=PRODUCTS[:self.num_variables],
            orientation="horizontal",
            default_value="0",
            cell_width=90
        )
        self.objective_input.pack(fill="x", padx=10, pady=5)
    
    def _create_constraints_input(self):
        """Create constraints matrix input section"""
        const_frame = ctk.CTkFrame(self.left_panel)
        const_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            const_frame,
            text="Constraint Coefficients (Resources per unit of product)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Matrix input
        self.constraint_matrix = MatrixInput(
            const_frame,
            rows=self.num_constraints,
            cols=self.num_variables,
            row_headers=RESOURCES[:self.num_constraints],
            col_headers=[p[:12] for p in PRODUCTS[:self.num_variables]],
            default_value="0",
            cell_width=70
        )
        self.constraint_matrix.pack(fill="both", expand=True, padx=10, pady=5)
        
        # RHS and constraint types
        rhs_frame = ctk.CTkFrame(const_frame)
        rhs_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            rhs_frame,
            text="Right-Hand Side (Resource Availability)",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)
        
        self.rhs_input = VectorInput(
            rhs_frame,
            size=self.num_constraints,
            labels=RESOURCES[:self.num_constraints],
            orientation="vertical",
            default_value="0",
            cell_width=100
        )
        self.rhs_input.pack(fill="x", padx=10, pady=5)
    
    def _create_action_buttons(self):
        """Create action buttons"""
        btn_frame = ctk.CTkFrame(self.left_panel)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="🔍 Solve Problem",
            command=self._solve,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#1E5B8C",
            hover_color="#164569"
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear All",
            command=self._clear,
            width=120,
            height=40,
            fg_color="#F44336",
            hover_color="#D32F2F"
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="📋 Export Results",
            command=self._export,
            width=120,
            height=40,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        ).pack(side="left", padx=10, pady=10)
    
    def _create_results_panel(self):
        """Create the results display panel"""
        # Result display
        self.result_display = ResultDisplay(
            self.middle_panel,
            title="Solution Results"
        )
        self.result_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Sensitivity analysis table
        self.sensitivity_table = SensitivityTable(
            self.middle_panel,
            title="Sensitivity Analysis"
        )
        self.sensitivity_table.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _create_whatif_panel(self):
        """Create the What-If analysis panel"""
        # Toggle button at top
        toggle_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        toggle_frame.pack(fill="x", padx=5, pady=5)
        
        self.toggle_btn = ctk.CTkButton(
            toggle_frame,
            text="◀ Hide Panel",
            width=100,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS.get("text_secondary", "#64748B"),
            hover_color="#475569",
            command=self._toggle_whatif_panel
        )
        self.toggle_btn.pack(side="right")
        
        # What-If Panel
        self.whatif_panel = WhatIfPanel(
            self.right_panel,
            on_resolve=self._resolve_whatif,
            on_variable_change=self._on_variable_change,
            on_constraint_change=self._on_constraint_change
        )
        self.whatif_panel.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _toggle_whatif_panel(self):
        """Toggle the visibility of the What-If panel"""
        if self.right_panel_visible:
            self.right_panel.pack_forget()
            self.right_panel_visible = False
            # Add a button to show the panel again
            self.show_panel_btn = ctk.CTkButton(
                self.middle_panel,
                text="▶ Show What-If Panel",
                width=160,
                height=30,
                fg_color=COLORS.get("primary", "#0F4C75"),
                command=self._toggle_whatif_panel
            )
            self.show_panel_btn.pack(pady=5)
        else:
            if hasattr(self, 'show_panel_btn'):
                self.show_panel_btn.destroy()
            self.right_panel.pack(side="right", fill="both", expand=False, padx=5, pady=5)
            self.right_panel_visible = True
    
    def _on_variable_change(self, action: str, index: int, name: str):
        """Handle variable addition/removal from What-If panel"""
        if action == 'add':
            # Update the main input fields to reflect the change
            messagebox.showinfo(
                "Variable Added", 
                f"Variable added. Click 'Re-Solve' in the What-If panel to update results."
            )
        elif action == 'remove':
            messagebox.showinfo(
                "Variable Removed", 
                f"Variable removed. Click 'Re-Solve' in the What-If panel to update results."
            )
    
    def _on_constraint_change(self, action: str, index: int, name: str):
        """Handle constraint addition/removal from What-If panel"""
        if action == 'add':
            messagebox.showinfo(
                "Constraint Added", 
                f"Constraint added. Click 'Re-Solve' in the What-If panel to update results."
            )
        elif action == 'remove':
            messagebox.showinfo(
                "Constraint Removed", 
                f"Constraint removed. Click 'Re-Solve' in the What-If panel to update results."
            )
    
    def _resolve_whatif(self):
        """Re-solve with modified parameters from What-If panel"""
        try:
            # Get modified problem data
            problem = self.whatif_panel.get_modified_problem()
            
            c = np.array(problem['objective_coeffs'])
            A_ub = problem['constraint_matrix']
            b_ub = np.array(problem['rhs_values'])
            var_names = problem['variable_names']
            const_names = problem['constraint_names']
            maximize = self.objective_var.get() == "maximize"
            
            # Create and solve
            solver = SimplexSolver(
                c=c,
                A_ub=A_ub,
                b_ub=b_ub,
                maximize=maximize,
                variable_names=var_names,
                constraint_names=const_names
            )
            
            result = solver.solve()
            
            # Build result dictionary
            result_dict = {
                'success': result.success,
                'message': result.message,
                'optimal_value': result.optimal_value,
                'solution': result.solution,
                'iterations': result.iterations
            }
            
            if result.sensitivity:
                result_dict['shadow_prices'] = result.sensitivity.shadow_prices
                result_dict['slack_values'] = result.sensitivity.slack_values
            
            # Get sensitivity report with ranges
            if result.success and result.sensitivity:
                sens_report = solver.get_sensitivity_report()
                result_dict['objective_ranges'] = sens_report.get('objective_ranges', [])
                result_dict['rhs_ranges'] = sens_report.get('rhs_ranges', [])
            
            # Update What-If panel with new solution
            self.whatif_panel.update_solution(result_dict)
            
            # Update main displays
            self.result_display.display_lp_result(result_dict, var_names)
            
            if result.success and result.sensitivity:
                sens_report = solver.get_sensitivity_report()
                self.sensitivity_table.display_full_analysis(sens_report)
            
            messagebox.showinfo("Re-Solved", "Problem re-solved with modified parameters!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to re-solve: {str(e)}")
    
    def _load_sample(self):
        """Load sample PP Chemicals problem"""
        # Sample objective coefficients (profit per ton)
        objectives = np.array([5000, 7500, 4000, 3500, 6000, 4500, 8000, 3000, 9000, 8500])
        self.objective_input.set_values(objectives)
        
        # Sample constraint matrix
        constraints = np.array([
            [2, 3, 1, 2, 1, 2, 3, 1, 2, 3],    # Raw Material A
            [1, 2, 3, 1, 2, 1, 2, 3, 1, 2],    # Raw Material B
            [3, 2, 4, 1, 2, 3, 1, 2, 4, 2],    # Production Line 1
            [1, 2, 1, 3, 4, 2, 1, 2, 1, 3],    # Production Line 2
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],    # Storage
            [4, 5, 3, 4, 5, 3, 4, 5, 3, 4],    # Labor
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],  # QC
            [0.1, 0.2, 0.15, 0.1, 0.2, 0.15, 0.1, 0.2, 0.15, 0.1],  # Environmental
            [10, 15, 8, 12, 10, 8, 15, 10, 12, 14],  # Energy
            [1, 2, 1, 1, 2, 1, 2, 1, 1, 2]     # Packaging
        ])
        self.constraint_matrix.set_matrix(constraints)
        
        # Sample RHS values
        rhs = np.array([5000, 4000, 480, 400, 1000, 2000, 300, 100, 10000, 2500])
        self.rhs_input.set_values(rhs)
        
        # Set to maximize
        self.objective_var.set("maximize")
    
    def _resize_problem(self):
        """Resize the problem dimensions"""
        try:
            new_vars = int(self.var_spinbox.get())
            new_const = int(self.const_spinbox.get())
            
            if new_vars < 1 or new_const < 1:
                return
            
            self.num_variables = new_vars
            self.num_constraints = new_const
            
            # Recreate input widgets
            self.objective_input.destroy()
            self.constraint_matrix.destroy()
            self.rhs_input.destroy()
            
            # Update headers
            var_labels = [PRODUCTS[i] if i < len(PRODUCTS) else f"x{i+1}" for i in range(new_vars)]
            const_labels = [RESOURCES[i] if i < len(RESOURCES) else f"C{i+1}" for i in range(new_const)]
            
            # Recreate objective input
            obj_parent = self.left_panel.winfo_children()[2]  # Objective frame
            self.objective_input = VectorInput(
                obj_parent,
                size=new_vars,
                labels=var_labels,
                orientation="horizontal",
                default_value="0",
                cell_width=90
            )
            self.objective_input.pack(fill="x", padx=10, pady=5)
            
            # Recreate constraint matrix
            const_parent = self.left_panel.winfo_children()[3]  # Constraint frame
            self.constraint_matrix = MatrixInput(
                const_parent,
                rows=new_const,
                cols=new_vars,
                row_headers=const_labels,
                col_headers=[v[:12] for v in var_labels],
                default_value="0",
                cell_width=70
            )
            self.constraint_matrix.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Recreate RHS input
            rhs_parent = const_parent.winfo_children()[-1]  # RHS frame
            self.rhs_input = VectorInput(
                rhs_parent,
                size=new_const,
                labels=const_labels,
                orientation="vertical",
                default_value="0",
                cell_width=100
            )
            self.rhs_input.pack(fill="x", padx=10, pady=5)
            
        except ValueError:
            pass
    
    def _solve(self):
        """Solve the LP problem"""
        try:
            # Get input data
            c = self.objective_input.get_values()
            A_ub = self.constraint_matrix.get_matrix()
            b_ub = self.rhs_input.get_values()
            maximize = self.objective_var.get() == "maximize"
            
            # Get variable names
            var_names = [PRODUCTS[i] if i < len(PRODUCTS) else f"x{i+1}" 
                        for i in range(self.num_variables)]
            const_names = [RESOURCES[i] if i < len(RESOURCES) else f"Constraint {i+1}"
                          for i in range(self.num_constraints)]
            
            # Create and solve
            solver = SimplexSolver(
                c=c,
                A_ub=A_ub,
                b_ub=b_ub,
                maximize=maximize,
                variable_names=var_names,
                constraint_names=const_names
            )
            
            result = solver.solve()
            
            # Display results
            result_dict = {
                'success': result.success,
                'message': result.message,
                'optimal_value': result.optimal_value,
                'solution': result.solution,
                'iterations': result.iterations
            }
            
            if result.sensitivity:
                result_dict['shadow_prices'] = result.sensitivity.shadow_prices
                result_dict['slack_values'] = result.sensitivity.slack_values
            
            self.result_display.display_lp_result(result_dict, var_names)
            
            # Display sensitivity analysis
            if result.success and result.sensitivity:
                sens_report = solver.get_sensitivity_report()
                self.sensitivity_table.display_full_analysis(sens_report)
                
                # Add ranges to result dict for What-If panel
                result_dict['objective_ranges'] = sens_report.get('objective_ranges', [])
                result_dict['rhs_ranges'] = sens_report.get('rhs_ranges', [])
            
            # Store for What-If analysis
            self.last_result = result
            self.last_solver = solver
            
            # Load problem into What-If panel
            self.whatif_panel.load_problem(
                num_variables=self.num_variables,
                num_constraints=self.num_constraints,
                variable_names=var_names,
                constraint_names=const_names,
                objective_coeffs=c,
                constraint_matrix=A_ub,
                rhs_values=b_ub,
                solution=result_dict
            )
            
        except Exception as e:
            self.result_display.set_status(False, f"Error: {str(e)}")
    
    def _clear(self):
        """Clear all inputs and results"""
        self.objective_input.clear()
        self.constraint_matrix.clear()
        self.rhs_input.clear()
        self.result_display.clear()
        self.sensitivity_table.clear()
        # Reset What-If panel
        self.whatif_panel.load_problem(
            num_variables=0,
            num_constraints=0,
            variable_names=[],
            constraint_names=[],
            objective_coeffs=[],
            constraint_matrix=None,
            rhs_values=[],
            solution={}
        )
        self.last_result = None
        self.last_solver = None
    
    def _export(self):
        """Export results to file"""
        # TODO: Implement export functionality
        pass
