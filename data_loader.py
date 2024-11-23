"""Responsible for data loading and preparing datasets."""

# data_loader.py
# Responsible for data loading and preparing datasets

import pandas as pd


class DataLoader:
    """
    A class used to load and prepare various datasets required for the application.

    This class provides static methods to load auto business data, population data for the year 2020,
    and to merge population data from different years for comparison.
    """

    @staticmethod
    def load_auto_business_data(file_path: str) -> pd.DataFrame:
        """
        Load auto business data from a CSV file into a Pandas DataFrame.

        Parameters:
            file_path (str): The file path to the CSV file containing auto business data.

        Returns:
            pd.DataFrame: A DataFrame containing the loaded auto business data.

        Raises:
            FileNotFoundError: If the specified CSV file does not exist.
            pd.errors.EmptyDataError: If the CSV file is empty.
            pd.errors.ParserError: If there is a parsing error while reading the CSV.
        """
        try:
            return pd.read_csv(file_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"The file {file_path} was not found.") from e
        except pd.errors.EmptyDataError as e:
            raise pd.errors.EmptyDataError(f"The file {file_path} is empty.") from e
        except pd.errors.ParserError as e:
            raise pd.errors.ParserError(f"Error parsing the file {file_path}.") from e

    @staticmethod
    def load_population_data_2020(population_2020_data: dict) -> pd.DataFrame:
        """
        Convert a dictionary of 2020 population data into a Pandas DataFrame.

        Parameters:
            population_2020_data (dict): A dictionary containing 2020 population data with keys 'County' and 'Population_2020'.

        Returns:
            pd.DataFrame: A DataFrame containing the 2020 population data.

        Raises:
            ValueError: If the input dictionary does not contain the required keys.
        """
        required_keys = {"County", "Population_2020"}
        if not required_keys.issubset(population_2020_data.keys()):
            missing_keys = required_keys - population_2020_data.keys()
            raise ValueError(f"Missing keys in population_2020_data: {missing_keys}")

        return pd.DataFrame(population_2020_data)

    @staticmethod
    def load_population_comparison(
        df_population_2010: pd.DataFrame, df_population_2020: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merge 2010 and 2020 population DataFrames based on the 'County' column for comparison.

        Parameters:
            df_population_2010 (pd.DataFrame): A DataFrame containing 2010 population data with at least the 'County' column.
            df_population_2020 (pd.DataFrame): A DataFrame containing 2020 population data with at least the 'County' column.

        Returns:
            pd.DataFrame: A merged DataFrame containing population data from both 2010 and 2020 for each county.

        Raises:
            KeyError: If the 'County' column is missing in either of the input DataFrames.
            pd.errors.MergeError: If the merge operation fails.
        """
        if "County" not in df_population_2010.columns:
            raise KeyError("The 'County' column is missing from df_population_2010.")
        if "County" not in df_population_2020.columns:
            raise KeyError("The 'County' column is missing from df_population_2020.")

        try:
            return pd.merge(df_population_2010, df_population_2020, on="County")
        except pd.errors.MergeError as e:
            raise pd.errors.MergeError("Failed to merge population data.") from e
