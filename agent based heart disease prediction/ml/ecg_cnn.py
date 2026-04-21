import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class ECGCNN(nn.Module):
    def __init__(self):
        super(ECGCNN, self).__init__()
        # Input: (Batch, 1, 100) - Simulating a window of ECG signal
        self.conv_layers = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )
        self.fc_layers = nn.Sequential(
            nn.Linear(32 * 25, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        # x shape: (Batch, 1, 100)
        x = self.conv_layers(x)
        x = x.view(x.size(0), -1)
        x = self.fc_layers(x)
        return x

def train_cnn_stub():
    model = ECGCNN()
    # Mock training for demonstration
    print("Initializing ECG CNN Branch...")
    torch.save(model.state_dict(), 'ml/models/ecg_cnn.pth')
    print("ECG CNN weights saved.")

if __name__ == "__main__":
    train_cnn_stub()
