"""Interactive map of transportation businesses in Tennessee."""
# app.py

import logging
import math
import os
from typing import List, Tuple

import folium
import geopandas as gpd
import gradio as gr
import hnswlib
import numpy as np
import pandas as pd
import plotly.express as px
from folium.plugins import MarkerCluster

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_csv(filepath: str) -> pd.DataFrame:
    """
    Load a CSV file into a Pandas DataFrame.

    Parameters:
        filepath (str): The path to the CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the loaded data.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError as e:
        logger.error(f"File not found: {filepath}")
        raise e


def load_shapefile(filepath: str, state_fp: str) -> gpd.GeoDataFrame:
    """
    Load a shapefile and filter it by the provided state FIPS code.

    Parameters:
        filepath (str): The path to the shapefile.
        state_fp (str): The FIPS code of the state to filter by.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing the filtered geographic data.

    Raises:
        FileNotFoundError: If the shapefile does not exist.
        KeyError: If the state FIPS column is not found in the shapefile.
    """
    try:
        geo_data = gpd.read_file(filepath)
        if "statefp" in geo_data.columns:
            geo_data = geo_data[geo_data["statefp"] == state_fp]
        elif "STATEFP" in geo_data.columns:
            geo_data = geo_data[geo_data["STATEFP"] == state_fp]
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
    """
    Categorize businesses based on their names into predefined business types.

    Parameters:
        df (pd.DataFrame): DataFrame containing business information with a 'name' column.

    Returns:
        pd.DataFrame: The original DataFrame with an additional 'business_type' column.
    """
    conditions = [
        df["name"].str.contains("Autozone", case=False, na=False),
        df["name"].str.contains("Napa Auto Parts", case=False, na=False),
        df["name"].str.contains("Firestone Complete Auto Care", case=False, na=False),
        df["name"].str.contains("O'Reilly Auto Parts", case=False, na=False),
        df["name"].str.contains("Advance Auto Parts", case=False, na=False),
        df["name"].str.contains(
            "Toyota|Honda|Kia|Nissan|Chevy|Ford|Carmax|GMC", case=False, na=False
        ),
    ]
    choices = [
        "Autozone",
        "Napa Auto",
        "Firestone",
        "O'Reilly Auto",
        "Advance Auto",
        "Car Dealership",
    ]
    df["business_type"] = np.select(
        conditions, choices, default="Other Auto Repair Shops"
    )
    return df


def merge_population_data(df_geo: pd.DataFrame, population_2020: dict) -> pd.DataFrame:
    """
    Merge population data from 2010 and 2020 based on county names.

    Parameters:
        df_geo (pd.DataFrame): GeoDataFrame containing geographic information with 'cntyname' and 'pop10' columns.
        population_2020 (dict): Dictionary containing 2020 population data with 'County' and 'Population_2020' keys.

    Returns:
        pd.DataFrame: A merged DataFrame comparing populations from 2010 and 2020.
    """
    df_population_2020 = pd.DataFrame(population_2020)
    df_population_2010 = (
        df_geo.groupby("cntyname")["pop10"]
        .sum()
        .reset_index()
        .rename(columns={"cntyname": "County", "pop10": "Population_2010"})
        .sort_values(by="Population_2010", ascending=False)
    )
    df_population_comparison = pd.merge(
        df_population_2010, df_population_2020, on="County"
    )
    return df_population_comparison


def prepare_hnswlib_index(df: pd.DataFrame) -> hnswlib.Index:
    """
    Initialize and prepare an hnswlib index for efficient nearest neighbor searches.

    Parameters:
        df (pd.DataFrame): DataFrame containing business locations with 'md_y' and 'md_x' columns.

    Returns:
        hnswlib.Index: An initialized hnswlib index populated with business coordinates.
    """
    coordinates = df[["md_y", "md_x"]].to_numpy().astype("float32")
    num_elements = coordinates.shape[0]

    index = hnswlib.Index(space="l2", dim=2)
    index.init_index(max_elements=num_elements, ef_construction=200, M=16)
    index.add_items(coordinates, ids=df.index.values)
    index.set_ef(50)
    return index


def find_nearest_shops(
    df: pd.DataFrame, index: hnswlib.Index, shop_name: str, k: int = 5
) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Identify the nearest auto shops to a selected shop using hnswlib.

    Parameters:
        df (pd.DataFrame): DataFrame containing business information.
        index (hnswlib.Index): An hnswlib index for nearest neighbor search.
        shop_name (str): The name of the shop to find neighbors for.
        k (int, optional): Number of nearest neighbors to retrieve. Defaults to 5.

    Returns:
        Tuple[pd.DataFrame, np.ndarray]: A tuple containing a DataFrame of neighboring shops and their distances.

    Raises:
        ValueError: If the specified shop is not found in the dataset.
    """
    selected_shops = df[df["name"] == shop_name]
    if selected_shops.empty:
        logger.error(f"Shop '{shop_name}' not found in the dataset.")
        raise ValueError(f"Shop '{shop_name}' not found.")

    selected_shop = selected_shops.iloc[0]
    selected_coords = np.array(
        [selected_shop["md_y"], selected_shop["md_x"]], dtype="float32"
    ).reshape(1, -1)

    labels, distances = index.knn_query(selected_coords, k=k + 1)
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
    df: pd.DataFrame,
) -> str:
    """
    Generate an interactive Folium map with specified geographic layers and business filters.

    Parameters:
        geo_layer (str): The geographic layer to display ('Counties', 'HSAs', 'HRRs').
        business_filters (List[str]): List of business types to filter on.
        counties_geo (gpd.GeoDataFrame): GeoDataFrame for counties.
        hsa_geo (gpd.GeoDataFrame): GeoDataFrame for HSAs.
        hrr_geo (gpd.GeoDataFrame): GeoDataFrame for HRRs.
        df (pd.DataFrame): DataFrame containing business information.

    Returns:
        str: HTML representation of the generated Folium map.
    """
    logger.info(
        f"Creating map with geo_layer: {geo_layer} and business_filters: {business_filters}"
    )
    m = folium.Map(location=[35.8601, -86.6602], zoom_start=7)

    geo_data_map = {"Counties": counties_geo, "HSAs": hsa_geo, "HRRs": hrr_geo}

    try:
        geo_data = geo_data_map.get(geo_layer, counties_geo)
        folium.GeoJson(geo_data, name=geo_layer).add_to(m)
        logger.info(f"Geo layer {geo_layer} added to the map.")
    except Exception as e:
        logger.error(f"Error loading GeoData for {geo_layer}: {e}")

    marker_cluster = MarkerCluster().add_to(m)

    if "All" not in business_filters:
        filtered_df = df[df["business_type"].isin(business_filters)]
    else:
        filtered_df = df.copy()

    logger.info(
        f"Filtered {len(filtered_df)} businesses based on filters: {business_filters}"
    )

    for _, row in filtered_df.iterrows():
        folium.Marker(
            location=[row["md_y"], row["md_x"]],
            popup=(
                f"<b>{row['name']}</b><br>"
                f"{row.get('address', 'N/A')}, {row.get('city', 'N/A')}, TN {row.get('postal_code', 'N/A')}"
            ),
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(marker_cluster)

    folium.LayerControl().add_to(m)
    logger.info("Map creation completed.")
    return m._repr_html_()


def plot_population_comparison(df: pd.DataFrame) -> px.bar:
    """
    Create a side-by-side bar chart comparing 2010 and 2020 population data.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'County', 'Population_2010', and 'Population_2020' columns.

    Returns:
        px.bar: A Plotly Express bar chart object.
    """
    df_melted = df.melt(
        id_vars="County",
        value_vars=["Population_2010", "Population_2020"],
        var_name="Year",
        value_name="Population",
    )
    fig = px.bar(
        df_melted,
        x="County",
        y="Population",
        color="Year",
        barmode="group",
        title="Tennessee Population Comparison: 2010 vs 2020",
        labels={"County": "County", "Population": "Population"},
        color_discrete_map={"Population_2010": "purple", "Population_2020": "blue"},
    )
    fig.update_layout(
        xaxis={"categoryorder": "total descending"}, template="plotly_white"
    )
    return fig


def create_app() -> gr.Blocks:
    """
    Construct and configure the Gradio application interface.

    This function loads necessary datasets, prepares data for visualization,
    and sets up various interactive tabs within the Gradio dashboard.

    Returns:
        gr.Blocks: The configured Gradio Blocks interface.
    """
    # Load datasets
    df_businesses = load_csv("data/location-of-auto-businesses.csv")
    cbg_geographic_data = load_csv("data/cbg_geographic_data.csv")

    # Define business types
    df_businesses = define_business_types(df_businesses)

    # Merge population data
    population_2020 = {
        "County": [
            "Shelby",
            "Davidson",
            "Knox",
            "Hamilton",
            "Rutherford",
            "Williamson",
            "Montgomery",
            "Sumner",
            "Blount",
            "Washington",
            "Madison",
            "Sevier",
            "Maury",
            "Wilson",
            "Bradley",
        ],
        "Population_2020": [
            929744,
            715884,
            478971,
            366207,
            341486,
            247726,
            220069,
            196281,
            135280,
            133001,
            98823,
            98380,
            100974,
            147737,
            108620,
        ],
    }
    df_population_comparison = merge_population_data(
        cbg_geographic_data, population_2020
    )

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
                    gr.Plot(plot_population_comparison(df_population_comparison))

            gr.Markdown("### 🛠️ Auto Businesses in Tennessee")

            gr.Dataframe(
                headers=[
                    "Location Name",
                    "Street Address",
                    "City",
                    "State",
                    "Postal Code",
                ],
                datatype=["str", "str", "str", "str", "str"],
                value=[
                    [
                        "AutoZone Auto Parts - Nashville #2080",
                        "100 Donelson Pike",
                        "Nashville",
                        "Tennessee",
                        "37214",
                    ],
                    [
                        "AutoZone Auto Parts - Nashville #3597",
                        "1007 Murfreesboro Pike",
                        "Nashville",
                        "Tennessee",
                        "37217",
                    ],
                    # ... (remaining rows omitted for brevity)
                ],
                row_count=52,  # Updated for the total number of rows
                interactive=False,
            )

            gr.Markdown("### 📍 Interactive Map")
            gr.HTML(
                create_map(
                    geo_layer="Counties",
                    business_filters=["All"],
                    counties_geo=counties_geo,
                    hsa_geo=hsa_geo,
                    hrr_geo=hrr_geo,
                    df=df_businesses,
                )
            )

        with gr.Tab("📍 Shops in TN Counties"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Filter Shops by Business Type")
                    business_options = ["All"] + sorted(
                        df_businesses["business_type"].unique()
                    )
                    business_filter = gr.CheckboxGroup(
                        label="Select Business Types",
                        choices=business_options,
                        value=["All"],
                    )
                    reset_button = gr.Button("Reset Filters")
                with gr.Column(scale=4):
                    shops_counties_map = gr.HTML()

            def update_counties_map(business_filters):
                """
                Update the counties map based on selected business type filters.

                Parameters:
                    business_filters (List[str]): List of selected business types.

                Returns:
                    str: HTML representation of the updated Folium map.
                """
                if "All" in business_filters or not business_filters:
                    business_filters = ["All"]
                return create_map(
                    geo_layer="Counties",
                    business_filters=business_filters,
                    counties_geo=counties_geo,
                    hsa_geo=hsa_geo,
                    hrr_geo=hrr_geo,
                    df=df_businesses,
                )

            business_filter.change(
                fn=update_counties_map,
                inputs=[business_filter],
                outputs=[shops_counties_map],
            )
            reset_button.click(
                fn=lambda: (
                    "All",
                    create_map(
                        geo_layer="Counties",
                        business_filters=["All"],
                        counties_geo=counties_geo,
                        hsa_geo=hsa_geo,
                        hrr_geo=hrr_geo,
                        df=df_businesses,
                    ),
                )[:1],
                outputs=[business_filter, shops_counties_map],
            )

        with gr.Tab("📍 Shops in TN HSAs"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Filter Shops by Business Type")
                    business_options_hsa = ["All"] + sorted(
                        df_businesses["business_type"].unique()
                    )
                    business_filter_hsa = gr.CheckboxGroup(
                        label="Select Business Types",
                        choices=business_options_hsa,
                        value=["All"],
                    )
                    reset_button_hsa = gr.Button("Reset Filters")
                with gr.Column(scale=4):
                    shops_hsa_map = gr.HTML()

            def update_hsa_map(business_filters):
                """
                Update the HSAs map based on selected business type filters.

                Parameters:
                    business_filters (List[str]): List of selected business types.

                Returns:
                    str: HTML representation of the updated Folium map.
                """
                if "All" in business_filters or not business_filters:
                    business_filters = ["All"]
                return create_map(
                    geo_layer="HSAs",
                    business_filters=business_filters,
                    counties_geo=counties_geo,
                    hsa_geo=hsa_geo,
                    hrr_geo=hrr_geo,
                    df=df_businesses,
                )

            business_filter_hsa.change(
                fn=update_hsa_map, inputs=[business_filter_hsa], outputs=[shops_hsa_map]
            )
            reset_button_hsa.click(
                fn=lambda: (
                    "All",
                    create_map(
                        geo_layer="HSAs",
                        business_filters=["All"],
                        counties_geo=counties_geo,
                        hsa_geo=hsa_geo,
                        hrr_geo=hrr_geo,
                        df=df_businesses,
                    ),
                )[:1],
                outputs=[business_filter_hsa, shops_hsa_map],
            )

        with gr.Tab("📍 Shops in TN HRRs"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Filter Shops by Business Type")
                    business_options_hrr = ["All"] + sorted(
                        df_businesses["business_type"].unique()
                    )
                    business_filter_hrr = gr.CheckboxGroup(
                        label="Select Business Types",
                        choices=business_options_hrr,
                        value=["All"],
                    )
                    reset_button_hrr = gr.Button("Reset Filters")
                with gr.Column(scale=4):
                    shops_hrr_map = gr.HTML()

            def update_hrr_map(business_filters):
                """
                Update the HRRs map based on selected business type filters.

                Parameters:
                    business_filters (List[str]): List of selected business types.

                Returns:
                    str: HTML representation of the updated Folium map.
                """
                if "All" in business_filters or not business_filters:
                    business_filters = ["All"]
                return create_map(
                    geo_layer="HRRs",
                    business_filters=business_filters,
                    counties_geo=counties_geo,
                    hsa_geo=hsa_geo,
                    hrr_geo=hrr_geo,
                    df=df_businesses,
                )

            business_filter_hrr.change(
                fn=update_hrr_map, inputs=[business_filter_hrr], outputs=[shops_hrr_map]
            )
            reset_button_hrr.click(
                fn=lambda: (
                    "All",
                    create_map(
                        geo_layer="HRRs",
                        business_filters=["All"],
                        counties_geo=counties_geo,
                        hsa_geo=hsa_geo,
                        hrr_geo=hrr_geo,
                        df=df_businesses,
                    ),
                )[:1],
                outputs=[business_filter_hrr, shops_hrr_map],
            )

        with gr.Tab("🔍 Nearest Shop Finder"):
            gr.Markdown("## Find Nearby Auto Shops in Tennessee")
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Select a Repair Shop")
                    shop_names = sorted(df_businesses["name"].unique().tolist())
                    shop_dropdown = gr.Dropdown(
                        label="Select Repair Shop", choices=shop_names
                    )
                with gr.Column(scale=4):
                    nearest_map = gr.HTML()

            def update_nearest_shops_map(selected_shop_name):
                """
                Update the Nearest Shop Finder map based on the selected repair shop.

                Parameters:
                    selected_shop_name (str): The name of the selected repair shop.

                Returns:
                    str: HTML representation of the updated Folium map showing nearest shops.

                Notes:
                    If no shop is selected, prompts the user to select one.
                    If the selected shop is not found, returns an error message.
                """
                if not selected_shop_name:
                    return "Please select a repair shop to find nearby auto shops."

                try:
                    neighbor_shops, neighbor_distances = find_nearest_shops(
                        df_businesses, index, selected_shop_name
                    )
                except ValueError as e:
                    return str(e)

                selected_shop = df_businesses[
                    df_businesses["name"] == selected_shop_name
                ].iloc[0]

                m = folium.Map(
                    location=[selected_shop["md_y"], selected_shop["md_x"]],
                    zoom_start=12,
                )

                # Add selected shop marker
                folium.Marker(
                    location=[selected_shop["md_y"], selected_shop["md_x"]],
                    popup=(
                        f"<b>Selected Shop:</b> {selected_shop['name']}<br>"
                        f"{selected_shop.get('address', 'N/A')}, {selected_shop.get('city', 'N/A')}, TN {selected_shop.get('postal_code', 'N/A')}"
                    ),
                    icon=folium.Icon(color="red", icon="star"),
                ).add_to(m)

                # Add markers for neighbor shops
                for idx, row in neighbor_shops.iterrows():
                    folium.Marker(
                        location=[row["md_y"], row["md_x"]],
                        popup=(
                            f"<b>Nearest Shop:</b> {row['name']}<br>"
                            f"{row.get('address', 'N/A')}, {row.get('city', 'N/A')}, TN {row.get('postal_code', 'N/A')}"
                        ),
                        icon=folium.Icon(color="blue", icon="info-sign"),
                    ).add_to(m)

                    # Draw a line between selected shop and neighbor shop
                    folium.PolyLine(
                        locations=[
                            [selected_shop["md_y"], selected_shop["md_x"]],
                            [row["md_y"], row["md_x"]],
                        ],
                        color="blue",
                    ).add_to(m)

                return m._repr_html_()

            shop_dropdown.change(
                fn=update_nearest_shops_map,
                inputs=[shop_dropdown],
                outputs=[nearest_map],
            )

        with gr.Tab("🔍 Help"):
            gr.Markdown(
                """
            ## How to Use This Dashboard

            - **Overview Tab:** Provides population statistics and a summary map of all auto businesses in Tennessee.

            - **Shops in TN Counties/HSAs/HRRs Tabs:**
                - **Filter by Business Type:** Use the checkboxes to select one or multiple business types to display on the map.
                - **Filter by Geographical Area:** Depending on the tab, you can filter businesses based on Counties, HSAs, or HRRs.
                - **Reset Filters:** Click the reset button to clear all selected filters and view all businesses.
                - **Interactive Map:** Zoom in/out, click on markers to view business details.

            - **Nearest Shop Finder Tab:**
                - **Select a Repair Shop:** Choose a shop from the dropdown menu to find nearby auto shops.
                - **View Results:** The map will display the selected shop and nearby auto shops with lines connecting them.

            """
            )

        gr.Markdown("### 📄 Source: Yellow Pages")

    return app


def main():
    """
    Launch the Gradio application.

    This function initializes the Gradio app and starts the server, making the dashboard accessible.
    """
    app = create_app()
    app.launch(server_name="0.0.0.0", server_port=7860, share=True)


if __name__ == "__main__":
    main()
