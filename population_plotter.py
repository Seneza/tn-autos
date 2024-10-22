#Responsible for plotting population statistics

import pandas as pd
import plotly.express as px

class PopulationPlotter:
    def __init__(self, df_population_2020):
        self.df_population_2020 = df_population_2020

    def plot_2020_population(self):
        fig = px.bar(self.df_population_2020, x='County', y='Population_2020', title='Tennessee Population 2020')
        fig.update_layout(xaxis={'categoryorder': 'total descending'}, template='plotly_white')
        return fig

    def plot_population_comparison(self, df_population_comparison):
        df_melted = df_population_comparison.melt(id_vars='County', var_name='Year', value_name='Population')
        fig = px.bar(df_melted, x='County', y='Population', color='Year', barmode='group', title="Tennessee Population Comparison: 2010 vs 2020")
        fig.update_layout(xaxis={'categoryorder': 'total descending'}, template='plotly_white')
        return fig
