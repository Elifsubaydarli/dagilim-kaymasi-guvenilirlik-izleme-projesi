"""
src/evaluation/model_architectures.py
------------------------------------
Faz 2 deneylerinde karşılaştırılacak model mimarileri:
1. Lojistik Regresyon (Lineer Taban Çizgisi)
2. Random Forest (Bagging Ağaç Topluluğu)
3. LightGBM (Gradient Boosting)
4. Çok Katmanlı Algılayıcı - MLP (Yapay Sinir Ağı)
"""

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
from sklearn.neural_network import MLPClassifier

def get_models():
    """Tanımlanan 4 model mimarisini ve varsayılan parametrelerini döndürür"""
    return {
        "LogisticRegression": LogisticRegression(
            C=1.0, penalty='l2', solver='lbfgs', max_iter=1000, random_state=42
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100, max_depth=15, min_samples_split=10, random_state=42, n_jobs=-1
        ),
        "LightGBM": LGBMClassifier(
            n_estimators=150, learning_rate=0.08, num_leaves=31, random_state=42, n_jobs=-1, verbose=-1
        ),
        "MLP_NeuralNet": MLPClassifier(
            hidden_layer_sizes=(128, 64), activation='relu', alpha=0.001, max_iter=200, early_stopping=True, random_state=42
        )
    }
