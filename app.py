import gradio as gr
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MousePosition
import numpy as np
import geopandas as gpd
from branca.element import Element  # Import Element from branca to add the legend
import os
import openrouteservice  # For generating isochrones
from openrouteservice import convert

# ORS client setup (You'll need to sign up for an API key at https://openrouteservice.org/sign-up/)
# Load the ORS API key from the environment variable
ORS_API_KEY = os.getenv('ors')
client = openrouteservice.Client(key=ORS_API_KEY)

# To add a new tab called Autozone Isochrone that draws 15-minute driving isochrones around each Autozone location, 
# we can utilize the OpenRouteService (ORS) API, which provides isochrone data. Here's how you can integrate it into your current Gradio interface:

# Function to create isochrones around Autozone locations
# Function to create isochrones around Autozone locations
def create_isochrone_map():
    # Create the base map centered on Tennessee
    m = folium.Map(location=[35.8601, -86.6602], zoom_start=8)
    
    # Filter the dataframe for Autozone locations only
    autozone_df = df_md_final1[df_md_final1['business_type'] == 'Autozone']
    
    # Iterate over Autozone locations and add 15-minute isochrones
    for idx, row in autozone_df.iterrows():
        coords = (row['md_x'], row['md_y'])
        try:
            # Call the ORS API and handle any potential errors
            isochrone = client.isochrones(locations=[coords], profile='driving-car', range=[1800])  # 30 minutes = 1800 seconds
            
            # Convert the isochrone geometry to GeoJSON and add it to the map
            folium.GeoJson(isochrone).add_to(m)
        except openrouteservice.exceptions.HTTPError as e:
            print(f"HTTPError: {e}")
            continue
        except requests.exceptions.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue
    
    return m._repr_html_()

# Data for 2020 Tennessee population by county
population_2020_data = {
    'County': ['Shelby', 'Davidson', 'Knox', 'Hamilton', 'Rutherford', 'Williamson', 'Montgomery', 'Sumner', 'Blount', 'Washington', 
               'Madison', 'Sevier', 'Maury', 'Wilson', 'Bradley'],
    'Population_2020': [929744, 715884, 478971, 366207, 341486, 247726, 220069, 196281, 135280, 133001, 
                        98823, 98380, 100974, 147737, 108620]
}

# Create a DataFrame for the top 15 counties
df_population_2020 = pd.DataFrame(population_2020_data)

# Function to create the bar plot for 2020 Tennessee population (top 15 counties)
def plot_2020_population_top15():
    fig = px.bar(df_population_2020, 
                 x='County', 
                 y='Population_2020', 
                 title='Tennessee Population 2020', 
                 labels={'County': 'County', 'Population_2020': '2020 Population'})
    
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    return fig

# Load datasets
df_md_final1 = pd.read_csv("data/location-of-auto-businesses.csv")
cbg_geographic_data = pd.read_csv("data/cbg_geographic_data.csv")
df_weekly = pd.read_parquet("data/mobility/tn_weekly_mobility_2019.parquet")
largest_counties = cbg_geographic_data.groupby('county')['pop10'].sum().nlargest(10).index

filtered_data = cbg_geographic_data[cbg_geographic_data['county'].isin(largest_counties)]
county_population = filtered_data.groupby('cntyname')['pop10'].sum().reset_index()
county_population = county_population.sort_values(by='pop10', ascending=False)

county_land = filtered_data.groupby('census_block_group')['amount_land'].sum().reset_index()
county_land = county_land.sort_values(by='amount_land', ascending=False)
county_data = cbg_geographic_data[cbg_geographic_data['pop10'] > 3200].sort_values(by="pop10", ascending=False)

