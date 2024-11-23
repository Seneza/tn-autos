"""tests test_app.py."""


# tests/test_app.py

import os

import pandas as pd
import pytest

from app import define_business_types, load_csv, merge_population_data


@pytest.fixture
def sample_businesses_df():
    """Fixture for a sample businesses DataFrame."""
    data = {
        "name": [
            "Autozone Superstore",
            "Napa Auto Parts Central",
            "Firestone Complete Auto Care",
            "O'Reilly Auto Parts Downtown",
            "Advance Auto Parts East",
            "Toyota Dealership",
            "Unknown Auto Shop",
        ],
        "md_y": [35.0, 36.0, 35.5, 36.5, 35.2, 36.2, 35.3],
        "md_x": [-86.0, -87.0, -86.5, -87.5, -86.2, -87.2, -86.3],
    }
    return pd.DataFrame(data)


def test_define_business_types(sample_businesses_df):
    """Test the define_business_types function."""
    result_df = define_business_types(sample_businesses_df)
    expected = [
        "Autozone",
        "Napa Auto",
        "Firestone",
        "O'Reilly Auto",
        "Advance Auto",
        "Car Dealership",
        "Other Auto Repair Shops",
    ]
    assert list(result_df["business_type"]) == expected


def test_merge_population_data():
    """Test the merge_population_data function."""
    # Mock geographic data
    data_geo = {
        "cntyname": ["Shelby", "Davidson", "Knox"],
        "pop10": [100000, 200000, 150000],
    }
    df_geo = pd.DataFrame(data_geo)

    # Mock population 2020 data
    population_2020 = {
        "County": ["Shelby", "Davidson", "Knox"],
        "Population_2020": [929744, 715884, 478971],
    }

    result_df = merge_population_data(df_geo, population_2020)
    expected = pd.DataFrame(
        {
            "County": ["Shelby", "Davidson", "Knox"],
            "Population_2010": [100000, 200000, 150000],
            "Population_2020": [929744, 715884, 478971],
        }
    )

    pd.testing.assert_frame_equal(result_df.reset_index(drop=True), expected)


def test_load_csv(tmp_path):
    """Test the load_csv function with a sample CSV."""
    # Create a sample CSV file
    sample_csv_path = tmp_path / "sample_data.csv"
    sample_data = {
        "name": ["Autozone", "Napa Auto Parts"],
        "md_y": [35.0, 36.0],
        "md_x": [-86.0, -87.0],
    }
    pd.DataFrame(sample_data).to_csv(sample_csv_path, index=False)

    # Load the CSV using the function
    df = load_csv(str(sample_csv_path))
    assert not df.empty
    assert list(df["name"]) == ["Autozone", "Napa Auto Parts"]

    # No need to clean up as tmp_path handles it
