import logging
import gradio as gr
import pandas as pd
import plotly.express as px
import folium
import numpy as np
import geopandas as gpd
from branca.element import Element
import os
import openrouteservice
from folium.plugins import MarkerCluster

import matplotlib.pyplot as plt
import io
import base64
import logfire

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logfire.configure()  # Configure logfire for logging

# ORS (OpenRouteService) client setup
ORS_API_KEY = os.getenv('ors')  # Retrieve ORS API key from environment variables
if not ORS_API_KEY:
    raise ValueError("OpenRouteService API key not found. Please set the 'ors' environment variable.")

client = openrouteservice.Client(key=ORS_API_KEY)  # Initialize ORS client

# Function to create isochrones around AutoZone locations
def create_isochrone_map():
    """
    Creates a Folium map with isochrones (travel time areas) around AutoZone locations.

    Returns:
        HTML representation of the map.
    """
    m = folium.Map(location=[35.8601, -86.6602], zoom_start=7)  # Center map on Tennessee
    autozone_df = df_md_final1[df_md_final1['business_type'] == 'Autozone']  # Filter for AutoZone locations

    for idx, row in autozone_df.iterrows():
        coords = (row['md_x'], row['md_y'])  # Get coordinates of the location
        try:
            # Request isochrone data from ORS API
            isochrone = client.isochrones(locations=[coords], profile='driving-car', range=[1800])
            # Add isochrone layer to the map
            folium.GeoJson(isochrone, name='Isochrones').add_to(m)
        except openrouteservice.exceptions.HTTPError as e:
            print(f"HTTPError: {e}")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

    folium.LayerControl().add_to(m)  # Add layer control to the map
    return m._repr_html_()  # Return the map as HTML

