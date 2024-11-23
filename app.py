# app.py

import math
import os
import logging
from typing import List, Tuple

import numpy as np
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import plotly.express as px
import gradio as gr
import hnswlib

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_csv(filepath: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError as e:
        logger.error(f"File not found: {filepath}")
        raise e


def load_shapefile(filepath: str, state_fp: str) -> gpd.GeoDataFrame:
    """Load and filter a shapefile by state FIPS code."""
    try:
        geo_data = gpd.read_file(filepath)
        if 'statefp' in geo_data.columns:
            geo_data = geo_data[geo_data['statefp'] == state_fp]
        elif 'STATEFP' in geo_data.columns:
            geo_data = geo_data[geo_data['STATEFP'] == state_fp]
        else:
            raise KeyError("State FIPS column not found in shapefile.")
        return geo_data
    except FileNotFoundError as e:
        logger.error(f"Shapefile not found: {filepath}")
        raise e
    except KeyError as e:
        logger.error(str(e))
        raise e


def define_business_types(df: pd.DataFrame) -> pd.DataFrame:
    """Define business types based on the business name."""
    conditions = [
        df['name'].str.contains("Autozone", case=False, na=False),
        df['name'].str.contains("Napa Auto Parts", case=False, na=False),
        df['name'].str.contains("Firestone Complete Auto Care", case=False, na=False),
        df['name'].str.contains("O'Reilly Auto Parts", case=False, na=False),
        df['name'].str.contains("Advance Auto Parts", case=False, na=False),
        df['name'].str.contains("Toyota|Honda|Kia|Nissan|Chevy|Ford|Carmax|GMC", case=False, na=False)
    ]
    choices = [
        "Autozone",
        "Napa Auto",
        "Firestone",
        "O'Reilly Auto",
        "Advance Auto",
        "Car Dealership"
    ]
    df['business_type'] = np.select(conditions, choices, default="Other Auto Repair Shops")
    return df


def merge_population_data(
    df_geo: pd.DataFrame,
    population_2020: dict
) -> pd.DataFrame:
    """Merge 2010 and 2020 population data."""
    df_population_2020 = pd.DataFrame(population_2020)
    df_population_2010 = (
        df_geo.groupby('cntyname')['pop10']
        .sum()
        .reset_index()
        .rename(columns={'cntyname': 'County', 'pop10': 'Population_2010'})
        .sort_values(by='Population_2010', ascending=False)
    )
    df_population_comparison = pd.merge(
        df_population_2010,
        df_population_2020,
        on='County'
    )
    return df_population_comparison


def prepare_hnswlib_index(df: pd.DataFrame) -> hnswlib.Index:
    """Prepare the hnswlib index for nearest neighbor search."""
    coordinates = df[['md_y', 'md_x']].to_numpy().astype('float32')
    num_elements = coordinates.shape[0]

    index = hnswlib.Index(space='l2', dim=2)
    index.init_index(max_elements=num_elements, ef_construction=200, M=16)
    index.add_items(coordinates, ids=df.index.values)
    index.set_ef(50)
    return index


def find_nearest_shops(df: pd.DataFrame, index: hnswlib.Index, shop_name: str, k: int = 5) -> Tuple[pd.DataFrame, np.ndarray]:
    """Find nearest shops using hnswlib."""
    selected_shop = df[df['name'] == shop_name].iloc[0]
    selected_coords = np.array([selected_shop['md_y'], selected_shop['md_x']], dtype='float32').reshape(1, -1)

    labels, distances = index.knn_query(selected_coords, k=k+1)
    neighbor_indices = labels[0]
    neighbor_distances = distances[0]

    if neighbor_indices[0] == selected_shop.name:
        neighbor_indices = neighbor_indices[1:]
        neighbor_distances = neighbor_distances[1:]
    else:
        neighbor_indices = neighbor_indices[neighbor_indices != selected_shop.name]
        neighbor_distances = neighbor_distances[1:]

    neighbor_shops = df.loc[neighbor_indices]
    return neighbor_shops, neighbor_distances


def create_map(
    geo_layer: str,
    business_filters: List[str],
    counties_geo: gpd.GeoDataFrame,
    hsa_geo: gpd.GeoDataFrame,
    hrr_geo: gpd.GeoDataFrame,
    df: pd.DataFrame
) -> str:
    """Create a Folium map with selected geographical boundaries and markers."""
    logger.info(f"Creating map with geo_layer: {geo_layer} and business_filters: {business_filters}")
    m = folium.Map(location=[35.8601, -86.6602], zoom_start=7)

    geo_data_map = {
        "Counties": counties_geo,
        "HSAs": hsa_geo,
        "HRRs": hrr_geo
    }

    try:
        geo_data = geo_data_map.get(geo_layer, counties_geo)
        folium.GeoJson(geo_data, name=geo_layer).add_to(m)
        logger.info(f"Geo layer {geo_layer} added to the map.")
    except Exception as e:
        logger.error(f"Error loading GeoData for {geo_layer}: {e}")

    marker_cluster = MarkerCluster().add_to(m)

    if "All" not in business_filters:
        filtered_df = df[df['business_type'].isin(business_filters)]
    else:
        filtered_df = df.copy()

    logger.info(f"Filtered {len(filtered_df)} businesses based on filters: {business_filters}")

    for _, row in filtered_df.iterrows():
        folium.Marker(
            location=[row['md_y'], row['md_x']],
            popup=(
                f"<b>{row['name']}</b><br>"
                f"{row.get('address', 'N/A')}, {row.get('city', 'N/A')}, TN {row.get('postal_code', 'N/A')}"
            ),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)

    folium.LayerControl().add_to(m)
    logger.info("Map creation completed.")
    return m._repr_html_()


def plot_population_comparison(df: pd.DataFrame) -> px.bar:
    """Create a side-by-side bar chart for 2010 and 2020 population."""
    df_melted = df.melt(
        id_vars='County',
        value_vars=['Population_2010', 'Population_2020'],
        var_name='Year',
        value_name='Population'
    )
    fig = px.bar(
        df_melted,
        x='County',
        y='Population',
        color='Year',
        barmode='group',
        title="Tennessee Population Comparison: 2010 vs 2020",
        labels={'County': 'County', 'Population': 'Population'},
        color_discrete_map={'Population_2010': 'purple', 'Population_2020': 'blue'}
    )
    fig.update_layout(xaxis={'categoryorder': 'total descending'}, template='plotly_white')
    return fig


def main():
    """Main function to launch the Gradio app."""
    # Load datasets
    df_businesses = load_csv("data/location-of-auto-businesses.csv")
    cbg_geographic_data = load_csv("data/cbg_geographic_data.csv")

    # Define business types
    df_businesses = define_business_types(df_businesses)

    # Merge population data
    population_2020 = {
        'County': [
            'Shelby', 'Davidson', 'Knox', 'Hamilton', 'Rutherford',
            'Williamson', 'Montgomery', 'Sumner', 'Blount', 'Washington',
            'Madison', 'Sevier', 'Maury', 'Wilson', 'Bradley'
        ],
        'Population_2020': [
            929744, 715884, 478971, 366207, 341486,
            247726, 220069, 196281, 135280, 133001,
            98823, 98380, 100974, 147737, 108620
        ]
    }
    df_population_comparison = merge_population_data(cbg_geographic_data, population_2020)

    # Load shapefiles
    counties_geo = load_shapefile("data/county/01_county-shape-file.shp", "47")
    hsa_geo = load_shapefile("data/hsa/01_hsa-shape-file.shp", "47")
    hrr_geo = load_shapefile("data/hrr/01_hrr-shape-file.shp", "47")

    # Prepare hnswlib index
    index = prepare_hnswlib_index(df_businesses)

    # Gradio Interface
    with gr.Blocks(theme=gr.themes.Default()) as app:
        gr.Markdown("# 🚗 Tennessee Auto Repair Businesses Dashboard")

        with gr.Tab("Overview"):
            gr.Markdown("## 📊 Tennessee Population Statistics")

            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 2010 vs 2020 Population Comparison")
                    pop_comp = gr.Plot(plot_population_comparison(df_population_comparison))

            gr.Markdown("### 🛠️ Auto Businesses in Tennessee")

            manual_table = gr.Dataframe(
                headers=["Location Name", "Street Address", "City", "State", "Postal Code"],
                datatype=["str", "str", "str", "str", "str"],
                value=[
                    # ... (table data)
                ],
                row_count=52,
                interactive=False
            )

            gr.Markdown("### 📍 Interactive Map")
            map_output_overview = gr.HTML(
                create_map(
                    geo_layer="Counties",
                    business_filters=["All"],
                    counties_geo=counties_geo,
                    hsa_geo=hsa_geo,
                    hrr_geo=hrr_geo,
                    df=df_businesses
                )
            )

        # Additional Tabs ...

        gr.Markdown("### 📄 Source: Yellow Pages")

    app.launch(server_name="0.0.0.0", server_port=7860, share=True)


if __name__ == "__main__":
    main()