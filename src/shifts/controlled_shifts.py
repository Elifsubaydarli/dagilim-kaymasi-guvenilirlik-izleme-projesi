"""
src/shifts/controlled_shifts.py
-------------------------------
Kontrollü dağılım kayması (gürültü ve eksik veri) simülasyon fonksiyonları:
1. Özellik (Kovaryat) Kayması
2. Eksik Veri (MCAR/MAR Maskeleme)
3. Gürültü Enjeksiyonu (Gauss gürültüsü)
4. Zamansal / Coğrafi Kayma
5. Kavram Kayması (P(Y|X))
6. Kısayol (Spurious) Kayması
"""

import numpy as np
import pandas as pd

def inject_gaussian_noise(X, numeric_cols, sigma_factor=0.5):
    """Sayısal özelliklere standart sapmayla orantılı Gauss gürültüsü ekler"""
    X_noisy = X.copy()
    for col in numeric_cols:
        if col in X_noisy.columns:
            std = X_noisy[col].std()
            noise = np.random.normal(0, sigma_factor * std, size=len(X_noisy))
            X_noisy[col] = X_noisy[col] + noise
    return X_noisy

def inject_missingness(X, missing_rate=0.20):
    """MCAR (Tamamen Rastgele Kayıp) maskeleme uygular"""
    X_missing = X.copy()
    mask = np.random.rand(*X_missing.shape) < missing_rate
    X_missing = X_missing.mask(mask)
    return X_missing
