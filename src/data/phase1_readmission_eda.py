"""UCI diyabet yeniden yatış verisi için Faz 1 keşif analizi."""

from __future__ import annotations

import json
import urllib.request
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "tableshift_diabetes"
ARCHIVE = DATA_DIR / "dataset_diabetes.zip"
RAW_CSV = DATA_DIR / "diabetic_data.csv"
OUTPUT_DIR = ROOT / "results" / "phase1"
FIGURE_DIR = ROOT / "reports" / "figures"
DATA_URL = (
    "https://archive.ics.uci.edu/static/public/296/"
    "diabetes+130-us+hospitals+for+years+1999-2008.zip"
)


def fetch_data() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not RAW_CSV.exists():
        urllib.request.urlretrieve(DATA_URL, ARCHIVE)
        with zipfile.ZipFile(ARCHIVE) as archive:
            archive.extractall(DATA_DIR)
    if not RAW_CSV.exists():
        raise FileNotFoundError(f"UCI arşivinde {RAW_CSV.name} bulunamadı")


def main() -> None:
    fetch_data()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(RAW_CSV, na_values=["?"], low_memory=False)
    # TableShift'in yayımladığı görev tanımı, 2.273 satırdaki eksik ırk
    # bilgisini çıkarır. Hasta kimlikleri yalnızca tekrarları ölçmek için kalır.
    data = raw.dropna(subset=["race"]).copy()
    data["readmit_within_30_days"] = data["readmitted"].eq("<30").astype(int)

    excluded = {"encounter_id", "patient_nbr", "readmitted", "readmit_within_30_days"}
    model_features = [
        column for column in data.columns
        if column not in excluded and column != "admission_source_id"
    ]
    # Weight alanının %95'ten fazlası eksiktir; ilk model hattında tutulmaz.
    if "weight" in model_features:
        model_features.remove("weight")

    missing = data[model_features].isna().mean().sort_values(ascending=False)
    missing.rename("missing_rate").to_csv(
        OUTPUT_DIR / "diabetes_missingness.csv", encoding="utf-8-sig"
    )

    classes = data["readmit_within_30_days"].value_counts().sort_index()
    raw_labels = data["readmitted"].value_counts().reindex(["<30", ">30", "NO"])
    source_counts = data["admission_source_id"].value_counts().sort_values(ascending=False)
    summary = {
        "dataset": "Diabetes 130-US Hospitals for Years 1999-2008",
        "source": "UCI Machine Learning Repository, dataset 296",
        "task_source": "TableShift diabetes_readmission task; UCI data, 2,273 missing-race rows removed",
        "raw_rows": int(len(raw)),
        "rows_after_task_filter": int(len(data)),
        "raw_columns": int(raw.shape[1]),
        "model_feature_count_after_exclusions": len(model_features),
        "model_features": model_features,
        "target": "readmitted == '<30'",
        "positive_n": int(classes.get(1, 0)),
        "negative_n": int(classes.get(0, 0)),
        "original_label_counts": {str(k): int(v) for k, v in raw_labels.items()},
        "rows_with_any_missing_model_feature": int(data[model_features].isna().any(axis=1).sum()),
        "unique_patients": int(data["patient_nbr"].nunique()),
        "repeat_encounters_beyond_first": int(len(data) - data["patient_nbr"].nunique()),
        "observed_admission_source_codes": int(data["admission_source_id"].nunique()),
        "emergency_source_id_7_rows": int((data["admission_source_id"] == 7).sum()),
        "max_feature_missing_rate": float(missing.max()),
    }
    pd.DataFrame([summary]).to_csv(
        OUTPUT_DIR / "diabetes_summary.csv", index=False, encoding="utf-8-sig"
    )
    (OUTPUT_DIR / "diabetes_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    class_names = {0: "30 gün içinde değil", 1: "30 gün içinde yeniden yatış"}
    plot_classes = classes.rename(index=class_names)
    sns.barplot(x=plot_classes.index, y=plot_classes.values, ax=ax, color="#4C78A8")
    ax.set_title("Diyabet yeniden yatış hedefi")
    ax.set_xlabel("Sınıf")
    ax.set_ylabel("Kayıt sayısı")
    ax.tick_params(axis="x", rotation=12)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "diabetes_siniflari.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    top_missing = missing[missing.gt(0)].head(10).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top_missing.index, top_missing.values * 100, color="#E45756")
    ax.set_title("En yüksek eksik değer oranına sahip özellikler")
    ax.set_xlabel("Eksik değer (%)")
    ax.set_ylabel("Özellik")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "diabetes_eksik_degerler.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    domains = data.groupby("admission_source_id")["readmit_within_30_days"].agg(
        toplam="size", pozitif="sum", oran="mean"
    ).sort_values("toplam", ascending=False).head(10)
    domains.to_csv(OUTPUT_DIR / "diabetes_admission_source.csv", encoding="utf-8-sig")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(domains.index.astype(str), domains["toplam"], color="#72B7B2")
    ax.set_title("Yatış kaynağına göre kayıt sayısı (ilk 10)")
    ax.set_xlabel("Yatış kaynağı kodu")
    ax.set_ylabel("Kayıt sayısı")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "diabetes_yatis_kaynagi.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
