import os

# Root directory name
root = "die-ops-customer-intel"

# All directories to create
dirs = [
    f"{root}/data",
    f"{root}/src/ingest",
    f"{root}/src/validation",
    f"{root}/src/features",
    f"{root}/src/models",
    f"{root}/src/decision_engine",
    f"{root}/src/api",
    f"{root}/src/dashboard",
    f"{root}/src/explain",
    f"{root}/src/utils",
    f"{root}/notebooks",
    f"{root}/docker",
    f"{root}/.github/workflows",
    f"{root}/docs",
]

# All files to create
files = [
    f"{root}/src/ingest/ingest.py",
    f"{root}/src/validation/validate.py",
    f"{root}/src/features/featurize.py",
    f"{root}/src/models/train_churn.py",
    f"{root}/src/models/train_cltv.py",
    f"{root}/src/models/train_uplift.py",
    f"{root}/src/decision_engine/optimizer.py",
    f"{root}/src/api/main.py",
    f"{root}/src/dashboard/app.py",
    f"{root}/src/explain/shap_narrative.py",
    f"{root}/src/utils/helpers.py",
    f"{root}/docker/Dockerfile",
    f"{root}/.github/workflows/ci.yml",
    f"{root}/requirements.txt",
    f"{root}/README.md",
    f"{root}/docs/architecture.md",
    f"{root}/docs/assumptions.md",
]

# Create directories
for d in dirs:
    os.makedirs(d, exist_ok=True)

# Create empty files
for f in files:
    with open(f, "w") as fp:
        pass

print("Project structure created successfully.")
