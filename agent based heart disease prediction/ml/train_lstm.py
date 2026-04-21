import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib
import os

def create_sequences(data, seq_length):
    xs = []
    ys = []
    for i in range(len(data) - seq_length):
        x = data[i:(i + seq_length), :-1]
        y = data[i + seq_length, -1]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

def train_lstm_model():
    if not os.path.exists('data/wearable_vitals.csv'):
        print("Wearable data not found.")
        return

    df = pd.read_csv('data/wearable_vitals.csv')
    
    # Feature selection
    # We use heart_rate, bp_sys, bp_dia, ecg_signal
    # For simulation, let's create a dummy target based on abnormal vitals
    df['target'] = ((df['heart_rate'] > 100) | (df['bp_sys'] > 140)).astype(int)
    
    features = ['heart_rate', 'bp_sys', 'bp_dia', 'ecg_signal', 'target']
    data = df[features].values
    
    # Scaling
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[['heart_rate', 'bp_sys', 'bp_dia', 'ecg_signal']])
    # Add target back
    processed_data = np.hstack([scaled_data, df[['target']].values])
    
    # Sequence length: 12 (e.g., 1 hour if 5-min intervals)
    SEQ_LENGTH = 12
    X, y = create_sequences(processed_data, SEQ_LENGTH)
    
    # Split
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    # Build LSTM
    model = Sequential([
        LSTM(64, input_shape=(SEQ_LENGTH, 4), return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    print("Training LSTM model...")
    model.fit(X_train, y_train, epochs=5, batch_size=32, validation_split=0.1, verbose=1)
    
    # Save
    os.makedirs('ml/models', exist_ok=True)
    model.save('ml/models/temporal_lstm_model.h5')
    joblib.dump(scaler, 'ml/models/lstm_scaler.pkl')
    print("LSTM model and scaler saved to ml/models/")

if __name__ == "__main__":
    train_lstm_model()
