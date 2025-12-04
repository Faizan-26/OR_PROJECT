"""
Data Model for Linear Programming Problems
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np


@dataclass
class LPModel:
    """
    Data model for Linear Programming problems
    
    Represents the standard form:
    Maximize/Minimize: c^T * x
    Subject to: A_ub * x <= b_ub
                A_eq * x = b_eq
                bounds[i][0] <= x[i] <= bounds[i][1]
    """
    # Objective function coefficients
    objective_coefficients: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Constraint matrices
    constraint_matrix: np.ndarray = field(default_factory=lambda: np.array([[]]))
    constraint_rhs: np.ndarray = field(default_factory=lambda: np.array([]))
    constraint_types: List[str] = field(default_factory=list)  # '<=', '>=', '='
    
    # Equality constraints (optional)
    equality_matrix: Optional[np.ndarray] = None
    equality_rhs: Optional[np.ndarray] = None
    
    # Variable bounds
    bounds: List[Tuple[float, Optional[float]]] = field(default_factory=list)
    
    # Problem type
    maximize: bool = True
    
    # Names for display
    variable_names: List[str] = field(default_factory=list)
    constraint_names: List[str] = field(default_factory=list)
    
    # Problem metadata
    problem_name: str = "Untitled LP Problem"
    description: str = ""
    
    def __post_init__(self):
        """Initialize default names if not provided"""
        if len(self.objective_coefficients) > 0:
            n_vars = len(self.objective_coefficients)
            if not self.variable_names:
                self.variable_names = [f"x{i+1}" for i in range(n_vars)]
            if not self.bounds:
                self.bounds = [(0, None) for _ in range(n_vars)]
        
        if len(self.constraint_rhs) > 0:
            n_constraints = len(self.constraint_rhs)
            if not self.constraint_names:
                self.constraint_names = [f"Constraint {i+1}" for i in range(n_constraints)]
            if not self.constraint_types:
                self.constraint_types = ['<='] * n_constraints
    
    @property
    def num_variables(self) -> int:
        """Number of decision variables"""
        return len(self.objective_coefficients)
    
    @property
    def num_constraints(self) -> int:
        """Number of constraints"""
        return len(self.constraint_rhs)
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate the LP model
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(self.objective_coefficients) == 0:
            return False, "Objective function coefficients are empty"
        
        if self.constraint_matrix.size > 0:
            if self.constraint_matrix.shape[1] != len(self.objective_coefficients):
                return False, "Constraint matrix columns must match number of variables"
            
            if self.constraint_matrix.shape[0] != len(self.constraint_rhs):
                return False, "Constraint matrix rows must match RHS values"
        
        if len(self.bounds) != len(self.objective_coefficients):
            return False, "Number of bounds must match number of variables"
        
        return True, "Valid"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary for serialization"""
        return {
            'problem_name': self.problem_name,
            'description': self.description,
            'maximize': self.maximize,
            'objective_coefficients': self.objective_coefficients.tolist(),
            'constraint_matrix': self.constraint_matrix.tolist(),
            'constraint_rhs': self.constraint_rhs.tolist(),
            'constraint_types': self.constraint_types,
            'bounds': self.bounds,
            'variable_names': self.variable_names,
            'constraint_names': self.constraint_names
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LPModel':
        """Create model from dictionary"""
        return cls(
            problem_name=data.get('problem_name', 'Untitled'),
            description=data.get('description', ''),
            maximize=data.get('maximize', True),
            objective_coefficients=np.array(data.get('objective_coefficients', [])),
            constraint_matrix=np.array(data.get('constraint_matrix', [[]])),
            constraint_rhs=np.array(data.get('constraint_rhs', [])),
            constraint_types=data.get('constraint_types', []),
            bounds=data.get('bounds', []),
            variable_names=data.get('variable_names', []),
            constraint_names=data.get('constraint_names', [])
        )


@dataclass
class LPResult:
    """Result of solving an LP problem"""
    success: bool = False
    message: str = ""
    optimal_value: float = 0.0
    solution: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Sensitivity analysis
    shadow_prices: np.ndarray = field(default_factory=lambda: np.array([]))
    reduced_costs: np.ndarray = field(default_factory=lambda: np.array([]))
    slack_values: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Ranges
    rhs_ranges: List[dict] = field(default_factory=list)
    objective_ranges: List[dict] = field(default_factory=list)
    
    # Solver info
    iterations: int = 0
    
    def to_dict(self) -> dict:
        """Convert result to dictionary"""
        return {
            'success': self.success,
            'message': self.message,
            'optimal_value': self.optimal_value,
            'solution': self.solution.tolist() if isinstance(self.solution, np.ndarray) else self.solution,
            'shadow_prices': self.shadow_prices.tolist() if isinstance(self.shadow_prices, np.ndarray) else self.shadow_prices,
            'reduced_costs': self.reduced_costs.tolist() if isinstance(self.reduced_costs, np.ndarray) else self.reduced_costs,
            'slack_values': self.slack_values.tolist() if isinstance(self.slack_values, np.ndarray) else self.slack_values,
            'rhs_ranges': self.rhs_ranges,
            'objective_ranges': self.objective_ranges,
            'iterations': self.iterations
        }


def create_sample_lp_model() -> LPModel:
    """
    Create a sample PP Chemicals production optimization model
    
    Returns:
        LPModel instance with sample data
    """
    # 10 decision variables (chemical products)
    objective = np.array([5000, 7500, 4000, 3500, 6000, 4500, 8000, 3000, 9000, 8500])
    
    variable_names = [
        "Bitumen Emulsion", "Modified Bitumen", "Concrete Plasticizer",
        "Curing Compound", "Waterproofing", "Road Paint",
        "Anti-Strip Agent", "Concrete Hardener", "Epoxy Coating", "PMB"
    ]
    
    # 10 constraints
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
    
    rhs = np.array([5000, 4000, 480, 400, 1000, 2000, 300, 100, 10000, 2500])
    
    constraint_names = [
        "Raw Material A (kg)", "Raw Material B (kg)",
        "Production Line 1 (hrs)", "Production Line 2 (hrs)",
        "Storage (tons)", "Labor (man-hrs)",
        "Quality Control (tests)", "Environmental (units)",
        "Energy (kWh)", "Packaging (units)"
    ]
    
    return LPModel(
        problem_name="PP Chemicals Production Optimization",
        description="Maximize profit from chemical production subject to resource constraints",
        maximize=True,
        objective_coefficients=objective,
        constraint_matrix=constraints,
        constraint_rhs=rhs,
        constraint_types=['<='] * 10,
        bounds=[(0, None)] * 10,
        variable_names=variable_names,
        constraint_names=constraint_names
    )
