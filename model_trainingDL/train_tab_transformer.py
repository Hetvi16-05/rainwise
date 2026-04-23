import os
import torch
import torch.nn as nn
import torch.optim as optim
from dataloader import prepare_data
from models import TabTransformer
import joblib
import matplotlib.pyplot as plt
import time

# =========================
# CONFIGURATION
# =========================
DATA_PATH = "data/processed/training_dataset_gujarat_advanced_labeled.csv"
MODEL_SAVE_PATH = "DLmodels/tab_transformer_rainfall.pth"
SCALER_SAVE_PATH = "DLmodels/tab_transformer_scaler.pkl"

# HYPERPARAMETERS
BATCH_SIZE = 128
EPOCHS = 40
LEARNING_RATE = 0.0005
EMBED_DIM = 32
TRANSFORMER_DEPTH = 3
ATTENTION_HEADS = 4
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

def train_transformer():
    os.makedirs("DLmodels", exist_ok=True)
    os.makedirs("outputs/dl", exist_ok=True)

    # 1. Load Data
    print(f"\n📂 Loading data for TAB-TRANSFORMER RAINFALL REGRESSION...")
    train_loader, test_loader, scaler, input_dim = prepare_data(
        DATA_PATH, 
        task_type="regression", 
        batch_size=BATCH_SIZE
    )
    
    # 2. Initialize TabTransformer
    print(f"🧠 Building TabTransformer...")
    print(f"   - Input Features: {input_dim}")
    print(f"   - Embedding Dim: {EMBED_DIM}")
    print(f"   - Transformer Depth: {TRANSFORMER_DEPTH}")
    print(f"   - Attention Heads: {ATTENTION_HEADS}")
    print(f"   - Total Hidden Neurons (MLP): 128, 64")
    
    model = TabTransformer(
        input_dim=input_dim,
        embed_dim=EMBED_DIM,
        depth=TRANSFORMER_DEPTH,
        heads=ATTENTION_HEADS
    ).to(DEVICE)
    
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    
    # 3. Training Loop
    print(f"🚀 Starting Training on {DEVICE}...")
    history = {"train_loss": [], "test_loss": []}
    best_loss = float('inf')
    start_time = time.time()
    
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
        
        scheduler.step(avg_test_loss)
        
        if (epoch+1) % 5 == 0 or epoch == 0:
            print(f"Epoch [{epoch+1:02d}/{EPOCHS}] | Train MSE: {avg_train_loss:.4f} | Test MSE: {avg_test_loss:.4f} | LR: {optimizer.param_groups[0]['lr']:.6f}")
            
        # Save Best Model
        if avg_test_loss < best_loss:
            best_loss = avg_test_loss
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            joblib.dump(scaler, SCALER_SAVE_PATH)
            
    total_time = time.time() - start_time
    print(f"\n✅ Training Complete in {total_time:.1f}s")
    print(f"🏆 Best Test MSE: {best_loss:.4f}")
    print(f"💾 Model Saved to {MODEL_SAVE_PATH}")
    
    # 4. Visualization
    plt.figure(figsize=(10, 6))
    plt.plot(history["train_loss"], label="Train MSE", color='blue', alpha=0.7)
    plt.plot(history["test_loss"], label="Test MSE", color='orange', linewidth=2)
    plt.yscale('log') # Log scale for better visualization of convergence
    plt.title("TabTransformer Rainfall Regression: Training vs Test Loss")
    plt.xlabel("Epochs")
    plt.ylabel("Mean Squared Error (log scale)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    save_path = "outputs/dl/tab_transformer_curves.png"
    plt.savefig(save_path)
    print(f"📈 Convergence curves saved to {save_path}")

if __name__ == "__main__":
    train_transformer()