# Define business type based on name with six categories
df_md_final1['business_type'] = np.where(df_md_final1['name'].str.contains("Autozone", case=False, na=False), "Autozone", 
                        np.where(df_md_final1['name'].str.contains("Napa Auto Parts", case=False, na=False), "Napa Auto Parts", 
                                 np.where(df_md_final1['name'].str.contains("O'Reilly Auto Parts", case=False, na=False), "O'Reilly Auto Parts",
                                          np.where(df_md_final1['name'].str.contains("Advance Auto Parts", case=False, na=False), "Advance Auto Parts",
                                                   np.where(df_md_final1['name'].str.contains("Toyota|Honda|Kia|Nissan|Chevy|Ford|Carmax|GMC", case=False, na=False), 
                                                            "Car Dealership", 
                                                            "Other Auto Repair Shop")))))

# Function to create the population distribution plot
def plot_population_distribution():
    fig = px.bar(county_data, 
                 x="cntyname", 
                 y="pop10", 
                 title="2010 Population by County", 
                 orientation='v',
                 labels={"cntyname": "County Name", "pop10": "2010 Population"})
    fig.update_layout(xaxis={'categoryorder':'total descending'})
    return fig

# Function to create the land distribution plot
def plot_land_distribution():
    fig = px.histogram(county_land, x='amount_land', title="Census Block Land Distribution", labels={'amount_land': 'Amount of Land'})
    fig.update_layout(barmode='overlay')
    fig.update_traces(opacity=0.75)
    return fig

# Function to create a Folium map with county boundaries, colored markers, and a legend
def create_map():
    # Create the base map centered on Tennessee
    m = folium.Map(location=[35.8601, -86.6602], zoom_start=8)

    # Load and filter county boundaries for Tennessee
    counties_geo = gpd.read_file("data/county/01_county-shape-file.shp")
    counties_geo = counties_geo[counties_geo['statefp'] == '47']  # Filter for Tennessee

    # Add county boundaries to the map
    folium.GeoJson(counties_geo).add_to(m)

    # Add mouse position plugin
    MousePosition().add_to(m)

    # Define marker colors based on business type
    def get_marker_color(business_type):
        if business_type == "Autozone":
            return "blue"
        elif business_type == "Napa Auto Parts":
            return "green"
        elif business_type == "O'Reilly Auto Parts":
            return "orange"
        elif business_type == "Advance Auto Parts":
            return "yellow"
        elif business_type == "Car Dealership":
            return "red"
        else:
            return "purple"  # Color for "Other Auto Repair Shop"

    # Iterate over the dataframe and add markers with different colors based on business type
    for idx, row in df_md_final1.iterrows():
        folium.Marker(
            location=[row['md_y'], row['md_x']],
            popup=str(row['name']),
            icon=folium.Icon(color=get_marker_color(row['business_type']))
        ).add_to(m)

    # Create custom HTML for the legend
    legend_html = '''
     <div style="position: fixed; 
                 bottom: 50px; left: 50px; width: 300px; height: 210px; 
                 background-color: white; z-index:9999; font-size:14px;
                 border:2px solid grey;
                 padding: 10px;">
     <b>Business Type Legend</b> <br>
     <i class="fa fa-map-marker fa-2x" style="color:blue"></i>&nbsp;Autozone<br>
     <i class="fa fa-map-marker fa-2x" style="color:green"></i>&nbsp;Napa Auto Parts<br>
     <i class="fa fa-map-marker fa-2x" style="color:orange"></i>&nbsp;O'Reilly Auto Parts<br>
     <i class="fa fa-map-marker fa-2x" style="color:yellow"></i>&nbsp;Advance Auto Parts<br>
     <i class="fa fa-map-marker fa-2x" style="color:red"></i>&nbsp;Car Dealership<br>
     <i class="fa fa-map-marker fa-2x" style="color:purple"></i>&nbsp;Other Auto Repair Shop<br>
     </div>
     '''

    # Add the legend to the map
    m.get_root().html.add_child(Element(legend_html))

    # Return the map's HTML representation
    return m._repr_html_()
    
