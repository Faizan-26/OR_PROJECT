"""
Output Formatting Utilities
Functions for formatting numbers, currency, and solutions
"""

from typing import List, Dict, Any, Optional
import numpy as np


def format_number(value: float, decimals: int = 2) -> str:
    """
    Format a number with thousands separator
    
    Args:
        value: The number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    if abs(value) >= 1e6:
        return f"{value:,.{decimals}f}"
    elif abs(value) >= 1000:
        return f"{value:,.{decimals}f}"
    else:
        return f"{value:.{decimals}f}"


def format_currency(value: float, symbol: str = "Rs.", decimals: int = 2) -> str:
    """
    Format a number as currency
    
    Args:
        value: The amount to format
        symbol: Currency symbol
        decimals: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    return f"{symbol}{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a number as percentage
    
    Args:
        value: The value to format (0-1 or 0-100)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value <= 1:
        value *= 100
    return f"{value:.{decimals}f}%"


def format_solution(
    solution: np.ndarray,
    variable_names: List[str] = None,
    threshold: float = 1e-6
) -> str:
    """
    Format an LP solution
    
    Args:
        solution: Solution vector
        variable_names: Optional variable names
        threshold: Minimum value to display
        
    Returns:
        Formatted solution string
    """
    lines = []
    names = variable_names or [f"x{i+1}" for i in range(len(solution))]
    
    for i, val in enumerate(solution):
        if abs(val) > threshold:
            name = names[i] if i < len(names) else f"x{i+1}"
            lines.append(f"{name}: {format_number(val, 4)}")
    
    return "\n".join(lines)


def format_matrix(
    matrix: np.ndarray,
    row_names: List[str] = None,
    col_names: List[str] = None,
    decimals: int = 2
) -> str:
    """
    Format a matrix as a string table
    
    Args:
        matrix: The matrix to format
        row_names: Optional row names
        col_names: Optional column names
        decimals: Number of decimal places
        
    Returns:
        Formatted table string
    """
    rows, cols = matrix.shape
    row_names = row_names or [f"R{i+1}" for i in range(rows)]
    col_names = col_names or [f"C{j+1}" for j in range(cols)]
    
    # Determine column widths
    col_width = max(10, max(len(str(n)) for n in col_names))
    row_width = max(12, max(len(str(n)) for n in row_names))
    
    lines = []
    
    # Header
    header = " " * (row_width + 1) + " | ".join(f"{n:>{col_width}}" for n in col_names)
    lines.append(header)
    lines.append("-" * len(header))
    
    # Rows
    for i, row_name in enumerate(row_names):
        row_values = [f"{matrix[i,j]:>{col_width}.{decimals}f}" for j in range(cols)]
        lines.append(f"{row_name:<{row_width}} | " + " | ".join(row_values))
    
    return "\n".join(lines)


def format_sensitivity_report(report: Dict[str, Any]) -> str:
    """
    Format a sensitivity analysis report
    
    Args:
        report: Sensitivity analysis dictionary
        
    Returns:
        Formatted report string
    """
    lines = []
    
    lines.append("=" * 60)
    lines.append("SENSITIVITY ANALYSIS REPORT")
    lines.append("=" * 60)
    
    # Shadow prices
    if 'shadow_prices' in report:
        lines.append("\nSHADOW PRICES (Dual Values)")
        lines.append("-" * 40)
        for item in report['shadow_prices']:
            lines.append(f"  {item['name']:.<30} {item['value']:>10.4f}")
    
    # Reduced costs
    if 'reduced_costs' in report:
        lines.append("\nREDUCED COSTS")
        lines.append("-" * 40)
        for item in report['reduced_costs']:
            lines.append(f"  {item['name']:.<30} {item['value']:>10.4f}")
    
    # Slack values
    if 'slack_values' in report:
        lines.append("\nSLACK/SURPLUS VALUES")
        lines.append("-" * 40)
        for item in report['slack_values']:
            lines.append(f"  Constraint {item['constraint']:.<24} {item['value']:>10.4f}")
    
    return "\n".join(lines)


def format_assignment_result(
    assignments: List[tuple],
    row_names: List[str],
    col_names: List[str],
    costs: List[float]
) -> str:
    """
    Format assignment problem results
    
    Args:
        assignments: List of (row, col) tuples
        row_names: Worker/row names
        col_names: Task/column names
        costs: Individual assignment costs
        
    Returns:
        Formatted result string
    """
    lines = []
    
    lines.append("OPTIMAL ASSIGNMENTS")
    lines.append("-" * 50)
    
    for i, (r, c) in enumerate(assignments):
        row_name = row_names[r] if r < len(row_names) else f"Worker {r+1}"
        col_name = col_names[c] if c < len(col_names) else f"Task {c+1}"
        cost = costs[i] if i < len(costs) else 0
        
        lines.append(f"  {row_name:.<20} → {col_name:.<15} ({cost:.0f})")
    
    total = sum(costs)
    lines.append("-" * 50)
    lines.append(f"  {'TOTAL':.<35} {total:>10.0f}")
    
    return "\n".join(lines)


def format_transportation_result(routes: List[Dict]) -> str:
    """
    Format transportation problem results
    
    Args:
        routes: List of route dictionaries
        
    Returns:
        Formatted result string
    """
    lines = []
    
    lines.append("SHIPPING ROUTES")
    lines.append("-" * 60)
    
    total_cost = 0
    for route in routes:
        qty = route.get('quantity', 0)
        if qty > 0.001:
            src = route.get('from', 'Source')
            dest = route.get('to', 'Dest')
            cost = route.get('unit_cost', 0)
            route_cost = route.get('route_cost', qty * cost)
            total_cost += route_cost
            
            lines.append(f"  {src:.<15} → {dest:.<15} : {qty:>6.0f} units @ {cost:.0f} = {route_cost:>10,.0f}")
    
    lines.append("-" * 60)
    lines.append(f"  {'TOTAL TRANSPORTATION COST':.<45} {total_cost:>10,.0f}")
    
    return "\n".join(lines)
