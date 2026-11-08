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

NUMERIC_FEATURES["DiabetesReadmission"] = [
    "time_in_hospital",
    "num_lab_procedures",
    "num_procedures",
    "num_medications",
    "number_outpatient",
    "number_emergency",
    "number_inpatient",
    "number_diagnoses",
]
CATEGORICAL_FEATURES["DiabetesReadmission"] = [
    "race",
    "gender",
    "age",
    "admission_type_id",
    "discharge_disposition_id",
    "payer_code",
    "medical_specialty",
    "diag_1",
    "diag_2",
    "diag_3",
    "max_glu_serum",
    "A1Cresult",
    "metformin",
    "repaglinide",
    "nateglinide",
    "chlorpropamide",
    "glimepiride",
    "acetohexamide",
    "glipizide",
    "glyburide",
    "tolbutamide",
    "pioglitazone",
    "rosiglitazone",
    "acarbose",
    "miglitol",
    "troglitazone",
    "tolazamide",
    "examide",
    "citoglipton",
    "insulin",
    "glyburide-metformin",
    "glipizide-metformin",
    "glimepiride-pioglitazone",
    "metformin-rosiglitazone",
    "metformin-pioglitazone",
    "change",
    "diabetesMed",
]


def normalize_missing_sentinel(X: pd.DataFrame) -> pd.DataFrame:
    """Folktables'ın eksikler için kullandığı -1 değerlerini NaN'a dönüştürür."""
    return X.replace(-1, np.nan)


def normalize_diabetes_missing(X: pd.DataFrame) -> pd.DataFrame:
    """UCI dosyasındaki '?' eksik değer işaretlerini NaN'a dönüştürür."""
    return X.replace("?", np.nan)


def build_preprocessor(task_name: str) -> ColumnTransformer:
    """Göreve uygun ön işleme hattını kurar; yalnızca eğitimde fit edilmelidir.

    Sayısal sütunlar medyanla tamamlanıp ölçeklenir. Kategorik sütunlarda en sık
    değer kullanılır ve one-hot kodlama yapılır. Bilinmeyen kategoriler atlanır.
    Doğrulama ve test verisinden bilgi sızmasını önlemek için bu dönüşümler,
    modelle birlikte bir sklearn Pipeline içine alınmalıdır.
    """
    if task_name not in NUMERIC_FEATURES or task_name not in CATEGORICAL_FEATURES:
        raise ValueError(f"Bilinmeyen veri görevi: {task_name}")

    numeric = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    )
    categorical_imputer = SimpleImputer(strategy="most_frequent")
    if task_name == "DiabetesReadmission":
        # Bu görevde bazı kategorik sütunların çoğu eksiktir; eksikliği ayrı bir
        # kategori olarak korumak, en sık değere doldurmaktan daha açıklayıcıdır.
        categorical_imputer = SimpleImputer(strategy="constant", fill_value="Eksik")
    categorical = Pipeline(
        steps=[
            ("imputer", categorical_imputer),
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
