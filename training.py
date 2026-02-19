import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

DATA_DIR = "data2"
MODEL_PATH = "modelo_gestos.pkl"

dfs = []

for file in os.listdir(DATA_DIR):
    if file.endswith(".csv"):
        df = pd.read_csv(os.path.join(DATA_DIR, file))
        dfs.append(df)

data = pd.concat(dfs, ignore_index=True)

X = data.drop("label", axis=1).values
y = data["label"].values

print("[INFO] Features:", X.shape)
print("[INFO] Labels:", set(y))

np.save("X_train.npy", X)

model = RandomForestClassifier(
    n_estimators=250,
    max_depth=25,
    random_state=42
)

model.fit(X, y)

joblib.dump(model, MODEL_PATH)

print("[OK] Modelo treinado e salvo!")
print("[OK] modelo_gestos.pkl")
