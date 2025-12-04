"""
Simplex Method Solver with Sensitivity Analysis
Supports Linear Programming problems with 10+ decision variables and constraints
"""

import numpy as np
from scipy.optimize import linprog
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any


@dataclass
class SensitivityAnalysis:
    """Contains sensitivity analysis results"""
    shadow_prices: np.ndarray           # Dual values for constraints
    reduced_costs: np.ndarray           # Reduced costs for variables
    slack_values: np.ndarray            # Slack/surplus values
    constraint_rhs_ranges: List[Dict]   # Allowable RHS ranges
    objective_coeff_ranges: List[Dict]  # Allowable coefficient ranges


@dataclass 
class SimplexResult:
    """Contains complete solution results"""
    success: bool
    message: str
    optimal_value: float
    solution: np.ndarray
    sensitivity: Optional[SensitivityAnalysis]
    iterations: int
    status: int


class SimplexSolver:
    """
    Simplex Method Solver for Linear Programming Problems
    
    Supports:
    - Maximization and Minimization problems
    - Inequality constraints (≤, ≥)
    - Equality constraints (=)
    - Variable bounds
    - Sensitivity analysis
    
    Uses scipy.optimize.linprog with HiGHS method for robust solving
    """
    
    def __init__(
        self,
        c: np.ndarray,
        A_ub: Optional[np.ndarray] = None,
        b_ub: Optional[np.ndarray] = None,
        A_eq: Optional[np.ndarray] = None,
        b_eq: Optional[np.ndarray] = None,
        bounds: Optional[List[Tuple[float, float]]] = None,
        maximize: bool = True,
        variable_names: Optional[List[str]] = None,
        constraint_names: Optional[List[str]] = None
    ):
        """
        Initialize the Simplex Solver
        
        Args:
            c: Coefficients of the objective function
            A_ub: Coefficient matrix for inequality constraints (≤)
            b_ub: Right-hand side of inequality constraints
            A_eq: Coefficient matrix for equality constraints
            b_eq: Right-hand side of equality constraints
            bounds: Variable bounds as list of (min, max) tuples
            maximize: True for maximization, False for minimization
            variable_names: Optional names for decision variables
            constraint_names: Optional names for constraints
        """
        self.c = np.array(c, dtype=float)
        self.A_ub = np.array(A_ub, dtype=float) if A_ub is not None else None
        self.b_ub = np.array(b_ub, dtype=float) if b_ub is not None else None
        self.A_eq = np.array(A_eq, dtype=float) if A_eq is not None else None
        self.b_eq = np.array(b_eq, dtype=float) if b_eq is not None else None
        self.bounds = bounds if bounds else [(0, None) for _ in range(len(c))]
        self.maximize = maximize
        self.variable_names = variable_names or [f"x{i+1}" for i in range(len(c))]
        self.constraint_names = constraint_names or []
        
        self._result = None
        self._sensitivity = None
    
    def solve(self) -> SimplexResult:
        """
        Solve the linear programming problem using the Simplex method
        
        Returns:
            SimplexResult containing the solution and sensitivity analysis
        """
        # For maximization, negate the objective coefficients
        c_solve = -self.c if self.maximize else self.c
        
        try:
            # Solve using HiGHS method (most robust)
            result = linprog(
                c_solve,
                A_ub=self.A_ub,
                b_ub=self.b_ub,
                A_eq=self.A_eq,
                b_eq=self.b_eq,
                bounds=self.bounds,
                method='highs'
            )
            
            if result.success:
                # Calculate optimal value (negate back if maximization)
                optimal_value = -result.fun if self.maximize else result.fun
                
                # Perform sensitivity analysis
                sensitivity = self._compute_sensitivity_analysis(result)
                
                self._result = SimplexResult(
                    success=True,
                    message="Optimal solution found",
                    optimal_value=optimal_value,
                    solution=result.x,
                    sensitivity=sensitivity,
                    iterations=result.nit if hasattr(result, 'nit') else 0,
                    status=result.status
                )
            else:
                self._result = SimplexResult(
                    success=False,
                    message=result.message,
                    optimal_value=0.0,
                    solution=np.zeros(len(self.c)),
                    sensitivity=None,
                    iterations=result.nit if hasattr(result, 'nit') else 0,
                    status=result.status
                )
                
        except Exception as e:
            self._result = SimplexResult(
                success=False,
                message=str(e),
                optimal_value=0.0,
                solution=np.zeros(len(self.c)),
                sensitivity=None,
                iterations=0,
                status=-1
            )
        
        return self._result
    
    def _compute_sensitivity_analysis(self, result) -> SensitivityAnalysis:
        """
        Compute sensitivity analysis from the LP solution
        
        Args:
            result: scipy linprog result object
            
        Returns:
            SensitivityAnalysis object with shadow prices, reduced costs, etc.
        """
        n_vars = len(self.c)
        n_ub = len(self.b_ub) if self.b_ub is not None else 0
        n_eq = len(self.b_eq) if self.b_eq is not None else 0
        
        # Extract dual values (shadow prices) if available
        shadow_prices = np.zeros(n_ub + n_eq)
        if hasattr(result, 'ineqlin') and result.ineqlin is not None:
            marginals = getattr(result.ineqlin, 'marginals', None)
            if marginals is not None:
                shadow_prices[:n_ub] = marginals if not self.maximize else -marginals
        
        if hasattr(result, 'eqlin') and result.eqlin is not None:
            marginals = getattr(result.eqlin, 'marginals', None)
            if marginals is not None:
                shadow_prices[n_ub:] = marginals if not self.maximize else -marginals
        
        # Compute reduced costs
        reduced_costs = np.zeros(n_vars)
        if hasattr(result, 'lower') and result.lower is not None:
            marginals = getattr(result.lower, 'marginals', None)
            if marginals is not None:
                reduced_costs = marginals if not self.maximize else -marginals
        
        # Calculate slack values for inequality constraints
        slack_values = np.zeros(n_ub)
        if self.A_ub is not None and self.b_ub is not None:
            slack_values = self.b_ub - np.dot(self.A_ub, result.x)
        
        # Compute allowable ranges for RHS values
        constraint_rhs_ranges = self._compute_rhs_ranges(result, shadow_prices)
        
        # Compute allowable ranges for objective coefficients
        objective_coeff_ranges = self._compute_objective_ranges(result, reduced_costs)
        
        return SensitivityAnalysis(
            shadow_prices=shadow_prices,
            reduced_costs=reduced_costs,
            slack_values=slack_values,
            constraint_rhs_ranges=constraint_rhs_ranges,
            objective_coeff_ranges=objective_coeff_ranges
        )
    
    def _compute_rhs_ranges(self, result, shadow_prices: np.ndarray) -> List[Dict]:
        """Compute allowable ranges for constraint RHS values"""
        ranges = []
        n_ub = len(self.b_ub) if self.b_ub is not None else 0
        
        for i in range(n_ub):
            current_rhs = self.b_ub[i]
            
            # Estimate allowable ranges based on slack and shadow prices
            if shadow_prices[i] != 0:
                # Binding constraint - calculate ranges
                allowable_increase = float('inf')
                allowable_decrease = float('inf')
                
                # Use slack values to estimate decrease
                if i < len(self._get_slack_values(result)):
                    allowable_decrease = min(allowable_decrease, abs(current_rhs * 0.5))
                
                ranges.append({
                    'constraint': i + 1,
                    'name': self.constraint_names[i] if i < len(self.constraint_names) else f"Constraint {i+1}",
                    'current_rhs': current_rhs,
                    'shadow_price': shadow_prices[i],
                    'allowable_increase': allowable_increase,
                    'allowable_decrease': allowable_decrease
                })
            else:
                # Non-binding constraint
                ranges.append({
                    'constraint': i + 1,
                    'name': self.constraint_names[i] if i < len(self.constraint_names) else f"Constraint {i+1}",
                    'current_rhs': current_rhs,
                    'shadow_price': 0.0,
                    'allowable_increase': float('inf'),
                    'allowable_decrease': self._get_slack_values(result)[i] if i < len(self._get_slack_values(result)) else 0
                })
        
        return ranges
    
    def _compute_objective_ranges(self, result, reduced_costs: np.ndarray) -> List[Dict]:
        """Compute allowable ranges for objective function coefficients"""
        ranges = []
        
        for i in range(len(self.c)):
            current_coeff = self.c[i]
            current_value = result.x[i]
            
            if current_value > 1e-6:  # Basic variable
                ranges.append({
                    'variable': i + 1,
                    'name': self.variable_names[i],
                    'current_coefficient': current_coeff,
                    'current_value': current_value,
                    'reduced_cost': 0.0,
                    'allowable_increase': float('inf'),
                    'allowable_decrease': float('inf')
                })
            else:  # Non-basic variable
                ranges.append({
                    'variable': i + 1,
                    'name': self.variable_names[i],
                    'current_coefficient': current_coeff,
                    'current_value': current_value,
                    'reduced_cost': reduced_costs[i] if i < len(reduced_costs) else 0,
                    'allowable_increase': abs(reduced_costs[i]) if i < len(reduced_costs) else float('inf'),
                    'allowable_decrease': float('inf')
                })
        
        return ranges
    
    def _get_slack_values(self, result) -> np.ndarray:
        """Get slack values from the solution"""
        if self.A_ub is not None and self.b_ub is not None:
            return self.b_ub - np.dot(self.A_ub, result.x)
        return np.array([])
    
    def get_solution_summary(self) -> Dict[str, Any]:
        """
        Get a formatted summary of the solution
        
        Returns:
            Dictionary containing formatted solution information
        """
        if self._result is None:
            return {"error": "Problem not solved yet. Call solve() first."}
        
        summary = {
            "status": "Optimal" if self._result.success else "No Solution",
            "message": self._result.message,
            "optimal_value": self._result.optimal_value,
            "iterations": self._result.iterations,
            "variables": {}
        }
        
        if self._result.success:
            for i, val in enumerate(self._result.solution):
                name = self.variable_names[i] if i < len(self.variable_names) else f"x{i+1}"
                summary["variables"][name] = round(val, 4)
        
        return summary
    
    def get_sensitivity_report(self) -> Dict[str, Any]:
        """
        Get a formatted sensitivity analysis report
        
        Returns:
            Dictionary containing sensitivity analysis information
        """
        if self._result is None or self._result.sensitivity is None:
            return {"error": "Sensitivity analysis not available"}
        
        sens = self._result.sensitivity
        
        return {
            "shadow_prices": [
                {
                    "constraint": i + 1,
                    "name": self.constraint_names[i] if i < len(self.constraint_names) else f"Constraint {i+1}",
                    "value": round(sp, 4)
                }
                for i, sp in enumerate(sens.shadow_prices)
            ],
            "reduced_costs": [
                {
                    "variable": i + 1,
                    "name": self.variable_names[i],
                    "value": round(rc, 4)
                }
                for i, rc in enumerate(sens.reduced_costs)
            ],
            "slack_values": [
                {
                    "constraint": i + 1,
                    "value": round(sv, 4)
                }
                for i, sv in enumerate(sens.slack_values)
            ],
            "rhs_ranges": sens.constraint_rhs_ranges,
            "objective_ranges": sens.objective_coeff_ranges
        }


