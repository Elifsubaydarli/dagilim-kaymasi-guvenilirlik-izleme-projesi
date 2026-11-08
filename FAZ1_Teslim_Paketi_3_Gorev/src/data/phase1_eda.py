"""Folktables ACS örneklerini indirir ve tekrarlanabilir Faz 1 EDA çıktıları üretir."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from folktables import ACSEmploymentFiltered, ACSDataSource, ACSIncome


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "folktables"
OUTPUT_DIR = ROOT / "results" / "phase1"
TASKS = {"ACSIncome": ACSIncome, "ACSEmployment": ACSEmploymentFiltered}
YEARS = (2014, 2018)
STATES = ("CA", "MI")
TASK_CATEGORICAL = {
    "ACSIncome": ["COW", "SCHL", "MAR", "OCCP", "POBP", "RELP", "SEX", "RAC1P"],
    "ACSEmployment": [
        "SCHL", "MAR", "RELP", "DIS", "ESP", "CIT", "MIG", "MIL", "ANC",
        "NATIVITY", "DEAR", "DEYE", "DREM", "SEX", "RAC1P", "GCL",
    ],
}


def as_series(values: object, name: str) -> pd.Series:
    if isinstance(values, pd.DataFrame):
        if values.shape[1] != 1:
            raise ValueError(f"Expected one target column, got {values.shape[1]}")
        values = values.iloc[:, 0]
    elif not isinstance(values, pd.Series):
        values = pd.Series(values)
    return values.rename(name).reset_index(drop=True)


def load_sample(
    task_name: str, year: int, state: str, raw: pd.DataFrame
) -> tuple[dict, pd.DataFrame, pd.Series]:
    task = TASKS[task_name]
    filtered = task._preprocess(raw.copy())
    X, y, _ = task.df_to_pandas(raw.copy())
    y = as_series(y, "target")

    if len(X) != len(y) or len(X) != len(filtered):
        raise RuntimeError(
            f"Row mismatch for {task_name}/{year}/{state}: "
            f"filtered={len(filtered)}, X={len(X)}, y={len(y)}"
        )

    class_counts = y.value_counts(dropna=False).sort_index()
    feature_missing = filtered[task.features].isna()
    summary = {
        "task": task_name,
        "source": "U.S. Census Bureau ACS PUMS, 1-year person microdata via Folktables",
        "folktables_version": "0.0.12",
        "task_definition": "ACSEmploymentFiltered (age 17-89; PWGTP >= 1)" if task_name == "ACSEmployment" else "ACSIncome (AGEP > 16, PINCP > 100, WKHP > 0, PWGTP >= 1)",
        "survey_year": year,
        "state": state,
        "raw_rows": int(len(raw)),
        "task_rows_after_official_filter": int(len(X)),
        "n_features": int(X.shape[1]),
        "numeric_features": ", ".join(c for c in X.columns if c not in TASK_CATEGORICAL[task_name]),
        "categorical_features": ", ".join(c for c in X.columns if c in TASK_CATEGORICAL[task_name]),
        "missing_cells_before_task_postprocess": int(feature_missing.sum().sum()),
        "rows_with_any_missing_before_task_postprocess": int(feature_missing.any(axis=1).sum()),
        "feature_missing_rates": json.dumps(
            {column: float(rate) for column, rate in feature_missing.mean().items()}
        ),
        "missing_cells_after_task_postprocess": int(X.isna().sum().sum()),
        "target_positive_n": int((y == 1).sum()),
        "target_negative_n": int((y == 0).sum()),
        "target_positive_rate": float((y == 1).mean()),
        "target_classes": json.dumps({str(k): int(v) for k, v in class_counts.items()}),
    }
    return summary, X.reset_index(drop=True), y


def plot_overview(summaries: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, task_name in zip(axes, TASKS):
        subset = summaries[summaries["task"] == task_name].copy()
        sns.barplot(data=subset, x="survey_year", y="task_rows_after_official_filter", hue="state", ax=ax)
        ax.set_title(f"{task_name}: filtre sonrası örnek sayısı")
        ax.set_xlabel("Eyalet ve ACS yılı")
        ax.set_ylabel("Kişi sayısı")
        ax.tick_params(axis="x", rotation=20)
        if ax.legend_:
            ax.legend_.remove()
    axes[1].legend(title="Eyalet", loc="upper right")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "ornek_sayilari.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, task_name in zip(axes, TASKS):
        subset = summaries[summaries["task"] == task_name].copy()
        sns.lineplot(
            data=subset,
            x="survey_year",
            y="target_positive_rate",
            hue="state",
            marker="o",
            ax=ax,
        )
        ax.set_title(f"{task_name}: pozitif sınıf oranı")
        ax.set_xlabel("ACS anket yılı")
        ax.set_ylabel("Pozitif sınıf oranı")
        ax.set_xticks(YEARS)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "sinif_oranlari.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_feature_distributions(samples: dict[tuple[str, int, str], tuple[pd.DataFrame, pd.Series]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, (task_name, feature) in zip(axes, [("ACSIncome", "AGEP"), ("ACSEmployment", "AGEP")]):
        parts = []
        for (name, year, state), (X, _) in samples.items():
            if name != task_name or feature not in X:
                continue
            part = X[[feature]].copy()
            part["year_state"] = f"{state} {year}"
            parts.append(part)
        plot_df = pd.concat(parts, ignore_index=True)
        sns.histplot(
            data=plot_df,
            x=feature,
            hue="year_state",
            stat="density",
            common_norm=False,
            element="step",
            fill=False,
            ax=ax,
        )
        ax.set_title(f"{task_name}: yaş dağılımı (AGEP)")
        ax.set_xlabel("Yaş")
        ax.set_ylabel("Yoğunluk")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "yas_dagilimlari.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--years", nargs="+", type=int, default=list(YEARS))
    parser.add_argument("--states", nargs="+", default=list(STATES))
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    summaries: list[dict] = []
    samples: dict[tuple[str, int, str], tuple[pd.DataFrame, pd.Series]] = {}

    for year in args.years:
        source = ACSDataSource(
            survey_year=str(year), horizon="1-Year", survey="person", root_dir=str(DATA_DIR)
        )
        for state in args.states:
            print(f"Yükleniyor: ACS {year} | {state}", flush=True)
            raw = source.get_data(states=[state], download=True)
            for task_name in TASKS:
                summary, X, y = load_sample(task_name, year, state, raw)
                summaries.append(summary)
                samples[(task_name, year, state)] = (X, y)

    # Rapor, resmi görev filtresinden sonra ve Folktables eksikleri -1 ile
    # değiştirmeden önceki özelliklere dayanır. Büyük ACS dosyalarını yeniden
    # okumamak için yukarıda yüklenen örnekler tekrar kullanılır.
    missing_rows = []
    for summary in summaries:
        rates = json.loads(summary.pop("feature_missing_rates"))
        for feature, missing_rate in rates.items():
            missing_rows.append(
                {
                    "task": summary["task"],
                    "survey_year": summary["survey_year"],
                    "state": summary["state"],
                    "feature": feature,
                    "missing_rate": missing_rate,
                }
            )
    pd.DataFrame(missing_rows).to_csv(
        OUTPUT_DIR / "eksik_deger_oranlari.csv", index=False, encoding="utf-8-sig"
    )

    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(OUTPUT_DIR / "veri_ozeti.csv", index=False, encoding="utf-8-sig")
    plot_overview(summary_df)
    plot_feature_distributions(samples)

    print(f"\nÖzet kaydedildi: {OUTPUT_DIR / 'veri_ozeti.csv'}")
    print(f"Grafikler kaydedildi: {OUTPUT_DIR}")
    print(summary_df[["task", "survey_year", "state", "task_rows_after_official_filter", "target_positive_rate"]].to_string(index=False))


if __name__ == "__main__":
    main()
