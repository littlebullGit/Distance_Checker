"""
Main window module for the Distance Checker application.
"""

import tkinter as tk
# from tkinter import ttk, scrolledtext, messagebox
from tkinter import ttk, messagebox
from gui.widgets import AddressEntry, AddressListBox, TimeEntry, StatusBar
import logging
from typing import List, Dict
from datetime import datetime
import pandas as pd
from utils.google_map_client import get_maps_client, GoogleMapsError
from gui.map_preview import MapPreview

logger = logging.getLogger(__name__)

class MainWindow:
    """Main application window class."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the main window.
        
        Args:
            root: The root tkinter window
        """
        self.root = root
        self.root.title("Derek's Distance Checker")
        self.root.geometry("900x700")
        
        # Initialize Google Maps client
        self.maps_client = get_maps_client()
        
        # Store results for later use
        self.current_results = []
        
        # Store sort state
        self.sort_column = 'address'
        self.sort_reverse = False
        
        # Store filter state
        self.status_filters = {
            'Within range': tk.BooleanVar(value=True),
            'Out of range': tk.BooleanVar(value=True)
        }
        
        # Store all tree items
        self.all_tree_items = []
        
        self.create_widgets()
        self.create_menu()
        self.setup_styles()

    def setup_styles(self):
        """Configure ttk styles for the application."""
        style = ttk.Style()
        
        # Configure Treeview colors and fonts
        style.configure(
            "Treeview",
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground="#000000",
            rowheight=25
        )
        
        # Configure heading style
        style.configure(
            "Treeview.Heading",
            font=('Arial', 10, 'bold')
        )
        
        # Configure tag colors for in/out of range
        self.results_tree.tag_configure('in_range', background='#90EE90')  # Light green
        self.results_tree.tag_configure('out_range', background='#FFB6C1')  # Light red

    def create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Results...", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_widgets(self):
        """Create and setup all GUI widgets."""
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weight
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Create input section
        input_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=10)
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Reference address
        ttk.Label(
            input_frame,
            text="Reference Location:"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.reference_address = AddressEntry(
            input_frame,
            placeholder="Enter reference address (e.g., school address)..."
        )
        self.reference_address.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Maximum drive time
        self.max_time = TimeEntry(
            input_frame,
            label="Maximum Drive Time (minutes):",
            width=10
        )
        self.max_time.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        self.max_time.set(15)
        
        # Addresses to check
        ttk.Label(
            input_frame,
            text="Addresses to Check:"
        ).grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        self.address_list = AddressListBox(
            input_frame,
            height=8,
            width=70
        )
        self.address_list.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Action buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Check Distances",
            style="Action.TButton",
            command=self.check_distances
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Clear All",
            command=self.clear_all
        ).pack(side=tk.LEFT, padx=5)

        # Results section - Now properly placed after input section
        results_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=10)
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Results header with buttons and filters
        results_header = ttk.Frame(results_frame)
        results_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Left side - Title and filters
        header_left = ttk.Frame(results_header)
        header_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(
            header_left,
            text="Results:",
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT)
        
        # Status filter
        filter_frame = ttk.LabelFrame(header_left, text="Status Filter")
        filter_frame.pack(side=tk.LEFT, padx=20)
        
        for status, var in self.status_filters.items():
            ttk.Checkbutton(
                filter_frame,
                text=status,
                variable=var,
                command=self._apply_filters
            ).pack(side=tk.LEFT, padx=5)
        
        # Right side - Buttons
        header_right = ttk.Frame(results_header)
        header_right.pack(side=tk.RIGHT)
        
        ttk.Button(
            header_right,
            text="Show on Map",
            command=self.show_map
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            header_right,
            text="Export",
            command=self.export_results
        ).pack(side=tk.RIGHT, padx=5)

        # Results tree
        columns = ('address', 'drive_time', 'distance', 'status')
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show='headings',
            height=10
        )
        
        # Configure columns with sort bindings
        self.results_tree.heading('address', text='Address',
                                command=lambda: self._sort_results('address'))
        self.results_tree.heading('drive_time', text='Drive Time (min)',
                                command=lambda: self._sort_results('drive_time'))
        self.results_tree.heading('distance', text='Distance (miles)',
                                command=lambda: self._sort_results('distance'))
        self.results_tree.heading('status', text='Status',
                                command=lambda: self._sort_results('status'))
        
        self.results_tree.column('address', width=400)
        self.results_tree.column('drive_time', width=100)
        self.results_tree.column('distance', width=100)
        self.results_tree.column('status', width=100)

        # Add scrollbar for results
        results_scroll = ttk.Scrollbar(
            results_frame,
            orient=tk.VERTICAL,
            command=self.results_tree.yview
        )
        self.results_tree.configure(yscrollcommand=results_scroll.set)

        # Grid the results tree and scrollbar
        self.results_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))

        # Configure results frame grid weights
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)

        # Status bar at the bottom
        self.status_bar = StatusBar(main_frame)
        self.status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # Bind double-click event on results
        self.results_tree.bind('<Double-1>', lambda e: self.show_map())

    def _sort_results(self, column):
        """Sort results by the specified column."""
        # Toggle sort direction if clicking the same column
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Get all items
        items = [(self.results_tree.set(item, column), item) for item in self.results_tree.get_children('')]
        
        # Sort items
        items.sort(reverse=self.sort_reverse)
        if column in ['drive_time', 'distance']:
            # Sort numerically for numeric columns, handling '-' for error cases
            items.sort(
                key=lambda x: float(x[0]) if x[0] != '-' else float('inf'),
                reverse=self.sort_reverse
            )
        
        # Rearrange items in sorted order
        for index, (_, item) in enumerate(items):
            self.results_tree.move(item, '', index)
        
        # Update headings to show sort direction
        for col in ['address', 'drive_time', 'distance', 'status']:
            if col == column:
                direction = ' ↓' if self.sort_reverse else ' ↑'
            else:
                direction = ''
            self.results_tree.heading(col, text=self.results_tree.heading(col)['text'].rstrip(' ↑↓') + direction)

    def _apply_filters(self):
        """Apply status filters to the results."""
        # Remove all items from tree
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Add back items that match the filter
        for item_id, values in self.all_tree_items:
            status = values['status']
            if status == 'Error' or self.status_filters.get(status, tk.BooleanVar(value=True)).get():
                # Create new item with the same values
                self.results_tree.insert('', 'end', values=(
                    values['address'],
                    values['drive_time'],
                    values['distance'],
                    values['status']
                ), tags=('in_range' if status == 'Within range' else 'out_range',))
        
        # Maintain sort order after filtering
        self._sort_results(self.sort_column)

    def check_distances(self):
        """Process addresses and check distances."""
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Clear stored items
        self.all_tree_items = []
        
        # Get inputs
        reference = self.reference_address.get().strip()
        try:
            max_minutes = self.max_time.get()
        except ValueError:
            messagebox.showerror(
                "Error",
                "Please enter a valid number for maximum drive time!"
            )
            return

        addresses = self.address_list.get_addresses()

        if not reference or not addresses:
            messagebox.showerror(
                "Error",
                "Please enter both reference address and addresses to check!"
            )
            return

        self.current_results = []
        total = len(addresses)
        self.status_bar.start_progress(total)
        for i, address in enumerate(addresses, 1):
            self.status_bar.set_status(f"Processing address {i} of {total}...")
            self.status_bar.update_progress(i)
            self.root.update_idletasks()
            
            try:
                result = self.maps_client.get_driving_time(reference, address)
                
                if result['status'] == 'OK':
                    is_in_range = result['duration_minutes'] <= max_minutes
                    status = "Within range" if is_in_range else "Out of range"
                    tag = 'in_range' if is_in_range else 'out_range'
                    
                    # Store the result data
                    result_data = {
                        'address': address,
                        'drive_time': f"{result['duration_minutes']:.1f}",
                        'distance': f"{result['distance_miles']:.1f}",
                        'status': status
                    }
                    
                    # Only insert into tree if it matches current filters
                    if self.status_filters.get(status, tk.BooleanVar(value=True)).get():
                        item = self.results_tree.insert('', 'end', values=(
                            address,
                            f"{result['duration_minutes']:.1f}",
                            f"{result['distance_miles']:.1f}",
                            status
                        ), tags=(tag,))
                    else:
                        item = None
                    
                    # Store the item and its values (even if not displayed)
                    self.all_tree_items.append((item, result_data))
                    
                    self.current_results.append({
                        'address': address,
                        'duration': result['duration_minutes'],
                        'distance': result['distance_miles'],
                        'status': status
                    })
                else:
                    # Error results are always shown
                    item = self.results_tree.insert('', 'end', values=(
                        address,
                        '-',
                        '-',
                        'Error'
                    ))
                    
                    result_data = {
                        'address': address,
                        'drive_time': '-',
                        'distance': '-',
                        'status': 'Error'
                    }
                    
                    self.all_tree_items.append((item, result_data))
                    self.current_results.append({
                        'address': address,
                        'duration': None,
                        'distance': None,
                        'status': 'Error'
                    })
                    
            except Exception as e:
                logger.error(f"Error processing address {address}: {str(e)}")
                # Error results are always shown
                item = self.results_tree.insert('', 'end', values=(
                    address,
                    '-',
                    '-',
                    'Error'
                ))
                
                result_data = {
                    'address': address,
                    'drive_time': '-',
                    'distance': '-',
                    'status': 'Error'
                }
                
                self.all_tree_items.append((item, result_data))
                self.current_results.append({
                    'address': address,
                    'duration': None,
                    'distance': None,
                    'status': 'Error'
                })
                
        self.status_bar.stop_progress()
        self.status_bar.set_status("Processing complete!")
        
        # Apply current sort after all results are added
        self._sort_results(self.sort_column)

    def clear_all(self):
        """Clear all inputs and results."""
        self.reference_address.set("")  # Use set() instead of delete()
        self.max_time.set(15)
        self.address_list.set_addresses([])
        # Clear results tree
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Clear stored results
        self.current_results = []
        self.all_tree_items = []
        self.status_bar.set_status("")

    def show_map(self):
        """Show selected result on map."""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning(
                "No Selection",
                "Please select an address from the results to show on map."
            )
            return
        
        # Get selected address
        selected_item = self.results_tree.item(selection[0])
        selected_address = selected_item['values'][0]
        
        # Get reference address
        reference = self.reference_address.get().strip()
        if not reference:
            messagebox.showerror(
                "Error",
                "Reference address is missing!"
            )
            return
        
        # Get all addresses from results
        all_addresses = []
        for item in self.results_tree.get_children():
            item_data = self.results_tree.item(item)['values']
            if item_data[3] != 'Error':  # Only include addresses that were successfully processed
                all_addresses.append({
                    'address': item_data[0],
                    'drive_time': float(item_data[1]) if item_data[1] != '-' else None,
                    'distance': float(item_data[2]) if item_data[2] != '-' else None,
                    'status': item_data[3]
                })
        
        try:
            if not hasattr(self, 'map_preview'):
                self.map_preview = MapPreview(self.root)
                
            self.map_preview.show_map(
                reference_address=reference,
                selected_address=selected_address,
                all_addresses=all_addresses,
                max_time=self.max_time.get()
            )
        except Exception as e:
            logger.error(f"Error showing map: {str(e)}")
            messagebox.showerror(
                "Error",
                f"Failed to show map: {str(e)}"
            )

    def on_result_double_click(self, event):
        """Handle double-click on result item."""
        self.show_map()

    def export_results(self):
        """Export results to CSV file."""
        if not self.current_results:
            messagebox.showwarning(
                "No Results",
                "There are no results to export!"
            )
            return
        
        try:
            filename = tk.filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                df = pd.DataFrame(self.current_results)
                df.to_csv(filename, index=False)
                messagebox.showinfo(
                    "Success",
                    f"Results exported successfully to {filename}"
                )
                
        except Exception as e:
            logger.error(f"Error exporting results: {str(e)}")
            messagebox.showerror(
                "Error",
                f"Failed to export results: {str(e)}"
            )

    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About Distance Checker",
            "Distance Checker v1.0\n\n"
            "A tool for checking driving distances and times "
            "between multiple locations using Google Maps."
        )