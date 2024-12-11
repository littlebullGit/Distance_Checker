"""
Main entry point for the Distance Checker application.
"""

import tkinter as tk
import sys
import logging
from pathlib import Path
from datetime import datetime
import argparse

from gui.main_window import MainWindow
from utils.config import get_config, ConfigurationError

def setup_logging(log_level: str = 'INFO') -> None:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level (default: INFO)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'distance_checker_{timestamp}.log'
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Distance Checker Application')
    parser.add_argument(
        '--env',
        help='Path to .env file',
        default=None
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level'
    )
    
    return parser.parse_args()

def main():
    """Main application entry point."""
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Setup logging
        setup_logging(args.log_level)
        logger = logging.getLogger(__name__)
        logger.info("Starting Distance Checker application")
        
        # Initialize configuration
        try:
            config = get_config()
            logger.debug("Configuration loaded successfully")
        except ConfigurationError as e:
            logger.error(f"Configuration error: {str(e)}")
            sys.exit(1)
        
        # Create the main window
        root = tk.Tk()
        root.title("Derek's Distance Checker")
        
        # Set window icon (if available)
        try:
            icon_path = Path(__file__).parent / 'resources' / 'icon.ico'
            if icon_path.exists():
                root.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"Could not load application icon: {str(e)}")
        
        # Configure window style
        root.configure(bg='#f0f0f0')
        
        # Create main application window
        app = MainWindow(root)
        
        # Center the window on screen
        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Calculate position
        window_width = 900
        window_height = 700
        position_top = int(screen_height/2 - window_height/2)
        position_right = int(screen_width/2 - window_width/2)
        
        # Set window size and position
        root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        
        # Set minimum window size
        root.minsize(800, 600)
        
        # Handle window close
        def on_closing():
            """Handle window closing event."""
            if hasattr(app, 'cleanup'):
                app.cleanup()
            root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the application
        logger.info("Application GUI initialized, starting main loop")
        root.mainloop()
        
    except Exception as e:
        logger.exception("Unexpected error occurred")
        sys.exit(1)
    finally:
        logger.info("Application shutting down")

if __name__ == "__main__":
    main()