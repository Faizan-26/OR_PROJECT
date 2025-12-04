"""
Export Utilities
Functions for exporting results to various formats
"""

import csv
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np


def numpy_to_list(obj):
    """Convert numpy arrays to lists for JSON serialization"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: numpy_to_list(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [numpy_to_list(i) for i in obj]
    return obj


def export_to_csv(
    filepath: str,
    data: Dict[str, Any],
    headers: List[str] = None
) -> bool:
    """
    Export data to CSV file
    
    Args:
        filepath: Path to output file
        data: Data dictionary to export
        headers: Optional column headers
        
    Returns:
        True if successful
    """
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write metadata
            writer.writerow(['PP Chemicals OR Solver Export'])
            writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
            writer.writerow([])
            
            # Write data based on type
            if 'solution' in data:
                # LP solution
                writer.writerow(['SOLUTION'])
                writer.writerow(['Variable', 'Value'])
                solution = data.get('solution', [])
                names = data.get('variable_names', [f'x{i+1}' for i in range(len(solution))])
                for i, val in enumerate(solution):
                    writer.writerow([names[i] if i < len(names) else f'x{i+1}', val])
            
            elif 'assignments' in data:
                # Assignment solution
                writer.writerow(['ASSIGNMENTS'])
                writer.writerow(['Worker', 'Task', 'Cost/Efficiency'])
                for assignment in data.get('assignments', []):
                    writer.writerow([assignment.get('worker', ''), 
                                   assignment.get('task', ''),
                                   assignment.get('cost', 0)])
            
            elif 'routes' in data:
                # Transportation solution
                writer.writerow(['ROUTES'])
                writer.writerow(['From', 'To', 'Quantity', 'Unit Cost', 'Total Cost'])
                for route in data.get('routes', []):
                    if route.get('quantity', 0) > 0:
                        writer.writerow([
                            route.get('from', ''),
                            route.get('to', ''),
                            route.get('quantity', 0),
                            route.get('unit_cost', 0),
                            route.get('route_cost', 0)
                        ])
            
            # Write summary
            writer.writerow([])
            writer.writerow(['SUMMARY'])
            if 'optimal_value' in data:
                writer.writerow(['Optimal Value', data['optimal_value']])
            if 'total_cost' in data:
                writer.writerow(['Total Cost', data['total_cost']])
            
        return True
    except Exception as e:
        print(f"Export error: {e}")
        return False


def export_to_json(filepath: str, data: Dict[str, Any]) -> bool:
    """
    Export data to JSON file
    
    Args:
        filepath: Path to output file
        data: Data dictionary to export
        
    Returns:
        True if successful
    """
    try:
        # Convert numpy arrays to lists
        export_data = numpy_to_list(data)
        
        # Add metadata
        export_data['_metadata'] = {
            'application': 'PP Chemicals OR Solver',
            'version': '1.0.0',
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Export error: {e}")
        return False


def export_to_excel(filepath: str, data: Dict[str, Any]) -> bool:
    """
    Export data to Excel file
    
    Args:
        filepath: Path to output file
        data: Data dictionary to export
        
    Returns:
        True if successful
    """
    try:
        import pandas as pd
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': [],
                'Value': []
            }
            
            if 'optimal_value' in data:
                summary_data['Metric'].append('Optimal Value')
                summary_data['Value'].append(data['optimal_value'])
            
            if 'total_cost' in data:
                summary_data['Metric'].append('Total Cost')
                summary_data['Value'].append(data['total_cost'])
            
            if 'iterations' in data:
                summary_data['Metric'].append('Iterations')
                summary_data['Value'].append(data['iterations'])
            
            if summary_data['Metric']:
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Solution sheet (LP)
            if 'solution' in data:
                solution = data['solution']
                names = data.get('variable_names', [f'x{i+1}' for i in range(len(solution))])
                sol_df = pd.DataFrame({
                    'Variable': names,
                    'Value': solution
                })
                sol_df.to_excel(writer, sheet_name='Solution', index=False)
            
            # Assignments sheet
            if 'assignments' in data:
                assignments = data.get('assignments', [])
                if assignments:
                    assign_df = pd.DataFrame(assignments)
                    assign_df.to_excel(writer, sheet_name='Assignments', index=False)
            
            # Routes sheet
            if 'routes' in data:
                routes = [r for r in data.get('routes', []) if r.get('quantity', 0) > 0]
                if routes:
                    routes_df = pd.DataFrame(routes)
                    routes_df.to_excel(writer, sheet_name='Routes', index=False)
            
            # Sensitivity sheet
            if 'shadow_prices' in data:
                sens_df = pd.DataFrame(data['shadow_prices'])
                sens_df.to_excel(writer, sheet_name='Sensitivity', index=False)
        
        return True
    except ImportError:
        print("pandas and openpyxl required for Excel export")
        return False
    except Exception as e:
        print(f"Export error: {e}")
        return False


def import_from_csv(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Import data from CSV file
    
    Args:
        filepath: Path to input file
        
    Returns:
        Data dictionary or None if failed
    """
    try:
        data = {'matrix': [], 'headers': []}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            if rows:
                # First row might be headers
                try:
                    # Try to parse as numbers
                    first_row = [float(x) for x in rows[0]]
                    data['matrix'].append(first_row)
                except ValueError:
                    # It's a header row
                    data['headers'] = rows[0]
                
                # Parse remaining rows
                for row in rows[1:]:
                    try:
                        data['matrix'].append([float(x) for x in row if x])
                    except ValueError:
                        continue
        
        if data['matrix']:
            data['matrix'] = np.array(data['matrix'])
        
        return data
    except Exception as e:
        print(f"Import error: {e}")
        return None


def import_from_json(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Import data from JSON file
    
    Args:
        filepath: Path to input file
        
    Returns:
        Data dictionary or None if failed
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert lists back to numpy arrays
        if 'matrix' in data:
            data['matrix'] = np.array(data['matrix'])
        if 'solution' in data:
            data['solution'] = np.array(data['solution'])
        
        return data
    except Exception as e:
        print(f"Import error: {e}")
        return None
