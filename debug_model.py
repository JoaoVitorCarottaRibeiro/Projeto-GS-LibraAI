import joblib

model = joblib.load("modelo_gestos.pkl")

print("Features esperadas:", model.n_features_in_)
print("Classes:", model.classes_)
