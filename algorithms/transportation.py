"""
Transportation Problem Solver
Methods: North-West Corner, Least Cost, VAM (initial solution)
         MODI Method (optimization)
Supports 10x10 or larger supply-demand matrices
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum


class InitialMethod(Enum):
    """Methods for finding initial basic feasible solution"""
    NORTH_WEST_CORNER = "north_west"
    LEAST_COST = "least_cost"
    VOGEL = "vam"  # Vogel's Approximation Method


@dataclass
class TransportationResult:
    """Contains transportation problem solution results"""
    success: bool
    message: str
    total_cost: float
    allocation_matrix: np.ndarray
    route_details: List[Dict]
    is_optimal: bool
    iterations: int
    initial_method: str


class TransportationSolver:
    """
    Transportation Problem Solver
    
    Finds the optimal way to transport goods from multiple sources (plants)
    to multiple destinations (sites) minimizing total transportation cost.
    
    Features:
    - Three methods for initial basic feasible solution
    - MODI method for optimization
    - Handles balanced and unbalanced problems
    - Degeneracy handling
    """
    
    def __init__(
        self,
        supply: np.ndarray,
        demand: np.ndarray,
        cost_matrix: np.ndarray,
        source_names: Optional[List[str]] = None,
        dest_names: Optional[List[str]] = None
    ):
        """
        Initialize the Transportation Solver
        
        Args:
            supply: Array of supply quantities at each source
            demand: Array of demand quantities at each destination
            cost_matrix: 2D array of transportation costs (m sources x n destinations)
            source_names: Optional names for sources
            dest_names: Optional names for destinations
        """
        self.supply = np.array(supply, dtype=float)
        self.demand = np.array(demand, dtype=float)
        self.cost_matrix = np.array(cost_matrix, dtype=float)
        
        self.m = len(supply)  # Number of sources
        self.n = len(demand)  # Number of destinations
        
        self.source_names = source_names or [f"Source {i+1}" for i in range(self.m)]
        self.dest_names = dest_names or [f"Dest {j+1}" for j in range(self.n)]
        
        # Balance the problem if needed
        self._balance_problem()
        
        self._result = None
        self._allocation = None
        self._is_balanced_originally = True
    
    def _balance_problem(self):
        """Balance the transportation problem if supply != demand"""
        total_supply = np.sum(self.supply)
        total_demand = np.sum(self.demand)
        
        if abs(total_supply - total_demand) > 1e-6:
            self._is_balanced_originally = False
            
            if total_supply > total_demand:
                # Add dummy destination
                diff = total_supply - total_demand
                self.demand = np.append(self.demand, diff)
                # Add zero-cost column for dummy destination
                dummy_col = np.zeros((self.m, 1))
                self.cost_matrix = np.hstack([self.cost_matrix, dummy_col])
                self.dest_names.append("Dummy Destination")
                self.n += 1
            else:
                # Add dummy source
                diff = total_demand - total_supply
                self.supply = np.append(self.supply, diff)
                # Add zero-cost row for dummy source
                dummy_row = np.zeros((1, self.n))
                self.cost_matrix = np.vstack([self.cost_matrix, dummy_row])
                self.source_names.append("Dummy Source")
                self.m += 1
    
    def _north_west_corner(self) -> np.ndarray:
        """
        North-West Corner Method for initial basic feasible solution
        
        Returns:
            Initial allocation matrix
        """
        allocation = np.zeros((self.m, self.n))
        supply_left = self.supply.copy()
        demand_left = self.demand.copy()
        
        i, j = 0, 0
        
        while i < self.m and j < self.n:
            quantity = min(supply_left[i], demand_left[j])
            allocation[i, j] = quantity
            supply_left[i] -= quantity
            demand_left[j] -= quantity
            
            if supply_left[i] == 0:
                i += 1
            if demand_left[j] == 0:
                j += 1
        
        return allocation
    
    def _least_cost_method(self) -> np.ndarray:
        """
        Least Cost Method for initial basic feasible solution
        
        Returns:
            Initial allocation matrix
        """
        allocation = np.zeros((self.m, self.n))
        supply_left = self.supply.copy()
        demand_left = self.demand.copy()
        
        # Create masked cost matrix
        cost_work = self.cost_matrix.copy()
        
        while np.sum(supply_left) > 1e-6 and np.sum(demand_left) > 1e-6:
            # Find minimum cost cell among available cells
            min_cost = np.inf
            min_i, min_j = 0, 0
            
            for i in range(self.m):
                for j in range(self.n):
                    if supply_left[i] > 0 and demand_left[j] > 0:
                        if cost_work[i, j] < min_cost:
                            min_cost = cost_work[i, j]
                            min_i, min_j = i, j
            
            # Allocate
            quantity = min(supply_left[min_i], demand_left[min_j])
            allocation[min_i, min_j] = quantity
            supply_left[min_i] -= quantity
            demand_left[min_j] -= quantity
        
        return allocation
    
    def _vogel_approximation_method(self) -> np.ndarray:
        """
        Vogel's Approximation Method (VAM) for initial basic feasible solution
        Generally gives a solution close to optimal
        
        Returns:
            Initial allocation matrix
        """
        allocation = np.zeros((self.m, self.n))
        supply_left = self.supply.copy()
        demand_left = self.demand.copy()
        
        # Track which rows/columns are still active
        active_rows = [True] * self.m
        active_cols = [True] * self.n
        
        while np.sum(supply_left) > 1e-6 and np.sum(demand_left) > 1e-6:
            # Calculate penalties for each row
            row_penalties = []
            for i in range(self.m):
                if not active_rows[i]:
                    row_penalties.append(-1)
                    continue
                costs = [self.cost_matrix[i, j] for j in range(self.n) 
                        if active_cols[j] and demand_left[j] > 0]
                if len(costs) >= 2:
                    costs.sort()
                    row_penalties.append(costs[1] - costs[0])
                elif len(costs) == 1:
                    row_penalties.append(costs[0])
                else:
                    row_penalties.append(-1)
            
            # Calculate penalties for each column
            col_penalties = []
            for j in range(self.n):
                if not active_cols[j]:
                    col_penalties.append(-1)
                    continue
                costs = [self.cost_matrix[i, j] for i in range(self.m) 
                        if active_rows[i] and supply_left[i] > 0]
                if len(costs) >= 2:
                    costs.sort()
                    col_penalties.append(costs[1] - costs[0])
                elif len(costs) == 1:
                    col_penalties.append(costs[0])
                else:
                    col_penalties.append(-1)
            
            # Find maximum penalty
            max_row_penalty = max(row_penalties) if row_penalties else -1
            max_col_penalty = max(col_penalties) if col_penalties else -1
            
            if max_row_penalty >= max_col_penalty and max_row_penalty >= 0:
                # Select row with max penalty
                i = row_penalties.index(max_row_penalty)
                # Find minimum cost in this row
                min_cost = np.inf
                min_j = 0
                for j in range(self.n):
                    if active_cols[j] and demand_left[j] > 0:
                        if self.cost_matrix[i, j] < min_cost:
                            min_cost = self.cost_matrix[i, j]
                            min_j = j
                j = min_j
            elif max_col_penalty >= 0:
                # Select column with max penalty
                j = col_penalties.index(max_col_penalty)
                # Find minimum cost in this column
                min_cost = np.inf
                min_i = 0
                for i in range(self.m):
                    if active_rows[i] and supply_left[i] > 0:
                        if self.cost_matrix[i, j] < min_cost:
                            min_cost = self.cost_matrix[i, j]
                            min_i = i
                i = min_i
            else:
                break
            
            # Allocate
            quantity = min(supply_left[i], demand_left[j])
            allocation[i, j] = quantity
            supply_left[i] -= quantity
            demand_left[j] -= quantity
            
            # Update active status
            if supply_left[i] <= 1e-6:
                active_rows[i] = False
            if demand_left[j] <= 1e-6:
                active_cols[j] = False
        
        return allocation
    
    def _get_basic_cells(self, allocation: np.ndarray) -> List[Tuple[int, int]]:
        """Get list of basic variable cells"""
        cells = []
        for i in range(self.m):
            for j in range(self.n):
                if allocation[i, j] > 0:
                    cells.append((i, j))
        return cells
    
    def _calculate_uv(self, allocation: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate u_i and v_j values for MODI method
        Using u_i + v_j = c_ij for basic cells
        """
        u = np.full(self.m, np.nan)
        v = np.full(self.n, np.nan)
        
        # Start with u_0 = 0
        u[0] = 0
        
        basic_cells = self._get_basic_cells(allocation)
        
        # Iteratively solve for u and v
        max_iterations = self.m + self.n
        for _ in range(max_iterations):
            for i, j in basic_cells:
                if not np.isnan(u[i]) and np.isnan(v[j]):
                    v[j] = self.cost_matrix[i, j] - u[i]
                elif np.isnan(u[i]) and not np.isnan(v[j]):
                    u[i] = self.cost_matrix[i, j] - v[j]
        
        # Fill any remaining NaN values
        u = np.nan_to_num(u, nan=0.0)
        v = np.nan_to_num(v, nan=0.0)
        
        return u, v
    
    def _calculate_opportunity_costs(
        self, 
        allocation: np.ndarray, 
        u: np.ndarray, 
        v: np.ndarray
    ) -> np.ndarray:
        """
        Calculate opportunity costs (delta_ij = c_ij - u_i - v_j) for non-basic cells
        """
        delta = np.zeros((self.m, self.n))
        
        for i in range(self.m):
            for j in range(self.n):
                if allocation[i, j] == 0:
                    delta[i, j] = self.cost_matrix[i, j] - u[i] - v[j]
                else:
                    delta[i, j] = 0  # Basic cells have zero opportunity cost
        
        return delta
    
    def _find_loop(
        self, 
        allocation: np.ndarray, 
        start_cell: Tuple[int, int]
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Find a closed loop starting from the entering cell
        """
        basic_cells = set(self._get_basic_cells(allocation))
        basic_cells.add(start_cell)
        
        def dfs(current, path, direction):
            """DFS to find loop - direction: 0=horizontal, 1=vertical"""
            if len(path) >= 4 and current == start_cell:
                return path
            
            if len(path) > 2 * (self.m + self.n):
                return None
            
            if direction == 0:  # Moving horizontally
                for j in range(self.n):
                    next_cell = (current[0], j)
                    if next_cell != current and next_cell in basic_cells:
                        if next_cell not in path or (next_cell == start_cell and len(path) >= 3):
                            result = dfs(next_cell, path + [next_cell], 1)
                            if result:
                                return result
            else:  # Moving vertically
                for i in range(self.m):
                    next_cell = (i, current[1])
                    if next_cell != current and next_cell in basic_cells:
                        if next_cell not in path or (next_cell == start_cell and len(path) >= 3):
                            result = dfs(next_cell, path + [next_cell], 0)
                            if result:
                                return result
            
            return None
        
        # Try starting horizontally and vertically
        loop = dfs(start_cell, [start_cell], 0)
        if loop is None:
            loop = dfs(start_cell, [start_cell], 1)
        
        return loop if loop and len(loop) >= 4 else None
    
    def _optimize_modi(self, allocation: np.ndarray, max_iterations: int = 100) -> Tuple[np.ndarray, int]:
        """
        Optimize using MODI (Modified Distribution) method
        
        Returns:
            Tuple of (optimized allocation, iterations)
        """
        allocation = allocation.copy()
        
        for iteration in range(max_iterations):
            # Handle degeneracy
            allocation = self._handle_degeneracy(allocation)
            
            # Calculate u and v
            u, v = self._calculate_uv(allocation)
            
            # Calculate opportunity costs
            delta = self._calculate_opportunity_costs(allocation, u, v)
            
            # Find minimum opportunity cost (most negative)
            min_delta = np.min(delta)
            
            if min_delta >= -1e-6:
                # Solution is optimal
                return allocation, iteration
            
            # Find entering cell
            entering_cell = None
            for i in range(self.m):
                for j in range(self.n):
                    if allocation[i, j] == 0 and abs(delta[i, j] - min_delta) < 1e-6:
                        entering_cell = (i, j)
                        break
                if entering_cell:
                    break
            
            if entering_cell is None:
                return allocation, iteration
            
            # Find loop and perform reallocation
            loop = self._find_loop(allocation, entering_cell)
            
            if loop is None:
                # Can't find loop, return current solution
                return allocation, iteration
            
            # Determine theta (minimum allocation at odd positions)
            odd_positions = loop[1::2]
            theta = min(allocation[i, j] for i, j in odd_positions)
            
            # Update allocations along the loop
            for idx, (i, j) in enumerate(loop[:-1]):  # Exclude last (same as first)
                if idx % 2 == 0:
                    allocation[i, j] += theta
                else:
                    allocation[i, j] -= theta
        
        return allocation, max_iterations
    
    def _handle_degeneracy(self, allocation: np.ndarray) -> np.ndarray:
        """
        Handle degenerate solutions by adding small epsilon to maintain m+n-1 basic variables
        """
        num_basic = np.sum(allocation > 0)
        required_basic = self.m + self.n - 1
        
        if num_basic < required_basic:
            epsilon = 1e-6
            count = int(required_basic - num_basic)
            
            for i in range(self.m):
                for j in range(self.n):
                    if count <= 0:
                        break
                    if allocation[i, j] == 0:
                        allocation[i, j] = epsilon
                        count -= 1
                if count <= 0:
                    break
        
        return allocation
    
    def solve(
        self, 
        method: InitialMethod = InitialMethod.VOGEL,
        optimize: bool = True
    ) -> TransportationResult:
        """
        Solve the transportation problem
        
        Args:
            method: Method for initial solution
            optimize: Whether to optimize using MODI
            
        Returns:
            TransportationResult containing the solution
        """
        try:
            # Get initial basic feasible solution
            if method == InitialMethod.NORTH_WEST_CORNER:
                self._allocation = self._north_west_corner()
            elif method == InitialMethod.LEAST_COST:
                self._allocation = self._least_cost_method()
            else:  # VAM
                self._allocation = self._vogel_approximation_method()
            
            iterations = 0
            is_optimal = False
            
            # Optimize if requested
            if optimize:
                self._allocation, iterations = self._optimize_modi(self._allocation)
                is_optimal = True
            
            # Calculate total cost
            total_cost = np.sum(self._allocation * self.cost_matrix)
            
            # Generate route details
            route_details = []
            for i in range(self.m):
                for j in range(self.n):
                    if self._allocation[i, j] > 1e-6:
                        route_details.append({
                            'from': self.source_names[i],
                            'to': self.dest_names[j],
                            'quantity': self._allocation[i, j],
                            'unit_cost': self.cost_matrix[i, j],
                            'route_cost': self._allocation[i, j] * self.cost_matrix[i, j]
                        })
            
            self._result = TransportationResult(
                success=True,
                message="Optimal solution found" if is_optimal else "Initial solution found",
                total_cost=total_cost,
                allocation_matrix=self._allocation,
                route_details=route_details,
                is_optimal=is_optimal,
                iterations=iterations,
                initial_method=method.value
            )
            
        except Exception as e:
            self._result = TransportationResult(
                success=False,
                message=str(e),
                total_cost=0.0,
                allocation_matrix=np.zeros((self.m, self.n)),
                route_details=[],
                is_optimal=False,
                iterations=0,
                initial_method=method.value
            )
        
        return self._result
    
    def get_solution_summary(self) -> Dict[str, Any]:
        """
        Get a formatted summary of the transportation solution
        
        Returns:
            Dictionary containing formatted solution information
        """
        if self._result is None:
            return {"error": "Problem not solved yet. Call solve() first."}
        
        if not self._result.success:
            return {"error": self._result.message}
        
        summary = {
            "status": "Optimal" if self._result.is_optimal else "Feasible",
            "total_cost": self._result.total_cost,
            "iterations": self._result.iterations,
            "initial_method": self._result.initial_method,
            "routes": self._result.route_details,
            "total_supply": np.sum(self.supply),
            "total_demand": np.sum(self.demand)
        }
        
        return summary
    
    def get_formatted_allocation(self) -> str:
        """
        Get a formatted string representation of the allocation matrix
        
        Returns:
            String representation of the solution
        """
        if self._result is None or not self._result.success:
            return "No solution available"
        
        # Header
        header = "             | " + " | ".join(f"{name[:10]:^10}" for name in self.dest_names) + " | Supply"
        separator = "-" * len(header)
        
        lines = [header, separator]
        
        for i in range(self.m):
            row_values = []
            for j in range(self.n):
                alloc = self._allocation[i, j]
                cost = self.cost_matrix[i, j]
                if alloc > 1e-6:
                    row_values.append(f"[{alloc:>4.0f}]/{cost:<3.0f}")
                else:
                    row_values.append(f"     /{cost:<3.0f}")
            
            supply_val = self.supply[i]
            lines.append(
                f"{self.source_names[i][:12]:<12} | " + 
                " | ".join(f"{v:^10}" for v in row_values) + 
                f" | {supply_val:>6.0f}"
            )
        
        # Demand row
        lines.append(separator)
        demand_row = "Demand       | " + " | ".join(f"{d:^10.0f}" for d in self.demand) + " |"
        lines.append(demand_row)
        
        return "\n".join(lines)


def create_sample_problem() -> TransportationSolver:
    """
    Create a sample PP Chemicals transportation problem
    
    Returns:
        TransportationSolver instance with sample data
    """
    # Supply from 10 plants (tons/month)
    supply = np.array([500, 400, 350, 450, 380, 420, 300, 360, 410, 330])
    
    # Demand at 10 construction sites (tons/month)
    demand = np.array([200, 180, 300, 250, 350, 280, 320, 400, 290, 330])
    
    # Transportation cost matrix (Rs. per ton)
    cost_matrix = np.array([
        [45, 72, 35, 58, 62, 48, 55, 80, 42, 65],   # Karachi
        [38, 65, 42, 52, 58, 45, 50, 75, 38, 60],   # Lahore
        [55, 48, 58, 42, 45, 52, 48, 62, 55, 45],   # Islamabad
        [62, 55, 48, 38, 42, 55, 52, 58, 48, 42],   # Faisalabad
        [70, 58, 52, 45, 38, 48, 45, 52, 55, 48],   # Rawalpindi
        [58, 52, 55, 48, 45, 35, 42, 48, 52, 55],   # Multan
        [85, 78, 72, 65, 58, 52, 45, 38, 65, 58],   # Peshawar
        [78, 72, 65, 58, 52, 48, 42, 45, 58, 55],   # Quetta
        [72, 68, 62, 55, 48, 52, 48, 42, 52, 48],   # Sialkot
        [95, 88, 82, 75, 68, 62, 55, 48, 72, 65]    # Gujranwala
    ])
    
    source_names = [
        "Karachi", "Lahore", "Islamabad", "Faisalabad", "Rawalpindi",
        "Multan", "Peshawar", "Quetta", "Sialkot", "Gujranwala"
    ]
    
    dest_names = [
        "M-2 Motorway", "Lahore Metro", "Attock Bridge", "Karachi Flyover", "GT Road",
        "Lowari Tunnel", "Islamabad Airport", "Gwadar Port", "Peshawar Railway", "Multan Stadium"
    ]
    
    return TransportationSolver(
        supply=supply,
        demand=demand,
        cost_matrix=cost_matrix,
        source_names=source_names,
        dest_names=dest_names
    )


if __name__ == "__main__":
    print("=" * 80)
    print("PP CHEMICALS - TRANSPORTATION PROBLEM")
    print("Distributing chemicals from plants to construction sites")
    print("=" * 80)
    
    solver = create_sample_problem()
    
    # Test all three initial methods
    for method in InitialMethod:
        print(f"\n{'-' * 60}")
        print(f"Method: {method.value.upper()}")
        print(f"{'-' * 60}")
        
        result = solver.solve(method=method, optimize=True)
        summary = solver.get_solution_summary()
        
        print(f"Status: {summary['status']}")
        print(f"Total Transportation Cost: Rs.{summary['total_cost']:,.2f}")
        print(f"MODI Iterations: {summary['iterations']}")
        
        print("\nTop 5 Routes (by quantity):")
        sorted_routes = sorted(summary['routes'], key=lambda x: x['quantity'], reverse=True)[:5]
        for route in sorted_routes:
            print(f"  {route['from']} → {route['to']}: {route['quantity']:.0f} tons @ Rs.{route['unit_cost']:.0f}/ton = Rs.{route['route_cost']:,.0f}")
    
    print("\n" + "=" * 80)
    print("Final Allocation Matrix (VAM + MODI):")
    print("=" * 80)
    solver.solve(method=InitialMethod.VOGEL, optimize=True)
    print(solver.get_formatted_allocation())
