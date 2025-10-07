import os

# Define folder structure
folders = [
    "backend/config",
    "backend/modules",
    "backend/database",
    "backend/utils",
    "frontend/css",
    "frontend/js",
    "frontend/components",
    "data",
    "tests",
    "docs"
]

# Define files to create
files = [
    "README.md",
    ".gitignore",
    "backend/app.py",
    "backend/requirements.txt",
    "backend/config/config.yaml",
    "backend/database/db.py",
    "backend/utils/helpers.py",
    "backend/modules/user_profile.py",
    "backend/modules/simulation_engine.py",
    "backend/modules/metrics_calculator.py",
    "backend/modules/scenario_comparator.py",
    "backend/modules/tips_generator.py",
    "frontend/index.html",
    "frontend/css/styles.css",
    "frontend/js/simulation_ui.js",
    "frontend/js/visualization.js",
    "frontend/components/profile_form.js",
    "frontend/components/scenario_selector.js",
    "frontend/components/result_dashboard.js",
    "data/nutrition_facts.csv",
    "data/exercise_effects.csv",
    "data/sleep_effects.csv",
    "tests/test_simulation.py",
    "tests/test_metrics.py",
    "docs/architecture.md",
    "docs/user_manual.md"
]

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create files
for file in files:
    with open(file, "w", encoding="utf-8") as f:
        # Add a small placeholder for README and .gitignore
        if file == "README.md":
            f.write("# Medical Clone\n\nAI-driven body effect simulator project.")
        elif file == ".gitignore":
            f.write("__pycache__/\n*.pyc\n*.pkl\n.env\n.DS_Store")
        else:
            pass  # leave other files empty

print("✅ Medical Clone project structure created successfully!")
