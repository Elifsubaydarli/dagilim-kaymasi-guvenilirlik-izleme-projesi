# Dağılım Kaymasına Duyarlı Güvenilirlik İzleme

Bu proje, tablosal makine öğrenmesi modellerinde dağılım kayması sırasında performans düşüşünü etiketsiz izleme sinyallerinin ne kadar erken ve ne kadar az yanlış alarmla yakalayabildiğini inceler. Proje önerisi: [`docs/proje-onerisi.pdf`](docs/proje-onerisi.pdf).

## Proje bilgileri

- **Proje başlığı:** Tablosal Veride Dağılım Kaymasına Duyarlı Güvenilirlik İzleme: Güven, Kalibrasyon, Veri Kayması ve Açıklama Sinyallerinin Erken Uyarı Performansının Karşılaştırmalı Analizi
- **Proje türü:** İki kişilik grup çalışması
- **Grup üyeleri:** Elif Su Baydarlı (241230017) ve Zehra Akgül (241230036)
- **Faz 1 kapsamı:** İki kaynak veri setinden üç sınıflandırma görevi incelenmiştir. ABD ACS PUMS verisinden, proje önerisindekiyle aynı Folktables ACSIncome ve ACSEmployment görevleri; UCI Diabetes 130-US Hospitals verisinden yeniden yatış görevi kullanılır.
- **Durum:** ACS ve UCI verilerinin keşif analizi ve ön işleme çalışmaları raporlanmıştır; dört model seçilmiştir ancak eğitilmemiştir. İkinci TableShift görevi henüz belirlenmemiştir.
- **TableShift kapsamı:** UCI Hospital Readmission görevi TableShift’in veri, hedef ve alan tanımıyla örtüşür; ancak kullanılan hasta bazlı bölmeler resmi TableShift bölmeleri değildir. ACSIncome ve ACSEmployment görevlerinin hedefleri de TableShift Income ve Unemployment görevleriyle aynı değildir. Bu nedenle önerideki en az iki TableShift göreviyle dış doğrulama henüz tamamlanmamıştır; ikinci görev Faz 2’de seçilip resmi bölmeler kullanılacaktır.

## Araştırma sorusu

Farklı kayma mekanizmalarında hangi etiketsiz sinyal performans bozulmasını en erken ve en az yanlış alarmla yakalar; sinyaller kayma türüne göre nasıl birleştirilmelidir?

## Çalışma planı

1. **Veri ve kapsam:** Faz 1’de Folktables ACSIncome ve ACSEmployment ile UCI Hospital Readmission görevlerinin sürüm, özellik ve örnek sayılarını `reports/faz1_raporu.md` içinde belirt. Proje önerisindeki en az iki TableShift göreviyle dış doğrulama henüz tamamlanmamıştır; ikinci görev Faz 2’de seçilip resmi bölmeler kullanılacaktır.
2. **Başlangıç modelleri:** Lojistik Regresyon, Random Forest, XGBoost ve uygun olmayan mimari kontrolü olarak 1B CNN'i kur; Accuracy, F1 ve AUC'yi kaydet.
3. **Kontrollü kaymalar:** Özellik/kovaryat, eksik veri, gürültü, zamansal/coğrafi, kavram ve kısayol kaymalarını artan şiddet seviyelerinde üret.
4. **İzleme sinyalleri:** Güven/belirsizlik; kalibrasyon; PSI, KS/Wasserstein ve alan sınıflandırıcısı; SHAP açıklama kayması; permütasyon önemi ve açıklama-bağımlılık uyuşmazlığını hesapla.
5. **Erken uyarı değerlendirmesi:** Eşikleri dağıtım içi bootstrap örneklerinde %5 yanlış alarm oranına göre belirle. Bozulma AUROC'si, uyarı önceliği ve yanlış alarm oranını ölç.
6. **Birleşim ve karşılaştırma:** Tek sinyal, sabit ağırlıklı ve kayma türüne duyarlı birleşimleri seçilen taban çizgileriyle karşılaştır; çoklu tohum, bootstrap aralıkları, eşleşmiş testler ve dışarıda bırakma doğrulaması kullan.
7. **Raporlama:** Bulguları ve sınırlılıkları yaz; yenilik iddiasını 15-20 çalışmalık literatür matrisiyle doğrula. Negatif sonuçları da raporla.


## Faz 1: veri keşfi

Veri sayıları, eksik değer incelemesi, grafikler, literatür özeti ve yöntem seçimi [`reports/faz1_raporu.md`](reports/faz1_raporu.md) dosyasındadır. Düzenlenebilir rapor `reports/faz1_raporu.docx`, PDF raporu `reports/faz1_raporu.pdf` olarak tutulur. Keşif kodları `src/data/phase1_eda.py` ve `src/data/phase1_readmission_eda.py` dosyalarındadır.

Ham veriler `data/` ve ön işleme matrisleri `results/phase1/preprocessed/` altında yerel tutulur. UCI analizinin küçük özet tabloları `results/phase1/`; raporda kullanılan grafikler ve özet tablolar `reports/figures/` altında sürümlenir.
