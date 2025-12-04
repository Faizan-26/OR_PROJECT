"""
Data Model for Assignment Problems
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np


@dataclass
class AssignmentModel:
    """
    Data model for Assignment Problems
    
    Represents the problem of assigning n workers to n tasks
    to minimize cost or maximize efficiency
    """
    # Cost/efficiency matrix
    cost_matrix: np.ndarray = field(default_factory=lambda: np.array([[]]))
    
    # Problem type
    maximize: bool = False  # False = minimize cost, True = maximize efficiency
    
    # Names for display
    row_names: List[str] = field(default_factory=list)  # Workers
    col_names: List[str] = field(default_factory=list)  # Tasks
    
    # Problem metadata
    problem_name: str = "Untitled Assignment Problem"
    description: str = ""
    
    def __post_init__(self):
        """Initialize default names if not provided"""
        if self.cost_matrix.size > 0:
            n_rows, n_cols = self.cost_matrix.shape
            if not self.row_names:
                self.row_names = [f"Worker {i+1}" for i in range(n_rows)]
            if not self.col_names:
                self.col_names = [f"Task {j+1}" for j in range(n_cols)]
    
    @property
    def num_rows(self) -> int:
        """Number of workers/rows"""
        return self.cost_matrix.shape[0] if self.cost_matrix.size > 0 else 0
    
    @property
    def num_cols(self) -> int:
        """Number of tasks/columns"""
        return self.cost_matrix.shape[1] if self.cost_matrix.size > 0 else 0
    
    @property
    def is_square(self) -> bool:
        """Check if matrix is square"""
        return self.num_rows == self.num_cols
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate the assignment model
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.cost_matrix.size == 0:
            return False, "Cost matrix is empty"
        
        if len(self.row_names) != self.num_rows:
            return False, "Number of row names must match matrix rows"
        
        if len(self.col_names) != self.num_cols:
            return False, "Number of column names must match matrix columns"
        
        return True, "Valid"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary for serialization"""
        return {
            'problem_name': self.problem_name,
            'description': self.description,
            'maximize': self.maximize,
            'cost_matrix': self.cost_matrix.tolist(),
            'row_names': self.row_names,
            'col_names': self.col_names
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AssignmentModel':
        """Create model from dictionary"""
        return cls(
            problem_name=data.get('problem_name', 'Untitled'),
            description=data.get('description', ''),
            maximize=data.get('maximize', False),
            cost_matrix=np.array(data.get('cost_matrix', [[]])),
            row_names=data.get('row_names', []),
            col_names=data.get('col_names', [])
        )


@dataclass
class AssignmentResult:
    """Result of solving an assignment problem"""
    success: bool = False
    message: str = ""
    total_cost: float = 0.0
    
    # Assignments as list of (row_index, col_index) tuples
    assignments: List[Tuple[int, int]] = field(default_factory=list)
    
    # Binary assignment matrix
    assignment_matrix: np.ndarray = field(default_factory=lambda: np.array([[]]))
    
    # Individual costs for each assignment
    individual_costs: List[float] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert result to dictionary"""
        return {
            'success': self.success,
            'message': self.message,
            'total_cost': self.total_cost,
            'assignments': self.assignments,
            'assignment_matrix': self.assignment_matrix.tolist() if isinstance(self.assignment_matrix, np.ndarray) else self.assignment_matrix,
            'individual_costs': self.individual_costs
        }
    
    def get_assignment_pairs(self, row_names: List[str], col_names: List[str]) -> List[dict]:
        """
        Get formatted assignment pairs with names
        
        Args:
            row_names: List of worker/row names
            col_names: List of task/column names
            
        Returns:
            List of assignment dictionaries
        """
        pairs = []
        for i, (r, c) in enumerate(self.assignments):
            pairs.append({
                'worker': row_names[r] if r < len(row_names) else f"Worker {r+1}",
                'task': col_names[c] if c < len(col_names) else f"Task {c+1}",
                'cost': self.individual_costs[i] if i < len(self.individual_costs) else 0
            })
        return pairs


def create_sample_assignment_model() -> AssignmentModel:
    """
    Create a sample PP Chemicals worker-task assignment model
    
    Returns:
        AssignmentModel instance with sample data
    """
    # 10x10 efficiency matrix
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
    
    return AssignmentModel(
        problem_name="PP Chemicals Worker Assignment",
        description="Assign workers to tasks to maximize efficiency",
        maximize=True,
        cost_matrix=efficiency_matrix,
        row_names=worker_names,
        col_names=task_names
    )
