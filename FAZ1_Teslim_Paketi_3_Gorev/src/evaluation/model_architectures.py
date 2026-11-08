"""Faz 2 için seçilen modeller: LR, RF, XGBoost ve 1B CNN kontrol modeli.

1B CNN, karışık tablosal özelliklerde sütun sırasının anlamı olmadığı için
düşük uygunluklu bir kontrol olarak tutulur. Bu modül model eğitimi yapmaz.
"""
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import torch
from torch import nn

def get_sklearn_models():
    """Faz 2 için scikit-learn arayüzlü uygun karşılaştırma modelleri."""
    return {
        "LogisticRegression": LogisticRegression(C=1.0, penalty="l2", solver="lbfgs", max_iter=1000, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=15, min_samples_split=10, random_state=42, n_jobs=-1),
        "XGBoost": XGBClassifier(n_estimators=150, learning_rate=0.08, max_depth=6, random_state=42, n_jobs=-1, eval_metric="logloss"),
    }

class TabularCNN1D(nn.Module):
    """Basit 1B CNN kontrol modeli; ozellik sutunlarinin sirasi varsayimsaldir."""
    def __init__(self, input_features: int):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=3, padding=1), nn.ReLU(),
            nn.Conv1d(16, 32, kernel_size=3, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool1d(1), nn.Flatten(),
        )
        self.output = nn.Linear(32, 1)

    def forward(self, x):
        if x.ndim == 2:
            x = x.unsqueeze(1)
        return self.output(self.features(x)).squeeze(-1)

def build_1d_cnn(input_features: int) -> TabularCNN1D:
    """Faz 2’de düşük uygunluk kontrolü için CNN mimarisini kurar."""
    if input_features < 1:
        raise ValueError("input_features pozitif olmalıdır")
    return TabularCNN1D(input_features)