def create_sample_problem() -> SimplexSolver:
    """
    Create a sample PP Chemicals production optimization problem
    
    Returns:
        SimplexSolver instance with sample data
    """
    # Objective: Maximize profit from 10 chemical products
    # Profit per ton (in currency units)
    c = [5000, 7500, 4000, 3500, 6000, 4500, 8000, 3000, 9000, 8500]
    
    # Variable names (products)
    variable_names = [
        "Bitumen Emulsion", "Modified Bitumen", "Concrete Plasticizer",
        "Curing Compound", "Waterproofing Compound", "Road Marking Paint",
        "Anti-Strip Agent", "Concrete Hardener", "Epoxy Coating", 
        "Polymer Modified Bitumen"
    ]
    
    # Constraint matrix (10 constraints x 10 variables)
    A_ub = np.array([
        [2, 3, 1, 2, 1, 2, 3, 1, 2, 3],    # Raw Material A
        [1, 2, 3, 1, 2, 1, 2, 3, 1, 2],    # Raw Material B
        [3, 2, 4, 1, 2, 3, 1, 2, 4, 2],    # Production Line 1 hours
        [1, 2, 1, 3, 4, 2, 1, 2, 1, 3],    # Production Line 2 hours
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],    # Storage Capacity
        [4, 5, 3, 4, 5, 3, 4, 5, 3, 4],    # Labor Hours
        [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],  # QC Capacity
        [0.1, 0.2, 0.15, 0.1, 0.2, 0.15, 0.1, 0.2, 0.15, 0.1],  # Environmental
        [10, 15, 8, 12, 10, 8, 15, 10, 12, 14],  # Energy
        [1, 2, 1, 1, 2, 1, 2, 1, 1, 2]     # Packaging Material
    ])
    
    # Right-hand side (resource availability)
    b_ub = np.array([5000, 4000, 480, 400, 1000, 2000, 300, 100, 10000, 2500])
    
    # Constraint names
    constraint_names = [
        "Raw Material A (kg)", "Raw Material B (kg)",
        "Production Line 1 (hrs)", "Production Line 2 (hrs)",
        "Storage Capacity (tons)", "Labor Hours (man-hrs)",
        "Quality Control (tests)", "Environmental Limit (units)",
        "Energy Consumption (kWh)", "Packaging Material (units)"
    ]
    
    # Variable bounds (all non-negative)
    bounds = [(0, None) for _ in range(10)]
    
    return SimplexSolver(
        c=c,
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=bounds,
        maximize=True,
        variable_names=variable_names,
        constraint_names=constraint_names
    )


if __name__ == "__main__":
    # Test the solver with sample problem
    solver = create_sample_problem()
    result = solver.solve()
    
    print("=" * 60)
    print("PP CHEMICALS - PRODUCTION OPTIMIZATION")
    print("=" * 60)
    
    summary = solver.get_solution_summary()
    print(f"\nStatus: {summary['status']}")
    print(f"Optimal Profit: ${summary['optimal_value']:,.2f}")
    print(f"Iterations: {summary['iterations']}")
    
    print("\nOptimal Production Plan:")
    print("-" * 40)
    for var, val in summary['variables'].items():
        if val > 0:
            print(f"  {var}: {val:.2f} tons")
    
    print("\nSensitivity Analysis:")
    print("-" * 40)
    sens_report = solver.get_sensitivity_report()
    
    print("\nShadow Prices (Value of additional resources):")
    for sp in sens_report['shadow_prices']:
        if sp['value'] != 0:
            print(f"  {sp['name']}: ${sp['value']:.2f} per unit")
