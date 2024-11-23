"""Responsible for plotting population statistics."""
# population_plotter.py
# Responsible for plotting population statistics

import pandas as pd
import plotly.express as px


class PopulationPlotter:
    """
    A class used to create visualizations for population data.

    Attributes:
        df_population_2020 (pd.DataFrame): DataFrame containing 2020 population data.
    """

    def __init__(self, df_population_2020: pd.DataFrame):
        """
        Initialize the PopulationPlotter with 2020 population data.

        Parameters:
            df_population_2020 (pd.DataFrame): DataFrame containing 2020 population data with columns 'County' and 'Population_2020'.
        """
        self.df_population_2020 = df_population_2020

    def plot_2020_population(self) -> px.bar:
        """
        Generate a bar chart of the 2020 population data.

        Creates a Plotly bar chart displaying the population of each county in Tennessee for the year 2020.

        Returns:
            px.bar: A Plotly Express bar chart object representing the 2020 population data.
        """
        fig = px.bar(
            self.df_population_2020,
            x="County",
            y="Population_2020",
            title="Tennessee Population 2020",
        )
        fig.update_layout(
            xaxis={"categoryorder": "total descending"}, template="plotly_white"
        )
        return fig

    def plot_population_comparison(
        self, df_population_comparison: pd.DataFrame
    ) -> px.bar:
        """
        Generate a side-by-side bar chart comparing 2010 and 2020 population data.

        Transforms the comparison DataFrame to a long format and creates a grouped bar chart to visualize population changes between 2010 and 2020.

        Parameters:
            df_population_comparison (pd.DataFrame): DataFrame containing population data for 2010 and 2020 with columns 'County', 'Population_2010', and 'Population_2020'.

        Returns:
            px.bar: A Plotly Express bar chart object representing the population comparison between 2010 and 2020.
        """
        df_melted = df_population_comparison.melt(
            id_vars="County", var_name="Year", value_name="Population"
        )
        fig = px.bar(
            df_melted,
            x="County",
            y="Population",
            color="Year",
            barmode="group",
            title="Tennessee Population Comparison: 2010 vs 2020",
        )
        fig.update_layout(
            xaxis={"categoryorder": "total descending"}, template="plotly_white"
        )
        return fig
