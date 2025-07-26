import subprocess

print("Starting full synthetic dialog pipeline...\n")

# === Step 1: Generate specifications and dialogs
print("\n ️ Step 1: Running batch_generate.py...")
subprocess.run(["python", "src/batch_generate.py"], check=True)

# === Step 2: Repair failed specifications (if any)
print("\n Step 2: Running repair_failed_specs.py...")
subprocess.run(["python", "src/repair_failed_specs.py"], check=True)

# === Step 3: Evaluate generated dialogs
print("\n Step 3: Running batch_evaluate.py...")
subprocess.run(["python", "src/batch_evaluate.py"], check=True)

print("\n✅ DONE: All tasks completed successfully.")
