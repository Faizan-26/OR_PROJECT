"""
Input Validation Utilities
Functions for validating user input data
"""

import numpy as np
from typing import Tuple, List, Any, Optional


def validate_numeric(value: Any) -> Tuple[bool, float]:
    """
    Validate that a value can be converted to a number
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, converted_value)
    """
    try:
        num = float(value)
        return True, num
    except (ValueError, TypeError):
        return False, 0.0


def validate_positive(value: Any) -> Tuple[bool, float]:
    """
    Validate that a value is a positive number
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, converted_value)
    """
    is_valid, num = validate_numeric(value)
    if is_valid and num > 0:
        return True, num
    return False, 0.0


def validate_non_negative(value: Any) -> Tuple[bool, float]:
    """
    Validate that a value is non-negative
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, converted_value)
    """
    is_valid, num = validate_numeric(value)
    if is_valid and num >= 0:
        return True, num
    return False, 0.0


def validate_matrix(matrix: np.ndarray) -> Tuple[bool, str]:
    """
    Validate a matrix for common issues
    
    Args:
        matrix: The matrix to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if matrix.size == 0:
        return False, "Matrix is empty"
    
    if not np.isfinite(matrix).all():
        return False, "Matrix contains invalid values (NaN or Inf)"
    
    return True, "Valid"


def validate_lp_inputs(
    c: np.ndarray,
    A: np.ndarray,
    b: np.ndarray
) -> Tuple[bool, str]:
    """
    Validate linear programming inputs
    
    Args:
        c: Objective function coefficients
        A: Constraint matrix
        b: Right-hand side values
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(c) == 0:
        return False, "Objective function coefficients are empty"
    
    if A.size == 0:
        return False, "Constraint matrix is empty"
    
    if len(b) == 0:
        return False, "RHS values are empty"
    
    if A.shape[1] != len(c):
        return False, f"Constraint matrix has {A.shape[1]} columns but there are {len(c)} variables"
    
    if A.shape[0] != len(b):
        return False, f"Constraint matrix has {A.shape[0]} rows but there are {len(b)} RHS values"
    
    return True, "Valid"


def validate_assignment_matrix(matrix: np.ndarray) -> Tuple[bool, str]:
    """
    Validate assignment problem matrix
    
    Args:
        matrix: The cost/efficiency matrix
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    is_valid, msg = validate_matrix(matrix)
    if not is_valid:
        return False, msg
    
    if matrix.ndim != 2:
        return False, "Matrix must be 2-dimensional"
    
    return True, "Valid"


def validate_transportation_inputs(
    supply: np.ndarray,
    demand: np.ndarray,
    costs: np.ndarray
) -> Tuple[bool, str]:
    """
    Validate transportation problem inputs
    
    Args:
        supply: Supply values
        demand: Demand values
        costs: Cost matrix
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(supply) == 0:
        return False, "Supply values are empty"
    
    if len(demand) == 0:
        return False, "Demand values are empty"
    
    if costs.size == 0:
        return False, "Cost matrix is empty"
    
    if costs.shape != (len(supply), len(demand)):
        return False, f"Cost matrix shape {costs.shape} doesn't match supply ({len(supply)}) and demand ({len(demand)})"
    
    if np.any(supply < 0):
        return False, "Supply values must be non-negative"
    
    if np.any(demand < 0):
        return False, "Demand values must be non-negative"
    
    if np.any(costs < 0):
        return False, "Cost values must be non-negative"
    
    return True, "Valid"
