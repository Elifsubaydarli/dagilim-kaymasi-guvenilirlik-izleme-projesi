"""Folktables Faz 1 görevleri için veri sızıntısını önleyen ön işleme."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler


NUMERIC_FEATURES = {
    "ACSIncome": ["AGEP", "WKHP"],
    "ACSEmployment": ["AGEP"],
}
CATEGORICAL_FEATURES = {
    "ACSIncome": ["COW", "SCHL", "MAR", "OCCP", "POBP", "RELP", "SEX", "RAC1P"],
    "ACSEmployment": [
        "SCHL", "MAR", "RELP", "DIS", "ESP", "CIT", "MIG", "MIL", "ANC",
        "NATIVITY", "DEAR", "DEYE", "DREM", "SEX", "RAC1P",
    ],
}
def normalize_missing_values(X: pd.DataFrame) -> pd.DataFrame:
    """Folktables ve UCI dosyalarındaki eksik değer işaretlerini düzenler."""
    return X.replace({-1: np.nan, "?": np.nan})


def stringify_categories(X: pd.DataFrame) -> pd.DataFrame:
    """Kategorik kodları eksik kategori etiketiyle aynı türde tutar."""
    return X.apply(
        lambda column: column.map(
            lambda value: str(value) if pd.notna(value) else np.nan
        )
    )

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


def build_preprocessor(task_name: str) -> Pipeline:
    """Göreve uygun ön işleme hattını kurar; yalnızca eğitimde fit edilmelidir.

    Sayısal sütunlar medyanla tamamlanıp ölçeklenir. ACSIncome kategorikleri en sık
    değerle, ACSEmployment ve UCI kategorikleri ayrı bir eksik değeriyle tamamlanır.
    Bilinmeyen kategoriler one-hot dönüşümünde atlanır.
    Doğrulama ve test verisinden bilgi sızmasını önlemek için hat yalnızca eğitim
    bölümünde fit edilir; diğer bölümlere aynı dönüşümler uygulanır.
    """
    if task_name not in NUMERIC_FEATURES or task_name not in CATEGORICAL_FEATURES:
        raise ValueError(f"Bilinmeyen veri görevi: {task_name}")

    numeric = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    )
    categorical_imputer = SimpleImputer(strategy="most_frequent")
    if task_name in {"ACSEmployment", "DiabetesReadmission"}:
        # Bu görevlerde eksiklik bilgisi yüksek oranlarda görüldüğünden ayrı tutulur.
        categorical_imputer = SimpleImputer(strategy="constant", fill_value="Eksik")
    categorical = Pipeline(
        steps=[
            ("stringify", FunctionTransformer(stringify_categories, validate=False)),
            ("imputer", categorical_imputer),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    columns = ColumnTransformer(
        transformers=[
            ("numeric", numeric, NUMERIC_FEATURES[task_name]),
            ("categorical", categorical, CATEGORICAL_FEATURES[task_name]),
        ],
        remainder="drop",
    )
    return Pipeline(
        steps=[
            (
                "missing_values",
                FunctionTransformer(
                    normalize_missing_values,
                    validate=False,
                    feature_names_out="one-to-one",
                ),
            ),
            ("columns", columns),
        ]
    )
