# Responsible for data loading and preparing datasets

import pandas as pd

class DataLoader:
    @staticmethod
    def load_auto_business_data(file_path):
        return pd.read_csv(file_path)

    @staticmethod
    def load_population_data_2020(population_2020_data):
        return pd.DataFrame(population_2020_data)

    @staticmethod
    def load_population_comparison(df_population_2010, df_population_2020):
        return pd.merge(df_population_2010, df_population_2020, on='County')
