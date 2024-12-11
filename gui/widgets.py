"""
Custom widgets for the Distance Checker application.
"""

import tkinter as tk
from tkinter import ttk
import re
from typing import Callable, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AddressEntry(ttk.Frame):
    def __init__(self, master, placeholder: str = "Enter address...", width: int = 60, **kwargs):
        super().__init__(master, **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_color = 'gray'
        self.default_color = 'black'
        
        # Create entry widget
        self.entry = ttk.Entry(self, width=width)
        self.entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        
        # Initialize with placeholder
        self._show_placeholder()

    def delete(self, first, last):
        """Delete characters from entry widget."""
        self.entry.delete(first, last)
        self._show_placeholder()

    def insert(self, index, string):
        """Insert string into entry widget."""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(foreground=self.default_color)
        self.entry.insert(index, string)

    def get(self) -> str:
        """Get the current value, excluding placeholder."""
        value = self.entry.get()
        return '' if value == self.placeholder else value

    def set(self, value: str):
        """Set the entry value."""
        self.entry.delete(0, tk.END)
        if value:
            self.entry.insert(0, value)
            self.entry.config(foreground=self.default_color)
        else:
            self._show_placeholder()

    def _show_placeholder(self):
        """Show placeholder text if entry is empty."""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(foreground=self.placeholder_color)

    def _hide_placeholder(self):
        """Hide placeholder text when entry gets focus."""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(foreground=self.default_color)

    def _on_focus_in(self, event):
        """Handle focus in event."""
        self._hide_placeholder()

    def _on_focus_out(self, event):
        """Handle focus out event."""
        self._show_placeholder()

class AddressListBox(ttk.Frame):
    """Custom widget for managing a list of addresses."""
    
    def __init__(
        self,
        master,
        height: int = 10,
        width: int = 60,
        **kwargs
    ):
        """
        Initialize the address list box.
        
        Args:
            master: Parent widget
            height (int): Number of visible lines
            width (int): Widget width
            **kwargs: Additional arguments for Frame
        """
        super().__init__(master, **kwargs)
        
        # Create main listbox
        self.listbox = tk.Listbox(
            self,
            height=height,
            width=width,
            selectmode=tk.EXTENDED
        )
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.listbox.yview
        )
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        # Create buttons
        button_frame = ttk.Frame(self)
        ttk.Button(
            button_frame,
            text="Add",
            command=self._add_address
        ).pack(side=tk.LEFT, padx=2)
 
        ttk.Button(
            button_frame,
            text="Bulk Add",  # Add this button
            command=self._bulk_add_addresses
        ).pack(side=tk.LEFT, padx=2)
                
        ttk.Button(
            button_frame,
            text="Remove",
            command=self._remove_selected
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            button_frame,
            text="Clear",
            command=self._clear_all
        ).pack(side=tk.LEFT, padx=2)
        
        # Layout widgets
        self.listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        button_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)

    def _add_address(self):
        """Show dialog to add new address."""
        dialog = AddressInputDialog(self)
        if dialog.result:
            # Check for duplicates before adding
            if dialog.result not in self.get_addresses():
                self.listbox.insert(tk.END, dialog.result)

    def _bulk_add_addresses(self):
        """Show dialog to add multiple addresses at once."""
        dialog = BulkAddressDialog(self)
        if dialog.result:
            # Get current addresses for duplicate checking
            current_addresses = self.get_addresses()
            # Add only non-duplicate addresses
            for addr in dialog.result:
                if addr not in current_addresses:
                    self.listbox.insert(tk.END, addr)

    def _remove_selected(self):
        """Remove selected addresses."""
        selection = self.listbox.curselection()
        for index in reversed(selection):
            self.listbox.delete(index)

    def _clear_all(self):
        """Clear all addresses."""
        self.listbox.delete(0, tk.END)

    def get_addresses(self) -> List[str]:
        """Get list of all addresses."""
        return list(self.listbox.get(0, tk.END))

    def set_addresses(self, addresses: List[str]):
        """Set the list of addresses."""
        self.listbox.delete(0, tk.END)
        for addr in addresses:
            self.listbox.insert(tk.END, addr)

