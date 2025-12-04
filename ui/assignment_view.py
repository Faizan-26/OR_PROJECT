"""
Assignment Problem View
UI for inputting and solving assignment problems using Hungarian algorithm
"""

import customtkinter as ctk
import numpy as np
from typing import Optional, List

from ui.components.matrix_input import MatrixInput
from ui.components.result_display import ResultDisplay, AllocationMatrixDisplay
from algorithms.assignment import AssignmentSolver, create_sample_problem
from config.settings import WORKERS, TASKS, DEFAULT_MATRIX_SIZE


class AssignmentView(ctk.CTkFrame):
    """
    View for Assignment Problems
    
    Features:
    - Cost/efficiency matrix input
    - Maximize/Minimize toggle
    - Custom row/column names
    - Visual assignment display
    - Load sample problem
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.matrix_size = DEFAULT_MATRIX_SIZE
        
        self._create_layout()
        self._create_widgets()
    
    def _create_layout(self):
        """Create the main layout structure"""
        # Left panel (inputs)
        self.left_panel = ctk.CTkScrollableFrame(self, width=650)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Right panel (results)
        self.right_panel = ctk.CTkFrame(self, width=550)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
    
    def _create_widgets(self):
        """Create all UI widgets"""
        self._create_header()
        self._create_settings()
        self._create_matrix_input()
        self._create_action_buttons()
        self._create_results_panel()
    
    def _create_header(self):
        """Create the header section"""
        header_frame = ctk.CTkFrame(self.left_panel)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="Assignment Problem (Hungarian Algorithm)",
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
    
    def _create_settings(self):
        """Create settings section"""
        settings_frame = ctk.CTkFrame(self.left_panel)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # Size settings
        size_frame = ctk.CTkFrame(settings_frame)
        size_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(size_frame, text="Matrix Size:").pack(side="left", padx=5)
        
        self.rows_entry = ctk.CTkEntry(size_frame, width=60, justify="center")
        self.rows_entry.insert(0, str(self.matrix_size))
        self.rows_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(size_frame, text="x").pack(side="left", padx=5)
        
        self.cols_entry = ctk.CTkEntry(size_frame, width=60, justify="center")
        self.cols_entry.insert(0, str(self.matrix_size))
        self.cols_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            size_frame,
            text="Resize",
            command=self._resize_matrix,
            width=80
        ).pack(side="left", padx=15)
        
        # Objective type
        obj_frame = ctk.CTkFrame(settings_frame)
        obj_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(obj_frame, text="Objective:").pack(side="left", padx=5)
        
        self.objective_var = ctk.StringVar(value="maximize")
        ctk.CTkRadioButton(
            obj_frame,
            text="Maximize Efficiency",
            variable=self.objective_var,
            value="maximize"
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            obj_frame,
            text="Minimize Cost",
            variable=self.objective_var,
            value="minimize"
        ).pack(side="left", padx=10)
        
        # Description
        desc_frame = ctk.CTkFrame(settings_frame)
        desc_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            desc_frame,
            text="💡 Enter efficiency scores (higher = better) or costs (lower = better)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(pady=5)
    
    def _create_matrix_input(self):
        """Create the matrix input section"""
        matrix_frame = ctk.CTkFrame(self.left_panel)
        matrix_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            matrix_frame,
            text="Cost/Efficiency Matrix (Workers × Tasks)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Matrix input widget
        self.matrix_input = MatrixInput(
            matrix_frame,
            rows=self.matrix_size,
            cols=self.matrix_size,
            row_headers=WORKERS[:self.matrix_size],
            col_headers=TASKS[:self.matrix_size],
            default_value="0",
            cell_width=70,
            editable_headers=True
        )
        self.matrix_input.pack(fill="both", expand=True, padx=10, pady=5)
    
    def _create_action_buttons(self):
        """Create action buttons"""
        btn_frame = ctk.CTkFrame(self.left_panel)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="🔍 Find Optimal Assignment",
            command=self._solve,
            width=180,
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
            text="🎲 Random Data",
            command=self._generate_random,
            width=120,
            height=40,
            fg_color="#9C27B0",
            hover_color="#7B1FA2"
        ).pack(side="left", padx=10, pady=10)
    
    def _create_results_panel(self):
        """Create the results display panel"""
        # Result display
        self.result_display = ResultDisplay(
            self.right_panel,
            title="Assignment Results"
        )
        self.result_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Assignment matrix visualization
        self.allocation_display = AllocationMatrixDisplay(
            self.right_panel,
            title="Optimal Assignment Matrix"
        )
        self.allocation_display.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _load_sample(self):
        """Load sample PP Chemicals worker assignment"""
        # Sample efficiency matrix
        efficiency_matrix = np.array([
            [85, 70, 65, 80, 75, 90, 60, 50, 70, 65],
            [75, 85, 70, 65, 80, 75, 70, 60, 65, 70],
            [80, 75, 90, 70, 65, 80, 75, 55, 80, 60],
            [65, 80, 75, 90, 70, 65, 80, 70, 75, 80],
            [70, 65, 80, 75, 90, 70, 65, 75, 60, 85],
            [90, 75, 70, 65, 80, 85, 70, 80, 65, 70],
            [60, 90, 65, 80, 75, 70, 95, 65, 80, 75],
            [55, 65, 80, 70, 85, 75, 70, 90, 70, 80],
            [75, 70, 85, 75, 70, 80, 75, 70, 95, 65],
            [70, 75, 60, 85, 80, 70, 80, 75, 70, 90]
        ])
        
        self.matrix_input.set_matrix(efficiency_matrix)
        self.matrix_input.set_row_headers([
            "Ali Khan", "Bilal Ahmed", "Chaudhry Imran", "Danish Malik",
            "Ejaz Shah", "Farhan Raza", "Ghulam Abbas", "Hassan Javed",
            "Irfan Siddiqui", "Junaid Tariq"
        ])
        self.matrix_input.set_col_headers([
            "Mixing", "Heating", "Testing", "Packing", "Loading",
            "QC", "Maintenance", "Docs", "Safety", "Dispatch"
        ])
        
        self.objective_var.set("maximize")
    
    def _resize_matrix(self):
        """Resize the matrix"""
        try:
            new_rows = int(self.rows_entry.get())
            new_cols = int(self.cols_entry.get())
            
            if new_rows < 1 or new_cols < 1:
                return
            
            self.matrix_size = max(new_rows, new_cols)
            self.matrix_input.resize(new_rows, new_cols)
            
        except ValueError:
            pass
    
    def _generate_random(self):
        """Generate random matrix data"""
        matrix = np.random.randint(10, 100, (self.matrix_size, self.matrix_size))
        self.matrix_input.set_matrix(matrix)
    
    def _solve(self):
        """Solve the assignment problem"""
        try:
            # Get input data
            cost_matrix = self.matrix_input.get_matrix()
            maximize = self.objective_var.get() == "maximize"
            row_names = self.matrix_input.get_row_headers()
            col_names = self.matrix_input.get_col_headers()
            
            # Create and solve
            solver = AssignmentSolver(
                cost_matrix=cost_matrix,
                maximize=maximize,
                row_names=row_names,
                col_names=col_names
            )
            
            result = solver.solve()
            
            # Display results
            result_dict = {
                'success': result.success,
                'message': result.message,
                'total_cost': result.total_cost,
                'assignments': result.assignments,
                'individual_costs': result.individual_costs,
                'maximize': maximize
            }
            
            self.result_display.display_assignment_result(
                result_dict,
                row_names=row_names,
                col_names=col_names
            )
            
            # Display assignment matrix
            if result.success:
                self.allocation_display.display_matrix(
                    result.assignment_matrix,
                    cost_matrix=cost_matrix,
                    row_names=row_names,
                    col_names=col_names,
                    highlight_nonzero=True
                )
            
        except Exception as e:
            self.result_display.set_status(False, f"Error: {str(e)}")
    
    def _clear(self):
        """Clear all inputs and results"""
        self.matrix_input.clear()
        self.result_display.clear()
        self.allocation_display.clear()
