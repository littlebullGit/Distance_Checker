# Derek's Distance Checker

A Python application that helps you find driving distances and times between multiple locations using Google Maps API. Perfect for finding houses, businesses, or any locations within a specific driving time from a reference point.

## Features

- Check driving distances and times for multiple addresses
- Visual map preview of routes and locations (Not working yet)
- Export results to CSV
- Interactive GUI interface
- Bulk address input support

## Prerequisites

- Python 3.8 or higher
- Google Maps API key
- Internet connection

## Getting Google Maps API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs for your project:

   - Directions API

4. Create credentials:

   - In the Google Cloud Console, go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy your API key

5. (Optional but recommended) Restrict your API key:
   - In the credentials page, click on your API key
   - Under "Application restrictions", select "IP addresses" or "HTTP referrers"
   - Under "API restrictions", select the APIs you enabled above
   - Click "Save"

## Installation

1. Clone the repository:

```bash
git clone https://github.com/littlebullGit/Distance_Checker.git
cd Distance_Checker
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Create a .env file in the project root:

```bash
GOOGLE_MAPS_API_KEY=your_api_key_here
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT=10
```

## Usage

1. Start the application:

```bash
python main.py
```

2. Using command-line options:

```bash
# Run with debug logging
python main.py --log-level DEBUG

# Use custom .env file
python main.py --env /path/to/custom/.env
```

Pingry Address is:

```
131 Martinsville Rd, Basking Ridge, NJ 07920
```

3. Using the application:
   1. Enter your reference address
   2. Set maximum drive time in minutes
   3. Add addresses to check using one of these methods:
      - Click "Add" to enter addresses one by one
      - Click "Bulk Add" to paste multiple addresses at once
      - Import from a file using File > Import Addresses
   4. Click "Check Distances" to process
   5. Double-click any result to view on map (not working yet)
   6. Export results using the "Export" File menu

### Using Bulk Add Feature

The Bulk Add feature allows you to quickly add multiple addresses at once:

1. Click the "Bulk Add" button
2. Paste your addresses in the text area (one per line)
3. Empty lines will be automatically ignored
4. Click "Add Addresses" to add them to the list

Example format for bulk adding addresses:

```
1425 Frontier Rd, Bridgewater, NJ 08807
41 Mt Horeb Rd, Warren, NJ 07059
3 Old Farm Rd, Warren, NJ 07059
1931 Washington Valley Rd, Martinsville, NJ 08836
```

### Exported Results

Results are exported as CSV files with the following columns:

- Address: The checked address
- Drive Time (min): Driving time in minutes
- Distance (miles): Distance in miles
- Status: Within range/Out of range/Error

## Map Preview

The map preview feature shows:

- Reference location (red marker)
- Selected address (green marker)
- Route between reference and selected address
- Other addresses color-coded by status:
  - Green: Within specified drive time
  - Red: Outside specified drive time
- Distance and drive time information in popups

## Troubleshooting

1. API Key Issues:

   - Verify your API key is correctly set in the .env file
   - Check if the required APIs are enabled
   - Verify any API key restrictions

2. Address Not Found:

   - Ensure addresses are properly formatted
   - Include city and state/country
   - Check for typos

3. No Results:
   - Check your internet connection
   - Verify the reference address is valid
   - Ensure maximum drive time is reasonable

## Logging

Logs are stored in the `logs` directory with timestamps:

```
logs/distance_checker_YYYYMMDD_HHMMSS.log
```

Set logging level using the --log-level option:

```bash
python main.py --log-level DEBUG
```

## License

Derek Peng

## Acknowledgments

- Google Maps Platform for their APIs
- Folium for map visualization (TODO)
- All other open-source libraries used in this project
