# Tablosal Veride Dağılım Kaymasına Duyarlı Güvenilirlik İzleme

Bu depo, **Uygulamalı Yapay Zekâ** dersi kapsamında yürütülen dönem projesinin ve akademik bildiri/makale çalışmasının resmi kod ve dokümantasyon deposudur.

## Proje Künyesi
- **Proje Başlığı:** Tablosal Veride Dağılım Kaymasına Duyarlı Güvenilirlik İzleme: Güven, Kalibrasyon, Veri Kayması ve Açıklama Sinyallerinin Erken Uyarı Performansının Karşılaştırmalı Analizi
- **Proje Türü:** Grup Projesi
- **Araştırmacılar / Grup Üyeleri:**
  - **Zehra Akgül** (Öğrenci No: 241230036)
  - **Elif Su Baydarlı** (Öğrenci No: 241230017)

---

## 1. Faz Özeti ve Tamamlanan Kazanımlar
1. **Veri Kümelerinin Temini:** ABD Nüfus Bürosu (Census) ACS verisinden türetilen Folktables görevleri (`ACSIncome` ve `ACSEmployment`) indirilmiş ve doğrulanmıştır.
   - Referans Eğitim / Dağıtım İçi (ID): 2018 California (195.665 satır)
   - Zamansal Dağılım Kayması (Temporal OOD): 2014 California (183.941 satır)
   - Coğrafi Dağılım Kayması (Geographic OOD): 2018 New York (103.021 satır)
   - İkinci Görev Doğrulama: 2018 California ACSEmployment (378.817 satır)
2. **Keşifçi Veri Analizi (EDA) ve Rapor Grafikleri:** 
   - Sınıf dengesi, özellik dağılımları ve korelasyon matrisi çıkarılmıştır.
   - KS-Testi ve Wasserstein Mesafesi ile zamansal ve coğrafi kaymalar kanıtlanmıştır.
   - 300 DPI çözünürlükte 6 adet bilimsel grafik `reports/figures/` altına kaydedilmiştir.
3. **Veri Ön İşleme (Preprocessing) Pipeline:**
   - **Sıfır Veri Sızıntısı (Zero Leakage):** Scaler ve One-Hot kodlayıcılar yalnızca %80 eğitim verisi üzerinde eğitilmiş (`fit`), test ve OOD verileri yalnızca dönüştürülmüştür (`transform`).
   - `preprocessor_pipeline.joblib` olarak paketlenmiştir.
4. **Model Mimarileri ve İzleme Protokolü:**
   - 4 Model Mimarisi: Lojistik Regresyon (Lineer), Random Forest (Bagging), LightGBM/XGBoost (Boosting), MLP (Derin Tablosal Ağ).
   - İzleme Metrikleri: Accuracy, F1, ROC-AUC, ECE (Kalibrasyon), Brier Skoru, PSI (Popülasyon Kararlılığı) ve XAI Uyuşmazlığı.
5. **Rapor:** Tebligata tam uyumlu 1. Faz Raporu `reports/PROJE_FAZ1_RAPORU.md` dosyasında hazırdır.

---

## Dosya Yapısı ve Proje Mimarisi

```text
dagilim_kaymasi/
├── 01_veri_indir.py                     # 1. Adım: Folktables veri indirme scripti
├── 02_kesifci_veri_analizi_eda.py        # 2. Adım: EDA, dağılım kayması testi ve grafikler
├── 03_on_isleme_pipeline.py             # 3. Adım: Veri sızıntısız preprocessing pipeline
├── 04_model_mimarileri_ve_rapor.py      # 4. Adım: Model mimarileri ve 1. Faz rapor üretimi
│
├── data/
│   ├── raw/                             # Ham Census ACS verileri ve özet tablosu
│   └── processed/                       # İşlenmiş train/test/OOD matrisleri ve pipeline (.joblib)
│
├── reports/
│   ├── PROJE_FAZ1_RAPORU.md             # Tebligat formatında eksiksiz 1. Faz Raporu
│   ├── eda_istatistik_ozeti.md          # İstatistiksel özet ve frekans tabloları
│   └── figures/                         # Rapora eklenen 300 DPI yüksek çözünürlüklü grafikler
│       ├── fig1_sinif_dagilimlari.png
│       ├── fig2_ozellik_dagilimlari.png
│       ├── fig3_korelasyon_matrisi.png
│       ├── fig4_zamansal_dagilim_kaymasi.png
│       ├── fig5_cografi_dagilim_kaymasi.png
│       └── fig6_model_mimarileri_ve_protokol.png
│
├── requirements.txt                     # Kütüphane bağımlılıkları
├── .gitignore                           # Git izleme filtreleri
└── README.md                            # Bu belge
```

---

## Kurulum ve Çalıştırma

### 1. Bağımlılıkların Kurulması
```bash
pip install -r requirements.txt
```

### 2. Adımların Sırayla Çalıştırılması
```bash
# 1. Veri setlerini indirme ve doğrulama
python 01_veri_indir.py

# 2. Keşifçi Veri Analizi (EDA) ve Grafik Üretimi
python 02_kesifci_veri_analizi_eda.py

# 3. Veri Ön İşleme (Preprocessing) Pipeline
python 03_on_isleme_pipeline.py

# 4. Model Mimarileri, İleri Metrikler ve Rapor Üretimi
python 04_model_mimarileri_ve_rapor.py
```

---

## Proje Ekibi ve Katkılar
Proje, grup üyeleri tarafından ortaklaşa yürütülmektedir:
- **Zehra Akgül** (241230036)
- **Elif Su Baydarlı** (241230017)
