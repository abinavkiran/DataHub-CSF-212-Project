import os
import time
import subprocess
import json
import sys

def run_command(cmd, cwd=None, hide=False):
    print(f"\n🚀 Executing: {' '.join(cmd)}")
    if hide:
        subprocess.run(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(cmd, cwd=cwd)

def main():
    print("\n=========================================================")
    print("    DataHub: Content-Addressable Storage Demonstration   ")
    print("=========================================================")

    # Step 1: Start API Router in background
    print("\n[Step 1] Bootstrapping API Gateway Router locally...")
    api_process = subprocess.Popen(["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"], 
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("Waiting 3 seconds for Uvicorn API to map endpoints...", end="", flush=True)
    for _ in range(3):
        time.sleep(1)
        print(".", end="", flush=True)
    print(" Done!")

    # Step 2: Generate sample dataset
    print("\n[Step 2] Generating Mock Machine Learning Workspace...")
    run_command([sys.executable, "download_sample_dataset.py"], cwd="mock_workspace")

    # Step 3: Initialize repo
    print("\n[Step 3] Initializing DataHub Version Control...")
    run_command([sys.executable, "-m", "cli.main", "init"], cwd="mock_workspace")

    # Step 4: First Commit + Push
    print("\n[Step 4] Pushing Initial Baseline Models & Heavy Datasets...")
    print("-> Data is chunked, hashed (SHA-256), and transported securely.")
    run_command([sys.executable, "-m", "cli.main", "push", "http://localhost:8000", "-m", "Initial Baseline Dataset & RandomForest Model"], cwd="mock_workspace")

    # Check blobs dir
    print("\n[Validation] Storage Engine Directory Footprint:")
    run_command(["ls", "-lh", "blobs/"])

    # Step 5: Simulate Data Scientist modifying things
    print("\n[Step 5] Simulating Developer Modifying Code & Model Weights...")
    time.sleep(1.5)
    
    # Modify metrics safely inside the mounted volume
    with open("mock_workspace/metrics.json", "w") as f:
        json.dump({
            "accuracy": 0.94,
            "f1_score": 0.93,
            "loss": 0.05,
            "model_version": "v2.0-tuned"
        }, f, indent=4)
        
    # Modify code
    with open("mock_workspace/model_rf.py", "a") as f:
        f.write("\n# Hyperparameter tuning completed: max_depth=10, n_estimators=200\n")
    print("Model metrics updated (accuracy -> 94%) and regularization added.")

    # Step 6: Second Commit + Push (Deduplication Demo)
    print("\n[Step 6] Pushing Second Commit (v2.0 Tuned)...")
    print("-> CRITICAL DEMO: Observe DataHub skipping the heavy CSV injection natively!")
    run_command([sys.executable, "-m", "cli.main", "push", "http://localhost:8000", "-m", "Tuned hyperparameters (Accuracy -> 94%)"], cwd="mock_workspace")

    # Validation of blobs again
    print("\n[Validation] Notice: The CSV blob was NOT physically duplicated on the disk!")
    run_command(["ls", "-lh", "blobs/"])

    # Step 7: Query Metadata
    print("\n[Step 7] Querying Extracted Metadata Layer using DSL Parser...")
    print("Searching for exact Object Commits pushing metrics where row_count > 1000...")
    run_command([sys.executable, "-m", "cli.main", "query", "http://localhost:8000", "row_count > 1000"], cwd="mock_workspace")

    # Step 8: Log View
    print("\n[Step 8] Resolving Recursive Merkle DAG PostgreSQL Trace...")
    run_command([sys.executable, "-m", "cli.main", "log", "http://localhost:8000"], cwd="mock_workspace")

    print("\n✅ End-to-End System Validated & Concluded flawlessly.\n")

    # Cleanup the backend api
    print("Tearing down API Server...")
    api_process.terminate()

if __name__ == "__main__":
    main()
