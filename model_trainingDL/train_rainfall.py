import os
import torch
import torch.nn as nn
import torch.optim as optim
from dataloader import prepare_data
from models import RainfallMLP
import joblib
import matplotlib.pyplot as plt

# =========================
# CONFIGURATION
# =========================
DATA_PATH = "data/processed/training_dataset_gujarat_advanced_labeled.csv"
MODEL_SAVE_PATH = "DLmodels/rainfall_model.pth"
SCALER_SAVE_PATH = "DLmodels/rainfall_scaler.pkl"
BATCH_SIZE = 64
EPOCHS = 30
LEARNING_RATE = 0.001
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

def train():
    os.makedirs("DLmodels", exist_ok=True)
    
    # 1. Load Data
    print(f"📂 Loading data for RAINFALL REGRESSION...")
    train_loader, test_loader, scaler, input_dim = prepare_data(DATA_PATH, task_type="regression", batch_size=BATCH_SIZE)
    
    # 2. Initialize Model
    model = RainfallMLP(input_dim).to(DEVICE)
    criterion = nn.MSELoss() # For regression
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # 3. Training Loop
    print(f"🚀 Starting Rainfall training on {DEVICE}...")
    history = {"train_loss": [], "test_loss": []}
    
    best_loss = float('inf')
    
    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0.0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
        # Validation
        model.eval()
        test_loss = 0.0
        with torch.no_grad():
            for X_batch, y_batch in test_loader:
                X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                test_loss += loss.item()
        
        avg_train_loss = train_loss / len(train_loader)
        avg_test_loss = test_loss / len(test_loader)
        
        history["train_loss"].append(avg_train_loss)
        history["test_loss"].append(avg_test_loss)
        
        if (epoch+1) % 5 == 0:
            print(f"Epoch [{epoch+1}/{EPOCHS}] - Train MSE: {avg_train_loss:.4f}, Test MSE: {avg_test_loss:.4f}")
            
        # Save Best Model
        if avg_test_loss < best_loss:
            best_loss = avg_test_loss
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            joblib.dump(scaler, SCALER_SAVE_PATH)
            
    print(f"✅ Rainfall Training Complete. Best Model Saved to {MODEL_SAVE_PATH}")
    
    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(history["train_loss"], label="Train MSE")
    plt.plot(history["test_loss"], label="Test MSE")
    plt.title("Rainfall Regression Loss (MSE)")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.legend()
    
    os.makedirs("outputs/dl", exist_ok=True)
    plt.savefig("outputs/dl/rainfall_curves.png")
    print("📈 Training curves saved to outputs/dl/rainfall_curves.png")

if __name__ == "__main__":
    train()
