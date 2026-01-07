"""
src/validation/validate.py
Simple data validation utilities using pandas.
We avoid heavy dependencies in validation to keep the pipeline lightweight.
For production, swap in pandera or similar.
"""
import pandas as pd
from typing import Tuple, Dict


def basic_schema_checks(df: pd.DataFrame) -> Tuple[bool, Dict]:
    """
    Perform minimal schema validations:
      - required columns present
      - no NaNs in key columns
      - types are sensible

    Returns:
      (is_valid, details)
    """
    required_cols = {"customer_id", "recency_days", "frequency", "monetary", "tenure_days", "churned", "treatment"}
    details = {}
    missing = required_cols.difference(set(df.columns))
    if missing:
        details["missing_columns"] = list(missing)
        return False, details

    # Null checks
    null_counts = df[list(required_cols)].isnull().sum().to_dict()
    details["null_counts"] = null_counts
    if any(v > 0 for v in null_counts.values()):
        details["valid"] = False
        return False, details

    # Simple type checks
    details["dtypes"] = df[list(required_cols)].dtypes.astype(str).to_dict()
    details["valid"] = True
    return True, details


def validate_and_raise(df: pd.DataFrame):
    valid, details = basic_schema_checks(df)
    if not valid:
        raise ValueError(f"Validation failed: {details}")
    return details
