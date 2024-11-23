"""A module for shap_utils."""
# shap_utils.py

import base64
import io

import matplotlib.pyplot as plt
import shap


class SHAPUtils:
    """
    A utility class for generating SHAP values and visualizations.

    This class provides static methods to compute SHAP values for a given model and dataset,
    and to create summary plots of the SHAP values.
    """

    @staticmethod
    def get_shap_values(model, X_train, X_test):
        """
        Compute SHAP values for the test dataset using the provided model.

        Parameters:
            model: The trained machine learning model for which SHAP values are to be computed.
            X_train: Training feature dataset used to initialize the SHAP explainer.
            X_test: Testing feature dataset for which SHAP values are to be calculated.

        Returns:
            shap.Explanation: An object containing the SHAP values for the test dataset.
        """
        explainer = shap.Explainer(model, X_train)
        return explainer(X_test)

    @staticmethod
    def get_shap_summary_plot(shap_values, X_test):
        """
        Generate a SHAP summary plot and return it as a base64-encoded PNG image.

        This method creates a summary plot of the SHAP values, saves the plot to an in-memory buffer,
        and encodes the image in base64 format for easy embedding in web applications.

        Parameters:
            shap_values: The SHAP values computed for the test dataset.
            X_test: The testing feature dataset used for generating the summary plot.

        Returns:
            str: A base64-encoded PNG image of the SHAP summary plot.
        """
        plt.figure()
        shap.summary_plot(shap_values, X_test, show=False)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)
        return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"
