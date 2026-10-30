# Faz 1 Raporu

**Proje:** Tablosal Veride Dağılım Kaymasına Duyarlı Güvenilirlik İzleme
**Grup:** Elif Su Baydarlı (241230017), Zehra Akgül (241230036)
**Durum:** ACS ana verilerinin keşif analizi tamamlandı. TableShift dış görevleri henüz indirilip doğrulanmadı.

## 1. Amaç

Etiketlerin geciktiği durumlarda, model güveni, kalibrasyon, girdi dağılımı ve açıklama değişimi gibi işaretlerin performans düşüşünü ne kadar erken gösterebildiği incelenecektir. Farklı kaymalarda bu işaretlerin uyarı başarısı ve birlikte kullanımın katkısı değerlendirilecektir. Bu aşamada model eğitimi yapılmamıştır.

## 2. Veri

ACS verileri ABD Census Bureau’nun ACS PUMS mikroverisinden Folktables 0.0.12 ile alındı. 2014 ve 2018 yıllarının California (CA) ve Michigan (MI) örnekleri incelendi. Veri gerçek kişilere ait, etiketli tablosal veridir; yapay veri üretilmedi.

| Görev | Hedef | Yıl | Eyalet | Ham kişi | Filtre sonrası | Özellik | Negatif | Pozitif | Pozitif oranı |
|---|---|---:|:---:|---:|---:|---:|---:|---:|---:|
| ACSIncome | Gelir > 50.000 USD | 2014 | CA | 372.553 | 183.941 | 10 | 118.714 | 65.227 | %35,46 |
| ACSIncome | Gelir > 50.000 USD | 2014 | MI | 98.180 | 47.888 | 10 | 34.289 | 13.599 | %28,40 |
| ACSIncome | Gelir > 50.000 USD | 2018 | CA | 378.817 | 195.665 | 10 | 115.330 | 80.335 | %41,06 |
| ACSIncome | Gelir > 50.000 USD | 2018 | MI | 99.419 | 50.008 | 10 | 33.147 | 16.861 | %33,72 |
| ACSEmploymentFiltered | Çalışıyor (`ESR == 1`) | 2014 | CA | 372.553 | 292.975 | 17 | 132.740 | 160.235 | %54,69 |
| ACSEmploymentFiltered | Çalışıyor (`ESR == 1`) | 2014 | MI | 98.180 | 78.691 | 17 | 37.296 | 41.395 | %52,60 |
| ACSEmploymentFiltered | Çalışıyor (`ESR == 1`) | 2018 | CA | 378.817 | 302.640 | 17 | 130.184 | 172.456 | %56,98 |
| ACSEmploymentFiltered | Çalışıyor (`ESR == 1`) | 2018 | MI | 99.419 | 80.126 | 17 | 36.261 | 43.865 | %54,75 |

Her iki görev sayısal ve kategorik özellikler içerir. ACSIncome’da 10; ACSEmploymentFiltered’da 17 özellik vardır. ACSIncome hedefi yıllık kişisel gelirin 50.000 USD üzerinde olmasıdır. İstihdam görevi Folktables’taki 17 özellikli, 16–90 yaş aralığına göre filtrelenmiş `ACSEmploymentFiltered` sürümüdür. İki görev de ikili sınıflandırmadır ve tabloda verilen tüm örneklerin etiketi vardır. Oranlar `PWGTP` kişi ağırlığı uygulanmadan hesaplanmıştır; nüfus tahmini değildir.

