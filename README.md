# Tennessee Auto Businesses Networks 🚛

![image](https://github.com/user-attachments/assets/fb8019a6-976b-4bdb-89fa-22e91b7ac7df)

## [Demo](https://www.loom.com/share/a2e4bd7ae5ef439a91f8d86ac027278f?sid=4cf7a528-9edd-4382-9817-4a020486ab4c)

Interactive web application built with Gradio to visualize auto businesses and population data across Tennessee. This application provides **maps**, **charts**, and **data tables** to explore **the distribution of auto-related businesses and demographic information by county, healthcare referral regions(HRRs) and HSAs**.

## Features

- **Interactive Maps**: Visualize the locations of various auto businesses across Tennessee with options to filter by zip code and business type.
- **Population Charts**: View bar charts displaying population distribution by county for the years 2010 and 2020.
- **Isochrone Maps**: Generate isochrone maps around AutoZone locations to visualize areas reachable within a specified driving time.
- **Data Tables**: Explore a curated list of auto repair and parts locations sourced from Yellowbook.

## Table of Contents

- [Features](#Features)
- [Demo](#Demo)
- [Installation](#Installation)
- [Data Sources](#data-sources)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.11 or higher
- An OpenRouteService API key (for isochrone map generation)

### Clone the Repository

```bash
git clone https://github.com/LNshuti/tn-autos.git
cd tn-autos
```

### Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

**Requirements.txt**

```
branca
folium
geopandas
gradio
numpy
openrouteservice
pandas
plotly
```

## Data Sources

- **Business Locations**: Custom dataset containing locations of auto businesses in Tennessee.
- **Population Data**: U.S. Census Bureau datasets for county-level population statistics.
- **Geographic Data**: Shapefiles for Tennessee counties to render geographic boundaries on maps.

## Usage

### Run the Application

```bash
python app.py
```
The application will launch and provide a local URL `http://127.0.0.1:7860` to interact with the dashboard.

### Application Overview

- **Overview Tab**:
  - *Tennessee Population 2010*: Displays a bar chart of the 2010 population by county.
  - *Auto Repair/Parts in Tennessee*: Shows a data table of selected auto businesses.
  - *Map Output*: Interactive map displaying business locations with markers color-coded by business type.

- **Tennessee Businesses by County Tab**:
  - *Filters*: Dropdown menus to select a specific zip code and business type.
  - *Map Output*: Updates interactively based on selected filters to display relevant businesses on the map.

## Configuration

### OpenRouteService API Key

To enable isochrone map functionality, you need an API key from OpenRouteService.

1. **Obtain an API Key**: Sign up at [OpenRouteService](https://openrouteservice.org/dev/#/signup) and obtain an API key.
2. **Set the API Key as an Environment Variable**:

   ```bash
   export ORS_API_KEY='your-api-key-here'  # On Windows, use `set ORS_API_KEY=your-api-key-here`
   ```

   Alternatively, you can create a `.env` file in the project root:

   ```
   ORS_API_KEY=your-api-key-here
   ```

### Adjusting Map Settings

- **Default Location**: The map centers on Tennessee coordinates `[35.8601, -86.6602]` with a default zoom level of 8. You can adjust these settings in the `create_map` function within `app.py`.

## Stack

- **OpenRouteService** to create 30 minutes isochrone.
- **Gradio** for the interactive web interface.
- **Folium and GeoPandas** for map rendering.
- **Plotly** for data visualization.
- **U.S. Census Bureau** for population data.

# Contact

For any questions or suggestions, please open an issue or contact [nshutl0@sewanee.edu](mailto:nshutl0@sewanee.edu).

## License

This project is licensed under the [MIT License](LICENSE).


