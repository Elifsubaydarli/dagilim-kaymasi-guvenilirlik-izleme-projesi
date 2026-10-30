# Dağılım Kaymasına Duyarlı Güvenilirlik İzleme

Bu proje, tablosal makine öğrenmesi modellerinde dağılım kayması sırasında performans düşüşünü etiketsiz izleme sinyallerinin ne kadar erken ve ne kadar az yanlış alarmla yakalayabildiğini inceler. Proje önerisi: [`docs/proje-onerisi.pdf`](docs/proje-onerisi.pdf).

## Araştırma sorusu

Farklı kayma mekanizmalarında hangi etiketsiz sinyal performans bozulmasını en erken ve en az yanlış alarmla yakalar; sinyaller kayma türüne göre nasıl birleştirilmelidir?

## Çalışma planı

1. **Veri ve kapsam:** Folktables ACSIncome ve ACSEmployment görevlerini sabitle; veri sürümü, bölünmeler, özellikler ve örnek sayılarını doğrula. TableShift'ten en az iki dış doğrulama görevi seç.
2. **Başlangıç modelleri:** Lojistik Regresyon, Random Forest ve XGBoost veya LightGBM modellerini kur; Accuracy, F1 ve AUC'yi kaydet.
3. **Kontrollü kaymalar:** Özellik/kovaryat, eksik veri, gürültü, zamansal/coğrafi, kavram ve kısayol kaymalarını artan şiddet seviyelerinde üret.
4. **İzleme sinyalleri:** Güven/belirsizlik; kalibrasyon; PSI, KS/Wasserstein ve alan sınıflandırıcısı; SHAP açıklama kayması; permütasyon önemi ve açıklama-bağımlılık uyuşmazlığını hesapla.
5. **Erken uyarı değerlendirmesi:** Eşikleri dağıtım içi bootstrap örneklerinde %5 yanlış alarm oranına göre belirle. Bozulma AUROC'si, uyarı önceliği ve yanlış alarm oranını ölç.
6. **Birleşim ve karşılaştırma:** Tek sinyal, sabit ağırlıklı ve kayma türüne duyarlı birleşimleri PDF'deki taban çizgileriyle karşılaştır; çoklu tohum, bootstrap aralıkları, eşleşmiş testler ve dışarıda bırakma doğrulaması kullan.
7. **Raporlama:** Bulguları ve sınırlılıkları yaz; yenilik iddiasını 15-20 çalışmalık literatür matrisiyle doğrula. Negatif sonuçları da raporla.

Deneyler henüz yapılmadı; hipotezler sonuç olarak sunulmayacaktır.

## Klasör yapısı

```text
configs/       Deney ayarları
data/          İndirilen veri (Git dışında tutulur)
docs/          Proje önerisi ve dokümantasyon
notebooks/     Keşif ve analiz not defterleri
reports/       Sonuç raporları
results/       Üretilen tablolar ve grafikler (Git dışında tutulur)
src/data/      Veri indirme ve hazırlama
src/shifts/    Kontrollü kayma üreticileri
src/signals/   İzleme sinyalleri
src/evaluation/Erken uyarı metrikleri ve kıyaslamalar
```

## Faz 1: veri keşfi

Veri sayıları, eksik değer incelemesi, grafikler, literatür özeti ve yöntem seçimi [`reports/faz1_raporu.md`](reports/faz1_raporu.md) dosyasındadır.

Ham veriler `data/` ve tekrar çalıştırıldığında üretilen ara çıktılar `results/` altında yerel tutulur. Raporda kullanılan paylaşılabilir grafikler ve özet CSV dosyaları `reports/figures/` altındadır.