Kaynaklar: [Folktables](https://github.com/socialfoundations/folktables) ve [ACS PUMS](https://www.census.gov/programs-surveys/acs/microdata.html). Dış doğrulama için [College Scorecard](https://github.com/mlfoundations/tableshift) ve [Hospital Readmission](https://github.com/mlfoundations/tableshift) görevleri seçilmiştir; henüz indirilip incelenmemiştir.

## 3. Eksik değer ve ön işleme

Eksik değerler, görev filtresinden sonra ve Folktables’ın eksikleri `-1` ile kodlamasından önce hesaplandı.

- ACSIncome’da incelenen özelliklerde eksik değer bulunmadı.
- ACSEmploymentFiltered’da ortalama hücre eksikliği yaklaşık %7’dir. `ESP` sütununda %98,42–%98,62, `GCL` sütununda yaklaşık %18,47–%22,22 eksiklik görüldü.
- `ESP`, ilk model hattından çıkarılacak ve etkisi ayrıca kontrol edilecektir. `-1` eksik değer olarak ele alınacaktır.
- Sayısal değişkenler medyanla doldurulup ölçeklenecek; kategorik değişkenler en sık değerle doldurulup one-hot kodlanacaktır. Dönüşümler yalnızca eğitim verisinde fit edilecektir.
- Planlanan bölmede 2014 CA eğitim, 2018 CA zamansal test ve MI coğrafi test verisi olarak kullanılacaktır. Bölme tohumu ve doğrulama yöntemi modelleme öncesi sabitlenecektir.

Ön işleme kodu: [`src/data/preprocessing.py`](../src/data/preprocessing.py).

## 4. Keşif analizi

Grafikler ve sayısal özetler `reports/figures/` klasöründedir.

![Görev ve bağlam başına örnek sayısı](figures/ornek_sayilari.png)

![Yıl ve eyalete göre pozitif sınıf oranı](figures/sinif_oranlari.png)

![Yaş dağılımları](figures/yas_dagilimlari.png)

2014’ten 2018’e ACSIncome pozitif oranı CA’da %35,46’dan %41,06’ya, MI’da %28,40’tan %33,72’ye çıktı. ACSEmploymentFiltered oranı CA’da %54,69’dan %56,98’e, MI’da %52,60’tan %54,75’e değişti. Bu, sınıf oranlarının bağlamlara göre farklı olduğunu gösterir; tek başına model performansının düştüğünü göstermez.

## 5. Literatür ve yöntem seçimi

| Çalışma | Yöntem/veri | Projeyle ilişkisi |
|---|---|---|
| Ding et al. (2021), [Retiring Adult](https://arxiv.org/abs/2108.04884) | Folktables ACS gelir ve istihdam görevlerini tanımlar. | Kullandığımız görevlerin kaynağıdır; izleme sinyallerini karşılaştırmaz. |
| Rabanser et al. (2019), [Failing Loudly](https://arxiv.org/abs/1810.11953) | İki örneklem testi ve sınıflandırıcıyla kayma tespiti. | Girdi dağılımı sinyalleri için yöntemsel dayanak sağlar. |
| Ovadia et al. (2019), [uncertainty under shift](https://arxiv.org/abs/1906.02530) | Kayma altında belirsizlik ve kalibrasyon değerlendirmesi. | Güven ve kalibrasyon ölçütlerinin incelenmesini destekler. |
| Garg et al. (2022), [ATC](https://arxiv.org/abs/2201.04234) | Etiketsiz tahmin güveninden dağıtım dışı başarı tahmini. | Gecikmeli etiket durumuyla doğrudan ilişkilidir. |
| Mougan et al. (2022), [Explanation Shift](https://arxiv.org/abs/2210.12369) | Tablosal veride açıklama uzayı kayması. | Açıklama değişimini izleme sinyali olarak ele alır. |
| Gardner et al. (2023), [TableShift](https://arxiv.org/abs/2312.07577) | Tablosal görevlerde gerçek dünya alan kaymaları. | Seçilen dış doğrulama görevlerinin benchmark kaynağıdır. |
| Liu et al. (2023), [distribution shifts in tabular data](https://arxiv.org/abs/2307.05284) | Tablosal veride kayma türlerinin tanımlanması. | Deneylerde kayma türlerini ayrı ele almayı destekler. |
| Grinsztajn et al. (2022), [tree-based models](https://arxiv.org/abs/2207.08815) | Tablosal veride ağaç ve derin öğrenme modellerinin karşılaştırılması. | Random Forest ve XGBoost seçimine dayanak sağlar. |
| Białek et al. (2025), [PAPE](https://papers.nips.cc/paper_files/paper/2025/hash/ebd8a977883fd8d5bccf9575e873ce75-Abstract-Conference.html) | Census/Folktables görevlerinde etiketsiz başarı tahmini. | Çalışmanın problemine en yakın kaynaklardan biridir; DOI: [10.52202/085713-5379](https://doi.org/10.52202/085713-5379). |

Bu çalışmaların tümü aynı ACS veri sürümünü ve araştırma sorusunu kullanmamaktadır. Bu nedenle aynı problem ve veri seti üzerinde en az beş çalışma bulunduğu iddia edilmemektedir. Literatür tablosu ilgili yöntemleri ve veri kaynaklarını özetlemektedir; araştırma boşluğu daha kapsamlı taramayla doğrulanacaktır.

Faz 2’de Lojistik Regresyon, Random Forest ve XGBoost karşılaştırılacaktır. Başarım Accuracy, F1 ve ROC-AUC; olasılık kalibrasyonu Brier skoru ve ECE ile değerlendirilecektir.

## 6. Sonraki deney planı

ACS verisinde özellik, eksik veri, gürültü, yıl/eyalet, kavram ve kısayol kaymaları incelenecektir. Güven/belirsizlik, kalibrasyon, PSI/KS/Wasserstein, alan sınıflandırıcısı ve açıklama değişimi sinyalleri karşılaştırılacaktır. Eşikler dağıtım içi veride %5 yanlış alarm hedefiyle belirlenecek; erken uyarı ve yanlış alarm ölçülecektir. Bu deneyler henüz yapılmamıştır.


## Kaynakça

1. Ding, F., Hardt, M., Miller, J., & Schmidt, L. (2021). *Retiring Adult: New datasets for fair machine learning*. NeurIPS. https://doi.org/10.48550/arXiv.2108.04884
2. Rabanser, S., Günnemann, S., & Lipton, Z. C. (2019). *Failing loudly: An empirical study of methods for detecting dataset shift*. NeurIPS. https://doi.org/10.48550/arXiv.1810.11953
3. Ovadia, Y. et al. (2019). *Can you trust your model's uncertainty? Evaluating predictive uncertainty under dataset shift*. NeurIPS. https://doi.org/10.48550/arXiv.1906.02530
4. Garg, S. et al. (2022). *Leveraging unlabeled data to predict out-of-distribution performance*. ICLR. https://doi.org/10.48550/arXiv.2201.04234
5. Mougan, C. et al. (2022). *Explanation shift: Detecting distribution shifts on tabular data via the explanation space*. NeurIPS Workshop. https://doi.org/10.48550/arXiv.2210.12369
6. Gardner, J., Popovic, Z., & Schmidt, L. (2023). *Benchmarking distribution shift in tabular data with TableShift*. NeurIPS Datasets & Benchmarks. https://doi.org/10.48550/arXiv.2312.07577
7. Liu, J. et al. (2023). *On the need for a language describing distribution shifts: Illustrations on tabular datasets*. NeurIPS Datasets & Benchmarks. https://doi.org/10.48550/arXiv.2307.05284
8. Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). *Why do tree-based models still outperform deep learning on typical tabular data?* NeurIPS Datasets & Benchmarks. https://doi.org/10.48550/arXiv.2207.08815
9. Białek, J., Kivimäki, J., Kuberski, W., & Perrakis, N. (2025). *Estimating model performance under covariate shift without labels*. NeurIPS 2025. https://doi.org/10.52202/085713-5379
