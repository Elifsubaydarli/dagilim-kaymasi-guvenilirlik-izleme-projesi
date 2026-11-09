"""Faz 1'de seçilen modellerin planı; eğitim Faz 2'de yapılacaktır."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    name: str
    purpose: str
    suitability: str


MODEL_PLAN = (
    ModelSpec(
        name="Lojistik Regresyon",
        purpose="Başlangıç sınıflandırıcısı",
        suitability="Tablosal veri için uygun; doğrusal karşılaştırma noktası.",
    ),
    ModelSpec(
        name="Random Forest",
        purpose="Doğrusal olmayan ilişkiler",
        suitability="Tablosal veri için uygun; ağaç topluluğu.",
    ),
    ModelSpec(
        name="XGBoost",
        purpose="Artırmalı ağaç karşılaştırması",
        suitability="Tablosal sınıflandırma için seçilen yöntem.",
    ),
    ModelSpec(
        name="1B CNN",
        purpose="Düşük uygunluk kontrolü",
        suitability="Tablo sütunlarının doğal sırası olmadığından kontrol modeli.",
    ),
)


def get_model_plan() -> tuple[ModelSpec, ...]:
    """Faz 1'de seçilmiş model tanımlarını döndürür."""
    return MODEL_PLAN
