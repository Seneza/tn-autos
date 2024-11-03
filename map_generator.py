# Responsible for generating the map

import folium
import logging
from folium.plugins import MarkerCluster
import pandas as pd


class MapGenerator:
    def __init__(self, geo_data, logger=None):
        self.geo_data = geo_data
        self.logger = logging.getLogger(__name__)

    def create_map(self, business_filters, business_df, geo_layer='Counties'):
        self.logger.info(f"Creating map with geo_layer: {geo_layer} and business_filters: {business_filters}")
        
        # Debugging statement to check geo_data contents
        self.logger.debug(f"geo_data keys: {self.geo_data.keys()}")
        
        if geo_layer not in self.geo_data:
            self.logger.error(f"Geo layer '{geo_layer}' not found in geo_data")
            raise KeyError(f"Geo layer '{geo_layer}' not found in geo_data")
        
        m = folium.Map(location=[35.5175, -86.5804], zoom_start=7)
        folium.GeoJson(self.geo_data[geo_layer], name=geo_layer).add_to(m)
        
        # Add business markers to the map
        for _, row in business_df.iterrows():
            if row['business_name'] in business_filters:
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=row['business_name']
                ).add_to(m)    
        return m._repr_html_()
    