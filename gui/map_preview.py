import tkinter as tk
from tkinter import ttk, messagebox
from tkinterweb import HtmlFrame
import folium
import tempfile
import os
import logging
import webbrowser
from typing import Dict, List, Optional
import json
from utils.google_map_client import get_maps_client, GoogleMapsError

logger = logging.getLogger(__name__)
class MapPreview:
    def __init__(self, parent):
        """Initialize map preview window."""
        self.parent = parent
        self.maps_client = get_maps_client()
        self.window = None
        self.html_frame = None
        self.current_map_file = None

    def show_map(self, reference_address: str, selected_address: str, 
                all_addresses: List[Dict], max_time: float):
        """Show map with reference point, selected address, and other locations."""
        # Create new window if it doesn't exist or was closed
        if not self.window or not tk.Toplevel.winfo_exists(self.window):
            self.create_window()
        
        self.window.lift()  # Bring window to front
        self.window.focus_force()  # Force focus
        
        try:
            self.create_map(reference_address, selected_address, all_addresses, max_time)
        except Exception as e:
            logger.error(f"Error creating map: {str(e)}")
            raise

    def create_window(self):
        """Create the map preview window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Map Preview")
        self.window.geometry("800x600")

        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)

        # Create toolbar
        toolbar = ttk.Frame(self.window)
        toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        ttk.Button(
            toolbar, 
            text="Open in Browser",
            command=self.open_in_browser
        ).pack(side=tk.LEFT, padx=5)

        # Create HTML frame for map
        self.html_frame = HtmlFrame(self.window, messages_enabled=False)
        self.html_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

    def create_map(self, reference_address: str, selected_address: str, 
                all_addresses: List[Dict], max_time: float):
        """Create the map with all locations and routes."""
        try:
            # Get coordinates for reference location
            ref_result = self.maps_client.get_coordinates(reference_address)
            logger.debug(f"Reference coordinates result: {ref_result}")
            
            if ref_result['status'] != 'OK':
                raise ValueError(f"Could not find coordinates for reference address: {reference_address}")

            if ref_result['lat'] == 0 and ref_result['lng'] == 0:
                raise ValueError(f"Invalid coordinates for reference address: {reference_address}")

            # Create map centered on reference location
            m = folium.Map(
                location=[ref_result['lat'], ref_result['lng']],
                zoom_start=12,
                control_scale=True
            )

            # Add reference marker
            folium.Marker(
                [ref_result['lat'], ref_result['lng']],
                popup=f"Reference: {reference_address}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)

            # Initialize bounds with reference point
            bounds = [[ref_result['lat'], ref_result['lng']]]

            # Add selected address marker and route
            sel_result = self.maps_client.get_coordinates(selected_address)
            logger.debug(f"Selected address coordinates result: {sel_result}")
            
            if sel_result['status'] == 'OK' and sel_result['lat'] != 0 and sel_result['lng'] != 0:
                # Add marker for selected address
                selected_coords = [sel_result['lat'], sel_result['lng']]
                bounds.append(selected_coords)
                
                selected_addr_info = next(
                    (a for a in all_addresses if a['address'] == selected_address), 
                    None
                )
                
                popup_text = f"Selected: {selected_address}"
                if selected_addr_info:
                    if selected_addr_info.get('drive_time'):
                        popup_text += f"<br>Drive time: {selected_addr_info['drive_time']} min"
                    if selected_addr_info.get('distance'):
                        popup_text += f"<br>Distance: {selected_addr_info['distance']} miles"
                
                folium.Marker(
                    selected_coords,
                    popup=popup_text,
                    icon=folium.Icon(color='green', icon='info-sign')
                ).add_to(m)

                # Get and add route
                route = self.maps_client.get_route(reference_address, selected_address)

                if route['status'] == 'OK' and route['points']:
                    try:
                        # Validate route points
                        validated_points = []
                        for point in route['points']:
                            if isinstance(point, (list, tuple)) and len(point) == 2:
                                try:
                                    lat, lng = float(point[0]), float(point[1])
                                    validated_points.append([lat, lng])
                                except (ValueError, TypeError):
                                    continue

                        if validated_points:
                            folium.PolyLine(
                                validated_points,
                                weight=3,
                                color='blue',
                                opacity=0.8,
                                popup=f"Drive time: {route['duration_minutes']:.1f} min<br>"
                                    f"Distance: {route['distance_miles']:.1f} miles"
                            ).add_to(m)
                        else:
                            logger.warning("No valid route points found")
                            
                    except Exception as e:
                        logger.error(f"Error drawing route: {str(e)}")                
                if route['status'] == 'OK' and route.get('points'):
                    folium.PolyLine(
                        route['points'],
                        weight=3,
                        color='blue',
                        opacity=0.8,
                        popup=f"Drive time: {route['duration_minutes']} min<br>"
                            f"Distance: {route['distance_miles']} miles"
                    ).add_to(m)

            # Add other addresses
            for addr_data in all_addresses:
                addr = addr_data['address']
                if addr != selected_address:
                    coords = self.maps_client.get_coordinates(addr)
                    logger.debug(f"Other address coordinates result for {addr}: {coords}")
                    
                    if (coords['status'] == 'OK' and 
                        coords['lat'] != 0 and coords['lng'] != 0):
                        
                        addr_coords = [coords['lat'], coords['lng']]
                        bounds.append(addr_coords)
                        
                        # Determine marker color based on drive time
                        try:
                            drive_time = float(addr_data.get('drive_time', 0))
                            color = 'green' if drive_time <= max_time else 'red'
                        except (TypeError, ValueError):
                            color = 'gray'
                        
                        popup_text = f"Address: {addr}"
                        if addr_data.get('drive_time'):
                            popup_text += f"<br>Drive time: {addr_data['drive_time']} min"
                        if addr_data.get('distance'):
                            popup_text += f"<br>Distance: {addr_data['distance']} miles"
                        
                        folium.Marker(
                            addr_coords,
                            popup=popup_text,
                            icon=folium.Icon(color=color, icon='info-sign')
                        ).add_to(m)

            # Fit bounds if we have multiple points
            if len(bounds) > 1:
                m.fit_bounds(bounds)

            # Save and display map
            try:
                # Clean up previous map file
                if self.current_map_file and os.path.exists(self.current_map_file):
                    os.unlink(self.current_map_file)

                # Create new temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
                    m.save(tmp.name)
                    self.current_map_file = tmp.name
                    self.html_frame.load_file(tmp.name)

            except Exception as e:
                logger.error(f"Error saving or displaying map: {str(e)}")
                raise

        except Exception as e:
            logger.error(f"Error creating map: {str(e)}")
            raise

    def open_in_browser(self):
        """Open the current map in default web browser."""
        if self.current_map_file and os.path.exists(self.current_map_file):
            webbrowser.open(f'file://{self.current_map_file}')
        else:
            messagebox.showwarning(
                "No Map",
                "No map is currently displayed to open in browser."
            )

    def cleanup(self):
        """Clean up temporary files."""
        if self.current_map_file and os.path.exists(self.current_map_file):
            try:
                os.unlink(self.current_map_file)
            except Exception as e:
                logger.error(f"Error cleaning up map file: {str(e)}")