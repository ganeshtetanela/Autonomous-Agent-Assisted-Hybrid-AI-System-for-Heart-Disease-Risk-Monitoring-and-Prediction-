import pandas as pd
import numpy as np
import random
from ml.prediction_pipeline import HybridPredictionPipeline
from ml.agent_gatekeeper import AgentGatekeeper
import time

def evaluate():
    print("Loading data and models...")
    df_static = pd.read_csv('data/uci_heart_disease.csv')
    df_wearable = pd.read_csv('data/wearable_vitals.csv')
    
    pipeline = HybridPredictionPipeline()
    agent = AgentGatekeeper()
    agent.load()
    
    # Select 20 random patients for simulation
    patient_ids = df_static['patient_id'].sample(20, random_state=42).tolist()
    
    results = []
    
    print("\nStarting Comparison Simulation (20 Patients)...")
    print("-" * 60)
    
    total_windows = 0
    
    # Metrics
    no_agent_calls = 0
    no_agent_detected = 0
    
    with_agent_calls = 0
    with_agent_detected = 0
    agent_triggers = 0
    
    start_time = time.time()
    
    for pid in patient_ids:
        clinical_full = df_static[df_static['patient_id'] == pid].iloc[0].to_dict()
        true_label = clinical_full['target']
        
        # Filter for model input (exclude metadata)
        clinical = {k: v for k, v in clinical_full.items() if k not in ['patient_id', 'target']}
        
        # Get patient vitals

        p_vitals = df_wearable[df_wearable['patient_id'] == pid]
        
        # Simulate sliding window of 12 steps (1 hour)
        # We take 5 random windows per patient to simulate monitoring
        for _ in range(5):
            if len(p_vitals) < 12: break
            
            start_idx = random.randint(0, len(p_vitals) - 12)
            window = p_vitals.iloc[start_idx : start_idx+12][['heart_rate', 'bp_sys', 'bp_dia', 'ecg_signal']].to_dict('records')
            
            total_windows += 1
            
            # --- SCENARIO 1: WITHOUT AGENT (Continuous) ---
            no_agent_calls += 1 # Always call hybrid
            res_no_agent = pipeline.predict(clinical, window)
            if res_no_agent['risk_score'] > 0.5:
                no_agent_detected += 1
                
            # --- SCENARIO 2: WITH AGENT (Event-Driven) ---
            # 1. Agent Check (Fast)
            is_anomaly = agent.check_stream(window)
            
            if is_anomaly:
                agent_triggers += 1
                with_agent_calls += 1 # Call hybrid only if trigger
                res_with_agent = pipeline.predict(clinical, window)
                if res_with_agent['risk_score'] > 0.5:
                    with_agent_detected += 1
            else:
                # Agent says safe -> Implicit "Low Risk" (0.0)
                pass 
                
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nSimulation Complete in {duration:.2f}s")
    print("-" * 60)
    print(f"Total Monitoring Windows: {total_windows}")
    print("\n--- WITHOUT AGENT (Continuous Monitoring) ---")
    print(f"Hybrid Model Computations: {no_agent_calls} (100% of windows)")
    print(f"High Risk Alerts Generated: {no_agent_detected}")
    
    print("\n--- WITH AGENT (Event-Driven Monitoring) ---")
    print(f"Agent Triggers: {agent_triggers}")
    print(f"Hybrid Model Computations: {with_agent_calls} ({with_agent_calls/total_windows*100:.1f}% of windows)")
    print(f"High Risk Alerts Generated: {with_agent_detected}")
    
    efficiency = (1 - (with_agent_calls / no_agent_calls)) * 100
    print("-" * 60)
    print(f"COMPUTATIONAL EFFICIENCY GAIN: {efficiency:.1f}%")
    print("-" * 60)

    # Verification: Did Agent miss any alerts?
    # In a perfect agent, with_agent_detected == no_agent_detected
    missed = no_agent_detected - with_agent_detected
    print(f"Missed Alerts (False Negatives by Agent): {missed}")
    if missed == 0:
        print("PERFORMANCE: 100% Retention of High-Risk Alerts.")
    else:
        print(f"PERFORMANCE: Agent filtered {missed} potential alerts (Trade-off).")

if __name__ == "__main__":
    evaluate()
