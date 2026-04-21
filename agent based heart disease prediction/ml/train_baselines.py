import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import os

def train_lr_baseline():
    if not os.path.exists('data/uci_heart_disease.csv'):
        return
    
    df = pd.read_csv('data/uci_heart_disease.csv')
    X = df.drop(['target', 'patient_id'], axis=1)
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Logistic Regression
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train_scaled, y_train)
    
    acc = accuracy_score(y_test, lr.predict(X_test_scaled))
    print(f"Baseline LR Accuracy: {acc:.4f}")
    
    os.makedirs('ml/models', exist_ok=True)
    joblib.dump(lr, 'ml/models/baseline_lr.pkl')

if __name__ == "__main__":
    train_lr_baseline()
