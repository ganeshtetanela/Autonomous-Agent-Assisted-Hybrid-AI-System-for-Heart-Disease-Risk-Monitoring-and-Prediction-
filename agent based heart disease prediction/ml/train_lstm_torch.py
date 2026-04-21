import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
import joblib
import os

class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, layer_dim, output_dim):
        super(LSTMModel, self).__init__()
        self.hidden_dim = hidden_dim
        self.layer_dim = layer_dim
        self.lstm = nn.LSTM(input_dim, hidden_dim, layer_dim, batch_first=True, dropout=0.2)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Linear(16, output_dim),
            nn.Sigmoid()
        )

    def forward(self, x):
        h0 = torch.zeros(self.layer_dim, x.size(0), self.hidden_dim).to(x.device)
        c0 = torch.zeros(self.layer_dim, x.size(0), self.hidden_dim).to(x.device)
        out, (hn, cn) = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

def create_sequences(data, seq_length):
    print(f"Creating sequences from {len(data)} samples...")
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        if i % 50000 == 0:
            print(f"  Processed {i} sequences...")
        x = data[i:(i + seq_length), :-1]
        y = data[i + seq_length, -1]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)


def train_lstm_torch():
    print("Starting LSTM training script...")
    if not os.path.exists('data/wearable_vitals.csv'):
        print("Wearable data not found.")
        return

    df = pd.read_csv('data/wearable_vitals.csv')
    # Limit to 100k samples for efficiency while maintaining learning quality
    df = df.head(100000)
    df['target'] = ((df['heart_rate'] > 100) | (df['bp_sys'] > 140)).astype(int)

    
    scaler = StandardScaler()
    scaled_vitals = scaler.fit_transform(df[['heart_rate', 'bp_sys', 'bp_dia', 'ecg_signal']])
    processed_data = np.hstack([scaled_vitals, df[['target']].values])
    
    SEQ_LENGTH = 12
    X, y = create_sequences(processed_data, SEQ_LENGTH)
    
    split = int(0.8 * len(X))
    X_train, y_train = torch.FloatTensor(X[:split]), torch.FloatTensor(y[:split]).view(-1, 1)
    X_test, y_test = torch.FloatTensor(X[split:]), torch.FloatTensor(y[split:]).view(-1, 1)
    
    train_ds = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    
    input_dim = 4
    hidden_dim = 64
    layer_dim = 2
    output_dim = 1
    
    model = LSTMModel(input_dim, hidden_dim, layer_dim, output_dim)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print("Training PyTorch LSTM...")
    model.train()
    for epoch in range(10):
        for inputs, targets in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch+1}/10, Loss: {loss.item():.4f}")
    
    # Save
    os.makedirs('ml/models', exist_ok=True)
    torch.save(model.state_dict(), 'ml/models/temporal_lstm_torch.pth')
    joblib.dump(scaler, 'ml/models/lstm_scaler.pkl')
    # Save model config for reconstruction
    joblib.dump({'input_dim': 4, 'hidden_dim': 64, 'layer_dim': 2, 'output_dim': 1}, 'ml/models/lstm_config.pkl')
    print("PyTorch LSTM model and scaler saved.")

if __name__ == "__main__":
    train_lstm_torch()
