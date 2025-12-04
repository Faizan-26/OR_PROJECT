"""
Reusable Matrix Input Widget
A scrollable, editable grid for entering matrices
"""

import customtkinter as ctk
import tkinter as tk
from typing import List, Optional, Callable
import numpy as np


class ScrollableFrame(ctk.CTkFrame):
    """
    A frame that supports both horizontal and vertical scrolling.
    Uses tkinter Canvas for full scrolling support.
    """
    
    def __init__(self, parent, width=800, height=400, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=self._apply_appearance_mode(self._fg_color))
        
        # Scrollbars
        self.h_scrollbar = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.v_scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        
        # Configure canvas
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        
        # Layout
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Inner frame for content
        self.inner_frame = ctk.CTkFrame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        
        # Bind events
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
        
        # Set initial size
        self.canvas.configure(width=width, height=height)
    
    def _on_frame_configure(self, event):
        """Update scroll region when inner frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        pass
    
    def _on_mousewheel(self, event):
        """Vertical scroll with mouse wheel"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_shift_mousewheel(self, event):
        """Horizontal scroll with Shift+mouse wheel"""
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def get_inner_frame(self):
        """Return the inner frame where widgets should be placed"""
        return self.inner_frame


class MatrixInput(ctk.CTkFrame):
    """
    A scrollable matrix input widget for entering 2D data
    
    Features:
    - Dynamic row/column sizing
    - Custom row and column headers
    - Validation support
    - Get/set matrix values
    """
    
    def __init__(
        self,
        parent,
        rows: int = 10,
        cols: int = 10,
        row_headers: Optional[List[str]] = None,
        col_headers: Optional[List[str]] = None,
        cell_width: int = 70,
        cell_height: int = 30,
        default_value: str = "0",
        editable_headers: bool = False,
        on_change: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize the matrix input widget
        
        Args:
            parent: Parent widget
            rows: Number of rows
            cols: Number of columns
            row_headers: Optional list of row header names
            col_headers: Optional list of column header names
            cell_width: Width of each cell
            cell_height: Height of each cell
            default_value: Default value for cells
            editable_headers: Whether headers are editable
            on_change: Callback when values change
        """
        super().__init__(parent, **kwargs)
        
        self.rows = rows
        self.cols = cols
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.default_value = default_value
        self.editable_headers = editable_headers
        self.on_change = on_change
        
        # Initialize headers
        self.row_headers = row_headers or [f"R{i+1}" for i in range(rows)]
        self.col_headers = col_headers or [f"C{j+1}" for j in range(cols)]
        
        # Storage for entry widgets
        self.cells: List[List[ctk.CTkEntry]] = []
        self.row_header_entries: List[ctk.CTkEntry] = []
        self.col_header_entries: List[ctk.CTkEntry] = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the matrix grid widgets"""
        # Create scrollable frame with both horizontal and vertical scrolling
        self.scroll_container = ScrollableFrame(
            self,
            width=min(750, (self.cols + 1) * self.cell_width + 60),
            height=min(450, (self.rows + 1) * self.cell_height + 60)
        )
        self.scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Get the inner frame for placing widgets
        self.scroll_frame = self.scroll_container.get_inner_frame()
        
        # Create corner cell (empty)
        corner = ctk.CTkLabel(
            self.scroll_frame,
            text="",
            width=self.cell_width,
            height=self.cell_height
        )
        corner.grid(row=0, column=0, padx=1, pady=1)
        
        # Create column headers
        for j, header in enumerate(self.col_headers):
            if self.editable_headers:
                entry = ctk.CTkEntry(
                    self.scroll_frame,
                    width=self.cell_width,
                    height=self.cell_height,
                    justify="center"
                )
                entry.insert(0, header)
                entry.grid(row=0, column=j+1, padx=1, pady=1)
                self.col_header_entries.append(entry)
            else:
                label = ctk.CTkLabel(
                    self.scroll_frame,
                    text=header[:10],
                    width=self.cell_width,
                    height=self.cell_height,
                    font=ctk.CTkFont(weight="bold"),
                    fg_color=("gray80", "gray30"),
                    corner_radius=5
                )
                label.grid(row=0, column=j+1, padx=1, pady=1)
        
        # Create rows with headers and cells
        for i in range(self.rows):
            row_cells = []
            
            # Row header
            if self.editable_headers:
                entry = ctk.CTkEntry(
                    self.scroll_frame,
                    width=self.cell_width,
                    height=self.cell_height,
                    justify="center"
                )
                entry.insert(0, self.row_headers[i] if i < len(self.row_headers) else f"R{i+1}")
                entry.grid(row=i+1, column=0, padx=1, pady=1)
                self.row_header_entries.append(entry)
            else:
                label = ctk.CTkLabel(
                    self.scroll_frame,
                    text=self.row_headers[i][:12] if i < len(self.row_headers) else f"R{i+1}",
                    width=self.cell_width,
                    height=self.cell_height,
                    font=ctk.CTkFont(weight="bold"),
                    fg_color=("gray80", "gray30"),
                    corner_radius=5
                )
                label.grid(row=i+1, column=0, padx=1, pady=1)
            
            # Data cells
            for j in range(self.cols):
                entry = ctk.CTkEntry(
                    self.scroll_frame,
                    width=self.cell_width,
                    height=self.cell_height,
                    justify="center"
                )
                entry.insert(0, self.default_value)
                entry.grid(row=i+1, column=j+1, padx=1, pady=1)
                
                if self.on_change:
                    entry.bind("<KeyRelease>", lambda e: self.on_change())
                
                row_cells.append(entry)
            
            self.cells.append(row_cells)
    
    def _recreate_grid_widgets(self):
        """Recreate only the grid widgets (used by resize)"""
        # Create corner cell (empty)
        corner = ctk.CTkLabel(
            self.scroll_frame,
            text="",
            width=self.cell_width,
            height=self.cell_height
        )
        corner.grid(row=0, column=0, padx=1, pady=1)
        
        # Create column headers
        for j, header in enumerate(self.col_headers[:self.cols]):
            if self.editable_headers:
                entry = ctk.CTkEntry(
                    self.scroll_frame,
                    width=self.cell_width,
                    height=self.cell_height,
                    justify="center"
                )
                entry.insert(0, header)
                entry.grid(row=0, column=j+1, padx=1, pady=1)
                self.col_header_entries.append(entry)
            else:
                label = ctk.CTkLabel(
                    self.scroll_frame,
                    text=header[:10],
                    width=self.cell_width,
                    height=self.cell_height,
                    font=ctk.CTkFont(weight="bold"),
                    fg_color=("gray80", "gray30"),
                    corner_radius=5
                )
                label.grid(row=0, column=j+1, padx=1, pady=1)
        
        # Create rows with headers and cells
        for i in range(self.rows):
            row_cells = []
            
            # Row header
            if self.editable_headers:
                entry = ctk.CTkEntry(
                    self.scroll_frame,
                    width=self.cell_width,
                    height=self.cell_height,
                    justify="center"
                )
                entry.insert(0, self.row_headers[i] if i < len(self.row_headers) else f"R{i+1}")
                entry.grid(row=i+1, column=0, padx=1, pady=1)
                self.row_header_entries.append(entry)
            else:
                label = ctk.CTkLabel(
                    self.scroll_frame,
                    text=self.row_headers[i][:12] if i < len(self.row_headers) else f"R{i+1}",
                    width=self.cell_width,
                    height=self.cell_height,
                    font=ctk.CTkFont(weight="bold"),
                    fg_color=("gray80", "gray30"),
                    corner_radius=5
                )
                label.grid(row=i+1, column=0, padx=1, pady=1)
            
            # Data cells
            for j in range(self.cols):
                entry = ctk.CTkEntry(
                    self.scroll_frame,
                    width=self.cell_width,
                    height=self.cell_height,
                    justify="center"
                )
                entry.insert(0, self.default_value)
                entry.grid(row=i+1, column=j+1, padx=1, pady=1)
                
                if self.on_change:
                    entry.bind("<KeyRelease>", lambda e: self.on_change())
                
                row_cells.append(entry)
            
            self.cells.append(row_cells)

    def get_matrix(self) -> np.ndarray:
        """
        Get the current matrix values as a numpy array
        
        Returns:
            2D numpy array of float values
        """
        matrix = np.zeros((self.rows, self.cols))
        
        for i in range(self.rows):
            for j in range(self.cols):
                try:
                    value = float(self.cells[i][j].get())
                except ValueError:
                    value = 0.0
                matrix[i, j] = value
        
        return matrix
    
    def set_matrix(self, matrix: np.ndarray):
        """
        Set the matrix values from a numpy array
        
        Args:
            matrix: 2D numpy array of values
        """
        rows, cols = matrix.shape
        
        for i in range(min(rows, self.rows)):
            for j in range(min(cols, self.cols)):
                self.cells[i][j].delete(0, "end")
                self.cells[i][j].insert(0, str(matrix[i, j]))
    
    def get_row_headers(self) -> List[str]:
        """Get current row headers"""
        if self.editable_headers:
            return [entry.get() for entry in self.row_header_entries]
        return self.row_headers
    
    def get_col_headers(self) -> List[str]:
        """Get current column headers"""
        if self.editable_headers:
            return [entry.get() for entry in self.col_header_entries]
        return self.col_headers
    
    def set_row_headers(self, headers: List[str]):
        """Set row headers"""
        self.row_headers = headers
        if self.editable_headers:
            for i, entry in enumerate(self.row_header_entries):
                entry.delete(0, "end")
                entry.insert(0, headers[i] if i < len(headers) else f"R{i+1}")
    
    def set_col_headers(self, headers: List[str]):
        """Set column headers"""
        self.col_headers = headers
        if self.editable_headers:
            for j, entry in enumerate(self.col_header_entries):
                entry.delete(0, "end")
                entry.insert(0, headers[j] if j < len(headers) else f"C{j+1}")
    
    def clear(self):
        """Clear all cell values to default"""
        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[i][j].delete(0, "end")
                self.cells[i][j].insert(0, self.default_value)
    
    def get_cell(self, row: int, col: int) -> str:
        """Get value of a specific cell"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col].get()
        return ""
    
    def set_cell(self, row: int, col: int, value: str):
        """Set value of a specific cell"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.cells[row][col].delete(0, "end")
            self.cells[row][col].insert(0, value)
    
    def highlight_cell(self, row: int, col: int, color: str = "#4CAF50"):
        """Highlight a specific cell"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.cells[row][col].configure(fg_color=color)
    
    def clear_highlights(self):
        """Clear all cell highlights"""
        for i in range(self.rows):
            for j in range(self.cols):
                self.cells[row][col].configure(fg_color=("white", "gray20"))
    
    def resize(self, rows: int, cols: int):
        """Resize the matrix (recreates the widget)"""
        self.rows = rows
        self.cols = cols
        
        # Clear existing widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        self.cells = []
        self.row_header_entries = []
        self.col_header_entries = []
        
        # Update headers if needed
        if len(self.row_headers) < rows:
            self.row_headers.extend([f"R{i+1}" for i in range(len(self.row_headers), rows)])
        if len(self.col_headers) < cols:
            self.col_headers.extend([f"C{j+1}" for j in range(len(self.col_headers), cols)])
        
        # Recreate all widgets
        self._recreate_grid_widgets()


class VectorInput(ctk.CTkFrame):
    """
    A simple vector input widget for 1D data (supply, demand, etc.)
    """
    
    def __init__(
        self,
        parent,
        size: int = 10,
        labels: Optional[List[str]] = None,
        cell_width: int = 80,
        cell_height: int = 30,
        default_value: str = "0",
        orientation: str = "horizontal",  # or "vertical"
        title: str = "",
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        self.size = size
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.default_value = default_value
        self.orientation = orientation
        self.labels = labels or [f"V{i+1}" for i in range(size)]
        self.title = title
        
        self.entries: List[ctk.CTkEntry] = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the vector input widgets"""
        if self.title:
            title_label = ctk.CTkLabel(
                self,
                text=self.title,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            title_label.pack(pady=(5, 10))
        
        # Use ScrollableFrame for horizontal orientation (supports horizontal scrolling)
        if self.orientation == "horizontal":
            self.scroll_container = ScrollableFrame(
                self,
                width=min(700, self.size * (self.cell_width + 10)),
                height=self.cell_height * 2 + 50
            )
            self.scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
            container = self.scroll_container.get_inner_frame()
        else:
            # Use CTkScrollableFrame for vertical (only needs vertical scroll)
            container = ctk.CTkScrollableFrame(
                self,
                width=self.cell_width * 2 + 40,
                height=min(400, self.size * (self.cell_height + 8))
            )
            container.pack(fill="both", expand=True, padx=5, pady=5)
        
        for i in range(self.size):
            if self.orientation == "horizontal":
                col = i
                row = 0
            else:
                col = 0
                row = i
            
            # Label
            label = ctk.CTkLabel(
                container,
                text=self.labels[i][:10] if i < len(self.labels) else f"V{i+1}",
                width=self.cell_width,
                font=ctk.CTkFont(size=11)
            )
            
            if self.orientation == "horizontal":
                label.grid(row=0, column=col, padx=2, pady=2)
            else:
                label.grid(row=row, column=0, padx=2, pady=2, sticky="w")
            
            # Entry
            entry = ctk.CTkEntry(
                container,
                width=self.cell_width,
                height=self.cell_height,
                justify="center"
            )
            entry.insert(0, self.default_value)
            
            if self.orientation == "horizontal":
                entry.grid(row=1, column=col, padx=2, pady=2)
            else:
                entry.grid(row=row, column=1, padx=2, pady=2)
            
            self.entries.append(entry)
    
    def get_values(self) -> np.ndarray:
        """Get values as numpy array"""
        values = np.zeros(self.size)
        for i, entry in enumerate(self.entries):
            try:
                values[i] = float(entry.get())
            except ValueError:
                values[i] = 0.0
        return values
    
    def set_values(self, values: np.ndarray):
        """Set values from numpy array"""
        for i in range(min(len(values), self.size)):
            self.entries[i].delete(0, "end")
            self.entries[i].insert(0, str(values[i]))
    
    def clear(self):
        """Clear all values"""
        for entry in self.entries:
            entry.delete(0, "end")
            entry.insert(0, self.default_value)
