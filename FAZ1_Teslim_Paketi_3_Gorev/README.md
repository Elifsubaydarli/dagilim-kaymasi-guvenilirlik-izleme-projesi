# Faz 1 rapor paketi

Bu paket, Faz 1 raporunu ve onu destekleyen kod ile özet çıktıları içerir. Sunum dosyası bu pakete dahil değildir. Kapsam üç görevdir: ACSIncome, ACSEmploymentFiltered ve UCI Diabetes 130-US Hospitals için 30 günlük yeniden yatış.

## Kapsam ve modeller

İki Folktables görevi (ACSIncome ve ACSEmploymentFiltered) ile UCI Diabetes yeniden yatış görevi kullanılır. Faz 2 için Lojistik Regresyon, Random Forest, XGBoost ve düşük uygunluk kontrolü olarak 1B CNN seçilmiştir. Faz 1’de model eğitimi veya performans sonucu yoktur.

## İçindekiler

- `reports/faz1_raporu.docx`: düzenlenebilir rapor.
- `reports/faz1_Raporu.md`: raporun Markdown sürümü.
- `reports/figures/`: raporda kullanılan görseller ve özet CSV dosyaları.
- `src/`: Faz 1 veri keşfi, ön işleme ve mimari tanımları.
- `results/phase1/`: UCI özetlerini destekleyen küçük CSV/JSON çıktıları.
- `requirements.txt`: kod bağımlılıkları.

Ham ACS/UCI verileri, büyük dönüştürülmüş matrisler ve geçici dosyalar pakete alınmadı. Veri indirme bağlantıları raporun kaynakçasındadır.

**Düzenleme notu:** Faz 1 kapsam ve metin tutarlılığı düzenlemelerinde AI desteği kullanılmıştır.
