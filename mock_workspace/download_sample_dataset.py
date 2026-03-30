import os
import json
import random
import string
import shutil

def setup_demo_workspace():
    # 1. Clean old workspace datahub cache if it exists (for fresh starts)
    if os.path.exists('.datahub'):
        shutil.rmtree('.datahub')

    print("[1/3] Creating mock Machine Learning dataset 'train_data.csv'...")
    with open('train_data.csv', 'w') as f:
        f.write("id,feature_A,feature_B,target\n")
        for i in range(15000):
            a = random.random() * 10
            b = random.random() * 5
            t = int(a + b > 7.5)
            f.write(f"{i},{a:.4f},{b:.4f},{t}\n")
            
    print("[2/3] Creating initial python source code 'model_rf.py'...")
    with open('model_rf.py', 'w') as f:
        f.write('''import pandas as pd
from sklearn.ensemble import RandomForestClassifier

def train_model():
    print("Loading data...")
    df = pd.read_csv("train_data.csv")
    print(f"Dataset successfully loaded with {len(df)} rows.")

if __name__ == "__main__":
    train_model()
''')

    print("[3/3] Creating experimental model metrics 'metrics.json'...")
    stats = {
        "accuracy": 0.81,
        "f1_score": 0.79,
        "loss": 0.18,
        "model_version": "v1.0-baseline"
    }
    with open('metrics.json', 'w') as f:
        json.dump(stats, f, indent=4)

    print("\n✅ Dataset Ready. Total directory contents generated.")

if __name__ == "__main__":
    setup_demo_workspace()
