# Kesim Optimizasyon Uygulaması
Bu proje, Tkinter tabanlı, çoklu dil ve tema destekli bir kesim optimizasyon uygulamasıdır.  
Kullanıcıların parça listelerine göre en uygun kesim planını oluşturmasını sağlar ve sonuçları görsel olarak görüntüleyip, Excel ve PDF formatında raporlar oluşturmasına olanak tanır.
---
## Özellikler
- Parça ekleme, düzenleme ve silme işlemleri  
- Kesim planı optimizasyonu (First Fit algoritması ve Optuna destekli optimizasyon)  
- Çoklu dil desteği: Türkçe, İngilizce, Almanca, Fransızca, İspanyolca, İtalyanca  
- Tema yönetimi ve 20+ farklı tema seçeneği (ttkthemes desteği)  
- Optimizasyon sonucunun grafiksel görselleştirilmesi (matplotlib)  
- Excel ve PDF formatında detaylı raporlama  
- Fire, verimlilik ve maliyet hesaplama özellikleri  
- Hata yönetimi ve güvenli kullanıcı girdi doğrulaması  
---
## Gereksinimler
- Python 3.7 ve üzeri  
- Gerekli paketler:
  - `Tkinter` (Çoğu Python kurulumunda yüklü gelir)  
  - `matplotlib`  
  - `optuna`  
  - `openpyxl`  
  - `reportlab`  
  - `ttkthemes` (tema desteği için)  
---
## Kurulum ve Çalıştırma
1. Gerekli paketleri yükleyin: pip install matplotlib optuna openpyxl reportlab ttkthemes
2. Proje klasöründe terminali açın ve programı çalıştırın:
    python main.py
---
## Kullanım
- Arayüzde parçalarınızı "Parça Adı", "Uzunluğu (mm)" ve "Adet" bilgilerini girerek listeye ekleyin.  
- "Optimize Et" butonuna basarak en uygun kesim planını oluşturun.  
- Çıkan planın görselini inceleyebilir, gerekli görsel ve istatistik bilgileri görebilirsiniz.  
- Excel veya PDF butonları ile raporları dışa aktarabilirsiniz.  
- Menüden tema seçebilir ve dil değiştirebilirsiniz.  
- Projenizi kaydedip daha sonra tekrar yükleyebilirsiniz.  
- CSV formatında parçalar içe ve dışa aktarılabilir.
---
## Proje Dosyaları
- `main.py` — Uygulama giriş noktası  
- `app.py` — Tkinter tabanlı GUI ve uygulama yönetimi  
- `constants.py` — Çoklu dil ve sabit değerler  
- `gui_helpers.py` — Çeviri, yardımcı fonksiyonlar  
- `optimization.py` — Kesim optimizasyon algoritmaları  
- `file_handlers.py` — Dosya okuma/yazma, dışa aktarma fonksiyonları  
- `theme_manager.py` — Tema yönetimi ve uygulamaya entegre edilmesi
---
## Lisans
Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakabilirsiniz.
---
## Katkıda Bulunma
Katkılarınızı memnuniyetle karşılıyoruz. Lütfen öncelikle yeni bir issue açarak önerinizi veya hata bildirimlerinizi paylaşın. Pull request göndermek için:
1. Fork yapın  
2. Değişikliklerinizi yapın  
3. Pull request gönderin  
---
© 2025 Kesim Optimizasyon Projesi  
   

