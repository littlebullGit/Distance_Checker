"""
Google Maps API client module for handling all interactions with Google Maps services.
"""

import googlemaps
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from .config import get_config
import time

logger = logging.getLogger(__name__)

class GoogleMapsError(Exception):
    """Custom exception for Google Maps API related errors."""
    pass

class GoogleMapsClient:
    """Client for interacting with Google Maps APIs."""
    
    def __init__(self):
        """Initialize Google Maps client with API key from config."""
        config = get_config()
        self.api_key = config.get('google_maps_api_key')
        self.max_retries = config.get('max_retries', 3)
        self.timeout = config.get('timeout', 10)
        
        try:
            self.client = googlemaps.Client(
                key=self.api_key,
                timeout=self.timeout,
                retry_over_query_limit=True,
                queries_per_second=10
            )
            logger.debug("Google Maps client initialized successfully")
        except Exception as e:
            raise GoogleMapsError(f"Failed to initialize Google Maps client: {str(e)}")

    def _handle_api_call(self, func, *args, **kwargs) -> Dict:
        """
        Handle API calls with retry logic and error handling.
        
        Args:
            func: Function to call
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Dict: API response
            
        Raises:
            GoogleMapsError: If API call fails after all retries
        """
        retries = 0
        while retries < self.max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries == self.max_retries:
                    raise GoogleMapsError(f"API call failed after {retries} retries: {str(e)}")
                logger.warning(f"API call failed (attempt {retries}), retrying...")
                time.sleep(1)  # Wait before retry

    def get_driving_time(
        self, 
        origin: str, 
        destination: str, 
        departure_time: Optional[datetime] = None
    ) -> Dict:
        """
        Get driving time and distance between two addresses.
        
        Args:
            origin (str): Starting address
            destination (str): Ending address
            departure_time (datetime, optional): Departure time for the journey
            
        Returns:
            Dict containing:
                - duration_minutes: Float, driving time in minutes
                - distance_km: Float, distance in kilometers
                - status: str, 'OK' or 'ERROR'
                - error_message: str, only present if status is 'ERROR'
        """
        try:
            result = self._handle_api_call(
                self.client.distance_matrix,
                origins=[origin],
                destinations=[destination],
                mode="driving",
                departure_time=departure_time or datetime.now(),
                traffic_model="best_guess"
            )

            if result['status'] != 'OK':
                raise GoogleMapsError(f"Distance Matrix API request failed with status: {result['status']}")

            element = result['rows'][0]['elements'][0]
            
            if element['status'] != 'OK':
                raise GoogleMapsError(f"Route calculation failed with status: {element['status']}")
            
            distance_meters = element['distance']['value']
            distance_km = distance_meters / 1000
            distance_miles = distance_km * 0.621371  # Convert km to miles
            
            return {
                'duration_minutes': element['duration']['value'] / 60,
                'distance_km': distance_km,
                'distance_miles': distance_miles,
                'status': 'OK'
            }
            
        except Exception as e:
            logger.error(f"Error getting driving time: {str(e)}")
            return {
                'duration_minutes': None,
                'distance_km': None,
                'distance_miles': None,
                'status': 'ERROR',
                'error_message': str(e)
            }

    def get_coordinates(self, address: str) -> Dict:
        """
        Get coordinates for an address using geocoding.
        
        Args:
            address (str): Address to geocode
            
        Returns:
            Dict containing:
                - lat: Float, latitude
                - lng: Float, longitude
                - formatted_address: str, formatted address
                - status: str, 'OK' or 'ERROR'
                - error_message: str, only present if status is 'ERROR'
        """
        try:
            # Add logging to debug the geocoding process
            logger.debug(f"Geocoding address: {address}")
            
            result = self._handle_api_call(self.client.geocode, address)
            
            if not result or len(result) == 0:
                logger.warning(f"No results found for address: {address}")
                return {
                    'lat': 0,
                    'lng': 0,
                    'formatted_address': None,
                    'status': 'ERROR',
                    'error_message': 'No results found'
                }
            
            # Log the raw result for debugging
            logger.debug(f"Geocoding result: {result}")
            
            location = result[0]['geometry']['location']
            formatted_address = result[0]['formatted_address']
            
            return {
                'lat': float(location['lat']),
                'lng': float(location['lng']),
                'formatted_address': formatted_address,
                'status': 'OK'
            }
            
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {str(e)}")
            return {
                'lat': 0,
                'lng': 0,
                'formatted_address': None,
                'status': 'ERROR',
                'error_message': str(e)
            }

    def get_route(self, origin: str, destination: str) -> Dict:
        """
        Get detailed route information between two addresses.
        
        Args:
            origin (str): Starting address
            destination (str): Ending address
            
        Returns:
            Dict containing:
                - points: List of [lat, lng] coordinates for the route
                - duration_minutes: Float, estimated duration
                - distance_km: Float, total distance
                - status: str, 'OK' or 'ERROR'
                - error_message: str, only present if status is 'ERROR'
        """
        try:
            result = self._handle_api_call(
                self.client.directions,
                origin,
                destination,
                mode="driving",
                departure_time=datetime.now()
            )

            if not result:
                logger.warning(f"No route found between {origin} and {destination}")
                return {
                    'points': [],
                    'duration_minutes': 0,
                    'distance_km': 0,
                    'distance_miles': 0,
                    'status': 'ERROR',
                    'error_message': 'No route found'
                }

            # Extract route points from the polyline
            route = result[0]
            points = []
            
            try:
                # Extract encoded polyline from overview_polyline
                overview_points = route['overview_polyline']['points']
                decoded_points = googlemaps.convert.decode_polyline(overview_points)
                # Convert to list of [lat, lng] coordinates
                points = [[point['lat'], point['lng']] for point in decoded_points]
            except Exception as e:
                logger.error(f"Error decoding route polyline: {str(e)}")
                points = []
            distance_meters = route['legs'][0]['distance']['value']
            distance_km = distance_meters / 1000
            distance_miles = distance_km * 0.621371
            return {
                'points': points,
                'duration_minutes': route['legs'][0]['duration']['value'] / 60,
                'distance_km': distance_km,
                'distance_miles': distance_miles,
                'status': 'OK'
            }
            
        except Exception as e:
            logger.error(f"Error getting route: {str(e)}")
        return {
            'points': [],
            'duration_minutes': 0,
            'distance_km': 0,
            'distance_miles': 0,
            'status': 'ERROR',
            'error_message': str(e)
        }

# Create a singleton instance
maps_client = GoogleMapsClient()

def get_maps_client() -> GoogleMapsClient:
    """
    Get Google Maps client instance.
    
    Returns:
        GoogleMapsClient: Singleton client instance
    """
    return maps_client