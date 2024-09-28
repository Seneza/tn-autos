# Kora Customer Map Analysis

# [Demo](https://leoncensh-tn.hf.space/) 
Welcome to **Kora Customer Map Analysis**! 🚀

Discover the power of data visualization with our Gradio web application that analyzes the distribution of auto repair and parts businesses across Tennessee. Dive deep into population trends and explore interactive maps that bring your data to life. We create isochrones (drive-time polygons) for business locations using the OpenRouteService (ORS) API. 

## 🌟 Features

- **Population Insights**: Tennessee's population distribution from 2010 to 2020 with bar charts.
- **Business Mapping**: locations of auto repair and parts businesses like Autozone, Napa Auto Parts, O'Reilly, and more on a Folium map.
- **Isochrones Creation**: 15-minute driving isochrones around each auto location to understand accessibility and reach using the OpenRouteService API.
- **Geospatial Data Visualization**: maps with county boundaries, colored markers based on business types, and legends.
- **Custom Data Tables**: auto business locations, with names, addresses, and contact details.

## 📊 Datasets

- **`location-of-auto-businesses.csv`**: information about auto businesses, including types and geographic coordinates.
- **`cbg_geographic_data.csv`**: Population and land data segmented by census block groups (CBG).
- **`county-shape-file.shp`**: Shapefile containing the geographic boundaries of Tennessee counties.

## 🛠️ Requirements

- `gradio`
- `pandas`
- `plotly`
- `folium`
- `numpy`
- `geopandas`
- `branca`
- `openrouteservice`

```bash
pip install gradio pandas plotly folium numpy geopandas branca openrouteservice
```

**Note**: To use the isochrone features, you'll need an API key from OpenRouteService (ORS). Sign up at [ORS Signup](https://openrouteservice.org/sign-up/)

## 🚀 Getting Started

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/kora-customer-map-analysis.git
    cd kora-customer-map-analysis
    ```

2. **Configure the ORS API Key**:
    - Create a `.env` file in the root directory:
      ```bash
      echo "ors=your_openrouteservice_api_key" > .env
      ```
    - Replace `your_openrouteservice_api_key` with the API key you obtained from ORS.

3. **Launch the Application**:
    ```bash
    python app.py
    ```

4. **Explore the App**:
    Open your web browser to [http://localhost:7860](http://localhost:7860) to start exploring!

## 🖥️ Application Interface

- **Overview Tab**:
  - **Population Distribution**: Tennessee's population in 2010 and 2020 with bar charts.
  - **Auto Repair & Parts Visualization**: location of auto businesses across the state.
  - **Business Locations Table**: table of auto repair and parts business locations.

- **Tennessee Businesses by County Tab**:
  - **Geospatial Insights**: businesses categorized by county with dynamic markers and county boundaries.

## 📜 License

This project is licensed under the **MIT License**. 

## 🙏 Acknowledgements

Thank you to the creators and maintainers of **Gradio**, **Folium**, **Plotly**, and **OpenRouteService**. 
