import PyInstaller.__main__
import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent

# Define the path to the main script
main_script = project_root / 'main.py'

# Create a template .env file for distribution
env_template = """# Google Maps API Configuration
GOOGLE_MAPS_API_KEY=your_api_key_here

# Application Settings
LOG_LEVEL=INFO
DEFAULT_REFERENCE_ADDRESS=
DEFAULT_MAX_TIME=15
"""

# Save the template .env file
with open(project_root / 'dist' / '.env.template', 'w') as f:
    f.write(env_template)

# Build the executable
PyInstaller.__main__.run([
    str(main_script),
    '--name=DistanceChecker',
    '--onefile',
    '--windowed',
    # f'--icon={icon_path}',  # Uncomment if you have an icon
    '--add-data=dist/.env.template;.',  # Include template instead of actual .env
    '--hidden-import=folium',
    '--hidden-import=tkinterweb',
    '--hidden-import=PIL',
    '--hidden-import=googlemaps',
    '--clean',
])