import cv2
import time
import json
import serial
import numpy as np
import firebase_admin
from datetime import datetime
from insightface.app import FaceAnalysis
from firebase_admin import credentials, db as firebase_db

# --- BAĞLANTILAR ---
# Lenovo bilgisayarındaki Arduino portu
arduino = serial.Serial('COM6', 9600)
time.sleep(2)

# Yüz Tanıma Modeli Hazırlığı
yuz_analiz_modeli = FaceAnalysis(name="buffalo_l")
yuz_analiz_modeli.prepare(ctx_id=0, det_size=(640, 640))

# Firebase Yetkilendirme
sertifika_yolu = "C:/Users/tunahan/Desktop/bitirmeProjesi/akilliKapi.json"
cred = credentials.Certificate(sertifika_yolu)
firebase_admin.initialize_app(cred, {"databaseURL": "https://akillikapi-default-rtdb.firebaseio.com/"})

# Kayıtlı Yüz Verilerini Yükleme
veriler_yolu = "C:/Users/tunahan/Desktop/bitirmeProjesi/embeddings.json"
ham_veriler = json.load(open(veriler_yolu))
yerel_hafiza = {}
for isim, pozlar in ham_veriler.items():
    vektor_listesi = []
    for poz in ["duz", "sag", "sol"]:
        if poz in pozlar and pozlar[poz]["mean_embedding"] is not None:
            vektor_listesi.append(np.array(pozlar[poz]["mean_embedding"]))
    if vektor_listesi:
        yerel_hafiza[isim] = vektor_listesi 

kamera = cv2.VideoCapture(0)

# Durum Değişkenleri
kapi_acik_mi = False
son_gorulme_zamani = time.time() 
bekleme_suresi = 5

print("Sistem Aktif. Senaryolar işleniyor...")

while True:
    ret, frame = kamera.read()
    if not ret:
        break

    # 1. ADIM: MOBİL DURUMUNU OKU
    kapi_durumu_mobil = firebase_db.reference("test_write6").get()

    # 2. ADIM: YÜZ TESPİTİ YAP
    tespit_edilenler = yuz_analiz_modeli.get(frame)
    su_an = time.time()
    
    kayitli_kisi_ekranda_mi = False 
    taninan_kisi_adi = ""
    en_yuksek_benzerlik = -1

    # Yüz analizi ve karşılaştırma döngüsü
    if len(tespit_edilenler) > 0:
        for yuz in tespit_edilenler:
            x1, y1, x2, y2 = map(int, yuz.bbox)
            yuz_izi = yuz.normed_embedding
            yuz_normu = np.linalg.norm(yuz_izi)

            gecerli_isim = "Bilinmiyor"
            gecerli_benzerlik = -1
            
            for isim, kayitli_izler in yerel_hafiza.items():
                for kayitli_iz in kayitli_izler:
                    oran = np.dot(yuz_izi, kayitli_iz) / (yuz_normu * np.linalg.norm(kayitli_iz))
                    if oran > gecerli_benzerlik:
                        gecerli_benzerlik = oran
                        gecerli_isim = isim

            if gecerli_benzerlik >= 0.5:
                kayitli_kisi_ekranda_mi = True
                if gecerli_benzerlik > en_yuksek_benzerlik:
                    en_yuksek_benzerlik = gecerli_benzerlik
                    taninan_kisi_adi = gecerli_isim

            # Ekrana çizim
            renk = (0, 255, 0) if gecerli_isim != "Bilinmiyor" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), renk, 2)
            cv2.putText(frame, f"{gecerli_isim} ({gecerli_benzerlik:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, renk, 2)

    # --- SENARYO MANTIĞI BAŞLIYOR ---

    # DURUM 1: Yüz Algılanırsa (Kapıyı aç veya süreyi sıfırla)
    if kayitli_kisi_ekranda_mi:
        son_gorulme_zamani = su_an  # Yüz olduğu sürece süre sıfırlanır
        
        if not kapi_acik_mi:
            # Kapı kapalıysa açıyoruz
            kapi_acik_mi = True
            log_verisi = {
                'person': taninan_kisi_adi,
                'accuracy': float(en_yuksek_benzerlik),
                'date_time': datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            }
            firebase_db.reference('test_write5').push(log_verisi)
            firebase_db.reference("test_write6").set("door opened")
            #arduino.write(b'1')
            print(f"Yüz tanındı ({taninan_kisi_adi}), kapı açıldı.")

    # DURUM 2 ve 3: Mobilden Açma İsteği (Sadece kapı kapalıysa işler)
    # Eğer kapı zaten açıksa mobil isteği sadece zamanlayıcıyı etkiler (aşağıdaki mantıkta)
    elif kapi_durumu_mobil == "door opened" and not kapi_acik_mi:
        kapi_acik_mi = True
        son_gorulme_zamani = su_an # Sayaç şimdi başladı
        #arduino.write(b'1')
        print("Mobil komut geldi, kapı açıldı. (5 saniye süre başladı)")

    # DURUM 4 ve 5: Kapanma Mantığı (Yüz YOKSA)
    # Kapı açıksa ve ekranda kimse yoksa süre işler
    if kapi_acik_mi and not kayitli_kisi_ekranda_mi:
        
        # Mobilden "kapat" denmişse süreyi beklemeden kapatabiliriz
        # Ancak isteğin şuydu: "Yüz algılanmıyorsa 5 saniye sonra kapansın"
        # Bu yüzden mobil "closed" dese bile süreyi kontrol ediyoruz veya manuel kapatıyoruz.
        # İsteğine sadık kalarak: Mobilden closed gelse bile, eğer yüz yoksa zaten süre işleyip kapanacak.
        
        gecen_sure = su_an - son_gorulme_zamani
        
        if gecen_sure >= bekleme_suresi:
            # Süre doldu, kapatıyoruz
            firebase_db.reference("test_write6").set("door closed") # Firebase'i güncelliyoruz ki tekrar açmasın
            #arduino.write(b'0')
            kapi_acik_mi = False
            print("Kapı kapandı (5 saniye doldu).")
        else:
            # Süre dolmadı, geri sayım gösteriyoruz
            kalan = int(bekleme_suresi - gecen_sure)
            # İstenilen yazı formatı:
            cv2.putText(frame, f"Kapi kapaniyor: {kalan}s", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Akilli Kapi Sistemi", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

kamera.release()
cv2.destroyAllWindows()