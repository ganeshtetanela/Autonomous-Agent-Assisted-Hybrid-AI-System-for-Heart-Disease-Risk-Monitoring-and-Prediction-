import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os
import logging

# Configure logging for agent explainability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - AGENT_DECISION - %(message)s')
logger = logging.getLogger(__name__)

class HeartMonitoringAgent:
    def __init__(self, model_path='agent/models/iso_forest.pkl'):
        self.model_path = model_path
        self.iso_forest = self._load_or_train_anomaly_detector()
        
        # Medical Thresholds (Rules)
        self.thresholds = {
            'heart_rate': {'min': 50, 'max': 100},
            'bp_sys': {'max': 140},
            'bp_dia': {'max': 90}
        }
        self.history = []
        self.adaptive_thresholds = self.thresholds.copy()

    def _update_adaptive_logic(self, vital_data):
        """
        IEEE Novelty: Personalization Branch
        Learns from patient's own baseline to adjust sensitivity.
        """
        self.history.append(vital_data)
        if len(self.history) >= 20: # Start adapting after 20 samples
            hist_df = pd.DataFrame(self.history[-50:]) # Look at last 50
            hr_mean = hist_df['heart_rate'].mean()
            hr_std = hist_df['heart_rate'].std()
            
            # Adjust max HR if patient has a naturally high/low baseline
            # But never exceed medical safety limits (e.g. 110)
            target_max = min(110, hr_mean + 2 * hr_std)
            if abs(target_max - self.adaptive_thresholds['heart_rate']['max']) > 2:
                self.adaptive_thresholds['heart_rate']['max'] = target_max
                logger.info(f"Agent adapted HR threshold to {target_max:.1f} based on patient profile.")

    def _load_or_train_anomaly_detector(self):
        if os.path.exists(self.model_path):
            return joblib.load(self.model_path)
        
        # Train on synthetic wearable data if model doesn't exist
        logger.info("Training Isolation Forest Anomaly Detector...")
        if os.path.exists('data/wearable_vitals.csv'):
            data = pd.read_csv('data/wearable_vitals.csv')
            features = ['heart_rate', 'bp_sys', 'bp_dia', 'ecg_signal']
            model = IsolationForest(contamination=0.05, random_state=42)
            model.fit(data[features])
            os.makedirs('agent/models', exist_ok=True)
            joblib.dump(model, self.model_path)
            return model
        return None

    def calculate_health_score(self, vital_data):
        """
        Calculates a composite health score (0-100).
        Starts at 100, deducts points for deviations.
        """
        score = 100
        hr = vital_data.get('heart_rate')
        bp_s = vital_data.get('blood_pressure_sys') or vital_data.get('bp_sys')
        
        if hr is not None:
            # Sensitive penalty: Deviate from perfect 72 BPM
            # even small changes like 75 vs 72 will drop score slightly (e.g. 99)
            # making it feel "alive"
            dist_opt = abs(hr - 72)
            score -= dist_opt * 0.4
            
        if bp_s is not None:
            # Sensitive penalty: Deviate from perfect 120 mmHg
            dist_bp = abs(bp_s - 120)
            score -= dist_bp * 0.2
            
        return max(0, int(score))

    def analyze_trends(self):
        """
        Detects slow drifts in vitals over the last 5 readings.
        """
        if len(self.history) < 5:
            return []
            
        recent = pd.DataFrame(self.history[-5:])
        trends = []
        
        # Check for monotonic increase in HR
        if 'heart_rate' in recent.columns and recent['heart_rate'].is_monotonic_increasing:
             if (recent['heart_rate'].iloc[-1] - recent['heart_rate'].iloc[0] > 5):
                trends.append("Heart Rate rising steadily")
            
        # Check for monotonic increase in BP
        if 'bp_sys' in recent.columns and recent['bp_sys'].is_monotonic_increasing:
             if (recent['bp_sys'].iloc[-1] - recent['bp_sys'].iloc[0] > 10):
                trends.append("Systolic BP rising steadily")
                
        return trends

    def analyze_vitals(self, vital_data):
        """
        Analyzes a single record or window of vitals.
        Handles both abbreviated (bp_sys) and full (blood_pressure_sys) keys.
        """
        # Normalize keys
        hr = vital_data.get('heart_rate')
        bp_s = vital_data.get('blood_pressure_sys') or vital_data.get('bp_sys')
        bp_d = vital_data.get('blood_pressure_dia') or vital_data.get('bp_dia')
        ecg = vital_data.get('ecg_signal')

        # Personalization Update
        if all(v is not None for v in [hr, bp_s, bp_d, ecg]):
            self._update_adaptive_logic({'heart_rate': hr, 'bp_sys': bp_s, 'bp_dia': bp_d, 'ecg_signal': ecg})

        reasons = []
        should_trigger = False
        
        # 0. Health Score & Trends
        health_score = self.calculate_health_score({'heart_rate': hr, 'bp_sys': bp_s})
        trends = self.analyze_trends()
        if trends:
            reasons.extend(trends)
            # Trends alone might not trigger emergency, but worth noting
        
        # 1. Rule-Based Check (Using ADAPTIVE Thresholds)
        if hr is not None:
            if hr > self.adaptive_thresholds['heart_rate']['max'] or hr < self.adaptive_thresholds['heart_rate']['min']:
                reasons.append(f"Heart rate ({hr}) outside personal normal range ({self.adaptive_thresholds['heart_rate']['min']}-{self.adaptive_thresholds['heart_rate']['max']:.1f}).")
                should_trigger = True
            
        if bp_s is not None:
            if bp_s > self.adaptive_thresholds['bp_sys']['max']:
                reasons.append(f"Systolic BP ({bp_s}) exceeds threshold.")
                should_trigger = True

        # 2. ML-Based Anomaly Detection (Isolation Forest)
        if self.iso_forest and all(v is not None for v in [hr, bp_s, bp_d, ecg]):
            features = np.array([[hr, bp_s, bp_d, ecg]])
            # Ensure features are in same order as training: heart_rate, bp_sys, bp_dia, ecg_signal
            is_anomaly = self.iso_forest.predict(features)[0] == -1
            if is_anomaly:
                reasons.append("ML model detected unusual pattern in vital streams.")
                should_trigger = True

        decision = {
            "trigger_prediction": should_trigger,
            "reasons": reasons,
            "confidence": 0.85 if should_trigger else 0.95,
            "health_score": health_score,
            "trends": trends
        }
        
        if should_trigger:
            logger.warning(f"Prediction Triggered: {', '.join(reasons)}")
        
        return decision

if __name__ == "__main__":
    # Test the agent
    agent = HeartMonitoringAgent()
    normal_vitals = {'heart_rate': 75, 'bp_sys': 120, 'bp_dia': 80, 'ecg_signal': 0.1}
    abnormal_vitals = {'heart_rate': 120, 'bp_sys': 150, 'bp_dia': 95, 'ecg_signal': -0.5}
    
    print("Normal Vitals Check:", agent.analyze_vitals(normal_vitals))
    print("Abnormal Vitals Check:", agent.analyze_vitals(abnormal_vitals))
