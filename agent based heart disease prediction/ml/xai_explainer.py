import shap
import joblib
import pandas as pd
import numpy as np

class HeartXAI:
    def __init__(self, model_path='ml/models/static_rf_model.pkl', 
                 background_path='ml/models/shap_background.pkl'):
        self.model = joblib.load(model_path)
        self.background = joblib.load(background_path)
        # Use TreeExplainer for Random Forest
        self.explainer = shap.TreeExplainer(self.model, self.background)
        self.feature_names = [
            'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 
            'restecg', 'thalach', 'exang', 'oldpeak', 
            'slope', 'ca', 'thal'
        ]

    def get_explanation(self, input_scaled):
        """
        input_scaled: a 2D numpy array (1, n_features)
        Returns a dict of feature names and their SHAP values (contribution)
        """
        shap_values = self.explainer.shap_values(input_scaled, check_additivity=False)
        
        # for binary classification with RF, shap_values is a list of [shap_class0, shap_class1]
        # we care about class 1 (heart disease)
        if isinstance(shap_values, list):
            vals = shap_values[1][0]
        else:
            # Newer SHAP versions return a single array for binary if using TreeExplainer on some models
            # but usually it's [..., output_index]
            if len(shap_values.shape) == 3:
                vals = shap_values[0, :, 1]
            else:
                vals = shap_values[0]

        explanation = {}
        for name, val in zip(self.feature_names, vals):
            explanation[name] = float(val)
        
        return explanation

    def get_top_contributors(self, input_scaled, top_n=3):
        explanation = self.get_explanation(input_scaled)
        # Sort by absolute contribution
        sorted_feats = sorted(explanation.items(), key=lambda x: abs(x[1]), reverse=True)
        return sorted_feats[:top_n]

if __name__ == "__main__":
    # Test
    xai = HeartXAI()
    test_input = np.random.randn(1, 13)
    print("SHAP explanation:", xai.get_explanation(test_input))
