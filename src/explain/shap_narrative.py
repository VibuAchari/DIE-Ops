"""
src/explain/shap_narrative.py
Generate local SHAP explanations and convert them to a short human-readable narrative.
If SHAP is not available or fails, fallback to a generic narrative.
"""
import shap
import numpy as np
import pandas as pd

def narrative_from_shap(model, X_row, feature_cols, top_k=3):
    """
    Compute SHAP values and return a templated sentence explaining top drivers.
    X_row: DataFrame with single row and feature columns
    """
    try:
        explainer = shap.Explainer(model.predict_proba, X_row)
        shap_vals = explainer(X_row)
        # shap_vals.values is shape (1, n_features, 2) for probabilistic models; handle gracefully
        # We'll compute contribution to class 1
        if hasattr(shap_vals, "values"):
            # try to extract class 1 contributions
            vals = np.array(shap_vals.values)
            # handle different shapes
            if vals.ndim == 3:
                contribs = vals[0, :, 1]
            else:
                contribs = vals[0, :]
        else:
            contribs = shap_vals.values[0]

        feature_importance = sorted(zip(feature_cols, contribs), key=lambda x: -abs(x[1]))[:top_k]
        parts = []
        for f, v in feature_importance:
            sign = "increases" if v > 0 else "decreases"
            parts.append(f"{f} {sign} risk (impact {v:.3f})")
        return "Top drivers: " + "; ".join(parts) + "."
    except Exception as e:
        return f"Explanation not available: {e}"
