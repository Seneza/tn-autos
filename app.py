# The main file where Gradio interface is defined.
import gradio as gr
from logger import setup_logger
from data_loader import DataLoader
from map_generator import MapGenerator
from population_plotter import PopulationPlotter
from random_forest_model import RandomForestModel

# Logger setup
logger = setup_logger()

# Load data
population_2020_data = {
    'County': ['Shelby', 'Davidson', 'Knox', 'Hamilton', 'Rutherford'], 
    'Population_2020': [929744, 715884, 478971, 366207, 341486]
}
df_population_2020 = DataLoader.load_population_data_2020(population_2020_data)
df_auto_businesses = DataLoader.load_auto_business_data("data/location-of-auto-businesses.csv")

# Generate map and plots
map_generator = MapGenerator(geo_data={}, logger=logger)
population_plotter = PopulationPlotter(df_population_2020)

with gr.Blocks() as app:
    gr.Markdown("# 🚗 Tennessee Auto Repair Businesses Dashboard")
    
    with gr.Tab("Overview"):
        gr.Markdown("## 📊 Tennessee Population Statistics")
        population_plot = gr.Plot(population_plotter.plot_2020_population)

    with gr.Tab("Business Map"):
        gr.Markdown("## 📍 Auto Repair Businesses")
        business_map = gr.HTML(map_generator.create_map(business_filters=["Autozone"], business_df=df_auto_businesses))

app.launch()
