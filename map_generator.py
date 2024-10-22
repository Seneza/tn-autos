# Responsible for generating the map

import folium
from folium.plugins import MarkerCluster
import pandas as pd

class MapGenerator:
    def __init__(self, geo_data, logger):
        self.geo_data = geo_data
        self.logger = logger

    def create_map(self, geo_layer="Counties", business_filters=["All"], business_df=None):
        self.logger.info(f"Creating map with geo_layer: {geo_layer} and business_filters: {business_filters}")
        m = folium.Map(location=[35.8601, -86.6602], zoom_start=7)
        folium.GeoJson(self.geo_data[geo_layer], name=geo_layer).add_to(m)

        marker_cluster = MarkerCluster().add_to(m)
        filtered_df = business_df[business_df['business_type'].isin(business_filters)] if "All" not in business_filters else business_df
        for _, row in filtered_df.iterrows():
            folium.Marker(location=[row['md_y'], row['md_x']], popup=f"<b>{row['name']}</b>").add_to(marker_cluster)

        folium.LayerControl().add_to(m)
        self.logger.info("Map creation completed.")
        return m._repr_html_()
