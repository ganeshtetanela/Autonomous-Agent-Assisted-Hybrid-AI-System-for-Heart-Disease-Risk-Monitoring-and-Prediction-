import joblib
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from prediction_pipeline import HybridPredictionPipeline, LSTMModel

def evaluate_model(name, y_true, y_pred_prob, threshold=0.5):
    y_pred = (y_pred_prob >= threshold).astype(int)
    return {
        "Model": name,
        "Accuracy": f"{accuracy_score(y_true, y_pred)*100:.1f}%",
        "Precision": f"{precision_score(y_true, y_pred)*100:.1f}%",
        "Recall": f"{recall_score(y_true, y_pred)*100:.1f}%",
        "F1-score": f"{f1_score(y_true, y_pred)*100:.1f}%"
    }

def generate_table_i():
    print("Generating Performance Report (Table I)...")
    
    # Load test data
    df_static = pd.read_csv('data/uci_heart_disease.csv')
    X_static = df_static.drop(['target', 'patient_id'], axis=1)
    y_static = df_static['target'].values
    
    # Static Scaler
    scaler_static = joblib.load('ml/models/static_scaler.pkl')
    X_static_scaled = scaler_static.transform(X_static)
    
    # 1. Logistic Regression
    lr = joblib.load('ml/models/baseline_lr.pkl')
    lr_probs = lr.predict_proba(X_static_scaled)[:, 1]
    res_lr = evaluate_model("Logistic Regression", y_static, lr_probs)
    
    # 2. Random Forest
    rf = joblib.load('ml/models/static_rf_model.pkl')
    rf_probs = rf.predict_proba(X_static_scaled)[:, 1]
    res_rf = evaluate_model("Random Forest", y_static, rf_probs)
    
    # 3. LSTM (Wearable Data)
    # For a fair "Table I" comparison, we evaluate on a batch of windows
    pipeline = HybridPredictionPipeline()
    df_wearable = pd.read_csv('data/wearable_vitals.csv')
    
    # Sample 100 test cases
    lstm_results = []
    y_lstm_true = []
    
    pids = df_wearable['patient_id'].unique()[:50]
    for pid in pids:
        patient_data = df_wearable[df_wearable['patient_id'] == pid].tail(12)
        if len(patient_data) < 12: continue
        
        # Ground truth: if any HR > 100 or BP > 140 in the window (simplified for report)
        true_label = 1 if (patient_data['heart_rate'] > 100).any() or (patient_data['bp_sys'] > 140).any() else 0
        
        window = patient_data[['heart_rate', 'bp_sys', 'bp_dia', 'ecg_signal']].to_dict('records')
        with torch.no_grad():
            lstm_input = pipeline._prepare_lstm_input(window)
            prob = pipeline.lstm_model(lstm_input).item()
            
        lstm_results.append(prob)
        y_lstm_true.append(true_label)
        
    res_lstm = evaluate_model("LSTM (Wearable Data)", np.array(y_lstm_true), np.array(lstm_results))
    
    # 4. Proposed Hybrid Model
    hybrid_probs = []
    y_hybrid_true = []
    
    # We evaluate on the combined "cases"
    for i in range(min(100, len(X_static))):
        clinical = X_static.iloc[i].to_dict()
        pid = df_static.iloc[i]['patient_id']
        
        # Build a realistic window for this patient
        patient_wearable = df_wearable[df_wearable['patient_id'] == pid].tail(12)
        if len(patient_wearable) < 12:
            # Fallback to dummy but patterned window if patient not in wearable (shouldn't happen with seed)
            window = [{'heart_rate': 75, 'bp_sys': 120, 'bp_dia': 80, 'ecg_signal': 0.1} for _ in range(12)]
        else:
            window = patient_wearable[['heart_rate', 'bp_sys', 'bp_dia', 'ecg_signal']].to_dict('records')
            
        res = pipeline.predict(clinical, window)
        hybrid_probs.append(res['risk_score'])
        # Hybrid ground truth is based on the static clinical label
        y_hybrid_true.append(y_static[i])
        
    res_hybrid = evaluate_model("Proposed Hybrid Model", np.array(y_hybrid_true), np.array(hybrid_probs), threshold=0.5)



    
    # Compile Table
    report_df = pd.DataFrame([res_lr, res_rf, res_lstm, res_hybrid])
    print("\n" + "="*60)
    print("TABLE I: PERFORMANCE COMPARISON")
    print("="*60)
    print(report_df.to_string(index=False))
    print("="*60)

if __name__ == "__main__":
    generate_table_i()
