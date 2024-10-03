# Geospatial Analysis of Tennessee Auto Repair Shops

# [Demo](https://leoncensh-tn.hf.space/) 
Welcome to **TN Auto Repair Shops Geospatial Analysis**! 🚀

![image](https://github.com/user-attachments/assets/7a79278b-d852-4ff3-8315-a20d374dbe71)

This is a Gradio web application that analyzes the distribution of auto repair and parts businesses across Tennessee. We create isochrones (drive-time polygons) for business locations using the OpenRouteService (ORS) API. 

## 🌟 Features

- **Population Insights**: Tennessee's population distribution from 2010 to 2020 with bar charts.
- **Business Mapping**: locations of auto repair and parts businesses like Autozone, Napa Auto Parts, O'Reilly, and more on a Folium map.
- **Isochrones Creation**: 15-minute driving isochrones around each auto location to understand accessibility and reach using the OpenRouteService API.
- **Geospatial Data Visualization**: maps with county boundaries, colored markers based on business types, and legends.
- **Custom Data Tables**: auto business locations, with names, addresses, and contact details.

## 📊 Datasets

- **`location-of-auto-businesses.csv`**: information about auto businesses, including types and geographic coordinates.
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

## Production

| **Directory/File**                | **Description**                                           |
|-----------------------------------|-----------------------------------------------------------|
| `TennesseeAutoDashboard/`         | Root folder of the project                                |
| `.vercel/`                        | Vercel-specific config directory (generated after setup)  |
| ├── `project.json`                | Vercel project configuration                             |
| └── `README.txt`                  | Vercel-generated README                                  |
| `public/`                         | Public assets (favicon, images, etc.)                     |
| ├── `favicon.ico`                 | Favicon file                                              |
| └── `other-assets`                | Other public assets                                       |
| `src/`                            | Source folder for the application                         |
| ├── `components/`                 | UI component folder                                       |
| │   ├── `ui/`                     | Contains reusable UI components                           |
| │   │   ├── `button.tsx`          | Button component                                          |
| │   │   ├── `card.tsx`            | Card component                                            |
| │   │   ├── `checkbox.tsx`        | Checkbox component                                        |
| │   │   ├── `scroll-area.tsx`     | Scroll area component                                     |
| │   │   ├── `tabs.tsx`            | Tabs components                                           |
| ├── `pages/`                      | Next.js routing folder                                    |
| │   ├── `api/`                    | Next.js API Routes (optional)                             |
| │   ├── `_app.tsx`                | App initialization (for global CSS, etc.)                 |
| │   └── `index.tsx`               | Home page or main entry point                             |
| ├── `styles/`                     | Global and Tailwind CSS styles                            |
| │   ├── `globals.css`             | Global styles (includes Tailwind imports)                 |
| │   └── `tailwind.css`            | TailwindCSS base styles (if necessary)                    |
| ├── `utils/`                      | Utility functions (if needed)                             |
| `.gitignore`                      | Git ignore rules                                          |
| `next.config.js`                  | Next.js configuration                                     |
| `package.json`                    | Node dependencies and scripts                             |
| `postcss.config.js`               | PostCSS configuration for Tailwind CSS                    |
| `tailwind.config.js`              | Tailwind CSS configuration                                |
| `tsconfig.json`                   | TypeScript configuration                                  |
| `README.md`                       | Project documentation                                     |
| `vercel.json`                     | Vercel configuration file (optional)                      |


## 📜 License

This project is licensed under the **MIT License**. 

## 🙏 Acknowledgements

Thank you to the creators and maintainers of **Gradio**, **Folium**, **Plotly**, and **OpenRouteService**. 
