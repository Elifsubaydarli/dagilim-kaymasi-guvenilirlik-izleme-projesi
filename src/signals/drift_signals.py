"""Faz 2 sinyal taslağı: ECE, PSI, entropi, KS ve Wasserstein; Brier yoktur."""

import numpy as np
from scipy.stats import ks_2samp, wasserstein_distance


def calculate_ece(y_true, y_probs, n_bins=10):
    """Etiket ve olasılıklarla Beklenen Kalibrasyon Hatasını hesaplar."""
    bin_limits = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total_samples = len(y_true)
    for i in range(n_bins):
        bin_mask = (y_probs > bin_limits[i]) & (y_probs <= bin_limits[i + 1])
        bin_size = np.sum(bin_mask)
        if bin_size > 0:
            bin_acc = np.mean(y_true[bin_mask])
            bin_conf = np.mean(y_probs[bin_mask])
            ece += (bin_size / total_samples) * np.abs(bin_acc - bin_conf)
    return float(ece)


def calculate_psi(expected, actual, num_buckets=10):
    """Beklenen ve gözlenen dağılımlar arasındaki PSI değerini hesaplar."""
    breakpoints = np.linspace(0, 100, num_buckets + 1)
    eps = 1e-4
    expected_pcts = (
        np.histogram(expected, bins=np.percentile(expected, breakpoints))[0]
        / len(expected)
        + eps
    )
    actual_pcts = (
        np.histogram(actual, bins=np.percentile(expected, breakpoints))[0]
        / len(actual)
        + eps
    )
    return float(np.sum((actual_pcts - expected_pcts) * np.log(actual_pcts / expected_pcts)))


def calculate_entropy(probs):
    """İkili tahmin olasılıklarından entropi hesaplar."""
    eps = 1e-12
    p = np.clip(probs, eps, 1 - eps)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def calculate_feature_shift(x_ref, x_target):
    """İki sayısal örneklem için KS ve Wasserstein ölçülerini hesaplar."""
    ks_stat, p_val = ks_2samp(x_ref, x_target)
    w_dist = wasserstein_distance(x_ref, x_target)
    return {"ks_stat": float(ks_stat), "p_val": float(p_val), "wasserstein": float(w_dist)}
