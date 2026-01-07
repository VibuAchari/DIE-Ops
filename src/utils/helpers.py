"""
src/utils/helpers.py
Small utility functions used across the project.
"""
import os
import json
import joblib

def ensure_dirs(path_list):
    for p in path_list:
        os.makedirs(p, exist_ok=True)

def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

def load_joblib(path):
    return joblib.load(path)
