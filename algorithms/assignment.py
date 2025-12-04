"""
Assignment Problem Solver using Hungarian Algorithm
Supports 10x10 or larger cost/efficiency matrices
"""

import numpy as np
from scipy.optimize import linear_sum_assignment
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any


@dataclass
class AssignmentResult:
    """Contains assignment problem solution results"""
    success: bool
    message: str
    total_cost: float
    assignments: List[Tuple[int, int]]  # List of (row, col) assignments
    assignment_matrix: np.ndarray        # Binary assignment matrix
    individual_costs: List[float]        # Cost of each assignment


class AssignmentSolver:
    """
    Assignment Problem Solver using the Hungarian Algorithm
    
    Solves the problem of assigning n workers to n tasks (or m workers to n tasks)
    to minimize total cost or maximize total efficiency/profit.
    
    Uses scipy.optimize.linear_sum_assignment which implements the Hungarian Algorithm
    with O(n³) complexity.
    """
    
    def __init__(
        self,
        cost_matrix: np.ndarray,
        maximize: bool = False,
        row_names: Optional[List[str]] = None,
        col_names: Optional[List[str]] = None
    ):
        """
        Initialize the Assignment Solver
        
        Args:
            cost_matrix: 2D numpy array of costs/efficiencies (n x m)
            maximize: True for maximization (efficiency), False for minimization (cost)
            row_names: Optional names for rows (workers)
            col_names: Optional names for columns (tasks)
        """
        self.cost_matrix = np.array(cost_matrix, dtype=float)
        self.maximize = maximize
        self.n_rows, self.n_cols = self.cost_matrix.shape
        self.row_names = row_names or [f"Worker {i+1}" for i in range(self.n_rows)]
        self.col_names = col_names or [f"Task {i+1}" for i in range(self.n_cols)]
        
        self._result = None
        self._row_ind = None
        self._col_ind = None
    
    def solve(self) -> AssignmentResult:
        """
        Solve the assignment problem using the Hungarian Algorithm
        
        Returns:
            AssignmentResult containing the optimal assignment
        """
        try:
            # For maximization, negate the cost matrix
            if self.maximize:
                solve_matrix = -self.cost_matrix
            else:
                solve_matrix = self.cost_matrix
            
            # Handle non-square matrices by making them square
            if self.n_rows != self.n_cols:
                # Pad with zeros (or high costs for minimization) to make square
                max_dim = max(self.n_rows, self.n_cols)
                padded_matrix = np.zeros((max_dim, max_dim))
                
                if not self.maximize:
                    # For minimization, pad with high value to avoid dummy assignments
                    padded_matrix.fill(np.max(solve_matrix) * 1000)
                
                padded_matrix[:self.n_rows, :self.n_cols] = solve_matrix
                solve_matrix = padded_matrix
            
            # Solve using Hungarian algorithm
            self._row_ind, self._col_ind = linear_sum_assignment(solve_matrix)
            
            # Filter out dummy assignments
            valid_assignments = [
                (r, c) for r, c in zip(self._row_ind, self._col_ind)
                if r < self.n_rows and c < self.n_cols
            ]
            
            # Calculate total cost/profit
            individual_costs = [
                self.cost_matrix[r, c] for r, c in valid_assignments
            ]
            total_cost = sum(individual_costs)
            
            # Create binary assignment matrix
            assignment_matrix = np.zeros_like(self.cost_matrix, dtype=int)
            for r, c in valid_assignments:
                assignment_matrix[r, c] = 1
            
            self._result = AssignmentResult(
                success=True,
                message="Optimal assignment found",
                total_cost=total_cost,
                assignments=valid_assignments,
                assignment_matrix=assignment_matrix,
                individual_costs=individual_costs
            )
            
        except Exception as e:
            self._result = AssignmentResult(
                success=False,
                message=str(e),
                total_cost=0.0,
                assignments=[],
                assignment_matrix=np.zeros_like(self.cost_matrix, dtype=int),
                individual_costs=[]
            )
        
        return self._result
    
    def get_solution_summary(self) -> Dict[str, Any]:
        """
        Get a formatted summary of the assignment solution
        
        Returns:
            Dictionary containing formatted solution information
        """
        if self._result is None:
            return {"error": "Problem not solved yet. Call solve() first."}
        
        if not self._result.success:
            return {"error": self._result.message}
        
        objective_type = "Efficiency" if self.maximize else "Cost"
        
        summary = {
            "status": "Optimal",
            "objective_type": objective_type,
            f"total_{objective_type.lower()}": self._result.total_cost,
            "assignments": []
        }
        
        for i, (r, c) in enumerate(self._result.assignments):
            row_name = self.row_names[r] if r < len(self.row_names) else f"Worker {r+1}"
            col_name = self.col_names[c] if c < len(self.col_names) else f"Task {c+1}"
            
            summary["assignments"].append({
                "worker": row_name,
                "task": col_name,
                objective_type.lower(): self._result.individual_costs[i]
            })
        
        return summary
    
    def get_formatted_matrix(self) -> str:
        """
        Get a formatted string representation of the assignment matrix
        
        Returns:
            String representation of the solution matrix
        """
        if self._result is None or not self._result.success:
            return "No solution available"
        
        # Create header
        header = "         | " + " | ".join(f"{name[:8]:^8}" for name in self.col_names)
        separator = "-" * len(header)
        
        lines = [header, separator]
        
        for i, row_name in enumerate(self.row_names):
            row_values = []
            for j in range(self.n_cols):
                if self._result.assignment_matrix[i, j] == 1:
                    row_values.append(f"[{self.cost_matrix[i,j]:>6.0f}]")
                else:
                    row_values.append(f" {self.cost_matrix[i,j]:>6.0f} ")
            lines.append(f"{row_name[:8]:<8} | " + " | ".join(row_values))
        
        return "\n".join(lines)
    
    def get_unassigned(self) -> Dict[str, List[str]]:
        """
        Get lists of unassigned workers and tasks (for non-square matrices)
        
        Returns:
            Dictionary with 'workers' and 'tasks' lists
        """
        if self._result is None or not self._result.success:
            return {"workers": [], "tasks": []}
        
        assigned_rows = set(r for r, c in self._result.assignments)
        assigned_cols = set(c for r, c in self._result.assignments)
        
        unassigned_workers = [
            self.row_names[i] for i in range(self.n_rows) 
            if i not in assigned_rows
        ]
        unassigned_tasks = [
            self.col_names[j] for j in range(self.n_cols)
            if j not in assigned_cols
        ]
        
        return {
            "workers": unassigned_workers,
            "tasks": unassigned_tasks
        }


