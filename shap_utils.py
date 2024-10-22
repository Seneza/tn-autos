# shap_utils.py
import shap
import matplotlib.pyplot as plt
import io
import base64

class SHAPUtils:
    @staticmethod
    def get_shap_values(model, X_train, X_test):
        explainer = shap.Explainer(model, X_train)
        return explainer(X_test)

    @staticmethod
    def get_shap_summary_plot(shap_values, X_test):
        plt.figure()
        shap.summary_plot(shap_values, X_test, show=False)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"
