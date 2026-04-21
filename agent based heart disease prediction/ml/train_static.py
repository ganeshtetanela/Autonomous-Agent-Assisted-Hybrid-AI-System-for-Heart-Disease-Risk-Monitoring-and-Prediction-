import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import joblib
import os

def train_static_model():
    # Load dataset
    if not os.path.exists('data/uci_heart_disease.csv'):
        print("Dataset not found. Please run scripts/data_generator.py first.")
        return

    df = pd.read_csv('data/uci_heart_disease.csv')
    
    # Preprocessing
    # Features: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
    X = df.drop(['target', 'patient_id'], axis=1)
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, model.predict_proba(X_test_scaled)[:, 1])
    
    print(f"Static Model Accuracy: {accuracy:.4f}")
    print(f"Static Model ROC-AUC: {auc:.4f}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    
    # Save model, scaler and SHAP background data
    os.makedirs('ml/models', exist_ok=True)
    joblib.dump(model, 'ml/models/static_rf_model.pkl')
    joblib.dump(scaler, 'ml/models/static_scaler.pkl')
    joblib.dump(X_train_scaled[:100], 'ml/models/shap_background.pkl')
    print("Static model, scaler, and SHAP background saved to ml/models/")

if __name__ == "__main__":
    train_static_model()
