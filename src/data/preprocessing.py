"""Folktables Faz 1 görevleri için veri sızıntısını önleyen ön işleme."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


NUMERIC_FEATURES = {
    "ACSIncome": ["AGEP", "WKHP"],
    "ACSEmployment": ["AGEP"],
}
CATEGORICAL_FEATURES = {
    "ACSIncome": ["COW", "SCHL", "MAR", "OCCP", "POBP", "RELP", "SEX", "RAC1P"],
    "ACSEmployment": [
        "SCHL", "MAR", "RELP", "DIS", "CIT", "MIG", "MIL", "ANC",
        "NATIVITY", "DEAR", "DEYE", "DREM", "SEX", "RAC1P", "GCL",
    ],
}
# İncelenen ACS bağlamlarında ESP değerlerinin %98,4-%98,6'sı eksiktir.
# İlk model hattından çıkarılır; etkisi duyarlılık analiziyle ayrıca incelenir.
EXCLUDED_HIGH_MISSING_FEATURES = {"ACSEmployment": ["ESP"]}


def normalize_missing_sentinel(X: pd.DataFrame) -> pd.DataFrame:
    """Folktables'ın eksikler için kullandığı -1 değerlerini NaN'a dönüştürür."""
    return X.replace(-1, np.nan)


def build_preprocessor(task_name: str) -> ColumnTransformer:
    """Ön işleme hattını kurar; yalnızca eğitim verisinde fit edilmelidir.

    Sayısal sütunlar medyanla tamamlanıp ölçeklenir. Kategorik sütunlarda en sık
    değer kullanılır ve one-hot kodlama yapılır. Bilinmeyen kategoriler atlanır.
    Doğrulama ve test verisinden bilgi sızmasını önlemek için bu dönüşümler,
    modelle birlikte bir sklearn Pipeline içine alınmalıdır.
    """
    if task_name not in NUMERIC_FEATURES:
        raise ValueError(f"Unknown Folktables task: {task_name}")

    numeric = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    )
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric, NUMERIC_FEATURES[task_name]),
            ("categorical", categorical, CATEGORICAL_FEATURES[task_name]),
        ],
        remainder="drop",
    )
