"""
Data Model for Transportation Problems
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np


@dataclass
class TransportationModel:
    """
    Data model for Transportation Problems
    
    Represents the problem of transporting goods from multiple sources
    to multiple destinations at minimum cost
    """
    # Supply at each source
    supply: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Demand at each destination
    demand: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # Cost matrix (sources x destinations)
    cost_matrix: np.ndarray = field(default_factory=lambda: np.array([[]]))
    
    # Names for display
    source_names: List[str] = field(default_factory=list)
    dest_names: List[str] = field(default_factory=list)
    
    # Problem metadata
    problem_name: str = "Untitled Transportation Problem"
    description: str = ""
    
    def __post_init__(self):
        """Initialize default names if not provided"""
        if len(self.supply) > 0:
            if not self.source_names:
                self.source_names = [f"Source {i+1}" for i in range(len(self.supply))]
        
        if len(self.demand) > 0:
            if not self.dest_names:
                self.dest_names = [f"Destination {j+1}" for j in range(len(self.demand))]
    
    @property
    def num_sources(self) -> int:
        """Number of sources"""
        return len(self.supply)
    
    @property
    def num_destinations(self) -> int:
        """Number of destinations"""
        return len(self.demand)
    
    @property
    def total_supply(self) -> float:
        """Total supply"""
        return np.sum(self.supply)
    
    @property
    def total_demand(self) -> float:
        """Total demand"""
        return np.sum(self.demand)
    
    @property
    def is_balanced(self) -> bool:
        """Check if supply equals demand"""
        return abs(self.total_supply - self.total_demand) < 1e-6
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate the transportation model
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(self.supply) == 0:
            return False, "Supply values are empty"
        
        if len(self.demand) == 0:
            return False, "Demand values are empty"
        
        if self.cost_matrix.size == 0:
            return False, "Cost matrix is empty"
        
        if self.cost_matrix.shape != (len(self.supply), len(self.demand)):
            return False, "Cost matrix dimensions must match supply and demand"
        
        if np.any(self.supply < 0):
            return False, "Supply values must be non-negative"
        
        if np.any(self.demand < 0):
            return False, "Demand values must be non-negative"
        
        if np.any(self.cost_matrix < 0):
            return False, "Cost values must be non-negative"
        
        return True, "Valid"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary for serialization"""
        return {
            'problem_name': self.problem_name,
            'description': self.description,
            'supply': self.supply.tolist(),
            'demand': self.demand.tolist(),
            'cost_matrix': self.cost_matrix.tolist(),
            'source_names': self.source_names,
            'dest_names': self.dest_names
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TransportationModel':
        """Create model from dictionary"""
        return cls(
            problem_name=data.get('problem_name', 'Untitled'),
            description=data.get('description', ''),
            supply=np.array(data.get('supply', [])),
            demand=np.array(data.get('demand', [])),
            cost_matrix=np.array(data.get('cost_matrix', [[]])),
            source_names=data.get('source_names', []),
            dest_names=data.get('dest_names', [])
        )


@dataclass
class TransportationResult:
    """Result of solving a transportation problem"""
    success: bool = False
    message: str = ""
    total_cost: float = 0.0
    
    # Allocation matrix
    allocation_matrix: np.ndarray = field(default_factory=lambda: np.array([[]]))
    
    # Route details
    routes: List[dict] = field(default_factory=list)
    
    # Solution info
    is_optimal: bool = False
    iterations: int = 0
    initial_method: str = ""
    
    def to_dict(self) -> dict:
        """Convert result to dictionary"""
        return {
            'success': self.success,
            'message': self.message,
            'total_cost': self.total_cost,
            'allocation_matrix': self.allocation_matrix.tolist() if isinstance(self.allocation_matrix, np.ndarray) else self.allocation_matrix,
            'routes': self.routes,
            'is_optimal': self.is_optimal,
            'iterations': self.iterations,
            'initial_method': self.initial_method
        }
    
    def get_active_routes(self) -> List[dict]:
        """Get only routes with positive allocation"""
        return [r for r in self.routes if r.get('quantity', 0) > 0]


def create_sample_transportation_model() -> TransportationModel:
    """
    Create a sample PP Chemicals transportation model
    
    Returns:
        TransportationModel instance with sample data
    """
    # Supply from 10 plants
    supply = np.array([500, 400, 350, 450, 380, 420, 300, 360, 410, 330])
    
    # Demand at 10 construction sites
    demand = np.array([200, 180, 300, 250, 350, 280, 320, 400, 290, 330])
    
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
    
    source_names = [
        "Karachi", "Lahore", "Islamabad", "Faisalabad", "Rawalpindi",
        "Multan", "Peshawar", "Quetta", "Sialkot", "Gujranwala"
    ]
    
    dest_names = [
        "M-2 Motorway", "Lahore Metro", "Attock Bridge", "Karachi Flyover", "GT Road",
        "Lowari Tunnel", "Islamabad Airport", "Gwadar Port", "Peshawar Railway", "Multan Stadium"
    ]
    
    return TransportationModel(
        problem_name="PP Chemicals Distribution Network",
        description="Minimize transportation cost from plants to construction sites",
        supply=supply,
        demand=demand,
        cost_matrix=cost_matrix,
        source_names=source_names,
        dest_names=dest_names
    )