class AddressInputDialog(tk.Toplevel):
    """Dialog for entering a new address."""
    
    def __init__(self, parent):
        """Initialize the dialog."""
        super().__init__(parent)
        self.title("Add Address")
        self.result = None
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create widgets
        ttk.Label(self, text="Enter address:").grid(
            row=0, column=0, padx=5, pady=5
        )
        
        self.entry = AddressEntry(self, width=50)
        self.entry.grid(row=1, column=0, padx=5, pady=5)
        
        button_frame = ttk.Frame(self)
        ttk.Button(
            button_frame,
            text="OK",
            command=self._on_ok
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        ).pack(side=tk.LEFT, padx=5)
        
        button_frame.grid(row=2, column=0, pady=10)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Center the dialog
        self.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Set focus
        self.entry.entry.focus_set()
        
        # Wait for window to be destroyed
        self.wait_window(self)

    def _on_ok(self):
        """Handle OK button click."""
        value = self.entry.get().strip()
        if value:
            self.result = value
            self.destroy()
        else:
            tk.messagebox.showwarning(
                "Invalid Input",
                "Please enter an address."
            )

    def _on_cancel(self):
        """Handle Cancel button click."""
        self.destroy()

class StatusBar(ttk.Frame):
    """Status bar widget with progress indicator."""
    
    def __init__(self, master, **kwargs):
        """Initialize the status bar."""
        super().__init__(master, **kwargs)
        
        # Create status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            padding=(5, 2)
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create progress bar
        self.progress = ttk.Progressbar(
            self,
            mode='determinate',
            length=100
        )
        self.progress.pack(side=tk.RIGHT, padx=5)
        
        # Hide progress bar initially
        self.progress.pack_forget()

    def set_status(self, message: str):
        """Set status message."""
        self.status_var.set(message)

    def start_progress(self, maximum: int = 100):
        """Start progress indication."""
        self.progress['maximum'] = maximum
        self.progress['value'] = 0
        self.progress.pack(side=tk.RIGHT, padx=5)

    def update_progress(self, value: int):
        """Update progress value."""
        self.progress['value'] = value

    def stop_progress(self):
        """Stop progress indication."""
        self.progress.pack_forget()

class TimeEntry(ttk.Frame):
    """Custom widget for entering time values with validation."""
    
    def __init__(
        self,
        master,
        label: str = "Time:",
        width: int = 10,
        **kwargs
    ):
        """Initialize the time entry widget."""
        super().__init__(master, **kwargs)
        
        # Create label
        if label:
            self.label = ttk.Label(self, text=label)
            self.label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Create entry with validation
        vcmd = (self.register(self._validate), '%P')
        self.entry = ttk.Entry(
            self,
            width=width,
            validate='key',
            validatecommand=vcmd
        )
        self.entry.pack(side=tk.LEFT)

    def _validate(self, new_value: str) -> bool:
        """Validate entry value."""
        if not new_value:
            return True
        try:
            value = float(new_value)
            return value >= 0
        except ValueError:
            return False

    def get(self) -> Optional[float]:
        """Get the current value."""
        try:
            return float(self.entry.get())
        except ValueError:
            return None

    def set(self, value: float):
        """Set the entry value."""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(value))

class BulkAddressDialog(tk.Toplevel):
    """Dialog for entering multiple addresses at once."""
    
    def __init__(self, parent):
        """Initialize the dialog."""
        super().__init__(parent)
        self.title("Bulk Add Addresses")
        self.result = None
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Set dialog size
        self.geometry("600x400")
        
        # Create widgets
        self.create_widgets()
        
        # Center the dialog
        self.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Wait for window to be destroyed
        self.wait_window(self)

    def create_widgets(self):
        """Create dialog widgets."""
        # Create main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Add instruction label
        ttk.Label(
            main_frame,
            text="Paste addresses below (one per line):",
            wraplength=550
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Add text area
        self.text_area = tk.Text(
            main_frame,
            width=60,
            height=20,
            wrap=tk.WORD
        )
        self.text_area.grid(
            row=1, column=0, columnspan=2, 
            sticky=(tk.W, tk.E, tk.N, tk.S),
            pady=(0, 10)
        )
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            main_frame,
            orient=tk.VERTICAL,
            command=self.text_area.yview
        )
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        # Add buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Add Addresses",
            command=self._on_ok
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        ).pack(side=tk.LEFT, padx=5)
        
        # Set focus to text area
        self.text_area.focus_set()

    def _on_ok(self):
        """Handle OK button click."""
        text = self.text_area.get("1.0", tk.END)
        # Split text into lines and filter out empty lines
        addresses = [
            addr.strip() 
            for addr in text.split('\n') 
            if addr.strip()
        ]
        
        if addresses:
            self.result = addresses
            self.destroy()
        else:
            tk.messagebox.showwarning(
                "No Addresses",
                "Please enter at least one address."
            )

    def _on_cancel(self):
        """Handle Cancel button click."""
        self.destroy()