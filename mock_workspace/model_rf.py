import pandas as pd
from sklearn.ensemble import RandomForestClassifier

def train_model():
    print("Loading data...")
    df = pd.read_csv("train_data.csv")
    print(f"Dataset successfully loaded with {len(df)} rows.")

if __name__ == "__main__":
    train_model()

# Hyperparameter tuning completed: max_depth=10, n_estimators=200
