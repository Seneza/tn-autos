# Tennessee Auto Businesses Dashboard 🚛

## [Demo](https://leoncensh-tn.hf.space)

An interactive web application built with Gradio that visualizes auto businesses and population data across Tennessee. This dashboard provides maps, charts, and data tables to explore the distribution of auto-related businesses and demographic information by county.

## Features

- **Interactive Maps**: Visualize the locations of various auto businesses across Tennessee with options to filter by zip code and business type.
- **Population Charts**: View bar charts displaying population distribution by county for the years 2010 and 2020.
- **Isochrone Maps**: Generate isochrone maps around AutoZone locations to visualize areas reachable within a specified driving time.
- **Data Tables**: Explore a curated list of auto repair and parts locations sourced from Yellowbook.

## [Demo](https://www.loom.com/share/b30b8ec1bba54365a15883b75133094d?sid=52075736-936a-42d9-a505-b20d533c39d9)

## Table of Contents

- [Features](## Features)
- [Demo](## [Demo](https://leoncensh-tn.hf.space))
- [Installation](## Installation)
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
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
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

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m 'Add YourFeature'
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```
5. **Open a Pull Request**

## What we use

- **OpenRouteService** to create 30 minutes isochrone.
- **Gradio** for the interactive web interface.
- **Folium and GeoPandas** for map rendering.
- **Plotly** for data visualization.
- **U.S. Census Bureau** for population data.

# Contact

For any questions or suggestions, please open an issue or contact [nshutl0@sewanee.edu](mailto:nshutl0@sewanee.edu).

## License

This project is licensed under the [MIT License](LICENSE).