def create_sample_problem() -> AssignmentSolver:
    """
    Create a sample PP Chemicals worker-task assignment problem
    
    Returns:
        AssignmentSolver instance with sample data
    """
    # Efficiency matrix: Workers (rows) x Tasks (columns)
    # Higher values = better efficiency for maximization
    efficiency_matrix = np.array([
        [85, 70, 65, 80, 75, 90, 60, 50, 70, 65],   # Ali Khan
        [75, 85, 70, 65, 80, 75, 70, 60, 65, 70],   # Bilal Ahmed
        [80, 75, 90, 70, 65, 80, 75, 55, 80, 60],   # Chaudhry Imran
        [65, 80, 75, 90, 70, 65, 80, 70, 75, 80],   # Danish Malik
        [70, 65, 80, 75, 90, 70, 65, 75, 60, 85],   # Ejaz Shah
        [90, 75, 70, 65, 80, 85, 70, 80, 65, 70],   # Farhan Raza
        [60, 90, 65, 80, 75, 70, 95, 65, 80, 75],   # Ghulam Abbas
        [55, 65, 80, 70, 85, 75, 70, 90, 70, 80],   # Hassan Javed
        [75, 70, 85, 75, 70, 80, 75, 70, 95, 65],   # Irfan Siddiqui
        [70, 75, 60, 85, 80, 70, 80, 75, 70, 90]    # Junaid Tariq
    ])
    
    worker_names = [
        "Ali Khan", "Bilal Ahmed", "Chaudhry Imran", "Danish Malik",
        "Ejaz Shah", "Farhan Raza", "Ghulam Abbas", "Hassan Javed",
        "Irfan Siddiqui", "Junaid Tariq"
    ]
    
    task_names = [
        "Mixing", "Heating", "Testing", "Packing", "Loading",
        "Quality Control", "Maintenance", "Documentation", 
        "Safety Check", "Dispatch"
    ]
    
    return AssignmentSolver(
        cost_matrix=efficiency_matrix,
        maximize=True,  # Maximize efficiency
        row_names=worker_names,
        col_names=task_names
    )


