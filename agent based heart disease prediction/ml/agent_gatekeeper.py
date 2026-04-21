import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

class AgentGatekeeper:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.is_fitted = False
        
    def fit(self, data):
        """
        Train the agent on historical vitals to learn "normal" vs "anomaly".
        data: DataFrame with ['heart_rate', 'bp_sys', 'bp_dia']
        """
        # We use HR and BP for fast specific anomaly detection
        features = data[['heart_rate', 'bp_sys', 'bp_dia']]
        self.model.fit(features)
        self.is_fitted = True
        
        # Save model
        os.makedirs('ml/models', exist_ok=True)
        joblib.dump(self.model, 'ml/models/agent_gatekeeper.pkl')
        print("Agent Gatekeeper trained and saved.")

    def load(self):
        try:
            self.model = joblib.load('ml/models/agent_gatekeeper.pkl')
            self.is_fitted = True
        except:
            print("Agent model not found. Please train first.")
            
    def check_stream(self, vital_stream):
        """
        Check a stream of vitals. Returns True if Anomaly (Risk), False if Normal (Safe).
        vital_stream: list of dicts or DataFrame
        """
        if not self.is_fitted:
            self.load()
            
        df = pd.DataFrame(vital_stream)
        features = df[['heart_rate', 'bp_sys', 'bp_dia']]
        
        # Isolation Forest returns -1 for anomaly, 1 for normal
        preds = self.model.predict(features)
        
        # If ANY point in the window is an anomaly, trigger the heavy model
        is_anomaly = -1 in preds
        return is_anomaly

if __name__ == "__main__":
    # Train on existing wearable data
    if os.path.exists('data/wearable_vitals.csv'):
        df = pd.read_csv('data/wearable_vitals.csv')
        # Train on a subset of 50k samples for speed
        agent = AgentGatekeeper(contamination=0.15) # 15% expected anomalies in our synthetic "high risk" focused data
        agent.fit(df.head(50000))
    else:
        print("No data found to train agent.")
