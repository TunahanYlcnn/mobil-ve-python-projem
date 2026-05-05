# 🔐 Akıllı Kapı Kilitleme Sistemi

Bu proje, yüz tanıma teknolojisi, mobil uygulama desteği ve donanım kontrolünü birleştiren modern bir güvenlik sistemidir.

## 🚀 Proje Hakkında
Sistem, kapıdaki kişiyi yüz tanıma algoritmalarıyla teşhis eder, verileri Firebase üzerinden anlık olarak senkronize eder ve yetkili kişilere mobil uygulama üzerinden kontrol imkanı sunar.

## 🛠️ Kullanılan Teknolojiler
* **Yazılım Dilleri:** Python, Kotlin, C++ (Arduino).
* **Kütüphaneler:** OpenCV, ArcFace, MediaPipe, Firebase Admin SDK.
* **Donanım:** Arduino / Raspberry Pi Zero 2.
* **Veritabanı ve Bulut:** Firebase Realtime Database, ThinkSpeak.

---

## 📂 Dosya Yapısı ve Görevleri

Proje ana dizinindeki önemli dosyaların işlevleri aşağıdadır:

### 📱 Mobil Uygulama
* **bitirmeMobil/**: Sistemin kontrol edildiği ve bildirimlerin alındığı Android tabanlı mobil uygulama kodları.

### 🐍 Python (Yüz Tanıma ve Mantık Katmanı)
* **FinalKod.py**: Sistemin ana çalışma dosyası.
* **arcFaceAlgılama.py**: Yüksek doğruluklu yüz tanıma algoritması.
* **faceDEtect.py / haar.py / dnn.py**: Farklı yöntemlerle yüz algılama modülleri.
* **firebase.py / firebaseMesajGönder.py**: Veritabanı iletişimi ve bildirim yönetimi.
* **veriOluşturma.py**: Tanınacak kişilerin yüz verilerini sisteme kaydetme aracı.

### 🔌 Donanım
* **bitirmeArdu.ino**: Kapı kilidini ve sensörleri kontrol eden Arduino yazılımı.
* **arduinoVeriGönder.py**: Python ve donanım arasındaki seri haberleşmeyi sağlar.

---

## ⚙️ Kurulum ve Çalıştırma
1.  **Gereksinimleri Yükleyin:**
```bash
pip install opencv-python firebase-admin pyserial
```
2. **Firebase Ayarları:** google-services.json dosyanızı ilgili dizinlere eklemeyi unutmayın.
3. **Donanım Bağlantısı:** Arduino'yu USB üzerinden bağlayın ve port numarasını arduinoVeriGönder.py içinde güncelleyin.
4. **Sistemi Başlatın:**
```bash
python FinalKod.py
```



