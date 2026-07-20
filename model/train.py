  import torch, pandas as pd, numpy as np
  from torch import nn
  from torch.utils.data import DataLoader, TensorDataset
  from sklearn.model_selection import train_test_split
  from sklearn.preprocessing import LabelEncoder
  from fusion_model import FusionModel
  
  def train():
      # ── Load dataset ──────────────────────────
      df = pd.read_csv('../dataset/training_dataset.csv')
      print(f'Dataset: {len(df)} rows')
      print(df['load_label'].value_counts())
  
      FEATURE_COLS = ['blink_rate', 'gaze_score', 'expression',
                      'wpm', 'backspace_rate', 'scroll_reversals', 'mouse_idle',
                      'response_time', 'confidence', 'f10', 'f11']
  
      # Add 2 padding columns if not present
      df['f10'] = 0.0; df['f11'] = 0.0
  
      X = df[FEATURE_COLS].values.astype(np.float32)
      le = LabelEncoder()
      y = le.fit_transform(df['load_label'])   # LOW=0, MEDIUM=1, OVERLOADED=2
  
      # ── Train/test split ──────────────────────
      X_train, X_test, y_train, y_test = train_test_split(
          X, y, test_size=0.2, random_state=42, stratify=y)
  
      train_ds = TensorDataset(torch.tensor(X_train), torch.tensor(y_train))
      test_ds  = TensorDataset(torch.tensor(X_test),  torch.tensor(y_test))
      train_dl = DataLoader(train_ds, batch_size=16, shuffle=True)
      test_dl  = DataLoader(test_ds,  batch_size=16)
  
      # ── Train ─────────────────────────────────
      model = FusionModel()
      optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
      criterion = nn.CrossEntropyLoss()
  
      print('Training...')
      for epoch in range(100):
          model.train()
          total_loss = 0
          for xb, yb in train_dl:
              optimizer.zero_grad()
              preds = model(xb)
              loss = criterion(preds, yb)
              loss.backward()
              optimizer.step()
              total_loss += loss.item()
  
          if epoch % 10 == 0:
              model.eval()
              correct = 0; total = 0
              with torch.no_grad():
                  for xb, yb in test_dl:
                      preds = model(xb).argmax(dim=1)
                      correct += (preds == yb).sum().item()
                      total += len(yb)
              acc = correct / total * 100
              print(f'Epoch {epoch:3d}  Loss: {total_loss:.3f}  Test Accuracy: {acc:.1f}%')
  
      # ── Save ─────────────────────────────────
      torch.save(model.state_dict(), 'fusion_model.pth')
      print('Model saved to fusion_model.pth')
      return model, le
  
  if __name__ == '__main__':
        train()