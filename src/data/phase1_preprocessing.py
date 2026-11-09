"""Faz 1 görevleri için eğitim verisine bağlı ön işleme çıktıları üretir."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from folktables import ACSDataSource
from scipy import sparse
from sklearn.model_selection import train_test_split

from phase1_eda import TASKS, load_sample
from phase1_readmission_eda import RAW_CSV, fetch_data
from preprocessing import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_preprocessor,
    normalize_missing_values,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "results" / "phase1" / "preprocessed"
RANDOM_STATE = 42
TEST_SIZE = 0.20
EMERGENCY_SOURCE_ID = 7


def _artifact_name(split_name: str, suffix: str) -> str:
    return f"{split_name}.{suffix}"


def transform_and_save(
    split_name: str,
    X: pd.DataFrame,
    y: pd.Series,
    preprocessor,
    task_name: str,
) -> dict:
    """Bir bölümü dönüştürür, seyrek matris ve etiketlerini yerel olarak kaydeder."""
    normalized = normalize_missing_values(X)
    task_key = task_name
    selected_columns = NUMERIC_FEATURES[task_key] + CATEGORICAL_FEATURES[task_key]
    missing_cells = int(normalized[selected_columns].isna().sum().sum())
    transformed = preprocessor.transform(X)
    if not sparse.issparse(transformed):
        transformed = sparse.csr_matrix(transformed)
    else:
        transformed = transformed.tocsr()
    if not np.isfinite(transformed.data).all():
        raise ValueError(f"Dönüşümden sonra sayısal olmayan değer kaldı: {split_name}")

    matrix_path = OUTPUT_DIR / _artifact_name(split_name, "npz")
    labels_path = OUTPUT_DIR / _artifact_name(split_name, "npy")
    sparse.save_npz(matrix_path, transformed, compressed=True)
    labels = y.to_numpy(dtype=np.int8)
    np.save(labels_path, labels)
    return {
        "split": split_name,
        "n_samples": int(len(y)),
        "positive_n": int(labels.sum()),
        "negative_n": int(len(labels) - labels.sum()),
        "input_missing_cells": missing_cells,
        "encoded_feature_count": int(transformed.shape[1]),
        "matrix_file": str(matrix_path.relative_to(ROOT)),
        "labels_file": str(labels_path.relative_to(ROOT)),
    }


def load_acs_sample(task_name: str, year: int, state: str):
    source = ACSDataSource(
        survey_year=str(year),
        horizon="1-Year",
        survey="person",
        root_dir=str(ROOT / "data" / "folktables"),
    )
    raw = source.get_data(states=[state], download=True)
    _, X, y = load_sample(task_name, year, state, raw)
    del raw
    return X, y


def process_acs_task(task_name: str, output_tag: str) -> list[dict]:
    X_source, y_source = load_acs_sample(task_name, 2014, "CA")
    X_train, X_validation, y_train, y_validation = train_test_split(
        X_source,
        y_source,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y_source,
    )
    preprocessor = build_preprocessor(task_name)
    preprocessor.fit(X_train)

    records = [
        transform_and_save(
            f"{output_tag}_ca_2014_train", X_train, y_train, preprocessor, task_name
        ),
        transform_and_save(
            f"{output_tag}_ca_2014_internal_validation",
            X_validation,
            y_validation,
            preprocessor,
            task_name,
        ),
    ]
    del X_source, y_source, X_train, X_validation, y_train, y_validation

    contexts = [
        (2018, "CA", "temporal"),
        (2014, "MI", "geographic"),
        (2018, "MI", "geographic"),
    ]
    for year, state, shift_type in contexts:
        X_eval, y_eval = load_acs_sample(task_name, year, state)
        split_name = f"{output_tag}_{state.lower()}_{year}_{shift_type}"
        records.append(
            transform_and_save(split_name, X_eval, y_eval, preprocessor, task_name)
        )
        del X_eval, y_eval

    joblib.dump(preprocessor, OUTPUT_DIR / f"preprocessor_{output_tag}.joblib")
    return records


def _save_uci_split(
    name: str,
    frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    preprocessor,
) -> dict:
    return transform_and_save(
        name,
        frame[feature_columns],
        frame[target_column].astype(np.int8),
        preprocessor,
        "DiabetesReadmission",
    )


def process_uci_task() -> dict:
    fetch_data()
    data = pd.read_csv(RAW_CSV, na_values=["?"], low_memory=False)
    data = data.dropna(subset=["race"]).copy()
    data["target"] = data["readmitted"].eq("<30").astype(np.int8)

    feature_columns = NUMERIC_FEATURES["DiabetesReadmission"] + CATEGORICAL_FEATURES[
        "DiabetesReadmission"
    ]
    target_patient_ids = set(
        data.loc[
            data["admission_source_id"].eq(EMERGENCY_SOURCE_ID), "patient_nbr"
        ].unique()
    )
    ood = data.loc[data["admission_source_id"].eq(EMERGENCY_SOURCE_ID)].copy()
    source = data.loc[
        data["admission_source_id"].ne(EMERGENCY_SOURCE_ID)
        & ~data["patient_nbr"].isin(target_patient_ids)
    ].copy()

    patient_labels = source.groupby("patient_nbr")["target"].max()
    train_patients, validation_patients = train_test_split(
        patient_labels.index.to_numpy(),
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=patient_labels.to_numpy(),
    )
    train_ids = set(train_patients)
    validation_ids = set(validation_patients)
    train = source.loc[source["patient_nbr"].isin(train_ids)].copy()
    validation = source.loc[source["patient_nbr"].isin(validation_ids)].copy()

    if train_ids & validation_ids or train_ids & target_patient_ids:
        raise RuntimeError("UCI bölümleri arasında hasta kimliği çakışması var")
    if validation_ids & target_patient_ids:
        raise RuntimeError("UCI değerlendirme bölümleri arasında hasta çakışması var")

    preprocessor = build_preprocessor("DiabetesReadmission")
    preprocessor.fit(train[feature_columns])
    records = [
        _save_uci_split(
            "uci_readmission_id_train",
            train,
            feature_columns,
            "target",
            preprocessor,
        ),
        _save_uci_split(
            "uci_readmission_id_internal_validation",
            validation,
            feature_columns,
            "target",
            preprocessor,
        ),
        _save_uci_split(
            "uci_readmission_ood_admission_source_7",
            ood,
            feature_columns,
            "target",
            preprocessor,
        ),
    ]
    for record, frame in zip(records, (train, validation, ood)):
        record["unique_patients"] = int(frame["patient_nbr"].nunique())
        record["admission_source_id"] = (
            "7" if record["split"].endswith("source_7") else "not 7"
        )

    joblib.dump(preprocessor, OUTPUT_DIR / "preprocessor_uci_readmission.joblib")
    return {
        "records": records,
        "patient_ids_disjoint": True,
        "source_rows_removed_for_patient_overlap": int(
            (data["admission_source_id"].ne(EMERGENCY_SOURCE_ID)
             & data["patient_nbr"].isin(target_patient_ids)).sum()
        ),
        "source_patient_count": int(source["patient_nbr"].nunique()),
        "emergency_patient_count": int(ood["patient_nbr"].nunique()),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    records.extend(process_acs_task("ACSIncome", "acs_income"))
    records.extend(process_acs_task("ACSEmployment", "acs_employment"))
    uci_summary = process_uci_task()
    records.extend(uci_summary["records"])

    manifest_path = OUTPUT_DIR / "bolum_ozeti.csv"
    pd.DataFrame(records).to_csv(manifest_path, index=False, encoding="utf-8-sig")
    summary = {
        "random_state": RANDOM_STATE,
        "internal_validation_fraction": TEST_SIZE,
        "acs_fit_context": "2014 California training split",
        "acs_evaluation_contexts": [
            "2014 California internal validation",
            "2018 California temporal",
            "2014 Michigan geographic",
            "2018 Michigan geographic",
        ],
        "uci_domain": "admission_source_id == 7 is held out as out-of-domain",
        "uci_patient_overlap_removed_before_split": uci_summary[
            "source_rows_removed_for_patient_overlap"
        ],
        "uci_patient_ids_disjoint": uci_summary["patient_ids_disjoint"],
        "manifest": str(manifest_path.relative_to(ROOT)),
        "splits": records,
    }
    (OUTPUT_DIR / "on_isleme_ozeti.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
