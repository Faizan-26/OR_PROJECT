"""
Transportation Problem View
UI for inputting and solving transportation problems using VAM and MODI
"""

import customtkinter as ctk
import numpy as np
from typing import Optional, List

from ui.components.matrix_input import MatrixInput, VectorInput
from ui.components.result_display import ResultDisplay, AllocationMatrixDisplay
from algorithms.transportation import TransportationSolver, InitialMethod
from config.settings import PLANTS, DESTINATIONS, DEFAULT_MATRIX_SIZE


class TransportationView(ctk.CTkFrame):
    """
    View for Transportation Problems
    
    Features:
    - Supply/demand input
    - Cost matrix input
    - Multiple solution methods (NW Corner, Least Cost, VAM)
    - MODI optimization
    - Visual allocation display
    - Load sample problem
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.num_sources = DEFAULT_MATRIX_SIZE
        self.num_destinations = DEFAULT_MATRIX_SIZE
        
        self._create_layout()
        self._create_widgets()
    
    def _create_layout(self):
        """Create the main layout structure"""
        # Left panel (inputs)
        self.left_panel = ctk.CTkScrollableFrame(self, width=700)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Right panel (results)
        self.right_panel = ctk.CTkFrame(self, width=500)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
    
    def _create_widgets(self):
        """Create all UI widgets"""
        self._create_header()
        self._create_settings()
        self._create_supply_input()
        self._create_cost_matrix_input()
        self._create_demand_input()
        self._create_action_buttons()
        self._create_results_panel()
    
    def _create_header(self):
        """Create the header section"""
        header_frame = ctk.CTkFrame(self.left_panel)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="Transportation Problem (VAM + MODI)",
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
        
        ctk.CTkLabel(size_frame, text="Sources:").pack(side="left", padx=5)
        self.sources_entry = ctk.CTkEntry(size_frame, width=60, justify="center")
        self.sources_entry.insert(0, str(self.num_sources))
        self.sources_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(size_frame, text="Destinations:").pack(side="left", padx=15)
        self.dest_entry = ctk.CTkEntry(size_frame, width=60, justify="center")
        self.dest_entry.insert(0, str(self.num_destinations))
        self.dest_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            size_frame,
            text="Resize",
            command=self._resize,
            width=80
        ).pack(side="left", padx=15)
        
        # Method selection
        method_frame = ctk.CTkFrame(settings_frame)
        method_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(method_frame, text="Initial Solution Method:").pack(side="left", padx=5)
        
        self.method_var = ctk.StringVar(value="vam")
        
        ctk.CTkRadioButton(
            method_frame,
            text="VAM (Best)",
            variable=self.method_var,
            value="vam"
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            method_frame,
            text="Least Cost",
            variable=self.method_var,
            value="least_cost"
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            method_frame,
            text="NW Corner",
            variable=self.method_var,
            value="north_west"
        ).pack(side="left", padx=10)
        
        # Optimize toggle
        optimize_frame = ctk.CTkFrame(settings_frame)
        optimize_frame.pack(fill="x", padx=10, pady=5)
        
        self.optimize_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            optimize_frame,
            text="Apply MODI Optimization",
            variable=self.optimize_var
        ).pack(side="left", padx=10)
        
        # Balance info
        self.balance_label = ctk.CTkLabel(
            optimize_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.balance_label.pack(side="right", padx=10)
    
    def _create_supply_input(self):
        """Create supply input section"""
        supply_frame = ctk.CTkFrame(self.left_panel)
        supply_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            supply_frame,
            text="Supply at Sources (Plants)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        self.supply_input = VectorInput(
            supply_frame,
            size=self.num_sources,
            labels=PLANTS[:self.num_sources],
            orientation="horizontal",
            default_value="0",
            cell_width=80
        )
        self.supply_input.pack(fill="x", padx=10, pady=5)
    
    def _create_cost_matrix_input(self):
        """Create cost matrix input section"""
        matrix_frame = ctk.CTkFrame(self.left_panel)
        matrix_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            matrix_frame,
            text="Transportation Costs (Rs. per unit)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        self.cost_matrix = MatrixInput(
            matrix_frame,
            rows=self.num_sources,
            cols=self.num_destinations,
            row_headers=PLANTS[:self.num_sources],
            col_headers=[d[:10] for d in DESTINATIONS[:self.num_destinations]],
            default_value="0",
            cell_width=70
        )
        self.cost_matrix.pack(fill="both", expand=True, padx=10, pady=5)
    
    def _create_demand_input(self):
        """Create demand input section"""
        demand_frame = ctk.CTkFrame(self.left_panel)
        demand_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            demand_frame,
            text="Demand at Destinations (Construction Sites)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        self.demand_input = VectorInput(
            demand_frame,
            size=self.num_destinations,
            labels=[d[:12] for d in DESTINATIONS[:self.num_destinations]],
            orientation="horizontal",
            default_value="0",
            cell_width=80
        )
        self.demand_input.pack(fill="x", padx=10, pady=5)
    
    def _create_action_buttons(self):
        """Create action buttons"""
        btn_frame = ctk.CTkFrame(self.left_panel)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="🔍 Find Optimal Shipment",
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
            text="⚖️ Check Balance",
            command=self._check_balance,
            width=120,
            height=40,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).pack(side="left", padx=10, pady=10)
    
    def _create_results_panel(self):
        """Create the results display panel"""
        # Result display
        self.result_display = ResultDisplay(
            self.right_panel,
            title="Transportation Results"
        )
        self.result_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Allocation matrix visualization
        self.allocation_display = AllocationMatrixDisplay(
            self.right_panel,
            title="Optimal Shipping Plan"
        )
        self.allocation_display.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _load_sample(self):
        """Load sample PP Chemicals transportation problem"""
        # Supply from 10 plants
        supply = np.array([500, 400, 350, 450, 380, 420, 300, 360, 410, 330])
        self.supply_input.set_values(supply)
        
        # Demand at 10 construction sites
        demand = np.array([200, 180, 300, 250, 350, 280, 320, 400, 290, 330])
        self.demand_input.set_values(demand)
        
        # Transportation cost matrix
        cost_matrix = np.array([
            [45, 72, 35, 58, 62, 48, 55, 80, 42, 65],
            [38, 65, 42, 52, 58, 45, 50, 75, 38, 60],
            [55, 48, 58, 42, 45, 52, 48, 62, 55, 45],
            [62, 55, 48, 38, 42, 55, 52, 58, 48, 42],
            [70, 58, 52, 45, 38, 48, 45, 52, 55, 48],
            [58, 52, 55, 48, 45, 35, 42, 48, 52, 55],
            [85, 78, 72, 65, 58, 52, 45, 38, 65, 58],
            [78, 72, 65, 58, 52, 48, 42, 45, 58, 55],
            [72, 68, 62, 55, 48, 52, 48, 42, 52, 48],
            [95, 88, 82, 75, 68, 62, 55, 48, 72, 65]
        ])
        self.cost_matrix.set_matrix(cost_matrix)
        
        self._check_balance()
    
    def _resize(self):
        """Resize the problem dimensions"""
        try:
            new_sources = int(self.sources_entry.get())
            new_dests = int(self.dest_entry.get())
            
            if new_sources < 1 or new_dests < 1:
                return
            
            self.num_sources = new_sources
            self.num_destinations = new_dests
            
            # Resize widgets
            self.supply_input.destroy()
            self.cost_matrix.destroy()
            self.demand_input.destroy()
            
            # Recreate supply input
            supply_parent = self.left_panel.winfo_children()[2]
            self.supply_input = VectorInput(
                supply_parent,
                size=new_sources,
                labels=[PLANTS[i] if i < len(PLANTS) else f"S{i+1}" for i in range(new_sources)],
                orientation="horizontal",
                default_value="0",
                cell_width=80
            )
            self.supply_input.pack(fill="x", padx=10, pady=5)
            
            # Recreate cost matrix
            matrix_parent = self.left_panel.winfo_children()[3]
            self.cost_matrix = MatrixInput(
                matrix_parent,
                rows=new_sources,
                cols=new_dests,
                row_headers=[PLANTS[i] if i < len(PLANTS) else f"S{i+1}" for i in range(new_sources)],
                col_headers=[DESTINATIONS[j][:10] if j < len(DESTINATIONS) else f"D{j+1}" for j in range(new_dests)],
                default_value="0",
                cell_width=70
            )
            self.cost_matrix.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Recreate demand input
            demand_parent = self.left_panel.winfo_children()[4]
            self.demand_input = VectorInput(
                demand_parent,
                size=new_dests,
                labels=[DESTINATIONS[j][:12] if j < len(DESTINATIONS) else f"D{j+1}" for j in range(new_dests)],
                orientation="horizontal",
                default_value="0",
                cell_width=80
            )
            self.demand_input.pack(fill="x", padx=10, pady=5)
            
        except ValueError:
            pass
    
    def _check_balance(self):
        """Check if supply equals demand"""
        supply = self.supply_input.get_values()
        demand = self.demand_input.get_values()
        
        total_supply = np.sum(supply)
        total_demand = np.sum(demand)
        
        if abs(total_supply - total_demand) < 1e-6:
            self.balance_label.configure(
                text=f"✓ Balanced (Supply = Demand = {total_supply:,.0f})",
                text_color="#4CAF50"
            )
        elif total_supply > total_demand:
            diff = total_supply - total_demand
            self.balance_label.configure(
                text=f"⚠ Unbalanced: Excess supply of {diff:,.0f}",
                text_color="#FF9800"
            )
        else:
            diff = total_demand - total_supply
            self.balance_label.configure(
                text=f"⚠ Unbalanced: Excess demand of {diff:,.0f}",
                text_color="#FF9800"
            )
    
    def _solve(self):
        """Solve the transportation problem"""
        try:
            # Get input data
            supply = self.supply_input.get_values()
            demand = self.demand_input.get_values()
            costs = self.cost_matrix.get_matrix()
            
            # Get method
            method_map = {
                'vam': InitialMethod.VOGEL,
                'least_cost': InitialMethod.LEAST_COST,
                'north_west': InitialMethod.NORTH_WEST_CORNER
            }
            method = method_map.get(self.method_var.get(), InitialMethod.VOGEL)
            optimize = self.optimize_var.get()
            
            # Get names
            source_names = [PLANTS[i] if i < len(PLANTS) else f"Source {i+1}" 
                           for i in range(self.num_sources)]
            dest_names = [DESTINATIONS[j] if j < len(DESTINATIONS) else f"Dest {j+1}"
                         for j in range(self.num_destinations)]
            
            # Create and solve
            solver = TransportationSolver(
                supply=supply,
                demand=demand,
                cost_matrix=costs,
                source_names=source_names,
                dest_names=dest_names
            )
            
            result = solver.solve(method=method, optimize=optimize)
            
            # Display results
            result_dict = {
                'success': result.success,
                'message': result.message,
                'total_cost': result.total_cost,
                'routes': result.route_details,
                'is_optimal': result.is_optimal,
                'iterations': result.iterations,
                'initial_method': result.initial_method
            }
            
            self.result_display.display_transportation_result(
                result_dict,
                source_names=source_names,
                dest_names=dest_names
            )
            
            # Display allocation matrix
            if result.success:
                self.allocation_display.display_matrix(
                    result.allocation_matrix,
                    cost_matrix=costs,
                    row_names=source_names,
                    col_names=dest_names,
                    highlight_nonzero=True
                )
            
            # Update balance info
            self._check_balance()
            
        except Exception as e:
            self.result_display.set_status(False, f"Error: {str(e)}")
    
    def _clear(self):
        """Clear all inputs and results"""
        self.supply_input.clear()
        self.demand_input.clear()
        self.cost_matrix.clear()
        self.result_display.clear()
        self.allocation_display.clear()
        self.balance_label.configure(text="", text_color="gray")