def create_cost_minimization_problem() -> AssignmentSolver:
    """
    Create a sample cost minimization assignment problem
    
    Returns:
        AssignmentSolver instance with cost data
    """
    # Cost matrix: Workers x Tasks (lower = better for minimization)
    cost_matrix = np.array([
        [15, 30, 35, 20, 25, 10, 40, 50, 30, 35],
        [25, 15, 30, 35, 20, 25, 30, 40, 35, 30],
        [20, 25, 10, 30, 35, 20, 25, 45, 20, 40],
        [35, 20, 25, 10, 30, 35, 20, 30, 25, 20],
        [30, 35, 20, 25, 10, 30, 35, 25, 40, 15],
        [10, 25, 30, 35, 20, 15, 30, 20, 35, 30],
        [40, 10, 35, 20, 25, 30, 5, 35, 20, 25],
        [45, 35, 20, 30, 15, 25, 30, 10, 30, 20],
        [25, 30, 15, 25, 30, 20, 25, 30, 5, 35],
        [30, 25, 40, 15, 20, 30, 20, 25, 30, 10]
    ])
    
    worker_names = [
        "Ahmed Khan", "Bilal Hussain", "Chaudhry Tariq", "Danish Ali",
        "Ejaz Ahmed", "Farhan Malik", "Ghulam Abbas", "Hassan Raza",
        "Imran Shah", "Junaid Iqbal"
    ]
    
    task_names = [
        "Mixing", "Heating", "Testing", "Packing", "Loading",
        "Quality Control", "Maintenance", "Documentation", 
        "Safety Check", "Dispatch"
    ]
    
    return AssignmentSolver(
        cost_matrix=cost_matrix,
        maximize=False,  # Minimize cost
        row_names=worker_names,
        col_names=task_names
    )


if __name__ == "__main__":
    # Test with efficiency maximization problem
    print("=" * 70)
    print("PP CHEMICALS - WORKER-TASK ASSIGNMENT (Efficiency Maximization)")
    print("=" * 70)
    
    solver = create_sample_problem()
    result = solver.solve()
    
    summary = solver.get_solution_summary()
    print(f"\nStatus: {summary['status']}")
    print(f"Total Efficiency Score: {summary['total_efficiency']:.0f}")
    
    print("\nOptimal Assignments:")
    print("-" * 50)
    for assignment in summary['assignments']:
        print(f"  {assignment['worker']} → {assignment['task']} (Efficiency: {assignment['efficiency']:.0f})")
    
    print("\nAssignment Matrix:")
    print("-" * 50)
    print(solver.get_formatted_matrix())
    
    # Test with cost minimization problem
    print("\n" + "=" * 70)
    print("PP CHEMICALS - WORKER-TASK ASSIGNMENT (Cost Minimization)")
    print("=" * 70)
    
    cost_solver = create_cost_minimization_problem()
    result = cost_solver.solve()
    
    summary = cost_solver.get_solution_summary()
    print(f"\nStatus: {summary['status']}")
    print(f"Total Cost: ${summary['total_cost']:.0f}")
    
    print("\nOptimal Assignments:")
    print("-" * 50)
    for assignment in summary['assignments']:
        print(f"  {assignment['worker']} → {assignment['task']} (Cost: ${assignment['cost']:.0f})")