# Data for 2020 Tennessee population by county
population_2020_data = {
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

# Create a DataFrame for the top 15 counties
df_population_2020 = pd.DataFrame(population_2020_data)

# Function to create a Folium map with selected geographical boundaries and markers
def create_map(geo_layer="Counties", business_filters=["All"]):
    """
    Creates an interactive map with selected geographical boundaries and business markers.

    Args:
        geo_layer (str): Geographical layer to display ('Counties', 'Zip Codes', 'HSAs', 'HRRs').
        business_filters (list): List of business types to include.

    Returns:
        HTML representation of the map.
    """
    logger.info(f"Creating map with geo_layer: {geo_layer} and business_filters: {business_filters}")

    m = folium.Map(location=[35.8601, -86.6602], zoom_start=7)  # Initialize map centered on Tennessee

    try:
        # Select the appropriate GeoDataFrame based on geo_layer
        if geo_layer == "Counties":
            geo_data = counties_geo
        elif geo_layer == "Zip Codes":
            geo_data = zcta_geo
        elif geo_layer == "HSAs":
            geo_data = hsa_geo
        elif geo_layer == "HRRs":
            geo_data = hrr_geo
        else:
            geo_data = counties_geo  # Default to counties
        logger.info(f"Geo layer {geo_layer} selected.")

        # Add geographical boundaries to the map
        folium.GeoJson(geo_data, name=geo_layer).add_to(m)
    except Exception as e:
        logger.error(f"Error loading GeoData for {geo_layer}: {e}")

    # Initialize Marker Cluster for better visualization of markers
    marker_cluster = MarkerCluster().add_to(m)

    # Filter businesses based on selected types
    if "All" not in business_filters:
        filtered_df = df_md_final1[df_md_final1['business_type'].isin(business_filters)]
    else:
        filtered_df = df_md_final1.copy()

    logger.info(f"Filtered {len(filtered_df)} businesses based on filters: {business_filters}")

    # Add markers for each business location
    for _, row in filtered_df.iterrows():
        folium.Marker(
            location=[row['md_y'], row['md_x']],
            popup=f"<b>{row['name']}</b>"
        ).add_to(marker_cluster)

    folium.LayerControl().add_to(m)  # Add layer control to toggle layers
    logger.info("Map creation completed.")
    return m._repr_html_()  # Return the map as HTML

# Function to create a bar plot for 2020 Tennessee population (top 15 counties)
def plot_2020_population_top15():
    """
    Creates a bar chart of the 2020 population for the top 15 Tennessee counties.

    Returns:
        Plotly Figure object.
    """
    fig = px.bar(
        df_population_2020, 
        x='County', 
        y='Population_2020', 
        title='Tennessee Population 2020', 
        labels={'County': 'County', 'Population_2020': ''},
        color='Population_2020',
        color_continuous_scale='Blues'
    )
    fig.update_layout(xaxis={'categoryorder':'total descending'}, template='plotly_white')
    return fig

# Function to create the population distribution plot for 2010
def plot_population_distribution():
    """
    Creates a bar chart of the 2010 population by county.

    Returns:
        Plotly Figure object.
    """
    print(cbg_geographic_data.head())  # Debugging statement
    # Group by county and sum the population
    county_data = (
        cbg_geographic_data
        .groupby('cntyname')['pop10']
        .sum()
        .reset_index()
        .sort_values(by='pop10', ascending=False)
    )

    fig = px.bar(
        county_data.head(15), 
        x="cntyname", 
        y="pop10", 
        title="2010 Population by County", 
        labels={"cntyname": "County", "pop10": "2010 Population"},
        color='pop10',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(xaxis={'categoryorder':'total descending'}, template='plotly_white')
    return fig

# Load datasets
df_md_final1 = pd.read_csv("data/location-of-auto-businesses.csv")
print(df_md_final1.columns)  # Debugging statement
print(df_md_final1.info())   # Debugging statement

cbg_geographic_data = pd.read_csv("data/cbg_geographic_data.csv")
print(cbg_geographic_data.columns)  # Debugging statement
print(cbg_geographic_data.info())   # Debugging statement

# Create DataFrame for 2010 population
df_population_2010 = (
    cbg_geographic_data
    .groupby('cntyname')['pop10']
    .sum()
    .reset_index()
    .sort_values(by='pop10', ascending=False)
)
df_population_2010.rename(columns={'cntyname': 'County', 'pop10': 'Population_2010'}, inplace=True)

# Merge 2010 and 2020 population data for comparison
df_population_comparison = pd.merge(df_population_2010, df_population_2020, on='County')

# Function to create a side-by-side bar chart for 2010 vs 2020 population
def plot_population_comparison():
    """
    Creates a bar chart comparing 2010 and 2020 population data by county.

    Returns:
        Plotly Figure object.
    """
    # Melt DataFrame to have 'Year' and 'Population' columns
    df_melted = df_population_comparison.melt(
        id_vars='County', 
        value_vars=['Population_2010', 'Population_2020'],
        var_name='Year', 
        value_name='Population'
    )
    print(df_melted)  # Debugging statement
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

# Load the County shapefile
county_shapefile_path = "data/county/01_county-shape-file.shp"
if not os.path.exists(county_shapefile_path):
    raise FileNotFoundError(f"County shapefile not found at {county_shapefile_path}. Please ensure the file exists.")

counties_geo = gpd.read_file(county_shapefile_path)
print("County Shapefile Info:", counties_geo.info())  # Debugging statement
print("County Shapefile Head:", counties_geo.head())  # Debugging statement

# Filter for Tennessee counties using state FIPS code '47'
counties_geo = counties_geo[counties_geo['statefp'] == '47']

# Define FIPS codes and abbreviations for TN and KY
state_fips = ['47', '21']  # TN and KY FIPS codes
state_abbr = ['TN', 'KY']

# Load the HSA shapefile
hsa_shapefile_path = "data/hsa/01_hsa-shape-file.shp"
if not os.path.exists(hsa_shapefile_path):
    raise FileNotFoundError(f"HSA shapefile not found at {hsa_shapefile_path}. Please ensure the file exists.")

hsa_geo = gpd.read_file(hsa_shapefile_path)
# Filter HSAs for specified states
if 'hsastate' in hsa_geo.columns:
    hsa_geo = hsa_geo[hsa_geo['hsastate'].isin(state_abbr)]
elif 'STATEFP' in hsa_geo.columns:
    hsa_geo = hsa_geo[hsa_geo['STATEFP'].isin(state_fips)]
else:
    raise KeyError("Column to filter state in HSA shapefile not found.")

# Load the HRR shapefile
hrr_shapefile_path = "data/hrr/01_hrr-shape-file.shp"
if not os.path.exists(hrr_shapefile_path):
    raise FileNotFoundError(f"HRR shapefile not found at {hrr_shapefile_path}. Please ensure the file exists.")

hrr_geo = gpd.read_file(hrr_shapefile_path)
# Filter HRRs for specified states
if 'hrrstate' in hrr_geo.columns:
    hrr_geo = hrr_geo[hrr_geo['hrrstate'].isin(state_abbr)]
elif 'STATEFP' in hrr_geo.columns:
    hrr_geo = hrr_geo[hrr_geo['STATEFP'].isin(state_fips)]
else:
    raise KeyError("Column to filter state in HRR shapefile not found.")

# Define business types based on business names
df_md_final1['business_type'] = np.where(
    df_md_final1['name'].str.contains("Autozone", case=False, na=False), "Autozone", 
    np.where(
        df_md_final1['name'].str.contains("Napa Auto Parts", case=False, na=False), "Napa Auto", 
        np.where(
            df_md_final1['name'].str.contains("Firestone Complete Auto Care", case=False, na=False), "Firestone",                                 
            np.where(
                df_md_final1['name'].str.contains("O'Reilly Auto Parts", case=False, na=False), "O'Reilly Auto",
                np.where(
                    df_md_final1['name'].str.contains("Advance Auto Parts", case=False, na=False), "Advance Auto",
                    np.where(
                        df_md_final1['name'].str.contains("Toyota|Honda|Kia|Nissan|Chevy|Ford|Carmax|GMC", case=False, na=False), 
                        "Car Dealership", 
                        "Other Auto Repair Shops"
                    )
                )
            )
        )
    )
)

# Prepare data for modeling
def prepare_model_data():
    """
    Prepares data for machine learning by aggregating business counts and merging with population data.

    Returns:
        DataFrame ready for modeling.
    """
    # Aggregate number of businesses per county
    business_counts = df_md_final1.groupby('county').size().reset_index(name='business_count')

    # Merge with population data
    df_model = pd.merge(df_population_2020, business_counts, left_on='County', right_on='county', how='left')
    df_model['business_count'] = df_model['business_count'].fillna(0)

    # Drop redundant columns
    df_model = df_model.drop(columns=['county'])  # Assuming 'county' is the same as 'County'

    # Additional feature engineering can be done here

    return df_model

# Train Random Forest model
def train_random_forest():
    """
    Trains a Random Forest Regressor to predict the number of businesses based on population.

    Returns:
        Dictionary containing model, test data, predictions, metrics, SHAP values, and feature importances.
    """
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, r2_score
    import shap

    df_model = prepare_model_data()

    # Features and target variable
    X = df_model[['Population_2020']]
    y = df_model['business_count']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train the Random Forest model
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = rf.predict(X_test)

    # Calculate evaluation metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # SHAP explanation for model interpretability
    explainer = shap.Explainer(rf, X_train)
    shap_values = explainer(X_test)

    # Feature importance
    feature_importances = pd.DataFrame({
        'feature': X.columns,
        'importance': rf.feature_importances_
    }).sort_values(by='importance', ascending=False)

    return {
        'model': rf,
        'X_test': X_test,
        'y_test': y_test,
        'y_pred': y_pred,
        'mse': mse,
        'r2': r2,
        'shap_values': shap_values,
        'feature_importances': feature_importances
    }

# Function to generate SHAP summary plot as a base64 string
def get_shap_summary_plot(shap_values, X):
    """
    Generates a SHAP summary plot and returns it as a base64 string.

    Args:
        shap_values: SHAP values from the model.
        X: Feature data.

    Returns:
        Base64 encoded image string.
    """
    plt.figure()
    shap.summary_plot(shap_values, X, show=False)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

# Function to generate feature importance plot as a base64 string
def get_feature_importance_plot(feature_importances):
    """
    Generates a feature importance bar chart and returns it as a base64 string.

    Args:
        feature_importances (DataFrame): DataFrame with features and their importances.

    Returns:
        Base64 encoded image string.
    """
    fig = px.bar(
        feature_importances, 
        x='feature', 
        y='importance', 
        title='Feature Importance from Random Forest',
        labels={'feature': 'Feature', 'importance': 'Importance'},
        color='importance',
        color_continuous_scale='Blues'
    )
    fig.update_layout(template='plotly_white')
    img_bytes = fig.to_image(format="png")
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"

# Gradio Interface
with gr.Blocks(theme=gr.themes.Default()) as app:
    gr.Markdown("# 🚗 Tennessee Auto Repair Businesses Dashboard")

    with gr.Tab("Overview"):
        gr.Markdown("## 📊 Tennessee Population Statistics")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### 2020 Population by County")
                pop_dist = gr.Plot(plot_2020_population_top15)

        gr.Markdown("### 🛠️ Auto Businesses in Tennessee")
        manual_table = gr.Dataframe(
            headers=["Location Name", "Street Address", "City", "State", "Postal Code"],
            datatype=["str", "str", "str", "str", "str"],
            value=[
                ["AutoZone", "257 Wears Valley Rd", "Pigeon Forge", "Tennessee", "37863"],
                ["Sterling Auto", "2064 Wilma Rudolph Blvd", "Clarksville", "Tennessee", "37040"],
                # Additional data entries...
            ],
            row_count=27,  # Adjusted total number of rows
            interactive=False
        )

        gr.Markdown("### 📍 Interactive Map")
        map_output_overview = gr.HTML(lambda: create_map(geo_layer="Counties", business_filters=["All"]))

    with gr.Tab("📍 Shops in TN Counties"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Filter Shops by Business Type")
                business_options = ["All"] + sorted(df_md_final1['business_type'].unique())
                business_filter = gr.CheckboxGroup(label="Select Business", choices=business_options, value=["All"])
                reset_button = gr.Button("Reset Filters")
            with gr.Column(scale=4):
                shops_counties_map = gr.HTML()

        def update_counties_map(business_filters):
            if "All" in business_filters or not business_filters:
                business_filters = ["All"]
            return create_map(geo_layer="Counties", business_filters=business_filters)

        business_filter.change(fn=update_counties_map, inputs=[business_filter], outputs=[shops_counties_map])
        reset_button.click(
            fn=lambda: (["All"], create_map(geo_layer="Counties", business_filters=["All"])),
            inputs=None, outputs=[business_filter, shops_counties_map]
        )

    with gr.Tab("📍 Shops in TN HSAs"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Filter Shops by Business Type")
                business_options_hsa = ["All"] + sorted(df_md_final1['business_type'].unique())
                business_filter_hsa = gr.CheckboxGroup(label="Select Business", choices=business_options_hsa, value=["All"])
                reset_button_hsa = gr.Button("Reset Filters")
            with gr.Column(scale=4):
                shops_hsa_map = gr.HTML()

        def update_hsa_map(business_filters):
            if "All" in business_filters or not business_filters:
                business_filters = ["All"]
            return create_map(geo_layer="HSAs", business_filters=business_filters)

        business_filter_hsa.change(fn=update_hsa_map, inputs=[business_filter_hsa], outputs=[shops_hsa_map])
        reset_button_hsa.click(
            fn=lambda: (["All"], create_map(geo_layer="HSAs", business_filters=["All"])),
            inputs=None, outputs=[business_filter_hsa, shops_hsa_map]
        )

    with gr.Tab("📍 Shops in TN HRRs"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Filter Shops by Business Type")
                business_options_hrr = ["All"] + sorted(df_md_final1['business_type'].unique())
                business_filter_hrr = gr.CheckboxGroup(label="Select Business", choices=business_options_hrr, value=["All"])
                reset_button_hrr = gr.Button("Reset Filters")
            with gr.Column(scale=4):
                shops_hrr_map = gr.HTML()

        def update_hrr_map(business_filters):
            if "All" in business_filters or not business_filters:
                business_filters = ["All"]
            return create_map(geo_layer="HRRs", business_filters=business_filters)

        business_filter_hrr.change(fn=update_hrr_map, inputs=[business_filter_hrr], outputs=[shops_hrr_map])
        reset_button_hrr.click(
            fn=lambda: (["All"], create_map(geo_layer="HRRs", business_filters=["All"])),
            inputs=None, outputs=[business_filter_hrr, shops_hrr_map]
        )

    with gr.Tab("🔍 Help"):
        gr.Markdown("""
        ## How to Use This Dashboard

        - **Overview Tab:** Provides population statistics and a summary map of all auto businesses in Tennessee.

        - **Shops in TN Counties/HSAs/HRRs Tabs:**
            - **Filter by Business Type:** Use the checkboxes to select one or multiple business types to display on the map.
            - **Reset Filters:** Click the reset button to clear all selected filters and view all businesses.
            - **Interactive Map:** Zoom in/out, click on markers to view business details.

        """)

    gr.Markdown("### 📄 Source: Yellowbook")  # Data source acknowledgment

# Launch the Gradio app
app.launch(server_name="0.0.0.0", server_port=7860, share=True)
