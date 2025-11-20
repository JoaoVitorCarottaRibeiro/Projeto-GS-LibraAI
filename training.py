import pandas as pd
import glob
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import joblib


files = glob.glob('data/gesto_*.csv')
if not files:
    raise FileNotFoundError("Nenhum arquivo CSV encontrado em 'data/'. Capture os gestos primeiro.")


dfs = [pd.read_csv(f) for f in files]
df = pd.concat(dfs, ignore_index=True)


X = df.drop('label', axis=1).values
y = df['label'].values


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


model = make_pipeline(StandardScaler(), SVC(kernel='rbf', probability=True, C=5, gamma='scale'))
model.fit(X_train, y_train)
acc = model.score(X_test, y_test)
print(f"[OK] Acurácia de teste: {acc:.2%}")


joblib.dump(model, 'modelo_gestos.pkl')
np.save('X_train.npy', X_train)
print("[OK] Modelo salvo como 'modelo_gestos.pkl' e X_train.npy salvo")