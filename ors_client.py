"""A module for interfacing with the OpenRouteService API."""
# map_generator.py
# Responsible for generating the map

import logging
from typing import Optional

import folium
import pandas as pd
from folium.plugins import MarkerCluster


class MapGenerator:
    """
    A class used to generate interactive maps for visualizing auto businesses.

    Attributes:
        geo_data (dict): A dictionary containing geographical data layers.
        logger (logging.Logger): Logger instance for logging information and errors.
    """

    def __init__(self, geo_data: dict, logger: Optional[logging.Logger] = None):
        """
        Initialize the MapGenerator with geographical data and an optional logger.

        Parameters:
            geo_data (dict): A dictionary containing geographical data layers, such as 'Counties', 'HSAs', 'HRRs'.
            logger (logging.Logger, optional): A logger instance for logging. If None, a default logger is created.
        """
        self.geo_data = geo_data
        self.logger = logger if logger else logging.getLogger(__name__)

    def create_map(
        self,
        business_filters: list,
        business_df: pd.DataFrame,
        geo_layer: str = "Counties",
    ) -> str:
        """
        Create an interactive Folium map with specified geographical layers and business filters.

        Parameters:
            business_filters (list): A list of business types to filter and display on the map.
            business_df (pd.DataFrame): A DataFrame containing business information, including 'business_name', 'latitude', and 'longitude'.
            geo_layer (str, optional): The geographical layer to display on the map. Defaults to "Counties".
                                       Options might include 'HSAs', 'HRRs', etc.

        Returns:
            str: An HTML representation of the generated Folium map.

        Raises:
            KeyError: If the specified geo_layer is not found in the geo_data.
        """
        self.logger.info(
            f"Creating map with geo_layer: {geo_layer} and business_filters: {business_filters}"
        )

        # Debugging statement to check geo_data contents
        self.logger.debug(f"geo_data keys: {self.geo_data.keys()}")

        if geo_layer not in self.geo_data:
            self.logger.error(f"Geo layer '{geo_layer}' not found in geo_data")
            raise KeyError(f"Geo layer '{geo_layer}' not found in geo_data")

        m = folium.Map(location=[35.5175, -86.5804], zoom_start=7)
        folium.GeoJson(self.geo_data[geo_layer], name=geo_layer).add_to(m)

        # Add business markers to the map
        for _, row in business_df.iterrows():
            if row["business_name"] in business_filters:
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    popup=row["business_name"],
                ).add_to(m)
        return m._repr_html_()