# Gradio Interface
with gr.Blocks() as app:
    gr.Markdown("# Kora Customer Map Analysis")

    with gr.Tab("Overview"):
        gr.Markdown("## Tennessee Population 2010")
        pop_dist = gr.Plot(plot_population_distribution)

        # Add the 2020 population distribution plot for top 15 counties
        gr.Markdown("### Tennessee Population 2020")
        pop_dist_2020_top15 = gr.Plot(plot_2020_population_top15)

        gr.Markdown("### Auto Repair/Parts in Tennessee")

        manual_table = gr.Dataframe(
            headers=["Location Name", "Street Address", "City", "State", "Postal Code"],  # Column names without "Brands"
            datatype=["str", "str", "str", "str", "str"],  # Data types for each column
            value=[
                ["AutoZone", "257 Wears Valley Rd", "Pigeon Forge", "Tennessee", "37863"],
                ["Sterling Auto", "2064 Wilma Rudolph Blvd", "Clarksville", "Tennessee", "37040"],
                ["Advance Auto Parts", "2124 N Highland Ave", "Jackson", "Tennessee", "38305"],
                ["FRIENDSHIP HYUNDAI OF BRISTOL", "1841 Volunteer Pkwy", "Bristol", "Tennessee", "37620"],
                ["Advance Auto Parts", "45 Main St", "Savannah", "Tennessee", "38372"],
                ["O'Reilly Auto Parts", "493 Craighead St", "Nashville", "Tennessee", "37204"],
                ["O'Reilly Auto Parts", "864 Highway 51 N", "Covington", "Tennessee", "38019"],
                ["NAPA Auto Parts", "711 Murfreesboro Pike", "Nashville", "Tennessee", "37210"],
                ["Goodyear Auto Service Centers", "5407 Highway 153", "Hixson", "Tennessee", "37343"],
                ["NAPA Auto Parts", "100 Center St", "Johnson City", "Tennessee", "37615"],
                # Adding new entries
                ["Cadillac,Buick,Chevrolet,GMC", "960 John R Rice Blvd", "Murfreesboro", "Tennessee", "37129"],
                ["AutoZone", "9760 Highway 64", "Lakeland", "Tennessee", "38002"],
                ["Honda", "1408 Highway 45 Byp", "Jackson", "Tennessee", "38305"],
                ["National Tire & Battery (NTB)", "532 Robert Rose Dr", "Murfreesboro", "Tennessee", "37129"],
                ["NAPA Auto Parts", "711 Murfreesboro Pike", "Nashville", "Tennessee", "37210"],
                ["Advance Auto Parts", "160 W Broadway", "Gallatin", "Tennessee", "37066"],
                ["Southern Tire Mart (STM)", "1551 S Wilcox Dr", "Kingsport", "Tennessee", "37660"],
                ["Chevrolet", "310 E 20th St", "Chattanooga", "Tennessee", "37408"],
                ["O'Reilly Auto Parts", "7534 Oak Ridge Hwy", "Knoxville", "Tennessee", "37931"],
                ["Goodyear Auto Service Centers", "971 Eastgate Loop", "Chattanooga", "Tennessee", "37411"],
                ["Firestone Complete Auto Care", "15127 Old Hickory Blvd", "Nashville", "Tennessee", "37211"],
                ["Christian Brothers Automotive", "10406 Kingston Pike", "Knoxville", "Tennessee", "37922"],
                ["Christian Brothers Automotive", "563 E Main St", "Hendersonville", "Tennessee", "37075"],
                ["O'Reilly Auto Parts", "101 Village Square Ln", "Mountain City", "Tennessee", "37683"],
                ["O'Reilly Auto Parts", "4219 Fort Henry Dr Ste A", "Kingsport", "Tennessee", "37663"],
                ["Precision Tune Auto Care", "4710 N Broadway St", "Knoxville", "Tennessee", "37918"],
                ["National Tire & Battery (NTB)", "234 Old Hickory Blvd", "Nashville", "Tennessee", "37221"]
            ],  # Data values
            row_count=27  # Adjusted total number of rows
        )

        gr.Markdown("Source: Yellowbook")

        map_output = gr.HTML(create_map)

    with gr.Tab("Tennessee Businesses by county"):
        map_output = gr.HTML(create_map)
        

app.launch(server_name="0.0.0.0", server_port=7860)
