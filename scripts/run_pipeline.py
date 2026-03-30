import os

print("Running Full AI Pipeline...\n")

# Step 1 — Collect Data
print("Collecting Data...")
os.system("python scripts/collect_data.py")

# Step 2 — Process Data
print("\nProcessing Data...")
os.system("python scripts/process_data.py")

# Step 3 — Analyze Data
print("\nAnalyzing Data...")
os.system("python scripts/analyze_data.py")

# Step 4 — AI Enrichment
print("\nAI Enrichment...")
os.system("python scripts/ai_enrichment.py")

# Step 5 — Decision Engine
print("\nMaking Decisions...")
os.system("python scripts/decision_engine.py")

# Step 6 — Execution Engine
print("\nGenerating Execution Plans...")
os.system("python scripts/execution_engine.py")

# Step 7 — Trust Scoring
print("\nApplying Trust Scoring...")
os.system("python scripts/trust_scoring.py")

# Step 7 — Memory Engine
print("\nUpdating Memory...")
os.system("python scripts/memory_engine.py")

# Step 8 — Pattern Detection
print("\nDetecting Patterns...")
os.system("python scripts/pattern_engine.py")

# Step 9 — Strategy Engine
print("\nGenerating Strategy...")
os.system("python scripts/strategy_engine.py")

print("\nFULL PIPELINE COMPLETE")